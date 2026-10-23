"""
Intelligent routing engine for SignalDesk AI
Recommends appropriate team/owner based on conversation context
"""
from typing import Dict, List, Tuple, Any
import re


# Team definitions with expertise areas
TEAMS = {
    'SDR Team': {
        'description': 'Sales Development Representatives - handles new leads and initial qualification',
        'keywords': ['lead', 'research', 'initial', 'early', 'qualification'],
        'stages': ['lead'],
        'urgencies': ['low', 'medium'],
        'intents': ['research', 'explore_options']
    },
    'Account Executive Team': {
        'description': 'Account Executives - manages qualified opportunities through closing',
        'keywords': ['proposal', 'negotiation', 'pricing', 'contract', 'demo', 'evaluate'],
        'stages': ['discovery', 'proposal', 'negotiation'],
        'urgencies': ['medium', 'high'],
        'intents': ['evaluate_solution', 'negotiate_price', 'finalize_contract', 'build_business_case']
    },
    'Customer Success Team': {
        'description': 'Customer Success - handles existing customers, renewals, and adoption',
        'keywords': ['renewal', 'existing', 'customer', 'adoption', 'expansion', 'won'],
        'stages': ['won'],
        'urgencies': ['low', 'medium', 'high'],
        'intents': ['renew_contract', 'expand_usage', 'resolve_issue']
    },
    'Escalation Team': {
        'description': 'Executive escalation - handles critical issues and high-risk situations',
        'keywords': ['complaint', 'escalate', 'critical', 'urgent', 'ceo', 'executive', 'emergency'],
        'stages': ['won', 'negotiation', 'discovery'],
        'urgencies': ['critical', 'high'],
        'intents': ['resolve_issue', 'escalate_complaint']
    }
}


def calculate_routing_score(conversation: Dict[str, Any], team_name: str) -> Tuple[float, List[str]]:
    """
    Calculate routing score for a team
    Returns: (score, reasons)
    """
    team = TEAMS[team_name]
    score = 0.0
    reasons = []
    
    # Stage matching (30 points)
    stage = conversation.get('stage', '').lower()
    if stage in team['stages']:
        score += 30
        reasons.append(f"Stage '{stage}' matches {team_name} expertise")
    
    # Urgency matching (25 points)
    urgency = conversation.get('urgency', '').lower()
    if urgency in team['urgencies']:
        score += 25
        reasons.append(f"Urgency level '{urgency}' appropriate for {team_name}")
    
    # Intent matching (25 points)
    intent = conversation.get('customer_intent', '').lower()
    if intent in team.get('intents', []):
        score += 25
        reasons.append(f"Customer intent '{intent}' aligns with {team_name}")
    
    # Keyword matching in summary and notes (15 points possible)
    text_to_search = ' '.join([
        conversation.get('conversation_summary', ''),
        conversation.get('transcript_or_notes', ''),
        conversation.get('objections', '')
    ]).lower()
    
    keyword_matches = []
    for keyword in team['keywords']:
        if keyword in text_to_search:
            keyword_matches.append(keyword)
    
    if keyword_matches:
        keyword_score = min(15, len(keyword_matches) * 5)
        score += keyword_score
        reasons.append(f"Keywords detected: {', '.join(keyword_matches[:3])}")
    
    # Deal value consideration (5 points for high value deals to AE/Escalation)
    try:
        deal_value_str = str(conversation.get('deal_value', '')).strip()
        if deal_value_str and deal_value_str.lower() not in ['unknown', 'nan', 'none', '']:
            # Remove currency symbols and commas
            clean_val = deal_value_str.replace('$', '').replace(',', '').strip()
            if clean_val:
                deal_value = float(clean_val)
                if deal_value >= 200000 and team_name in ['Account Executive Team', 'Escalation Team']:
                    score += 5
                    reasons.append(f"High-value deal (${deal_value:,.0f}) requires senior attention")
    except (ValueError, AttributeError):
        pass
    
    return score, reasons


