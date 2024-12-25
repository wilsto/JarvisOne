import logging
from core.core_agent import CoreAgent, DummyLLM

# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

system_instructions = """You are a query analyzer. 
                         Your job is to understand user intent and return the name of the agent
                         that should be used to process the query. The available agents are : 
                         'chat_agent' and 'file_search_agent'. 
                         If the query is related to file search return 'file_search_agent', if the query is a general conversation, return 'chat_agent'. 
                         Return only the agent's name.
                        """

# Create the agent instance
agent = CoreAgent(
    agent_name="Query Analyzer Agent",
    system_instructions=system_instructions,
    llm = DummyLLM()
)

def analyze_query_tool(query: str) -> str:
    """Analyzes the query and returns the name of the agent to use."""
    return agent.run(query)['content']

if __name__ == '__main__':
    query = "cherche un fichier pdf"
    response = agent.run(query)
    print(response['content'])