"""
Reddit Sentiment Analysis MCP Server
Provides tools for analyzing Reddit posts and comments for sentiment and competitive intelligence.
"""

import os
from typing import Any
from dotenv import load_dotenv
from fastmcp import FastMCP
from praw import Reddit
from praw.models import Comment
from prawcore.exceptions import PrawcoreException
from textblob import TextBlob
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Reddit Sentiment Analyzer")

# Initialize Reddit API client
try:
    reddit = Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
    )
except Exception as e:
    print(f"Warning: Reddit API initialization failed: {e}")
    reddit = None


class SentimentResult(BaseModel):
    """Sentiment analysis result"""
    text: str
    polarity: float
    subjectivity: float
    sentiment: str  # positive, negative, neutral


class RedditPost(BaseModel):
    """Reddit post data"""
    title: str
    author: str
    score: int
    num_comments: int
    url: str
    selftext: str
    created_utc: float
    sentiment: SentimentResult


def analyze_sentiment(text: str) -> SentimentResult:
    """Analyze sentiment of text using TextBlob"""
    blob = TextBlob(text)
    sentiment_obj = blob.sentiment
    polarity: float = float(sentiment_obj.polarity)  # type: ignore
    subjectivity: float = float(sentiment_obj.subjectivity)  # type: ignore
    
    if polarity > 0.1:
        sentiment = "positive"
    elif polarity < -0.1:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    return SentimentResult(
        text=text[:100] + "..." if len(text) > 100 else text,
        polarity=round(polarity, 3),
        subjectivity=round(subjectivity, 3),
        sentiment=sentiment,
    )


@mcp.tool()
async def search_reddit(
    query: str,
    subreddit: str = "all",
    limit: int = 10,
    sort: str = "relevance",
    time_filter: str = "all",
) -> dict[str, Any]:
    """
    Search Reddit for posts matching a query.
    
    Args:
        query: Search terms
        subreddit: Subreddit to search in (default: "all")
        limit: Number of results to return (1-100)
        sort: Sort order - relevance, hot, top, new, comments
        time_filter: Time filter for sorting - all, day, week, month, year
    
    Returns:
        List of posts with sentiment analysis
    """
    if not reddit:
        return {"error": "Reddit API not initialized. Check your credentials."}
    
    try:
        search_results = []
        subreddit_obj = reddit.subreddit(subreddit)
        
        # Search based on sort parameter
        if sort == "relevance":
            posts = subreddit_obj.search(query, limit=limit)
        elif sort == "hot":
            posts = subreddit_obj.search(query, sort="hot", limit=limit)
        elif sort == "top":
            posts = subreddit_obj.search(
                query, sort="top", time_filter=time_filter, limit=limit
            )
        elif sort == "new":
            posts = subreddit_obj.search(query, sort="new", limit=limit)
        elif sort == "comments":
            posts = subreddit_obj.search(query, sort="comments", limit=limit)
        else:
            posts = subreddit_obj.search(query, limit=limit)
        
        for post in posts:
            text_to_analyze = f"{post.title} {post.selftext}"
            sentiment = analyze_sentiment(text_to_analyze)
            
            search_results.append({
                "title": post.title,
                "author": str(post.author),
                "score": post.score,
                "num_comments": post.num_comments,
                "url": post.url,
                "subreddit": post.subreddit.display_name,
                "created_utc": post.created_utc,
                "sentiment": sentiment.model_dump(),
            })
        
        return {
            "query": query,
            "subreddit": subreddit,
            "total_results": len(search_results),
            "results": search_results,
        }
    
    except PrawcoreException as e:
        return {"error": f"Reddit API error: {str(e)}"}
    except Exception as e:
        return {"error": f"Error searching Reddit: {str(e)}"}


@mcp.tool()
async def analyze_post_sentiment(
    post_url: str, include_comments: bool = False
) -> dict[str, Any]:
    """
    Analyze sentiment of a specific Reddit post and optionally its comments.
    
    Args:
        post_url: Full URL to the Reddit post
        include_comments: Whether to analyze top comments
    
    Returns:
        Post data with sentiment analysis
    """
    if not reddit:
        return {"error": "Reddit API not initialized. Check your credentials."}
    
    try:
        submission = reddit.submission(url=post_url)
        
        # Analyze post sentiment
        post_text = f"{submission.title} {submission.selftext}"
        post_sentiment = analyze_sentiment(post_text)
        
        result = {
            "title": submission.title,
            "author": str(submission.author),
            "score": submission.score,
            "num_comments": submission.num_comments,
            "url": submission.url,
            "created_utc": submission.created_utc,
            "post_sentiment": post_sentiment.model_dump(),
            "comments": [],
        }
        
        # Analyze comments if requested
        if include_comments:
            submission.comments.replace_more(limit=None)
            comment_sentiments = []
            
            for comment in submission.comments.list()[:20]:  # Limit to top 20
                if isinstance(comment, Comment) and comment.body != "[deleted]":
                    sentiment = analyze_sentiment(comment.body)
                    comment_sentiments.append({
                        "author": str(comment.author),
                        "score": comment.score,
                        "body": comment.body[:200] + "..."
                        if len(comment.body) > 200
                        else comment.body,
                        "sentiment": sentiment.model_dump(),
                    })
            
            result["comments"] = comment_sentiments
        
        return result
    
    except Exception as e:
        return {"error": f"Error analyzing post: {str(e)}"}


