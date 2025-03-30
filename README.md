# Commit Assistant Agent (CAA)

An AI-powered Git assistant that helps generate conventional commit messages and pull request descriptions using the smolagents library.

## Features

- Generate conventional commit messages based on staged changes
- Generate pull request titles and descriptions
- Configurable AI provider (supports various models like DeepSeek, OpenAI, etc.)
- Follows commitlint conventions
- Customizable templates for PR generation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/commit-assistant-agent.git
cd commit-assistant-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make the script executable:
```bash
chmod +x caa.py
```

4. Create a symbolic link (optional):
```bash
ln -s "$(pwd)/caa.py" /usr/local/bin/caa
```

## Configuration

1. Copy the example configuration:
```bash
cp config.yaml.example config.yaml
```

2. Edit `config.yaml` to set your preferred provider and model.

3. Set up your environment variables:
```bash
# For DeepSeek
export DEEPSEEK_API_KEY=your_api_key_here

# For OpenAI
export OPENAI_API_KEY=your_api_key_here
```

## Usage

### Generate Commit Message

```bash
# Basic usage
caa commit

# With scope
caa commit -s feature-name
```

### Generate Pull Request

```bash
# Basic usage
caa pr

# With custom title
caa pr -t "feat: implement new feature"

# With additional context
caa pr -b "This PR implements the following features: ..."
```

## Configuration Options

### Provider Configuration

```yaml
provider:
  name: "deepseek"  # Provider name (deepseek, openai, anthropic)
  model: "deepseek-chat"  # Model name
  api_key: ""  # Will be loaded from environment variable
```

### Commit Message Configuration

```yaml
commit:
  types:
    - feat
    - fix
    - docs
    - style
    - refactor
    - test
    - chore
  max_header_length: 72
  max_body_length: 100
```

### PR Template Configuration

```yaml
pr:
  template:
    title_format: "{type}({scope}): {description}"
    sections:
      - "Description"
      - "Changes"
      - "Testing"
      - "Additional Notes"
```

## License

MIT 