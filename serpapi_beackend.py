import os
import serpapi


def search_web(query):

    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        return "SerpApi API key is not configured."

    client = serpapi.Client(api_key=api_key)

    results = client.search({
        "engine": "google",
        "q": query,
        "location": "India"
    })

    organic_results = results.get("organic_results", [])

    if not organic_results:
        return "No useful web results were found."

    output = []

    for result in organic_results[:5]:

        title = result.get("title", "No title")
        link = result.get("link", "")
        snippet = result.get("snippet", "")

        output.append(
            f"Title: {title}\n"
            f"Snippet: {snippet}\n"
            f"Link: {link}"
        )

    return "\n\n".join(output)