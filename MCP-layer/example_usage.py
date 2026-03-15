"""
Example usage of the Reddit Sentiment Analysis MCP Server
This file demonstrates how to use the various tools available
"""

import asyncio
from reddit_sentiment_server import (
    search_reddit,
    analyze_post_sentiment,
    get_trending_sentiment,
    monitor_competitor_mentions,
    analyze_community_sentiment,
)


async def main():
    """Example usage demonstrations"""
    
    print("=" * 60)
    print("Reddit Sentiment Analysis MCP Server - Examples")
    print("=" * 60)
    
    # Example 1: Search for AI startups
    print("\n1. Searching for 'AI startup' mentions...")
    print("-" * 60)
    search_result = await search_reddit(
        query="AI startup",
        subreddit="technology",
        limit=5,
        sort="top",
        time_filter="week",
    )
    print(f"Found {search_result.get('total_results', 0)} results")
    for post in search_result.get("results", [])[:2]:
        print(f"  - {post['title']}")
        print(f"    Sentiment: {post['sentiment']['sentiment']} "
              f"(polarity: {post['sentiment']['polarity']})")
    
    # Example 2: Analyze trending sentiment in technology subreddit
    print("\n2. Analyzing trending sentiment in r/technology...")
    print("-" * 60)
    trending = await get_trending_sentiment(
        subreddit="technology",
        limit=10,
    )
    print(f"Average polarity: {trending['average_polarity']}")
    print(f"Sentiment distribution: {trending['sentiment_distribution']}")
    
    # Example 3: Monitor competitor mentions
    print("\n3. Monitoring competitor mentions...")
    print("-" * 60)
    competitors = ["OpenAI", "Anthropic"]
    monitoring = await monitor_competitor_mentions(
        competitor_names=competitors,
        subreddits=["technology", "startups"],
        limit=20,
    )
    for competitor, data in monitoring["results"].items():
        print(f"\n{competitor}:")
        print(f"  Total mentions: {data['total_mentions']}")
        print(f"  Sentiment: {data['sentiment_distribution']}")
    
    # Example 4: Analyze community sentiment
    print("\n4. Analyzing r/machinelearning community sentiment...")
    print("-" * 60)
    community = await analyze_community_sentiment(
        subreddit="machinelearning",
        sample_size=20,
    )
    stats = community["statistics"]
    print(f"Average polarity: {stats['average_polarity']}")
    print(f"Average subjectivity: {stats['average_subjectivity']}")
    print(f"Dominant sentiment: {stats['dominant_sentiment']}")
    print(f"Distribution: {stats['sentiment_distribution']}")
    
    # Example 5: Analyze a specific post (you'll need a real URL)
    print("\n5. Analyzing specific post sentiment...")
    print("-" * 60)
    print("(Replace with actual Reddit post URL)")
    # post_analysis = await analyze_post_sentiment(
    #     post_url="https://reddit.com/r/technology/comments/...",
    #     include_comments=True
    # )


if __name__ == "__main__":
    asyncio.run(main())
