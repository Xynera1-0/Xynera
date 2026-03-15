"""Reddit user voice intelligence using PRAW"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from praw import Reddit
from praw.models import Comment
from prawcore.exceptions import PrawcoreException
from textblob import TextBlob
from services.utils.models import IntelligenceSignal, SignalConfidence, IntelligenceDomain
from services.playwright_crawler import smart_fallback_crawl


def authenticate_reddit() -> Reddit:
    """Authenticate with Reddit API using OAuth2"""
    return Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "VeracityGrowthBot/1.0"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
    )


def calculate_sentiment(text: str) -> float:
    """Calculate sentiment polarity (-1 to 1)"""
    blob = TextBlob(text)
    sentiment_obj = blob.sentiment
    return float(sentiment_obj.polarity)  # type: ignore


async def get_reddit_user_voice(
    keywords: List[str],
    subreddits: Optional[List[str]] = None,
    limit: int = 10,
    min_score: int = 5,
) -> List[IntelligenceSignal]:
    """
    Extract user voice signals from Reddit.
    
    Maps to: Market & Trend Sensing, Competitive Landscape, Win/Loss Intelligence
    
    Falls back to Playwright crawler if Reddit API fails or credentials missing.
    
    Args:
        keywords: Search terms (e.g., ["pricing", "competitor_name"])
        subreddits: Subreddits to search (default: ["SaaS", "startups", "Entrepreneur"])
        limit: Number of posts per keyword
        min_score: Minimum upvotes to consider signal
    
    Returns:
        List of IntelligenceSignal objects with confidence scores
    """
    if subreddits is None:
        subreddits = ["SaaS", "startups", "Entrepreneur"]
    
    signals: List[IntelligenceSignal] = []
    
    try:
        reddit = authenticate_reddit()
        loop = asyncio.get_event_loop()
        
        for keyword in keywords:
            for subreddit_name in subreddits:
                subreddit = reddit.subreddit(subreddit_name)
                
                # Run blocking PRAW call in thread pool
                submissions = await loop.run_in_executor(
                    None,
                    lambda: list(subreddit.search(keyword, sort="hot", limit=limit))
                )
                
                # Search and filter
                for submission in submissions:
                    if submission.score < min_score:
                        continue
                    
                    # Extract top comment (the "pain point")
                    top_comment = None
                    if submission.comments:
                        comments_list = submission.comments.list()[:5]
                        for comment in comments_list:
                            if isinstance(comment, Comment) and comment.score > 0:
                                top_comment = comment.body[:500]
                                break
                    
                    # Analyze sentiment to filter relevance
                    text_to_analyze = f"{submission.title} {submission.selftext}"
                    sentiment = calculate_sentiment(text_to_analyze)
                    
                    # Map sentiment to domain
                    domain = IntelligenceDomain.MARKET_TRENDS
                    if "price" in keyword.lower() or "cost" in keyword.lower():
                        domain = IntelligenceDomain.PRICING
                    elif "competitor" in keyword.lower() or any(c in keyword.lower() for c in ["vs", "alternative"]):
                        domain = IntelligenceDomain.COMPETITIVE
                    
                    # Confidence: upvote ratio + comment activity
                    confidence_score = min(
                        (submission.upvote_ratio * submission.score) / 100,
                        1.0
                    )
                    
                    signal = IntelligenceSignal(
                        domain=domain,
                        source="reddit",
                        title=submission.title,
                        content=top_comment or submission.selftext[:500],
                        url=submission.url,
                        timestamp=str(submission.created_utc),
                        confidence=SignalConfidence(
                            score=confidence_score,
                            reasoning=f"High engagement in {subreddit_name}",
                            supporting_metric=f"{submission.score} upvotes, {len(submission.comments)} comments"
                        ),
                        raw_metadata={
                            "author": str(submission.author),
                            "score": submission.score,
                            "num_comments": submission.num_comments,
                            "upvote_ratio": submission.upvote_ratio,
                            "sentiment_polarity": sentiment,
                        }
                    )
                    signals.append(signal)
        
        return signals
    
    except (PrawcoreException, Exception) as e:
        # Fallback to Playwright crawler if Reddit API fails
        print(f"[reddit_tools] API error, falling back to web crawler: {str(e)}")
        
        # Use first keyword for crawler fallback
        fallback_query = ' '.join(keywords[:3]) if keywords else "product feedback"
        
        # Directly await fallback - no asyncio.run() needed!
        try:
            fallback_signals = await smart_fallback_crawl(fallback_query, IntelligenceDomain.MARKET_TRENDS)
            return fallback_signals if fallback_signals else []
        except Exception as fallback_error:
            print(f"[reddit_tools] Fallback crawler also failed: {str(fallback_error)}")
            return []
