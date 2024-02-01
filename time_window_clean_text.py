from exa_py import Exa
from bs4 import BeautifulSoup
from openai import OpenAI
import os
from datetime import datetime
from termcolor import colored
import json

def search_and_summarize(question, start_date, end_date, num_results_per_domain):
    print(colored("Initializing Exa and OpenAI clients...", 'green'))
    exa = Exa(os.getenv('EXA_API_KEY'))
    openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    year, month, _ = start_date.split("-")
    domains = ["techcrunch.com", "nytimes.com", "theverge.com", "wired.com", "breitbart.com"]
    all_summaries = []

    md_filename = f'cleaned_text_{month}_{year}.md'

    for domain in domains:
        print(colored(f"Searching {num_results_per_domain} results for: '{question}' within {start_date} to {end_date} in {domain}", 'green'))
        try:
            responses = exa.search_and_contents(
                question,
                start_published_date=start_date, 
                end_published_date=end_date,
                num_results=num_results_per_domain, 
                include_domains=[domain], 
                use_autoprompt=True,
                text=True,
                highlights={"highlights_per_url": 2, "num_sentences": 3, "query": "These are the highlight queries:"}
            )

            url_summaries = []

            for result in responses.results:
                if result.text:
                    soup = BeautifulSoup(result.text, 'html.parser')
                    text = soup.get_text()
                    clean_text = ' '.join(text.split())

                    with open(md_filename, 'a') as md_file:
                        md_file.write(f"\n## Timeframe: {month}/{year}\n")
                        md_file.write(f"### URL: {result.url}\n")
                        md_file.write(f"### Relevance Score: {result.score}\n")
                        md_file.write(f"### Highlights: {result.highlights}\n")
                        md_file.write(f"\n{clean_text}\n")
                        md_file.write("\n---\n")

                    url_summaries.append({
                        "timeframe": f"{month}/{year}",
                        "url": result.url, 
                        "relevance_score": result.score, 
                        "highlights": result.highlights, 
                        "summary": None  # Placeholder for GPT summary
                    })

            all_summaries.extend(url_summaries)
        
        except Exception as e:
            print(colored(f"An error occurred while searching: {e}", 'red'))

    json_filename = f'output_{month}_{year}.json'
    with open(json_filename, 'w') as f:
        json.dump({"timeframe": f"{month}/{year}", "question": question, "summaries": all_summaries}, f, indent=4)
        f.write('\n')

    print(colored(f"Data has been saved to {json_filename}", 'red'))

    return all_summaries

# Get user input before iterating over time windows
question = input(colored("What news are you looking for?: ", 'yellow'))
num_results_per_domain = input(colored("How many results per domain to summarize? ", 'yellow'))

try:
    num_results_per_domain = int(num_results_per_domain)
except ValueError:
    print(colored("Please enter a valid number for results to summarize.", 'red'))
    exit(0)

# Define the time windows
time_windows = [
    ("2022-01-01", "2022-01-31"),
    ("2023-01-01", "2023-01-31"),
    ("2024-01-01", "2024-01-31")
]

# Iterate over each time window using the same query and number of results
for start_date, end_date in time_windows:
    print(colored(f"Summarizing for timeframe: {start_date} to {end_date}", 'green'))
    summary = search_and_summarize(question, start_date, end_date, num_results_per_domain)
    print(colored("Done for this timeframe.", 'green'))
