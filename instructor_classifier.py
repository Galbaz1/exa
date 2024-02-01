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
    TECHNICAL = "technical"
    CONTROVERSIAL = "controversial"
    PESSIMISTIC = "pessimistic"
    OPTIMISTIC = "optimistic"
    SPECULATIVE = "speculative"
    OTHER = "other"


ALLOWED_TYPES = [t.value for t in SentimentAnalysis]

class SentimentClassification(BaseModel):
    """Predict the sentiment of the article. Can be more than be one.

    Here are some guidelines to predict the sentiment:

    CRITICAL: "The article criticizes or questions the subject, pointing out flaws, risks or challenges."
    TECHNICAL: "The article is highly technical, using jargon or specialized language aimed at a informed audience, not suitable for the general public."
    CONTROVERSIAL: "The article addresses a divisive, sexual or violent topic or presents a polarizing viewpoint."
    PESSIMISTIC: "The article has a negative or gloomy tone, focusing on the downsides and risks for work, life or humanity."
    OPTIMISTIC: "The article expresses hope, positivity, or a forward-looking perspective for the future."
    SPECULATIVE: "The article is clearly not grounded in truth, or is populistic."
    OTHER: "The article's sentiment does not fit into the standard categories."
    """

    classifications: List[SentimentAnalysis] = Field(
        description=f"An accuracy and correct prediction predicted dominating sentiments of the article. Only allowed types: {ALLOWED_TYPES}, should be used",

   # classification: SentimentAnalysis = Field(
   #      description=f"An accuracy and correct prediction predicted dominating sentiment of the article. Only allowed types: {ALLOWED_TYPES}, should be used",
    )

    @field_validator("classifications", mode="before")
    def validate_classification(cls, v):
        # sometimes the API returns a single value, just make sure it's a list
        if not isinstance(v, list):
            v = [v]
        return v

class Article(BaseModel):
    """Infer from the source data. Incase present literally in the data, information needs to be inferred from the data."""

    source: Optional[str] = Field(default=None, description="The source of the article", example="techcrunch.com")

    chain_of_thought: str = Field(default=None, description="Reasoning behind the political stance of the media outlet that published the article. It should be based on the media outlet known political stance, not on the article contents", exclude=True)

    political_stance: Optional[Literal["left wing progressive", "liberal", "centre", "right wing conservative"]] = Field(default=None, description="The political stance of the media outlet")

    time_frame: str = Field(..., description="The month and year the article was published", example="January 2022")
    new_summary: str = Field(..., description="New more consice and entity dense summary of the article in max 300 characters", max_length=300)
    sentiment: SentimentClassification = Field(description="The sentiment of the article")
    
   
Articles = Iterable[Article]

directory_path = '/Users/faustoalbers/Coding/exa/output'
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
            temperature=0.1,
            response_model=Articles,
            messages=[
                {
                    "role": "system",
                    "content": "You are a perfect entity extraction system",
                },
                {
                    "role": "user",
                    "content": (
                        f"Consider the data below:\n{data}"
                        "Perform thoughtful analysis and extract, or infer the information"
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
