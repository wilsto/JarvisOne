import logging
from typing import Dict, Any
import importlib
import pkgutil
from core.core_agent import CoreAgent
from .query_analyzer_agent import analyze_query_tool, agent as query_analyzer_agent

# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AgentOrchestrator:
    """Orchestrates the routing of queries to appropriate agents."""

    def __init__(self):
        """Initializes the orchestrator with available agents."""
        self.query_analyzer = query_analyzer_agent
        self.available_agents = self._load_agents()
        logger.info(f"AgentOrchestrator initialized with agents: {list(self.available_agents.keys())}")

    def _load_agents(self) -> Dict[str, CoreAgent]:
        """Loads available agents from the agents package."""
        available_agents = {}
        package = importlib.import_module("features.agents")
        for _, name, is_package in pkgutil.walk_packages(package.__path__):
            if not is_package and name != "__init__":
                module = importlib.import_module(f"features.agents.{name}")
                for item_name in module.__dict__.keys():
                     item = module.__dict__[item_name]
                     if isinstance(item, CoreAgent):
                        available_agents[name.replace("_agent", "")] = item
        
        return available_agents

    def _select_agent(self, user_query: str) -> CoreAgent:
        """Selects the appropriate agent based on user query."""
        try:
            agent_name = analyze_query_tool(user_query)
            logger.info(f"Query analyzer identified agent: {agent_name}")
            
            # Normalize agent name by removing _agent suffix if present
            normalized_name = agent_name.replace("_agent", "")
            
            if normalized_name in self.available_agents:
                return self.available_agents[normalized_name]
            else:
                logger.warning(f"No agent found for name: {agent_name}. Defaulting to Chat Agent")
                return self.available_agents["chat"]
        except Exception as e:
            logger.error(f"Error in agent selection: {str(e)}", exc_info=True)
            return self.available_agents["chat"]

    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process a user query by routing it to the appropriate agent."""
        try:
            selected_agent = self._select_agent(user_query)
            logger.info(f"Selected agent: {selected_agent.agent_name}")
            response = selected_agent.run(user_query)
            logger.info(f"Response from agent '{selected_agent.agent_name}': {response}")
            return response
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return {"error": True, "message": f"An error occurred while processing your request."}