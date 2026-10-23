"""
SignalDesk AI - Sales Intelligence Inbox
Main Streamlit application
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import json

# Import custom modules
from src.database import Database
from src.ingestion import process_import, create_sample_template
from src.routing import recommend_routing, get_difficult_routing_example, TEAMS
from src.insights import generate_findings, get_rejected_decision_example
from src.exports import (
    export_conversations_csv, export_routing_decisions_csv,
    export_findings_json, export_audit_log, generate_manifest
)
from src.validation import VALID_STAGES, VALID_SENTIMENTS, VALID_URGENCIES, VALID_CHANNELS

# Page configuration
st.set_page_config(
    page_title="SignalDesk AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
@st.cache_resource
def get_database():
    return Database()

db = get_database()


# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #6366f1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .synthetic-label {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("📊 SignalDesk AI")
st.sidebar.markdown("**Sales Intelligence Inbox**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    [
        "📈 Executive Dashboard",
        "💬 Conversation Explorer",
        "🎯 Intelligent Routing Lab",
        "🔍 Findings & Decisions",
        "📥 Import & Sync",
        "✏️ Manual Editing & Audit",
        "📤 Export Center"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown('<div class="synthetic-label">🧪 DEMO MODE - SYNTHETIC DATA</div>', unsafe_allow_html=True)
st.sidebar.markdown("This application uses synthetic demo data for demonstration purposes.")


# ============================================================================
# PAGE: Executive Dashboard
# ============================================================================
if page == "📈 Executive Dashboard":
    st.markdown('<div class="main-header">📈 Executive Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-time sales conversation intelligence and metrics</div>', unsafe_allow_html=True)
    
    # Load data
    df = db.get_all_conversations()
    
    if df.empty:
        st.warning("No conversation data available. Please import data from the Import & Sync page.")
        st.info("👉 Use the sidebar to navigate to **📥 Import & Sync** to load the sample dataset.")
    else:
        # Filters
        st.subheader("🔍 Filters")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            date_filter = st.selectbox("Date Range", ["All Time", "Last 7 Days", "Last 30 Days", "Custom"])
        
        with col2:
            stages = ['All'] + sorted(df['stage'].dropna().unique().tolist())
            stage_filter = st.selectbox("Stage", stages)
        
        with col3:
            owners = ['All'] + sorted(df['owner'].dropna().unique().tolist())
            owner_filter = st.selectbox("Owner", owners)
        
        with col4:
            if st.button("🔄 Reset Filters"):
                st.rerun()
        
        # Apply filters
        filtered_df = df.copy()
        
        if stage_filter != 'All':
            filtered_df = filtered_df[filtered_df['stage'] == stage_filter]
        
        if owner_filter != 'All':
            filtered_df = filtered_df[filtered_df['owner'] == owner_filter]
        
        if date_filter != "All Time":
            try:
                filtered_df['conversation_date'] = pd.to_datetime(filtered_df['conversation_date'])
                today = datetime.now()
                
                if date_filter == "Last 7 Days":
                    cutoff = today - timedelta(days=7)
                    filtered_df = filtered_df[filtered_df['conversation_date'] >= cutoff]
                elif date_filter == "Last 30 Days":
                    cutoff = today - timedelta(days=30)
                    filtered_df = filtered_df[filtered_df['conversation_date'] >= cutoff]
            except:
                pass
        
        st.markdown("---")
        
        # Key Metrics
        st.subheader("📊 Key Metrics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Conversations", len(filtered_df))
        
        with col2:
            # New conversations (last 7 days)
            try:
                filtered_df['conversation_date'] = pd.to_datetime(filtered_df['conversation_date'])
                recent = filtered_df[filtered_df['conversation_date'] >= datetime.now() - timedelta(days=7)]
                st.metric("New (7 days)", len(recent))
            except:
                st.metric("New (7 days)", "N/A")
        
        with col3:
            # High priority
            try:
                filtered_df['priority_score_num'] = pd.to_numeric(filtered_df['priority_score'], errors='coerce')
                high_priority = filtered_df[filtered_df['priority_score_num'] >= 75]
                st.metric("High Priority", len(high_priority))
            except Exception as e:
                st.metric("High Priority", "N/A")
        
        with col4:
            # Follow-ups due/overdue
            try:
                filtered_df['follow_up_date'] = pd.to_datetime(filtered_df['follow_up_date'], errors='coerce')
                today = pd.Timestamp.now()
                due_soon = filtered_df[
                    (filtered_df['follow_up_date'].notna()) & 
                    (filtered_df['follow_up_date'] <= today + timedelta(days=7))
                ]
                st.metric("Follow-ups Due", len(due_soon))
            except:
                st.metric("Follow-ups Due", "N/A")
        
        with col5:
            # Open opportunities
            open_stages = ['discovery', 'proposal', 'negotiation']
            open_opps = filtered_df[filtered_df['stage'].isin(open_stages)]
            st.metric("Open Opportunities", len(open_opps))
        
        st.markdown("---")
        
        # Pipeline value
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Pipeline Value")
            try:
                # Calculate known pipeline value
                pipeline_df = filtered_df[filtered_df['stage'].isin(['discovery', 'proposal', 'negotiation'])].copy()
                
                known_value = 0
                unknown_count = 0
                
                for val in pipeline_df['deal_value']:
                    try:
                        if pd.notna(val) and str(val).lower().strip() not in ['unknown', 'nan', '']:
                            # Remove any currency symbols and commas
                            clean_val = str(val).replace('$', '').replace(',', '').strip()
                            if clean_val:
                                known_value += float(clean_val)
                        else:
                            unknown_count += 1
                    except (ValueError, AttributeError):
                        unknown_count += 1
                
                st.metric("Known Pipeline Value", f"${known_value:,.0f}")
                if unknown_count > 0:
                    st.caption(f"⚠️ {unknown_count} opportunities have unknown deal values")
                st.caption("*Calculation: Sum of known deal values in discovery, proposal, and negotiation stages*")
            except Exception as e:
                st.metric("Known Pipeline Value", "Error calculating")
                st.caption("Unable to calculate pipeline value")
        
        with col2:
            st.subheader("📈 Conversations by Stage")
            try:
                stage_counts = filtered_df['stage'].value_counts()
                fig = px.pie(
                    values=stage_counts.values,
                    names=stage_counts.index,
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.info("No stage data available")
        
        # Additional charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👥 Conversations by Owner")
            try:
                owner_counts = filtered_df['owner'].value_counts().head(10)
                fig = px.bar(
                    x=owner_counts.values,
                    y=owner_counts.index,
                    orientation='h',
                    color_discrete_sequence=['#6366f1']
                )
                fig.update_layout(
                    xaxis_title="Count",
                    yaxis_title="Owner",
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.info("No owner data available")
        
        with col2:
            st.subheader("🎯 Priority Distribution")
            try:
                filtered_df_temp = filtered_df.copy()
                filtered_df_temp['priority_score_num'] = pd.to_numeric(filtered_df_temp['priority_score'], errors='coerce')
                valid_priorities = filtered_df_temp['priority_score_num'].dropna()
                
                if len(valid_priorities) > 0:
                    priority_bins = pd.cut(
                        valid_priorities,
                        bins=[0, 25, 50, 75, 100],
                        labels=['Low (0-25)', 'Medium (25-50)', 'High (50-75)', 'Critical (75-100)'],
                        include_lowest=True
                    )
                    priority_counts = priority_bins.value_counts()
                    
                    fig = px.bar(
                        x=priority_counts.index.astype(str),
                        y=priority_counts.values,
                        color_discrete_sequence=['#8b5cf6']
                    )
                    fig.update_layout(
                        xaxis_title="Priority Level",
                        yaxis_title="Count",
                        height=400,
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No valid priority data available")
            except Exception as e:
                st.info(f"No priority data available")
        
        # Sentiment and recent activity
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("😊 Sentiment Distribution")
            try:
                sentiment_counts = filtered_df['sentiment'].value_counts()
                colors = {'positive': '#10b981', 'neutral': '#6b7280', 'negative': '#ef4444', 'unknown': '#d1d5db'}
                color_map = [colors.get(s, '#6366f1') for s in sentiment_counts.index]
                
                fig = px.bar(
                    x=sentiment_counts.index,
                    y=sentiment_counts.values,
                    color=sentiment_counts.index,
                    color_discrete_map=colors
                )
                fig.update_layout(
                    xaxis_title="Sentiment",
                    yaxis_title="Count",
                    height=300,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.info("No sentiment data available")
        
        with col2:
            st.subheader("📅 Recent Activity")
            try:
                recent_convs = filtered_df.nlargest(5, 'conversation_date')
                for _, row in recent_convs.iterrows():
                    with st.container():
                        st.markdown(f"**{row['customer_name']}** - {row['company']}")
                        st.caption(f"{row['stage']} | {row['conversation_date']}")
            except:
                st.info("No recent activity")
        
        # Top next actions
        st.markdown("---")
        st.subheader("✅ Top Recommended Next Actions")
        try:
            action_counts = filtered_df['next_action'].value_counts().head(5)
            for action, count in action_counts.items():
                st.markdown(f"- **{action}** ({count} conversations)")
        except:
            st.info("No next action data available")


# ============================================================================
# PAGE: Conversation Explorer
# ============================================================================
elif page == "💬 Conversation Explorer":
    st.markdown('<div class="main-header">💬 Conversation Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Search and analyze individual conversations</div>', unsafe_allow_html=True)
    
    df = db.get_all_conversations()
    
    if df.empty:
        st.warning("No conversation data available. Please import data from the Import & Sync page.")
    else:
        # Search and filters
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_query = st.text_input("🔍 Search", placeholder="Search by customer, company, or summary...")
        
        with col2:
            stage_options = ['All'] + sorted(df['stage'].dropna().unique().tolist())
            stage_filter = st.selectbox("Stage", stage_options, key="explorer_stage")
        
        with col3:
            sentiment_options = ['All'] + sorted(df['sentiment'].dropna().unique().tolist())
            sentiment_filter = st.selectbox("Sentiment", sentiment_options)
        
        # Apply filters
        filtered_df = df.copy()
        
        if search_query:
            mask = (
                filtered_df['customer_name'].str.contains(search_query, case=False, na=False) |
                filtered_df['company'].str.contains(search_query, case=False, na=False) |
                filtered_df['conversation_summary'].str.contains(search_query, case=False, na=False) |
                filtered_df['source_id'].str.contains(search_query, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        if stage_filter != 'All':
            filtered_df = filtered_df[filtered_df['stage'] == stage_filter]
        
        if sentiment_filter != 'All':
            filtered_df = filtered_df[filtered_df['sentiment'] == sentiment_filter]
        
        st.markdown(f"**{len(filtered_df)} conversations found**")
        
        if filtered_df.empty:
            st.info("No conversations match your search criteria.")
        else:
            # Display table
            display_cols = ['source_id', 'customer_name', 'company', 'conversation_date', 
                          'stage', 'sentiment', 'urgency', 'owner']
            
            available_cols = [col for col in display_cols if col in filtered_df.columns]
            
            st.dataframe(
                filtered_df[available_cols],
                use_container_width=True,
                height=400
            )
            
            # Conversation detail view
            st.markdown("---")
            st.subheader("📄 Conversation Details")
            
            conv_options = [f"{row['source_id']} - {row['customer_name']} ({row['company']})" 
                          for _, row in filtered_df.iterrows()]
            
            if conv_options:
                selected_conv = st.selectbox("Select a conversation to view details", conv_options)
                
                if selected_conv:
                    source_id = selected_conv.split(' - ')[0]
                    conv = db.get_conversation_by_source_id(source_id)
                    
                    if conv:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Customer Information**")
                            st.write(f"**Name:** {conv.get('customer_name', 'N/A')}")
                            st.write(f"**Company:** {conv.get('company', 'N/A')}")
                            st.write(f"**Date:** {conv.get('conversation_date', 'N/A')}")
                            st.write(f"**Channel:** {conv.get('channel', 'N/A')}")
                            st.write(f"**Sentiment:** {conv.get('sentiment', 'N/A')}")
                        
                        with col2:
                            st.markdown("**Deal Information**")
                            st.write(f"**Stage:** {conv.get('stage', 'N/A')}")
                            st.write(f"**Deal Value:** {conv.get('deal_value', 'N/A')}")
                            st.write(f"**Urgency:** {conv.get('urgency', 'N/A')}")
                            st.write(f"**Intent:** {conv.get('customer_intent', 'N/A')}")
                            st.write(f"**Objections:** {conv.get('objections', 'N/A')}")
                        
                        st.markdown("---")
                        st.markdown("**Conversation Summary**")
                        st.write(conv.get('conversation_summary', 'N/A'))
                        
                        st.markdown("**Notes/Transcript**")
                        st.text_area("", conv.get('transcript_or_notes', 'N/A'), height=150, disabled=True)
                        
                        st.markdown("---")
                        st.markdown("**Routing & Actions**")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Owner:** {conv.get('owner', 'N/A')}")
                            st.write(f"**Priority Score:** {conv.get('priority_score', 'N/A')}")
                            st.write(f"**Status:** {conv.get('status', 'N/A')}")
                        
                        with col2:
                            st.write(f"**Next Action:** {conv.get('next_action', 'N/A')}")
                            st.write(f"**Follow-up Date:** {conv.get('follow_up_date', 'N/A')}")
                            manual = "Yes" if conv.get('manual_override') == 'TRUE' else "No"
                            st.write(f"**Manual Override:** {manual}")
                        
                        st.markdown("**Routing Explanation**")
                        st.info(conv.get('routing_reason', 'No routing reason available'))
                        
                        st.markdown("**Evidence Quote**")
                        quote = conv.get('evidence_quote', 'No evidence quote available')
                        st.success(f"💬 \"{quote}\"")


# ============================================================================
# PAGE: Intelligent Routing Lab
# ============================================================================
elif page == "🎯 Intelligent Routing Lab":
    st.markdown('<div class="main-header">🎯 Intelligent Routing Lab</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Transparent conversation routing with explainable recommendations</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔍 Test Routing", "👥 Team Profiles", "🤔 Difficult Example"])
    
    with tab1:
        st.subheader("Test Routing Engine")
        st.write("Select a conversation to see routing recommendations and scores for all teams.")
        
        df = db.get_all_conversations()
        
        if df.empty:
            st.warning("No conversation data available. Please import data first.")
        else:
            conv_options = [f"{row['source_id']} - {row['customer_name']} ({row['company']})" 
                          for _, row in df.iterrows()]
            
            selected = st.selectbox("Select Conversation", conv_options)
            
            if selected:
                source_id = selected.split(' - ')[0]
                conv = db.get_conversation_by_source_id(source_id)
                
                if conv:
                    # Show conversation context
                    with st.expander("📋 Conversation Context", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Stage:** {conv.get('stage')}")
                            st.write(f"**Urgency:** {conv.get('urgency')}")
                        with col2:
                            st.write(f"**Intent:** {conv.get('customer_intent')}")
                            st.write(f"**Deal Value:** {conv.get('deal_value')}")
                        with col3:
                            st.write(f"**Sentiment:** {conv.get('sentiment')}")
                            st.write(f"**Objections:** {conv.get('objections')}")
                        
                        st.markdown("**Summary:**")
                        st.write(conv.get('conversation_summary'))
                    
                    # Get routing recommendation
                    if st.button("🎯 Calculate Routing", type="primary"):
                        recommendation = recommend_routing(conv)
                        
                        st.markdown("---")
                        st.subheader("🎯 Routing Recommendation")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Recommended Team", recommendation['recommended_team'])
                        
                        with col2:
                            st.metric("Priority Score", f"{recommendation['priority_score']:.0f}")
                        
                        with col3:
                            st.metric("Confidence", recommendation['confidence'])
                        
                        st.markdown("**Routing Reason:**")
                        st.info(recommendation['routing_reason'])
                        
                        st.markdown("**Evidence from Source:**")
                        st.success(f"💬 \"{recommendation['evidence_quote']}\"")
                        
                        st.markdown("**Suggested Next Action:**")
                        st.write(recommendation['next_action'])
                        
                        # Show all team scores
                        st.markdown("---")
                        st.subheader("📊 All Team Scores")
                        
                        scores_df = pd.DataFrame([
                            {'Team': team, 'Score': score}
                            for team, score in recommendation['all_scores'].items()
                        ]).sort_values('Score', ascending=False)
                        
                        fig = px.bar(
                            scores_df,
                            x='Score',
                            y='Team',
                            orientation='h',
                            color='Score',
                            color_continuous_scale='Blues'
                        )
                        fig.update_layout(height=300, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Manual override option
                        st.markdown("---")
                        st.subheader("✏️ Manual Override")
                        st.write("As a manager, you can override the automated recommendation.")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            manual_team = st.selectbox(
                                "Select different team",
                                list(TEAMS.keys()),
                                index=list(TEAMS.keys()).index(recommendation['recommended_team'])
                            )
                        
                        with col2:
                            override_reason = st.text_input("Reason for override (optional)")
                        
                        if st.button("Apply Manual Override"):
                            # Update with manual override
                            updates = {
                                'owner': manual_team,
                                'manual_override': 'TRUE'
                            }
                            
                            db.update_conversation(source_id, updates, preserve_manual=False)
                            
                            # Log audit
                            db.log_audit_event(
                                action_type='manual_override',
                                record_id=source_id,
                                field_name='owner',
                                previous_value=recommendation['recommended_team'],
                                new_value=manual_team,
                                reason=override_reason or 'Manual manager override'
                            )
                            
                            st.success(f"✅ Routing overridden to {manual_team}")
                            st.rerun()
    
    with tab2:
        st.subheader("Team Profiles & Expertise")
        st.write("These are the configurable team definitions used by the routing engine.")
        
        for team_name, team_info in TEAMS.items():
            with st.expander(f"**{team_name}**", expanded=False):
                st.write(f"**Description:** {team_info['description']}")
                st.write(f"**Primary Stages:** {', '.join(team_info['stages'])}")
                st.write(f"**Urgency Levels:** {', '.join(team_info['urgencies'])}")
                st.write(f"**Customer Intents:** {', '.join(team_info['intents'])}")
                st.write(f"**Keywords:** {', '.join(team_info['keywords'])}")
    
    with tab3:
        st.subheader("Difficult Routing Example")
        st.write("This example demonstrates a conversation that could reasonably be routed to multiple teams.")
        
        st.markdown(get_difficult_routing_example())


# ============================================================================
# PAGE: Findings & Decisions
# ============================================================================
elif page == "🔍 Findings & Decisions":
    st.markdown('<div class="main-header">🔍 Findings & Decision Support</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Evidence-backed insights and decision analysis</div>', unsafe_allow_html=True)
    
    df = db.get_all_conversations()
    
    if df.empty:
        st.warning("No conversation data available. Please import data first.")
    else:
        # Generate findings
        findings = generate_findings(df)
        
        st.subheader(f"📊 {len(findings)} Key Findings")
        
        for idx, finding in enumerate(findings, 1):
            with st.expander(f"**Finding {idx}: {finding['title']}**", expanded=True):
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("**📈 Metric**")
                    st.write(finding['metric'])
                    
                    st.markdown("**💡 Business Implication**")
                    st.write(finding['implication'])
                    
                    st.markdown("**✅ Recommended Action**")
                    st.success(finding['recommendation'])
                
                with col2:
                    st.markdown("**📋 Supporting Conversations**")
                    if finding['supporting_conversations']:
                        for conv_id in finding['supporting_conversations'][:5]:
                            st.write(f"- {conv_id}")
                    else:
                        st.write("N/A")
                
                # Show evidence
                st.markdown("**🔍 Evidence**")
                if finding['evidence'] and len(finding['evidence']) > 0:
                    for evidence in finding['evidence'][:3]:
                        if isinstance(evidence, dict):
                            st.markdown(f"""
                            **{evidence.get('conversation_id', 'N/A')}** - {evidence.get('customer', 'N/A')} ({evidence.get('company', 'N/A')})
                            
                            > "{evidence.get('quote', 'No quote available')}"
                            """)
                        else:
                            st.write(evidence)
                else:
                    st.write("No specific evidence quotes available")
                
                # Show limitations
                if finding.get('limitations'):
                    st.markdown("**⚠️ Limitations**")
                    st.caption(finding['limitations'])
        
        # Rejected decision
        st.markdown("---")
        st.subheader("❌ Considered and Rejected Decision")
        st.markdown(get_rejected_decision_example())


# ============================================================================
# PAGE: Import & Sync
# ============================================================================
elif page == "📥 Import & Sync":
    st.markdown('<div class="main-header">📥 Import & Synchronization</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload and sync conversation data with duplicate detection</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📤 Upload File", "📋 Import History", "📥 Sample Template"])
    
    with tab1:
        st.subheader("Upload Conversation Data")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**Supported Formats:** CSV, Excel (.xlsx, .xls)")
            st.write("**Required Column:** source_id")
            
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=['csv', 'xlsx', 'xls'],
                help="Upload a CSV or Excel file with conversation data"
            )
        
        with col2:
            st.info("**Quick Start:** Load the sample dataset to explore the application.")
            if st.button("📊 Load Sample Dataset", type="primary"):
                sample_path = "data/sample_conversations.csv"
                if Path(sample_path).exists():
                    result = process_import(sample_path, db)
                    
                    if result['success']:
                        st.success("✅ Sample dataset loaded successfully!")
                        st.json(result['stats'])
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result.get('error')}")
                else:
                    st.error("Sample dataset file not found.")
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            temp_path = f"temp_{uploaded_file.name}"
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"File uploaded: {uploaded_file.name}")
            
            # Preview
            try:
                if uploaded_file.name.endswith('.csv'):
                    preview_df = pd.read_csv(temp_path).head(5)
                else:
                    preview_df = pd.read_excel(temp_path).head(5)
                
                st.subheader("📋 Preview (First 5 rows)")
                st.dataframe(preview_df, use_container_width=True)
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Confirm Import", type="primary"):
                        with st.spinner("Processing import..."):
                            result = process_import(temp_path, db)
                        
                        # Clean up temp file
                        try:
                            Path(temp_path).unlink()
                        except:
                            pass
                        
                        if result['success']:
                            st.success("✅ Import completed successfully!")
                            
                            stats = result['stats']
                            
                            col_a, col_b, col_c, col_d = st.columns(4)
                            with col_a:
                                st.metric("Total Records", stats.get('total', 0))
                            with col_b:
                                st.metric("New", stats.get('new', 0))
                            with col_c:
                                st.metric("Updated", stats.get('updated', 0))
                            with col_d:
                                st.metric("Unchanged", stats.get('unchanged', 0))
                            
                            if stats.get('duplicates', 0) > 0:
                                st.warning(f"⚠️ {stats['duplicates']} duplicate source_ids found within the file and skipped.")
                                if result.get('duplicate_source_ids'):
                                    st.write("Duplicate IDs:", ', '.join(result['duplicate_source_ids'][:10]))
                            
                            if stats.get('failed', 0) > 0:
                                st.error(f"❌ {stats['failed']} records failed validation.")
                                if result.get('validation_errors'):
                                    with st.expander("Show validation errors"):
                                        for error in result['validation_errors'][:20]:
                                            st.write(f"- {error}")
                            
                            st.balloons()
                        else:
                            st.error(f"❌ Import failed: {result.get('error')}")
                            if result.get('validation_errors'):
                                with st.expander("Show validation errors"):
                                    for error in result['validation_errors'][:20]:
                                        st.write(f"- {error}")
                
                with col2:
                    if st.button("❌ Cancel"):
                        try:
                            Path(temp_path).unlink()
                        except:
                            pass
                        st.rerun()
            
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    with tab2:
        st.subheader("Import History")
        
        import_history = db.get_import_history()
        
        if import_history.empty:
            st.info("No import history available.")
        else:
            st.dataframe(
                import_history[['timestamp', 'filename', 'total_records', 'new_records', 
                              'updated_records', 'unchanged_records', 'status']],
                use_container_width=True
            )
    
    with tab3:
        st.subheader("Download Sample Template")
        st.write("Download a CSV template with the correct structure and example data.")
        
        template_df = create_sample_template()
        
        csv = template_df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download CSV Template",
            data=csv,
            file_name="conversation_template.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        st.subheader("Template Preview")
        st.dataframe(template_df, use_container_width=True)


# ============================================================================
# PAGE: Manual Editing & Audit
# ============================================================================
elif page == "✏️ Manual Editing & Audit":
    st.markdown('<div class="main-header">✏️ Manual Editing & Audit History</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Edit conversations and track all changes</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["✏️ Edit Conversation", "📜 Audit Log"])
    
    with tab1:
        st.subheader("Edit Conversation")
        
        df = db.get_all_conversations()
        
        if df.empty:
            st.warning("No conversations available to edit.")
        else:
            conv_options = [f"{row['source_id']} - {row['customer_name']} ({row['company']})" 
                          for _, row in df.iterrows()]
            
            selected = st.selectbox("Select conversation to edit", conv_options)
            
            if selected:
                source_id = selected.split(' - ')[0]
                conv = db.get_conversation_by_source_id(source_id)
                
                if conv:
                    st.info(f"Editing: **{conv['customer_name']}** from **{conv['company']}**")
                    
                    with st.form("edit_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_owner = st.selectbox(
                                "Owner",
                                list(TEAMS.keys()),
                                index=list(TEAMS.keys()).index(conv['owner']) if conv['owner'] in TEAMS else 0
                            )
                            
                            new_status = st.text_input("Status", value=conv.get('status', ''))
                            
                            new_stage = st.selectbox(
                                "Stage",
                                VALID_STAGES,
                                index=VALID_STAGES.index(conv['stage']) if conv['stage'] in VALID_STAGES else 0
                            )
                        
                        with col2:
                            new_urgency = st.selectbox(
                                "Urgency",
                                VALID_URGENCIES,
                                index=VALID_URGENCIES.index(conv['urgency']) if conv['urgency'] in VALID_URGENCIES else 0
                            )
                            
                            try:
                                current_priority = pd.to_numeric(conv.get('priority_score', 50), errors='coerce')
                                if pd.isna(current_priority):
                                    current_priority = 50.0
                                else:
                                    current_priority = float(current_priority)
                            except:
                                current_priority = 50.0
                            
                            new_priority = st.slider("Priority Score", 0, 100, int(current_priority))
                            
                            new_follow_up = st.date_input("Follow-up Date")
                        
                        new_next_action = st.text_area("Next Action", value=conv.get('next_action', ''))
                        
                        edit_reason = st.text_input("Reason for edit (optional)")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            submit = st.form_submit_button("💾 Save Changes", type="primary")
                        
                        with col2:
                            reset_override = st.form_submit_button("🔄 Reset Manual Override")
                        
                        if submit:
                            # Prepare updates
                            updates = {
                                'owner': new_owner,
                                'status': new_status,
                                'stage': new_stage,
                                'urgency': new_urgency,
                                'priority_score': str(new_priority),
                                'next_action': new_next_action,
                                'follow_up_date': str(new_follow_up),
                                'manual_override': 'TRUE'
                            }
                            
                            # Update database
                            success = db.update_conversation(source_id, updates, preserve_manual=False)
                            
                            if success:
                                # Log changes
                                db.log_audit_event(
                                    action_type='manual_edit',
                                    record_id=source_id,
                                    reason=edit_reason or 'Manual edit via UI',
                                    metadata={'fields_updated': list(updates.keys())}
                                )
                                
                                st.success("✅ Changes saved successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to save changes.")
                        
                        if reset_override:
                            # Recalculate routing
                            recommendation = recommend_routing(conv)
                            
                            updates = {
                                'owner': recommendation['recommended_team'],
                                'priority_score': str(recommendation['priority_score']),
                                'routing_reason': recommendation['routing_reason'],
                                'next_action': recommendation['next_action'],
                                'manual_override': 'FALSE'
                            }
                            
                            success = db.update_conversation(source_id, updates, preserve_manual=False)
                            
                            if success:
                                db.log_audit_event(
                                    action_type='reset_override',
                                    record_id=source_id,
                                    reason='Manual override reset - routing recalculated'
                                )
                                
                                st.success("✅ Manual override reset. Routing recalculated.")
                                st.rerun()
                            else:
                                st.error("Failed to reset override.")
    
    with tab2:
        st.subheader("Audit Log")
        st.write("Track all changes made to conversations.")
        
        audit_log = db.get_audit_log(limit=100)
        
        if audit_log.empty:
            st.info("No audit log entries yet.")
        else:
            # Filters
            action_types = ['All'] + sorted(audit_log['action_type'].unique().tolist())
            action_filter = st.selectbox("Filter by Action Type", action_types)
            
            if action_filter != 'All':
                filtered_log = audit_log[audit_log['action_type'] == action_filter]
            else:
                filtered_log = audit_log
            
            st.dataframe(
                filtered_log[['timestamp', 'action_type', 'record_id', 'field_name', 'reason']],
                use_container_width=True,
                height=400
            )


# ============================================================================
# PAGE: Export Center
# ============================================================================
elif page == "📤 Export Center":
    st.markdown('<div class="main-header">📤 Export Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Download conversations, routing decisions, and findings</div>', unsafe_allow_html=True)
    
    df = db.get_all_conversations()
    
    if df.empty:
        st.warning("No data available to export.")
    else:
        st.subheader("Available Exports")
        
        # Ensure exports directory exists
        Path("exports").mkdir(exist_ok=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Conversations Export")
            st.write("Export all conversation data to CSV format.")
            
            if st.button("📥 Export All Conversations"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"conversations_{timestamp}.csv"
                filepath = f"exports/{filename}"
                
                result = export_conversations_csv(df, filepath)
                
                if result['success']:
                    with open(filepath, 'rb') as f:
                        st.download_button(
                            label="⬇️ Download Conversations CSV",
                            data=f,
                            file_name=filename,
                            mime="text/csv"
                        )
                    st.success(f"✅ Exported {result['record_count']} conversations")
                    st.code(f"SHA-256: {result['checksum']}", language="text")
                else:
                    st.error(f"Export failed: {result.get('error')}")
        
        with col2:
            st.markdown("### 🎯 Routing Decisions Export")
            st.write("Export routing decisions and recommendations.")
            
            if st.button("📥 Export Routing Decisions"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"routing_decisions_{timestamp}.csv"
                filepath = f"exports/{filename}"
                
                result = export_routing_decisions_csv(df, filepath)
                
                if result['success']:
                    with open(filepath, 'rb') as f:
                        st.download_button(
                            label="⬇️ Download Routing Decisions CSV",
                            data=f,
                            file_name=filename,
                            mime="text/csv"
                        )
                    st.success(f"✅ Exported {result['record_count']} routing decisions")
                    st.code(f"SHA-256: {result['checksum']}", language="text")
                else:
                    st.error(f"Export failed: {result.get('error')}")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔍 Findings Export")
            st.write("Export analysis findings as JSON.")
            
            if st.button("📥 Export Findings"):
                findings = generate_findings(df)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"findings_{timestamp}.json"
                filepath = f"exports/{filename}"
                
                result = export_findings_json(findings, filepath)
                
                if result['success']:
                    with open(filepath, 'rb') as f:
                        st.download_button(
                            label="⬇️ Download Findings JSON",
                            data=f,
                            file_name=filename,
                            mime="application/json"
                        )
                    st.success(f"✅ Exported {result['record_count']} findings")
                    st.code(f"SHA-256: {result['checksum']}", language="text")
                else:
                    st.error(f"Export failed: {result.get('error')}")
        
        with col2:
            st.markdown("### 📜 Audit Log Export")
            st.write("Export audit history as CSV.")
            
            if st.button("📥 Export Audit Log"):
                audit_log = db.get_audit_log(limit=1000)
                
                if not audit_log.empty:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"audit_log_{timestamp}.csv"
                    filepath = f"exports/{filename}"
                    
                    result = export_audit_log(audit_log, filepath, format='csv')
                    
                    if result['success']:
                        with open(filepath, 'rb') as f:
                            st.download_button(
                                label="⬇️ Download Audit Log CSV",
                                data=f,
                                file_name=filename,
                                mime="text/csv"
                            )
                        st.success(f"✅ Exported {result['record_count']} audit entries")
                        st.code(f"SHA-256: {result['checksum']}", language="text")
                    else:
                        st.error(f"Export failed: {result.get('error')}")
                else:
                    st.info("No audit log entries to export.")
        
        st.markdown("---")
        
        st.markdown("### 📦 Generate Export Manifest")
        st.write("Create a manifest file with checksums for all exports.")
        
        if st.button("📦 Generate Manifest", type="primary"):
            # Generate all exports
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            exports = []
            
            with st.spinner("Generating exports..."):
                # Conversations
                conv_file = f"exports/conversations_{timestamp}.csv"
                conv_result = export_conversations_csv(df, conv_file)
                if conv_result['success']:
                    exports.append(conv_result)
                
                # Routing decisions
                routing_file = f"exports/routing_decisions_{timestamp}.csv"
                routing_result = export_routing_decisions_csv(df, routing_file)
                if routing_result['success']:
                    exports.append(routing_result)
                
                # Findings
                findings = generate_findings(df)
                findings_file = f"exports/findings_{timestamp}.json"
                findings_result = export_findings_json(findings, findings_file)
                if findings_result['success']:
                    exports.append(findings_result)
                
                # Audit log
                audit_log = db.get_audit_log(limit=1000)
                if not audit_log.empty:
                    audit_file = f"exports/audit_log_{timestamp}.csv"
                    audit_result = export_audit_log(audit_log, audit_file, format='csv')
                    if audit_result['success']:
                        exports.append(audit_result)
                
                # Generate manifest
                manifest_file = f"exports/manifest_{timestamp}.json"
                manifest_result = generate_manifest(exports, manifest_file)
            
            if manifest_result['success']:
                st.success(f"✅ Generated {len(exports)} exports with manifest")
                
                # Display manifest
                with st.expander("📋 View Manifest"):
                    with open(manifest_file, 'r') as f:
                        manifest_data = json.load(f)
                    st.json(manifest_data)
                
                # Download manifest
                with open(manifest_file, 'rb') as f:
                    st.download_button(
                        label="⬇️ Download Manifest JSON",
                        data=f,
                        file_name=f"manifest_{timestamp}.json",
                        mime="application/json"
                    )
                
                st.info("📁 All export files have been saved to the exports/ directory")
