import ssl
import json
import urllib.request

def lambda_handler(event, context):
    request_string = event.get("request", "default value")

    # Split the request_string at the SEARCH marker
    if "\n\nSEARCH" in request_string:
        prompt_part, search_part = request_string.split("\nSEARCH", 1)
        # Remove trailing colon after PROMPT or SEARCH if present
        prompt_part = prompt_part.strip()
        if prompt_part.upper().startswith("PROMPT"):
            prompt_part = prompt_part[6:].lstrip()  # Remove 'PROMPT'
            if prompt_part.startswith(":"):
                prompt_part = prompt_part[1:].lstrip()
        search_term = search_part.strip()
        if search_term.startswith(":"):
            search_term = search_term[1:].lstrip()
    else:
        prompt_part = request_string
        search_term = request_string  # fallback

    context_ssl = ssl._create_unverified_context()
    enrichment = ""
    try:
        # Step 1: Search for the term using Wikipedia's search API
        search_api_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(search_term)}&format=json"
        search_req = urllib.request.Request(search_api_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(search_req, context=context_ssl) as search_response:
            search_data = json.loads(search_response.read().decode())
        search_results = search_data.get("query", {}).get("search", [])
        if search_results:
            top_title = search_results[0]["title"]
            # Step 2: Get the summary for the top result
            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(top_title)}"
            summary_req = urllib.request.Request(summary_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(summary_req, context=context_ssl) as summary_response:
                summary_data = json.loads(summary_response.read().decode())
            enrichment = summary_data.get("extract", "")
        else:
            enrichment = "No Wikipedia results found."
    except Exception as e:
        enrichment = f"Wikipedia lookup failed: {str(e)}"

    prompt = f"{prompt_part.strip()}\n\nEnrichment: {enrichment.strip()}\n\n"
    return {
        "statusCode": 200,
        "request": prompt  # chain for next agent in the step function orchestration
    }