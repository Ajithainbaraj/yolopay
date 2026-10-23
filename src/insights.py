"""
Insights and findings generator for SignalDesk AI
Analyzes conversation data to generate actionable business insights
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd


def generate_findings(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Generate evidence-backed findings from conversation data
    Only reports findings that are actually supported by the data
    """
    findings = []
    
    if df.empty:
        return [{
            'title': 'Insufficient Data',
            'metric': 'No conversations in database',
            'implication': 'Cannot generate insights without conversation data',
            'recommendation': 'Import conversation data to begin analysis',
            'supporting_conversations': [],
            'evidence': [],
            'limitations': 'No data available for analysis'
        }]
    
    # Finding 1: High-priority conversations without follow-up dates
    finding1 = analyze_missing_followups(df)
    if finding1:
        findings.append(finding1)
    
    # Finding 2: Repeated objections across conversations
    finding2 = analyze_repeated_objections(df)
    if finding2:
        findings.append(finding2)
    
    # Finding 3: Stalled opportunities
    finding3 = analyze_stalled_opportunities(df)
    if finding3:
        findings.append(finding3)
    
    # Finding 4: Negative sentiment alerts
    finding4 = analyze_negative_sentiment(df)
    if finding4:
        findings.append(finding4)
    
    return findings if findings else [{
        'title': 'No Significant Patterns Detected',
        'metric': 'Analysis complete',
        'implication': 'Current data shows no urgent patterns requiring immediate attention',
        'recommendation': 'Continue monitoring as more conversations are added',
        'supporting_conversations': [],
        'evidence': [],
        'limitations': 'Small sample size may limit pattern detection'
    }]


def analyze_missing_followups(df: pd.DataFrame) -> Dict[str, Any]:
    """Identify high-priority conversations without scheduled follow-ups"""
    # Filter high-priority conversations
    df_temp = df.copy()
    df_temp['priority_score_num'] = pd.to_numeric(df_temp['priority_score'], errors='coerce')
    
    high_priority = df_temp[
        (df_temp['priority_score_num'].notna()) & 
        (df_temp['priority_score_num'] >= 75) &
        (df_temp['stage'].isin(['discovery', 'proposal', 'negotiation'])) &
        ((df_temp['follow_up_date'].isna()) | (df_temp['follow_up_date'] == ''))
    ]
    
    if len(high_priority) == 0:
        return None
    
    evidence = []
    conv_ids = []
    
    for _, row in high_priority.head(5).iterrows():
        conv_ids.append(row['source_id'])
        try:
            priority_val = float(row['priority_score_num'])
        except:
            priority_val = 0
        
        evidence.append({
            'conversation_id': row['source_id'],
            'customer': row['customer_name'],
            'company': row['company'],
            'stage': row['stage'],
            'priority': priority_val,
            'quote': row.get('evidence_quote', 'No quote available')[:150]
        })
    
    return {
        'title': 'High-Priority Conversations Missing Follow-Up Dates',
        'metric': f'{len(high_priority)} conversations with priority ≥75 lack scheduled follow-ups',
        'implication': 'Important opportunities may be neglected without clear next steps',
        'recommendation': 'Schedule follow-up dates for all high-priority active opportunities within 24 hours',
        'supporting_conversations': conv_ids,
        'evidence': evidence,
        'limitations': 'Analysis based on current priority scores; business context may vary'
    }


def analyze_repeated_objections(df: pd.DataFrame) -> Dict[str, Any]:
    """Identify common objections appearing across multiple conversations"""
    # Filter conversations with objections
    with_objections = df[df['objections'].notna() & (df['objections'] != '')]
    
    if len(with_objections) < 2:
        return None
    
    # Count objection types
    objection_counts = {}
    objection_examples = {}
    
    for _, row in with_objections.iterrows():
        objection = str(row['objections']).lower().strip()
        
        # Categorize common objection types
        if 'price' in objection or 'cost' in objection or 'budget' in objection:
            category = 'price_concerns'
        elif 'timeline' in objection or 'time' in objection:
            category = 'timeline_concerns'
        elif 'technical' in objection or 'integration' in objection or 'api' in objection:
            category = 'technical_feasibility'
        elif 'compliance' in objection or 'security' in objection:
            category = 'compliance_requirements'
        else:
            category = objection[:30]
        
        if category not in objection_counts:
            objection_counts[category] = 0
            objection_examples[category] = []
        
        objection_counts[category] += 1
        objection_examples[category].append({
            'conversation_id': row['source_id'],
            'customer': row['customer_name'],
            'company': row['company'],
            'objection': objection,
            'quote': row.get('evidence_quote', 'No quote available')[:150]
        })
    
    # Find most common objection
    if not objection_counts:
        return None
    
    most_common = max(objection_counts, key=objection_counts.get)
    count = objection_counts[most_common]
    
    if count < 2:
        return None
    
    evidence = objection_examples[most_common][:5]
    conv_ids = [e['conversation_id'] for e in evidence]
    
    return {
        'title': f'Repeated Objection Pattern: {most_common.replace("_", " ").title()}',
        'metric': f'{count} conversations mention {most_common.replace("_", " ")} as a concern',
        'implication': 'Common objections indicate potential gaps in product positioning or sales enablement',
        'recommendation': f'Develop standardized response materials and competitive positioning for {most_common.replace("_", " ")} objections',
        'supporting_conversations': conv_ids,
        'evidence': evidence,
        'limitations': 'Categorization based on keyword matching; manual review recommended'
    }