@mcp.tool()
async def get_trending_sentiment(
    subreddit: str = "all", limit: int = 20
) -> dict[str, Any]:
    """
    Get sentiment analysis of trending posts in a subreddit.
    
    Args:
        subreddit: Subreddit to analyze (default: "all")
        limit: Number of posts to analyze
    
    Returns:
        Trending posts with sentiment distribution
    """
    if not reddit:
        return {"error": "Reddit API not initialized. Check your credentials."}
    
    try:
        subreddit_obj = reddit.subreddit(subreddit)
        posts = []
        sentiment_scores = {"positive": 0, "negative": 0, "neutral": 0}
        
        for post in subreddit_obj.hot(limit=limit):
            text = f"{post.title} {post.selftext}"
            sentiment = analyze_sentiment(text)
            sentiment_scores[sentiment.sentiment] += 1
            
            posts.append({
                "title": post.title,
                "author": str(post.author),
                "score": post.score,
                "url": post.url,
                "sentiment": sentiment.model_dump(),
            })
        
        avg_polarity = (
            sum(p["sentiment"]["polarity"] for p in posts) / len(posts)
            if posts
            else 0
        )
        
        return {
            "subreddit": subreddit,
            "total_posts": len(posts),
            "posts": posts,
            "sentiment_distribution": sentiment_scores,
            "average_polarity": round(avg_polarity, 3),
        }
    
    except Exception as e:
        return {"error": f"Error getting trending sentiment: {str(e)}"}


@mcp.tool()
async def monitor_competitor_mentions(
    competitor_names: list[str],
    subreddits: list[str] | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Monitor mentions of competitors across Reddit with sentiment analysis.
    Useful for competitive intelligence and brand monitoring.
    
    Args:
        competitor_names: List of competitor names/brands to monitor
        subreddits: List of subreddits to search (default: ["technology", "startups"])
        limit: Number of results per competitor
    
    Returns:
        Competitor mentions with sentiment analysis and distribution
    """
    if not reddit:
        return {"error": "Reddit API not initialized. Check your credentials."}
    
    if subreddits is None:
        subreddits = ["technology", "startups", "business"]
    
    results = {}
    
    try:
        for competitor in competitor_names:
            competitor_mentions = []
            sentiments = {"positive": 0, "negative": 0, "neutral": 0}
            
            for sub in subreddits:
                try:
                    subreddit_obj = reddit.subreddit(sub)
                    posts = subreddit_obj.search(competitor, limit=limit // len(subreddits))
                    
                    for post in posts:
                        text = f"{post.title} {post.selftext}"
                        sentiment = analyze_sentiment(text)
                        sentiments[sentiment.sentiment] += 1
                        
                        competitor_mentions.append({
                            "title": post.title,
                            "subreddit": sub,
                            "score": post.score,
                            "url": post.url,
                            "created_utc": post.created_utc,
                            "sentiment": sentiment.model_dump(),
                        })
                
                except PrawcoreException:
                    continue
            
            results[competitor] = {
                "total_mentions": len(competitor_mentions),
                "sentiment_distribution": sentiments,
                "mentions": competitor_mentions[:limit],
            }
        
        return {
            "competitors_monitored": competitor_names,
            "results": results,
        }
    
    except Exception as e:
        return {"error": f"Error monitoring competitors: {str(e)}"}


@mcp.tool()
async def analyze_community_sentiment(
    subreddit: str, sample_size: int = 50
) -> dict[str, Any]:
    """
    Analyze overall sentiment of a Reddit community.
    
    Args:
        subreddit: Subreddit to analyze
        sample_size: Number of posts to sample
    
    Returns:
        Community sentiment metrics and insights
    """
    if not reddit:
        return {"error": "Reddit API not initialized. Check your credentials."}
    
    try:
        subreddit_obj = reddit.subreddit(subreddit)
        sentiments = []
        posts_data = []
        
        for post in subreddit_obj.hot(limit=sample_size):
            text = f"{post.title} {post.selftext}"
            sentiment = analyze_sentiment(text)
            sentiments.append(sentiment)
            
            posts_data.append({
                "title": post.title,
                "sentiment": sentiment.model_dump(),
            })
        
        # Calculate statistics
        polarity_scores = [s.polarity for s in sentiments]
        subjectivity_scores = [s.subjectivity for s in sentiments]
        
        avg_polarity = sum(polarity_scores) / len(polarity_scores)
        avg_subjectivity = sum(subjectivity_scores) / len(subjectivity_scores)
        
        sentiment_counts = {}
        for s in sentiments:
            sentiment_counts[s.sentiment] = sentiment_counts.get(s.sentiment, 0) + 1
        
        dominant_sentiment = "neutral"
        if sentiment_counts:
            dominant_sentiment = max(
                sentiment_counts.items(),
                key=lambda x: x[1]
            )[0]
        
        return {
            "subreddit": subreddit,
            "sample_size": len(sentiments),
            "statistics": {
                "average_polarity": round(avg_polarity, 3),
                "average_subjectivity": round(avg_subjectivity, 3),
                "sentiment_distribution": sentiment_counts,
                "dominant_sentiment": dominant_sentiment
            },
            "posts": posts_data,
        }
    
    except Exception as e:
        return {"error": f"Error analyzing community sentiment: {str(e)}"}


if __name__ == "__main__":
    print("Starting Reddit Sentiment Analysis MCP Server...")
    print("Ensure your .env file is configured with Reddit API credentials")
    mcp.run()
