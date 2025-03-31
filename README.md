# Commit Assistant Agent

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

The tool will be available as `caa` in your terminal. You can use it from any git repository:

```bash
# Generate a commit message for staged changes
caa commit [OPTIONS]

# Generate a PR title and description
caa pr SOURCE_BRANCH TARGET_BRANCH [OPTIONS]

# Commit command options:
caa commit --help  # Show all available options
caa commit --scope backend  # Specify commit scope
caa commit --brief  # Generate brief commit message
caa commit --emoji  # Include emoji in commit message
caa commit --simplified  # Use simplified diff for large changes
caa commit --force  # Force accept message even if validation fails

# PR command options:
caa pr --help  # Show all available options
caa pr feature-branch main --scope backend  # Generate PR with scope
caa pr feature-branch main --brief  # Generate brief PR content
caa pr feature-branch main --simplified  # Use simplified diff for large changes
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