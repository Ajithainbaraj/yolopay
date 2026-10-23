"""
Tests for routing engine
"""
import pytest
from src.routing import recommend_routing, calculate_routing_score, TEAMS


def test_routing_returns_valid_team():
    """Test that routing returns a valid team"""
    conversation = {
        'stage': 'discovery',
        'urgency': 'medium',
        'customer_intent': 'evaluate_solution',
        'conversation_summary': 'Customer wants to see a demo of our product',
        'transcript_or_notes': 'Quote: "We are evaluating multiple solutions"',
        'deal_value': '150000'
    }
    
    result = recommend_routing(conversation)
    
    assert result['recommended_team'] in TEAMS.keys()
    assert 'priority_score' in result
    assert 'routing_reason' in result
    assert 'evidence_quote' in result
    assert 'next_action' in result


def test_escalation_for_critical_urgency():
    """Test that critical urgency routes to escalation team"""
    conversation = {
        'stage': 'won',
        'urgency': 'critical',
        'customer_intent': 'resolve_issue',
        'conversation_summary': 'Complaint about major service outage',
        'transcript_or_notes': 'Quote: "CEO demanding immediate attention"',
        'sentiment': 'negative'
    }
    
    result = recommend_routing(conversation)
    
    # Should route to escalation team due to critical urgency
    assert result['recommended_team'] == 'Escalation Team'
    assert result['priority_score'] > 80  # Should be high priority


def test_sdr_for_new_leads():
    """Test that new leads route to SDR team"""
    conversation = {
        'stage': 'lead',
        'urgency': 'low',
        'customer_intent': 'research',
        'conversation_summary': 'Initial inquiry about our products',
        'transcript_or_notes': 'Quote: "Just exploring options for next year"'
    }
    
    result = recommend_routing(conversation)
    
    assert result['recommended_team'] == 'SDR Team'


def test_evidence_quote_extraction():
    """Test that evidence quotes are properly extracted"""
    conversation = {
        'stage': 'proposal',
        'urgency': 'medium',
        'customer_intent': 'evaluate_solution',
        'conversation_summary': 'Discussing pricing',
        'transcript_or_notes': 'Customer said: Quote: "We need better pricing to move forward"',
        'evidence_quote': ''
    }
    
    result = recommend_routing(conversation)
    
    # Should extract the quote
    assert 'We need better pricing to move forward' in result['evidence_quote']


def test_all_teams_get_scores():
    """Test that all teams receive routing scores"""
    conversation = {
        'stage': 'negotiation',
        'urgency': 'high',
        'customer_intent': 'negotiate_price'
    }
    
    result = recommend_routing(conversation)
    
    assert 'all_scores' in result
    assert len(result['all_scores']) == len(TEAMS)
