# Commit Assistant

An AI-powered git commit message generator using DeepSeek API.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/commit-assistant.git
cd commit-assistant
```

2. Install the package:
```bash
pip install -e .
```

3. Set up your environment:
Create a `.env` file in your project directory with your DeepSeek API key:
```bash
DEEPSEEK_API_KEY=your_api_key_here
```

## Usage

The tool will be available as `commit-assistant` in your terminal. You can use it from any git repository:

```bash
# Generate a commit message for staged changes
commit-assistant

# Options:
commit-assistant --help  # Show all available options
commit-assistant --scope backend  # Specify commit scope
commit-assistant --brief  # Generate brief commit message
commit-assistant --emoji  # Include emoji in commit message
commit-assistant --simplified  # Use simplified diff for large changes
commit-assistant --force  # Force accept message even if validation fails
```

## Configuration

The tool looks for a `config.yaml` file in the current directory. If not found, it uses the default configuration from the package.

You can create your own `config.yaml` to customize the settings:

```yaml
commit:
  types:
    - "feat"
    - "fix"
    - "docs"
    - "style"
    - "refactor"
    - "test"
    - "chore"
    - "perf"
  max_header_length: 50

pr:
  template:
    title_format: "{type}({scope}): {description}"
    sections:
      - "Summary"
      - "Changes"
      - "Testing"
      - "Notes"
```

## Requirements

- Python 3.6+
- Git
- DeepSeek API key