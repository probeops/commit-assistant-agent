#!/usr/bin/env python3

import os
import sys
import click
import yaml
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from git import Repo

# Load environment variables
load_dotenv()

def load_config():
    # Look for config in current directory first
    local_config = Path("config.yaml")
    if local_config.exists():
        config_path = local_config
    else:
        # Fall back to package default config
        package_dir = Path(__file__).parent
        config_path = package_dir / "config.yaml"
        if not config_path.exists():
            click.echo("Error: config.yaml not found in current directory or package", err=True)
            sys.exit(1)
    
    with open(config_path) as f:
        return yaml.safe_load(f)

def get_git_diff():
    try:
        repo = Repo(os.getcwd())
        # Check for staged changes first
        if repo.index.diff("HEAD"):
            return repo.git.diff("--staged")
        # If no staged changes, check for unstaged changes
        elif repo.is_dirty():
            return repo.git.diff()
        return ""
    except Exception as e:
        click.echo(f"Error getting git diff: {str(e)}", err=True)
        return ""

def validate_commit_message(message, config):
    commit_config = config["commit"]
    
    # Basic validation
    if not message or len(message.split("\n")[0]) > commit_config["max_header_length"]:
        return False
    
    # Check commit type
    commit_type = message.split(":")[0].split("(")[0] if ":" in message else ""
    return commit_type in commit_config["types"]

def call_deepseek_api(prompt, api_key):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that generates git commit messages."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        message = result["choices"][0]["message"]["content"]
        return message.strip()
    except requests.exceptions.RequestException as e:
        click.echo(f"API request error: {str(e)}", err=True)
        return None
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        click.echo(f"Error parsing API response: {str(e)}", err=True)
        return None

@click.command()
@click.option('--scope', '-s', help='The scope of the commit')
@click.option('--brief/--no-brief', default=False, help='Use brief style for commit message')
@click.option('--emoji/--no-emoji', default=False, help='Include emoji in commit message')
@click.option('--simplified/--no-simplified', default=False, help='Use simplified diff for API compatibility')
@click.option('--force/--no-force', default=False, help='Force accept the message even if validation fails')

def commit(scope, brief, emoji, simplified, force):
    """Generate a commit message based on staged changes (direct API call)"""
    try:
        config = load_config()
    except Exception as e:
        click.echo(f"Error loading config: {str(e)}", err=True)
        sys.exit(1)
    
    diff = get_git_diff()
    if not diff:
        click.echo("No changes detected")
        return
    
    # For API compatibility, optionally simplify the diff
    if simplified and len(diff) > 1000:
        lines = diff.split('\n')
        first_10_lines = '\n'.join(lines[:10])
        last_10_lines = '\n'.join(lines[-10:])
        diff_summary = f"{first_10_lines}\n\n... [diff truncated for API compatibility] ...\n\n{last_10_lines}"
        diff = diff_summary
        click.echo("Using simplified diff for API compatibility")
    
    # Get API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        click.echo(f"Error: DEEPSEEK_API_KEY not found in environment", err=True)
        sys.exit(1)
    
    prompt = f"""Please write a commit message for my changes.
Only respond with the commit message. Don't give any notes.
Explain what were the changes and why the changes were done.
Focus the most important changes.
Use the present tense.
Use a semantic commit prefix.
Hard wrap lines at 72 characters.
Ensure the title is only 50 characters.
Do not start any lines with the hash symbol.
{f'Use brief, concise language' if brief else ''}
{f'Include relevant emoji at the start of the title' if emoji else ''}

Available semantic prefixes: {', '.join(config['commit']['types'])}
Max header length: {config['commit']['max_header_length']}
Scope: {scope if scope else 'not specified'}

Here is my git diff:
```
{diff}
```"""
    
    click.echo("Generating commit message via direct API call...")
    message = call_deepseek_api(prompt, api_key)
    
    if message:
        if not validate_commit_message(message, config) and not force:
            click.echo("Error: Generated commit message does not follow the convention", err=True)
            click.echo("Run with --force to use it anyway.", err=True)
            return
        
        click.echo("\nGenerated commit message:")
        click.echo("-" * 40)
        click.echo(message)
        click.echo("-" * 40)
    else:
        click.echo("Failed to generate a commit message", err=True)

if __name__ == "__main__":
    commit() 