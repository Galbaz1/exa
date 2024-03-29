from exa_py import Exa
from bs4 import BeautifulSoup
import os
from datetime import datetime
from termcolor import colored
import json

def search_and_get_content(question, start_date, end_date, num_results_per_domain):
    print(colored("Initializing Exa and OpenAI clients...", 'green'))
    exa = Exa(os.getenv('METAPHOR_API_KEY'))

    year, month, _ = start_date.split("-")
    domains = ["techcrunch.com", "nytimes.com", "foxnews.com", "wired.com", "breitbart.com"]
    all_content = []

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
                #highlights={"highlights_per_url": 2, "num_sentences": 3, "query": "These are the highlight queries:"}

            )


            if responses.autoprompt_string:
                print(colored("Reformed question by Exa's autoprompt:", 'green'), responses.autoprompt_string)
            else:
                print(colored("No autoprompt reformation was applied.", 'red'))


            url_content = []

            for result in responses.results:
                if result.text:
                    soup = BeautifulSoup(result.text, 'html.parser')
                    text = soup.get_text()
                    clean_text = ' '.join(text.split())

                    with open(md_filename, 'a') as md_file:
                        md_file.write(f"\n## Article published: {month}/{year}\n")
                        md_file.write(f"### Source URL: {result.url}\n")
                        md_file.write(f"### Query Relevance Score: {result.score}\n")
                        md_file.write(f"### Highlights: {result.highlights}\n")
                        md_file.write(f"\n{clean_text}\n")
                        md_file.write("\n---\n")

                    url_content.append({
                        "article_published": f"{month}/{year}", 
                        "source": result.url, 
                        "relevance_score": result.score, 
                        "content": f"{clean_text}",

                    })

            all_content.extend(url_content)
        
        except Exception as e:
            print(colored(f"An error occurred while searching: {e}", 'red'))

    json_filename = f'output_{month}_{year}.json'
    with open(json_filename, 'w') as f:
        json.dump({
            "time_window": f"{month}/{year}",
            "articles": all_content
        }, f, indent=4)
        f.write('\n')

    print(colored(f"Data has been saved to {json_filename}", 'red'))

    return all_content

# Get user input before iterating over time windows
question = input(colored("What news are you looking for?: ", 'yellow'))
num_results_per_domain = input(colored("How many results per domain to search for? ", 'yellow'))

try:
    num_results_per_domain = int(num_results_per_domain)
except ValueError:
    print(colored("Please enter a valid number for results to summarize.", 'red'))
    exit(0)

# Define the time windows
time_windows = [
    ("2015-01-01", "2015-01-31"),
    ("2020-01-01", "2020-01-31"),
    ("2024-01-01", "2024-01-31")
]

# Iterate over each time window using the same query and number of results
for start_date, end_date in time_windows:
    print(colored(f"Searching for timeframe: {start_date} to {end_date}", 'green'))
    summary = search_and_get_content(question, start_date, end_date, num_results_per_domain)
    print(colored("Done for this timeframe.", 'green'))
