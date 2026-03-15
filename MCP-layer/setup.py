"""Setup configuration for Reddit Sentiment Analysis MCP Server"""

from setuptools import setup, find_packages  # type: ignore

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="reddit-sentiment-mcp",
    version="1.0.0",
    author="Xynera Team",
    description="A FastMCP server for Reddit sentiment analysis and competitive intelligence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Xynera1-0/Xynera",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastmcp>=0.1.0",
        "praw>=7.7.0",
        "textblob>=0.17.1",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
    ],
)
