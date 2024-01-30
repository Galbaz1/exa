
from exa_py import Exa
from bs4 import BeautifulSoup
from openai import OpenAI
import os
from datetime import datetime, timedelta
from termcolor import colored
import json

three_year_ago = (datetime.now() - timedelta(days=365*3))
one_week_ago = (datetime.now() - timedelta(days=7))
date_cutoff = three_year_ago.strftime("%Y-%m-%d")

def search_and_summarize(question, num_results=5):
    print(colored("Initializing Exa and OpenAI clients...", 'green'))
    exa = Exa(os.getenv('METAPHOR_API_KEY'))
    openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    print(colored(f"Searching Exa for: '{question}' with a date cutoff of {date_cutoff}", 'green'))
    responses = exa.search_and_contents(
        question, 
        start_published_date=date_cutoff, 
        num_results=num_results, 
        use_autoprompt=True,
        highlights=True,
        text=True
    )

    if responses.autoprompt_string:
        print(colored("Reformed question by Exa's autoprompt:", 'green'), responses.autoprompt_string)
    else:
        print(colored("No autoprompt reformation was applied.", 'red'))

    print(colored("Processing contents from Exa search results...", 'green'))
    extracts = []
    for result in responses.results:
        if result.text:
            soup = BeautifulSoup(result.text, 'html.parser')
            text = soup.get_text()
            clean_text = ' '.join(text.split())
            extracts.append(clean_text)

            print(colored(f"\nURL: {result.url}", 'blue'))
            print(colored(f"Relevance Score: {result.score}", 'magenta'))
            print(colored(f"Highlights: {result.highlights}", 'yellow'))
            print(colored(f"Cleaned Text: {clean_text}", 'cyan'))  # Added line to print cleaned text

            
    full_extract = ' '.join(extracts)
    messages = [
        {"role": "system", "content": "You are a helpful research assistant. Start by generating 3 new topics to explore related to the user query. Use the question and topics (the original and the 3 new ones) to put the text provided in pespective."},
        {"role": "user", "content": question},
        {"role": "user", "content": full_extract}
    ]

    print(colored("Querying GPT...", 'green'))
    gpt_responses = ''

    response = openai.chat.completions.create(
        model="gpt-4-0125-preview",
        temperature=0.3,
        stream=True,
        messages=messages
    )

    for chunk in response:
        if chunk.choices[0].delta.content: 
            text_chunk = chunk.choices[0].delta.content 
            print(text_chunk, end='', flush=True)
            gpt_responses += str(text_chunk)

    print(colored("Summarization complete.", 'green'))

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"summary_{timestamp}.md"
    with open(filename, 'w') as file:
        file.write(f"# Summary for: {question}\n\n")
        file.write(gpt_responses)
    print(colored(f"Summary has been saved to {filename}", 'red'))

# Save to JSON file
    json_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Use timestamp to create a unique filename
    data = {
        "question": question,
        "full_extract": full_extract,  # Ensure full_extract is defined earlier in the function
        "gpt_response": gpt_responses
    }

    json_filename = f'output_{json_timestamp}.json'  # Modified to include timestamp in filename
    with open(json_filename, 'w') as f:  # Changed from 'a' to 'w' to write in a new file each time
        json.dump(data, f, indent=4)
        f.write('\n')

    print(colored(f"Data has been saved to {json_filename}", 'red'))

    return gpt_responses

while True:
    question = input(colored("Ask a question: ", 'yellow'))
    num_results = input(colored("How many results to summarize? ", 'yellow'))
    try:
        num_results = int(num_results)
    except ValueError:
        print(colored("Please enter a valid number for results to summarize.", 'red'))
        continue

    print(colored("Summarizing...", 'green'))
    summary = search_and_summarize(question, num_results)
 
    print(colored("Done.", 'green'))