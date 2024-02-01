import instructor
from openai import OpenAI
from typing import Iterable, Optional, List, Literal
from pydantic import BaseModel, Field, field_validator
import os
import json
from enum import Enum

client = instructor.patch(OpenAI(), mode=instructor.function_calls.Mode.JSON)

class SentimentAnalysis(str, Enum):
    """posible sentiment types for the article"""
    CRITICAL = "critical"
    NEUTRAL = "neutral"
    TECHNICAL = "technical"
    CONTROVERSIAL = "controversial"
    PESSIMISTIC = "pessimistic"
    OPTIMISTIC = "optimistic"
    SPECULATIVE = "speculative"
    OTHER = "other"


ALLOWED_TYPES = [t.value for t in SentimentAnalysis]

class SentimentClassification(BaseModel):
    """Predict the sentiment of the article. Can be multiple.

    Here are some guidelines to predict the sentiment:

    CRITICAL: "The article criticizes or questions the subject, pointing out flaws or challenges."
    NEUTRAL: "The article remains unbiased and doesn't lean towards a positive or negative judgment."
    TECHNICAL: "The article is highly technical, using jargon or specialized language aimed at a informed audience."
    CONTROVERSIAL: "The article addresses a divisive topic or presents a polarizing viewpoint."
    PESSIMISTIC: "The article has a negative or gloomy tone, focusing on the downsides."
    OPTIMISTIC: "The article expresses hope, positivity, or a forward-looking perspective."
    SPECULATIVE: "The article discusses hypotheses, theories, or future possibilities."
    OTHER: "The article's sentiment does not fit into the standard categories."
    """

    classification: SentimentAnalysis = Field(
        description=f"An accuracy and correct prediction predicted dominating sentiments of the article. Only allowed types: {ALLOWED_TYPES}, should be used",
    )

    # @field_validator("classification", mode="before")
    # def validate_classification(cls, v):
    #     # sometimes the API returns a single value, just make sure it's a list
    #     if not isinstance(v, list):
    #         v = [v]
    #     return v

class Article(BaseModel):
    """Infer from the source data. Incase present literally in the data, but needs to be inferred from the data."""

    source: Optional[str] = Field(default=None, description="The source of the article", example="techcrunch.com")

    chain_of_thought: Optional[str] = Field(default=None, description="Reasoning behind the political stance of the media outlet that published the article. This is a very important field and should be filled out with the utmost care. It should be based on the media outlet known political stance", exclude=True)

    political_stance: Optional[Literal["left wing progressive", "liberal", "centre", "right wing conservative"]] = Field(default=None, description="The political stance of the media outlet")

    time_frame: str = Field(..., description="The month and year the article was published", example="January 2022")
    new_summary: str = Field(..., description="New more consice and entity dense summary of the article in max 300 characters", max_length=300)
    sentiment: Optional[SentimentClassification] = Field(default=None, description="The sentiment of the article")
    
   
Articles = Iterable[Article]

directory_path = '/Users/fausto/exa/output'
all_articles = []

print("Starting to process JSON files in the directory...")

# Iterate over each file in the directory
for filename in os.listdir(directory_path):
    if filename.endswith('.json'):
        file_path = os.path.join(directory_path, filename)
        print(f"Processing file: {filename}")

        # Read the contents of the file
        with open(file_path, 'r') as file:
            data = file.read()
        print("File data read successfully.")

        # Process the current file's data
        print("Sending data for processing...")
        # Process the current file's data
        articles = client.chat.completions.create(
            model="gpt-4-0125-preview",
            temperature=0.5,
            response_model=Article,
            messages=[
                {
                    "role": "system",
                    "content": "You are a perfect entity extraction system",
                },
                {
                    "role": "user",
                    "content": (
                        f"Consider the data below:\n{data}"
                        "Correctly segment it into articles and extract the source, time frame and summary for each article."
                        "Make sure the JSON is correct"
                    ),
                },
            ],
        )

        print("Data processed. Extracting articles...")
        for article in articles:
            assert isinstance(article, Article)  
            all_articles.append(json.loads(article.model_dump_json()))  # Collect articles as dictionaries
        print(f"Articles extracted from {filename}.")

print("All files processed. Writing to the output JSON file...")

# Write all articles to a JSON file
with open('classified_articles.json', 'w') as file:
    json.dump(all_articles, file, indent=4)

print("Data successfully written to classified_articles.json")
