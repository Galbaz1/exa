# Neural Web Summarizer

## Overview
Neural Web Summarizer is a Python tool that leverages the Exa API and OpenAI's GPT-4 to search for content related to a user's query, summarize the findings, and generate a scientific meta-review.

## Features
- Search content using Exa API with a date cutoff to get the most relevant and recent articles.
- Clean and process HTML content from search results using BeautifulSoup.
- Generate additional research questions and a comprehensive meta-review using OpenAI's GPT-4.
- Save summaries in Markdown format with a unique timestamp.
- Store search results and summaries in a JSON file for later reference.
