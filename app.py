import json
import instructor
import asyncio
import re
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from typing import List
from enum import Enum

client = instructor.patch(AsyncOpenAI(), mode=instructor.Mode.TOOLS)
sem = asyncio.Semaphore(5)

class SentimentType(Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"

class ArticleSentiment(BaseModel):
    sentiment: SentimentType = Field(...)

async def classify(article_content: str) -> ArticleSentiment:
    async with sem:  # Apply simple rate limiting
        response = await client.chat.completions.create(
            model="gpt-4",
            prompt=f"Classify the sentiment of the following text: {article_content[:4000]}",  # Trim to fit model token limits
            max_tokens=60
        )
        sentiment_text = response['choices'][0]['text'].strip().upper()
        # Convert response to SentimentType
        if sentiment_text not in SentimentType._member_names_:
            sentiment = SentimentType.NEUTRAL
        else:
            sentiment = SentimentType[sentiment_text]
        return {"content": article_content, "sentiment": sentiment.value}

async def main(articles: List[str], *, path_to_json: str):
    tasks = [classify(article) for article in articles]
    results = await asyncio.gather(*tasks)

    with open(path_to_json, "w") as f:
        json.dump(results, f, indent=4)

def extract_articles_from_md(md_path: str) -> List[str]:
    with open(md_path, "r", encoding="utf-8") as md_file:
        content = md_file.read()
        # Splitting articles based on the provided markdown structure
        articles_raw = content.split('---\n')[1:]  # Skip the first split as it might be header or empty
        articles_content = []
        for article_raw in articles_raw:
            # Extracting the main content of each article
            match = re.search(r'### Highlights: \[.*?\]\n\n(.+)', article_raw, re.DOTALL)
            if match:
                articles_content.append(match.group(1).strip())
        return articles_content

if __name__ == "__main__":
    md_path = "cleaned_text_01_2022.md"
    path_to_json = "article_sentiments.json"
    articles = extract_articles_from_md(md_path)
    asyncio.run(main(articles, path_to_json=path_to_json))