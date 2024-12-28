<!-- markdownlint-disable MD029 -->
# JarvisOne: Your Modular Personal AI Assistant 

JarvisOne is a modular and scalable conversational AI assistant that integrates with external tools, notably for file searching. Designed to be flexible and customizable, JarvisOne allows you to interact with different LLMs and manage your files effectively.

## Key Features ✨

* **Modular Architecture:** Built for easy integration of new features and external tools.
* **File Search:** Powerful file searching capability via integration with [Everything](https://www.voidtools.com/).
* **Multiple LLMs:** Supports various Language Models, including Gemini 2.0, ChatGPT-4, Ollama and Anthropic.
* **Workspace Support:** Multiple workspaces each with unique system prompt.
* **Intuitive Chat Interface:** User-friendly chat interface built with Streamlit.
* **Flexible Configuration:** Easy configuration of LLM providers, external tools, and system prompts for different use cases.

## Installation 🚀

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/JarvisOne.git
    cd JarvisOne
    ```

2. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Configure your environment:**
    * Copy `.env.example` to `.env`.
    * Add your API keys and paths to external tools to the `.env` file as needed.
    * Make sure to setup your `config/config.yaml` to your specifications

4. **Install required external tools:**
    * For file searching: Download and install [Everything](https://www.voidtools.com/).
    * Ensure that external tools are correctly configured and running.

## Usage 💬

1. **Launch the application:**

    ```bash
    streamlit run src/main.py
    ```

2. **In the interface:**
    * Select your preferred LLM provider and workspace from the sidebar.
    * Use the chat input to interact with JarvisOne.
    * Access external tool functionalities via natural language in the chat.

## Usage Examples 💡

* "Find markdown files modified today" (using Everything).
* "Search for Word documents containing 'report'" (using Everything).
* "Explain the prompt system"

## Contribution Guidelines 🤝

Contributions are welcome! Here’s how you can contribute:

1. Fork the project.
2. Create a new branch: `git checkout -b feature/YourFeature`.
3. Commit your changes: `git commit -m 'Add YourFeature'`.
4. Push to the branch: `git push origin feature/YourFeature`.
5. Open a pull request.
