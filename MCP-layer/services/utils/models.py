"""Shared data models for growth intelligence"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum


class IntelligenceDomain(str, Enum):
    """Six intelligence domains for product growth"""
    MARKET_TRENDS = "market_trends"          # Market & Trend Sensing
    COMPETITIVE = "competitive"               # Competitive Landscape & Feature Bets
    WIN_LOSS = "win_loss"                     # Win/Loss Intelligence
    PRICING = "pricing"                       # Pricing & Packaging Intelligence
    POSITIONING = "positioning"               # Positioning & Messaging Gaps
    ADJACENT = "adjacent"                     # Adjacent Market Collision


class SignalConfidence(BaseModel):
    """Confidence scoring using source metadata"""
    score: float  # 0-1
    reasoning: str
    supporting_metric: str  # e.g., "22 upvotes", "5M views"


class IntelligenceSignal(BaseModel):
    """Core intelligence signal unit"""
    domain: IntelligenceDomain
    source: str  # "reddit", "hackernews", "patents", "meta_ads", "linkedin_ads", "playwright"
    title: str
    content: str
    url: str
    timestamp: Optional[str]
    confidence: SignalConfidence
    raw_metadata: Dict[str, Any]


class ConversationContext(BaseModel):
    """Context for multi-turn intelligence gathering"""
    question: str
    domains: List[IntelligenceDomain]
    signals: List[IntelligenceSignal] = []
    summary: Optional[str] = None