def analyze_stalled_opportunities(df: pd.DataFrame) -> Dict[str, Any]:
    """Identify opportunities that may be stalled in a stage"""
    # Only analyze active stages
    active = df[df['stage'].isin(['discovery', 'proposal', 'negotiation'])]
    
    if len(active) == 0:
        return None
    
    # Check if we have date information
    if 'conversation_date' not in active.columns:
        return None
    
    # Convert dates
    today = datetime.now()
    stalled = []
    
    for _, row in active.iterrows():
        try:
            conv_date_str = str(row['conversation_date'])
            if not conv_date_str or conv_date_str == 'nan':
                continue
            
            conv_date = pd.to_datetime(conv_date_str)
            days_ago = (today - conv_date).days
            
            # Consider stalled if >14 days with no follow-up scheduled
            if days_ago > 14:
                has_followup = row.get('follow_up_date') and str(row.get('follow_up_date')) != 'nan' and str(row.get('follow_up_date')).strip() != ''
                
                if not has_followup:
                    stalled.append({
                        'conversation_id': row['source_id'],
                        'customer': row['customer_name'],
                        'company': row['company'],
                        'stage': row['stage'],
                        'days_since_conversation': days_ago,
                        'quote': row.get('evidence_quote', 'No quote available')[:150]
                    })
        except:
            continue
    
    if len(stalled) == 0:
        return None
    
    conv_ids = [s['conversation_id'] for s in stalled[:5]]
    
    return {
        'title': 'Potentially Stalled Opportunities',
        'metric': f'{len(stalled)} active opportunities with no activity in >14 days',
        'implication': 'Long inactive periods in active stages may indicate stalled deals or insufficient follow-up',
        'recommendation': 'Review stalled opportunities and establish re-engagement strategy or qualify out',
        'supporting_conversations': conv_ids,
        'evidence': stalled[:5],
        'limitations': 'Based on last conversation date; recent activity in other systems may not be reflected'
    }


def analyze_negative_sentiment(df: pd.DataFrame) -> Dict[str, Any]:
    """Identify conversations with negative sentiment requiring attention"""
    negative = df[df['sentiment'] == 'negative']
    
    if len(negative) == 0:
        return None
    
    evidence = []
    conv_ids = []
    
    for _, row in negative.head(5).iterrows():
        conv_ids.append(row['source_id'])
        evidence.append({
            'conversation_id': row['source_id'],
            'customer': row['customer_name'],
            'company': row['company'],
            'stage': row['stage'],
            'urgency': row['urgency'],
            'summary': row.get('conversation_summary', '')[:100],
            'quote': row.get('evidence_quote', 'No quote available')[:150]
        })
    
    return {
        'title': 'Negative Sentiment Conversations Requiring Attention',
        'metric': f'{len(negative)} conversations with negative sentiment detected',
        'implication': 'Negative sentiment may indicate customer dissatisfaction, complaints, or at-risk relationships',
        'recommendation': 'Prioritize response to negative sentiment conversations and implement recovery plans',
        'supporting_conversations': conv_ids,
        'evidence': evidence,
        'limitations': 'Sentiment classification based on available data; tone and context should be verified manually'
    }


def get_rejected_decision_example() -> str:
    """Return an example of a considered and rejected decision"""
    return """
    **Considered and Rejected Decision: Automatic Sentiment Analysis via AI**
    
    **Proposed Approach:**
    Integrate OpenAI API to automatically analyze conversation transcripts and assign sentiment scores 
    (positive, neutral, negative) without manual input.
    
    **Rationale for Consideration:**
    - Reduces manual data entry burden
    - Provides consistent sentiment classification
    - Enables real-time analysis of large conversation volumes
    - Industry-standard approach used by many sales intelligence platforms
    
    **Evidence Against:**
    1. **Privacy Risk**: Sending customer conversation transcripts to third-party APIs raises data privacy 
       and compliance concerns, especially for regulated industries (healthcare, finance)
    
    2. **API Dependency**: Application functionality would depend on external API availability and cost. 
       If the API is unavailable or the user lacks an API key, sentiment analysis would fail.
    
    3. **Accuracy Concerns**: AI sentiment analysis can misinterpret sarcasm, domain-specific language, 
       or cultural nuances, leading to incorrect classifications that could misdirect sales actions.
    
    4. **Cost at Scale**: OpenAI API costs scale with conversation volume. For teams with hundreds of 
       daily conversations, costs could become prohibitive.
    
    **Alternative Chosen:**
    Implement manual sentiment tagging with validation rules during CSV import. Users assign sentiment 
    based on their direct knowledge of the conversation context.
    
    **Benefits of Chosen Alternative:**
    - No external API dependencies or costs
    - Complete data privacy and security control
    - Higher accuracy through human judgment
    - Works offline and in all deployment scenarios
    - Transparent and auditable
    
    **Tradeoffs Accepted:**
    - Requires manual effort during data import
    - Does not scale automatically to thousands of conversations
    - Sentiment consistency depends on individual judgment
    
    **Future Consideration:**
    Optional AI sentiment analysis could be added as an opt-in enhancement for users who accept the 
    privacy and cost tradeoffs, with clear disclosure and explicit consent. The manual approach would 
    remain the default and fallback method.
    """
