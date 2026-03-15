# Reddit Sentiment Analysis MCP Server

A FastMCP-based Model Context Protocol server that provides competitive intelligence and sentiment analysis tools for Reddit data. Perfect for hackathons and rapid competitive analysis.

## Features

- **Post Search & Analysis**: Search Reddit and get instant sentiment analysis
- **Trending Sentiment**: Monitor sentiment trends in real-time
- **Competitor Monitoring**: Track competitor mentions across subreddits with sentiment
- **Community Analysis**: Understand overall community sentiment and engagement
- **Comment Analysis**: Deep dive into post comments for detailed sentiment insights

## Quick Start

### 1. Setup

```bash
# Clone the repository
cd MCP-layer

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create Application"
3. Fill in the form:
   - Name: "Reddit Sentiment Tool"
   - Type: "Script"
   - Redirect URI: http://localhost:8000
4. Copy credentials and create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=reddit-sentiment-tool:v1.0 (by /u/your_username)
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

### 3. Start the Server

```bash
python reddit_sentiment_server.py
```

## Available Tools

### search_reddit

Search Reddit for posts and analyze sentiment in real-time.

**Parameters:**

- `query` (str): Search terms
- `subreddit` (str): Target subreddit (default: "all")
- `limit` (int): Number of results (1-100)
- `sort` (str): Sort order - relevance, hot, top, new, comments
- `time_filter` (str): Time filter - all, day, week, month, year

**Example:**

```python
await search_reddit(
    query="AI startup",
    subreddit="technology",
    limit=20,
    sort="top",
    time_filter="week"
)
```

### analyze_post_sentiment

Deep analysis of a specific post and its comments.

**Parameters:**

- `post_url` (str): Full Reddit post URL
- `include_comments` (bool): Analyze top comments (default: False)

**Example:**

```python
await analyze_post_sentiment(
    post_url="https://reddit.com/r/technology/comments/...",
    include_comments=True
)
```

### get_trending_sentiment

Monitor sentiment of trending posts in a subreddit.

**Parameters:**

- `subreddit` (str): Target subreddit (default: "all")
- `limit` (int): Number of posts to analyze

**Example:**

```python
await get_trending_sentiment(
    subreddit="startups",
    limit=25
)
```

### monitor_competitor_mentions

Track competitor mentions and sentiment across Reddit.

**Parameters:**

- `competitor_names` (list): Brand/company names to monitor
- `subreddits` (list): Subreddits to search (default: ["technology", "startups", "business"])
- `limit` (int): Results per competitor

**Example:**

```python
await monitor_competitor_mentions(
    competitor_names=["OpenAI", "Anthropic", "Google"],
    subreddits=["technology", "startups"],
    limit=50
)
```

### analyze_community_sentiment

Understand the overall sentiment of a Reddit community.

**Parameters:**

- `subreddit` (str): Target subreddit
- `sample_size` (int): Number of posts to sample

**Example:**

```python
await analyze_community_sentiment(
    subreddit="machinelearning",
    sample_size=50
)
```

## Sentiment Analysis Output

Each sentiment analysis includes:

- **polarity** (-1 to 1): Negative to positive sentiment
- **subjectivity** (0 to 1): Objective to subjective
- **sentiment**: Classified as "positive", "negative", or "neutral"

## Use Cases

### For Hackathons

- Quick competitive intelligence gathering
- Real-time market sentiment analysis
- Community feedback analysis

### For Product Teams

- Monitor user sentiment about your product
- Track competitor mentions and perception
- Identify trending features and pain points
- Analyze community needs and demands

### For Investors

- Track sentiment around companies and sectors
- Monitor community reception of announcements
- Analyze emerging trends and discussions

## Architecture

```
reddit_sentiment_server.py
├── FastMCP Server
│   ├── search_reddit() - Search and analyze
│   ├── analyze_post_sentiment() - Deep post analysis
│   ├── get_trending_sentiment() - Trend monitoring
│   ├── monitor_competitor_mentions() - Competitor tracking
│   └── analyze_community_sentiment() - Community analysis
├── PRAW Client
│   └── Reddit API Integration
└── TextBlob
    └── Sentiment Analysis Engine
```

## Integration with Xynera

This MCP server plugs into Xynera's competitive intelligence platform, providing:

- Real-time Reddit sentiment data
- Competitor monitoring capabilities
- Community perception analysis
- Trend identification

## Requirements

- Python 3.8+
- Reddit API credentials
- Internet connection

## License

MIT

## Support

For issues or feature requests, please check the main Xynera repository.
