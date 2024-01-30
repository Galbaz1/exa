# pip install exa_py
from exa_py import Exa
import os

# Create an Exa instance with your API key
exa = Exa(os.getenv('METAPHOR_API_KEY'))

# Search using the Exa API
search_response = exa.search_and_contents(
    query="Here is the entire food menu of the Louisiana:",
    include_domains=["thelouisiana.nl"],
    start_published_date="2023-06-25",
    text=True  # Specify if you want the text contents of the pages
)

# Print content for each result
for result in search_response.results:
    print(f"Title: {result.title}\nURL: {result.url}\nContent:\n{result.text}\n")
