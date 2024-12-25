from core.core_agent import CoreAgent # Import the CoreAgent

everything_docs = "Documentation pour Everything..." # Replace this by your documentation

def search_function(query: str):
    """Execute search and format results."""
    results = ["resultat 1", "resultat 2", "resultat 3"]  # Replace by actual search
    return {
        "results": results,
        "count": len(results)
    }

def format_result(content):
    return f"Formatted: {content}"

agent = CoreAgent(
    agent_name="File Search Agent",
    system_instructions=[
        "You are a file search query analyzer. Format search queries for Everything search engine.",
        "Convert natural language to Everything syntax using the following documentation:",
        "",
        everything_docs,
        "",
        "After formatting the query, I will execute it using Everything search engine."
    ],
    tools=[search_function],
    output_formatter = format_result
)


if __name__ == '__main__':
    query = "cherche des fichier pdf avec le mot clé test"
    response = agent.run(query)
    print(response['content'])