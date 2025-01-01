# Configuration Guide

## Environment Variables

API keys and other sensitive information are managed through environment variables. Create a `.env` file in the root directory based on `.env.example`:

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your API keys
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `GOOGLE_API_KEY`: Your Google API key

Optional environment variables:
- `OPENAI_ORG_ID`: Your OpenAI organization ID
- `ANTHROPIC_ORG_ID`: Your Anthropic organization ID
- `LOG_LEVEL`: Logging level (default: INFO)

## Configuration File

Non-sensitive configuration is stored in `config/config.yaml`. This includes:

- Application settings
- UI preferences
- Logging configuration
- LLM preferences
- Tool paths and settings

Example configuration:
```yaml
app:
  name: JarvisOne
  version: 0.1.0

ui:
  theme: light
  layout: wide

llm:
  provider: Ollama (Local)
  model: mistral:latest
```

## Security Note

Never commit your `.env` file or API keys to version control. The `.env` file is listed in `.gitignore` to prevent accidental commits.
