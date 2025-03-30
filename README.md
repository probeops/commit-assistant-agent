# Commit Assistant Agent (CAA)

An AI-powered Git assistant that helps generate conventional commit messages and pull request descriptions using the smolagents library.

## Features

- Generate conventional commit messages based on staged changes
- Generate pull request titles and descriptions
- Configurable AI provider (supports various models like DeepSeek, OpenAI, etc.)
- Follows commitlint conventions
- Customizable templates for PR generation

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/commit-assistant-agent.git
   cd commit-assistant-agent
   ```

2. Create a virtual environment and install dependencies:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Set up your environment:
   ```
   cp config.yaml.example config.yaml
   cp .env.example .env  # If .env.example exists
   ```

4. Get your API keys:
   - For DeepSeek: Sign up at [DeepSeek AI](https://deepseek.com) and generate an API key
   - Add your API key to the `.env` file: `DEEPSEEK_API_KEY=your_api_key_here`

5. Run the tool using the provided script:
   ```
   ./run.sh commit  # Generate commit message
   ./run.sh pr      # Generate PR description
   ```

6. Optional command flags:
   ```
   ./run.sh commit --scope frontend --emoji  # Generate commit message for frontend with emoji
   ./run.sh pr --title "Custom PR Title" --body "Additional context"
   ```

## API Compatibility Mode

If you encounter JSON deserialization issues with the smolagents library, you can use the direct API implementation:

```
./run.sh direct [options]  # Uses direct API calls instead of smolagents
```

This alternate implementation makes direct API calls to the LLM provider and bypasses compatibility issues with the smolagents library. It supports the same options as the standard implementation:

```
./run.sh direct --simplified --force  # Simplify diff and force accept any message
```

## Configuration

1. Copy the example configuration:
```