def recommend_routing(conversation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recommend the best team for a conversation
    Returns routing recommendation with score, reasons, and evidence
    """
    # Calculate scores for all teams
    team_scores = {}
    team_reasons = {}
    
    for team_name in TEAMS.keys():
        score, reasons = calculate_routing_score(conversation, team_name)
        team_scores[team_name] = score
        team_reasons[team_name] = reasons
    
    # Find best match
    recommended_team = max(team_scores, key=team_scores.get)
    best_score = team_scores[recommended_team]
    
    # Extract evidence quote from notes
    evidence_quote = conversation.get('evidence_quote', '')
    if not evidence_quote:
        # Try to extract from transcript
        transcript = conversation.get('transcript_or_notes', '')
        if 'Quote:' in transcript:
            # Extract text after "Quote:"
            quote_match = re.search(r'Quote:\s*["\']?([^"\']+)["\']?', transcript)
            if quote_match:
                evidence_quote = quote_match.group(1).strip()
        elif transcript:
            # Use first sentence as evidence
            evidence_quote = transcript.split('.')[0][:200] + '...' if len(transcript) > 200 else transcript.split('.')[0]
    
    # Determine suggested next action
    next_action = suggest_next_action(conversation, recommended_team)
    
    # Calculate priority score
    priority = calculate_priority(conversation, best_score)
    
    return {
        'recommended_team': recommended_team,
        'priority_score': priority,
        'routing_score': best_score,
        'routing_reason': ' | '.join(team_reasons[recommended_team][:3]) if team_reasons[recommended_team] else 'Default routing',
        'evidence_quote': evidence_quote,
        'next_action': next_action,
        'all_scores': team_scores,
        'confidence': get_confidence_level(best_score, team_scores)
    }


def suggest_next_action(conversation: Dict[str, Any], team: str) -> str:
    """Suggest next action based on conversation context"""
    # If already has next action, keep it
    existing_action = conversation.get('next_action', '').strip()
    if existing_action:
        return existing_action
    
    stage = conversation.get('stage', '').lower()
    urgency = conversation.get('urgency', '').lower()
    intent = conversation.get('customer_intent', '').lower()
    
    # Urgent/critical situations
    if urgency == 'critical':
        return 'Schedule immediate executive call'
    
    # Stage-based suggestions
    if stage == 'lead':
        return 'Conduct qualification call'
    elif stage == 'discovery':
        return 'Schedule product demonstration'
    elif stage == 'proposal':
        return 'Send detailed proposal'
    elif stage == 'negotiation':
        return 'Prepare pricing options'
    elif stage == 'won':
        if 'complaint' in conversation.get('conversation_summary', '').lower():
            return 'Resolve customer issue'
        return 'Schedule onboarding call'
    elif stage == 'lost':
        return 'Document loss reason and archive'
    
    # Intent-based fallback
    if 'renew' in intent:
        return 'Prepare renewal proposal'
    elif 'negotiate' in intent:
        return 'Schedule pricing discussion'
    
    return 'Schedule follow-up call'


def calculate_priority(conversation: Dict[str, Any], routing_score: float) -> float:
    """Calculate priority score (0-100)"""
    priority = routing_score  # Start with routing score
    
    # Urgency multiplier
    urgency = conversation.get('urgency', '').lower()
    urgency_weights = {'critical': 1.3, 'high': 1.15, 'medium': 1.0, 'low': 0.85}
    priority *= urgency_weights.get(urgency, 1.0)
    
    # Deal value boost
    try:
        deal_value_str = str(conversation.get('deal_value', '')).strip()
        if deal_value_str and deal_value_str.lower() not in ['unknown', 'nan', 'none', '']:
            # Remove currency symbols and commas
            clean_val = deal_value_str.replace('$', '').replace(',', '').strip()
            if clean_val:
                deal_value = float(clean_val)
                if deal_value >= 300000:
                    priority += 10
                elif deal_value >= 150000:
                    priority += 5
    except (ValueError, AttributeError):
        pass
    
    # Stage considerations
    stage = conversation.get('stage', '').lower()
    if stage == 'negotiation':
        priority += 5  # Close to closing
    elif stage == 'lost':
        priority = min(priority, 20)  # Lower priority for lost deals
    
    # Sentiment impact
    sentiment = conversation.get('sentiment', '').lower()
    if sentiment == 'negative':
        priority += 8  # Urgent attention needed
    
    return min(100, max(0, priority))


def get_confidence_level(best_score: float, all_scores: Dict[str, float]) -> str:
    """Determine confidence level of routing recommendation"""
    sorted_scores = sorted(all_scores.values(), reverse=True)
    
    if best_score < 25:
        return 'Low - Limited matching criteria'
    elif len(sorted_scores) > 1 and sorted_scores[0] - sorted_scores[1] < 10:
        return 'Medium - Close competition between teams'
    elif best_score >= 60:
        return 'High - Strong match with team expertise'
    else:
        return 'Medium - Reasonable match'


def get_difficult_routing_example() -> str:
    """Return explanation of a difficult routing decision from the dataset"""
    return """
    **Difficult Routing Example: CONV004 - RetailMax Escalation**
    
    **Situation:**
    David Park from RetailMax (existing customer, $250K deal) submitted a critical complaint about 
    a 3-hour production outage. The CEO is demanding immediate executive attention.
    
    **Competing Considerations:**
    
    1. **Customer Success Team** (Score: 55)
       - ✓ Existing customer (won stage)
       - ✓ Ongoing relationship management
       - ✗ May lack authority for executive escalation
    
    2. **Escalation Team** (Score: 82) ✓ RECOMMENDED
       - ✓ Critical urgency level
       - ✓ CEO involvement requires executive response
       - ✓ Keywords: "complaint", "unacceptable", "demanding"
       - ✓ High deal value at risk
    
    **Decision:**
    Route to **Escalation Team** due to critical urgency and executive involvement.
    
    **Reasoning:**
    While Customer Success normally handles existing customers, the severity (production outage), 
    urgency (critical), and stakeholder level (CEO) require immediate escalation to senior 
    leadership. The customer relationship is at risk, and a standard CS response would be 
    insufficient.
    
    **Evidence:**
    "This is unacceptable. We lost revenue and customer trust. I need a call with your VP today."
    
    **Recommended Action:**
    Emergency call with leadership within 2 hours
    
    **Human Override Option:**
    A manager could reasonably argue for Customer Success Team if:
    - The CS team has a strong existing relationship with the customer
    - A dedicated executive sponsor is already assigned
    - The CS team has authority to coordinate executive involvement
    
    This demonstrates why human judgment remains essential for context-sensitive routing decisions.
    """
