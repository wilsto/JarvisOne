from core.core_agent import CoreAgent, DummyLLM # Import the CoreAgent and DummyLLM

agent = CoreAgent(
    agent_name="Chat Agent",
    system_instructions="Tu es un assistant chat qui répond aux questions."
)

if __name__ == '__main__':
    query = "Bonjour, comment allez-vous ?"
    response = agent.run(query)
    print(response['content'])