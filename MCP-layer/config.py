"""Configuration for Reddit Sentiment Analysis MCP Server"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Reddit API Configuration
    reddit_client_id: str
    reddit_client_secret: str
    reddit_user_agent: str
    reddit_username: Optional[str] = None
    reddit_password: Optional[str] = None
    
    # Server Configuration
    server_host: str = "127.0.0.1"
    server_port: int = 8000
    debug: bool = False
    
    # Sentiment Analysis Configuration
    min_polarity_threshold: float = -0.1
    max_polarity_threshold: float = 0.1
    
    # Reddit Search Configuration
    default_limit: int = 10
    max_limit: int = 100
    default_subreddit: str = "all"
    
    # Competitor Monitoring Configuration
    default_monitored_subreddits: list[str] = [
        "technology",
        "startups",
        "business",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def sentiment_classification(self) -> dict:
        """Sentiment classification thresholds"""
        return {
            "positive": f"> {self.max_polarity_threshold}",
            "negative": f"< {self.min_polarity_threshold}",
            "neutral": f">= {self.min_polarity_threshold} and <= {self.max_polarity_threshold}",
        }


# Load settings from environment
try:
    settings = Settings(
        reddit_client_id=os.getenv("REDDIT_CLIENT_ID", ""),
        reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
        reddit_user_agent=os.getenv("REDDIT_USER_AGENT", "GrowthIntelligenceBot"),
    )
except Exception as e:
    print(f"Error loading settings: {e}")
    print("Make sure your .env file is configured correctly")
    settings = None
