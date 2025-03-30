#!/usr/bin/env python3

import os
import sys
import click
import yaml
import json
from pathlib import Path
from dotenv import load_dotenv
from git import Repo
from smolagents import CodeAgent, OpenAIServerModel

# Load environment variables
load_dotenv()

def load_config():
    config_path = Path("config.yaml")
    if not config_path.exists():
        click.echo("Error: config.yaml not found", err=True)
        sys.exit(1)
    
    with open(config_path) as f:
        return yaml.safe_load(f)

def get_agent(config):
    provider_config = config["provider"]
    api_key = os.getenv(f"{provider_config['name'].upper()}_API_KEY")
    if not api_key:
        click.echo(f"Error: {provider_config['name'].upper()}_API_KEY not found in environment", err=True)
        sys.exit(1)
    
    try:
        # Use the correct model initialization based on provider
        if provider_config["name"].lower() == "deepseek":
            # Standard DeepSeek models that should work
            valid_models = ["deepseek-chat", "deepseek-coder"]
            
            # Try to use the model specified in config
            model_id = provider_config.get("model", "deepseek-coder")
            
            # For DeepSeek specific errors
            if not model_id or model_id.strip() == "":
                model_id = "deepseek-coder"
                click.echo(f"Warning: No model specified, using default model '{model_id}'", err=True)
            
            # Add DeepSeek-specific parameters to avoid JSON deserialization issues
            model = OpenAIServerModel(
                model_id=model_id,
                api_base="https://api.deepseek.com/v1/",
                api_key=api_key,
                # Add specific parameters to handle response issues
                extra_headers={"Accept": "application/json"}
            )
            # Initialize CodeAgent with required empty tools list
            return CodeAgent(model=model, tools=[])
        else:
            # For other providers, use standard initialization
            return CodeAgent(
                provider=provider_config["name"],
                model=provider_config.get("model"),
                api_key=api_key,
                tools=[]
            )
    except Exception as e:
        click.echo(f"Error initializing the AI agent: {str(e)}", err=True)
        sys.exit(1)

def get_git_diff():
    try:
        repo = Repo(".")
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

@click.group()
def cli():
    """Commit Assistant Agent - AI-powered git helper"""
    pass

@cli.command()
@click.option('--scope', '-s', help='The scope of the commit')
@click.option('--brief/--no-brief', default=False, help='Use brief style for commit message')
@click.option('--emoji/--no-emoji', default=False, help='Include emoji in commit message')
@click.option('--simplified/--no-simplified', default=False, help='Use simplified diff for API compatibility')
@click.option('--force/--no-force', default=False, help='Force accept the message even if validation fails')
def commit(scope, brief, emoji, simplified, force):
    """Generate a commit message based on staged changes"""
    config = load_config()
    
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
    
    try:
        agent = get_agent(config)
        
        prompt = f"""Please could you write a commit message for my changes.
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
        
        try:
            response = agent.run(prompt)
            message = response.strip()
            
            if not validate_commit_message(message, config) and not force:
                click.echo("Error: Generated commit message does not follow the convention", err=True)
                return
            
            click.echo("\nGenerated commit message:")
            click.echo("-" * 40)
            click.echo(message)
            click.echo("-" * 40)
        except Exception as api_error:
            error_str = str(api_error)
            click.echo(f"API Error: {error_str}", err=True)
            
            # Check for error output that contains a commit message
            if "code parsing" in error_str and "Here is your code snippet" in error_str:
                # Try to extract the commit message from the error output
                lines = error_str.split('\n')
                message_lines = []
                found_marker = False
                
                for line in lines:
                    if "Here is your code snippet:" in line:
                        found_marker = True
                        continue
                    if found_marker and line.strip() and not "Make sure to include code" in line:
                        # Just in case there's indentation
                        clean_line = line.strip()
                        # Remove common indentation from error output
                        if clean_line.startswith('            '):
                            clean_line = clean_line[12:]
                        message_lines.append(clean_line)
                    if found_marker and "Make sure to include code" in line:
                        break
                
                if message_lines:
                    message = '\n'.join(message_lines)
                    click.echo("\nExtracted commit message from error output:")
                    click.echo("-" * 40)
                    click.echo(message)
                    click.echo("-" * 40)
                    
                    if validate_commit_message(message, config) or force:
                        click.echo("Commit message extracted successfully!")
                        return
                    else:
                        click.echo("Warning: The extracted message does not follow the commit convention.", err=True)
                        if force:
                            return
                        click.echo("Run with --force to use it anyway.", err=True)
            
            # Try simplified diff approach
            if not simplified and ("deserialize" in error_str.lower() or "json" in error_str.lower()):
                click.echo("\nTrying again with simplified diff. Run with --simplified flag to use this automatically.", err=True)
                # Try again with simplified diff
                lines = diff.split('\n')
                first_10_lines = '\n'.join(lines[:10])
                last_10_lines = '\n'.join(lines[-10:])
                diff_summary = f"{first_10_lines}\n\n... [diff truncated for API compatibility] ...\n\n{last_10_lines}"
                
                prompt = prompt.replace(diff, diff_summary)
                try:
                    response = agent.run(prompt)
                    message = response.strip()
                    
                    if not validate_commit_message(message, config) and not force:
                        click.echo("Error: Generated commit message does not follow the convention", err=True)
                        return
                    
                    click.echo("\nGenerated commit message (with simplified diff):")
                    click.echo("-" * 40)
                    click.echo(message)
                    click.echo("-" * 40)
                    return
                except Exception as simplified_error:
                    click.echo(f"Error with simplified diff: {str(simplified_error)}", err=True)
            
            # Handle specific error types
            if "deserialize" in error_str.lower() or "json" in error_str.lower():
                click.echo("\nJSON deserialization error detected. This is likely due to an issue with the API response format.", err=True)
                click.echo("Possible solutions:", err=True)
                click.echo("1. Try a different API provider or model in your config.yaml", err=True)
                click.echo("2. Check if your API key has the correct permissions", err=True)
                click.echo("3. The provider's API might be experiencing issues. Try again later.", err=True)
                click.echo("4. Try running with the --simplified flag to truncate large diffs", err=True)
                click.echo("5. Try running with --force to extract message from error output", err=True)
            elif "rate" in error_str.lower() and "limit" in error_str.lower():
                click.echo("\nYou've hit a rate limit with the API provider.", err=True)
                click.echo("Please wait a while before trying again.", err=True)
            elif "authentication" in error_str.lower() or "api key" in error_str.lower():
                click.echo("\nAPI authentication error. Please check your API key in the .env file.", err=True)
                click.echo("1. Make sure your .env file contains a valid API key for your provider.", err=True)
                click.echo(f"2. The expected environment variable is {config['provider']['name'].upper()}_API_KEY", err=True)
                click.echo("3. Get a valid API key from your provider's website.", err=True)
            else:
                click.echo("An unexpected error occurred with the API. You may want to try:", err=True)
                click.echo("1. Using a different model in config.yaml", err=True)
                click.echo("2. Trying again with a smaller code diff", err=True)
                click.echo("3. Checking if your API service is functioning correctly", err=True)
                click.echo("4. Try running with --force to extract message from error output", err=True)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        click.echo("An unexpected error occurred. Please try again later.", err=True)

@cli.command()
@click.option('--title', '-t', help='Custom PR title')
@click.option('--body', '-b', help='Additional context for PR description')
def pr(title, body):
    """Generate a Pull Request title and description"""
    config = load_config()
    
    diff = get_git_diff()
    
    try:
        agent = get_agent(config)
        
        prompt = f"""
        Generate a Pull Request title and description based on the following template:
        
        Title format: {config['pr']['template']['title_format']}
        Required sections: {', '.join(config['pr']['template']['sections'])}
        
        Changes:
        {diff}
        
        Additional context:
        Title override: {title if title else 'None'}
        Body context: {body if body else 'None'}
        """
        
        try:
            response = agent.run(prompt)
            
            click.echo("\nGenerated Pull Request:")
            click.echo("-" * 40)
            click.echo(response)
            click.echo("-" * 40)
        except Exception as api_error:
            error_str = str(api_error)
            click.echo(f"API Error: {error_str}", err=True)
            
            # Handle JSON deserialization errors
            if "deserialize" in error_str.lower() or "json" in error_str.lower():
                click.echo("\nJSON deserialization error detected. This is likely due to an issue with the API response format.", err=True)
                click.echo("Possible solutions:", err=True)
                click.echo("1. Try a different API provider or model in your config.yaml", err=True)
                click.echo("2. Check if your API key has the correct permissions", err=True)
                click.echo("3. The provider's API might be experiencing issues. Try again later.", err=True)
            # Check for rate limits
            elif "rate" in error_str.lower() and "limit" in error_str.lower():
                click.echo("\nYou've hit a rate limit with the API provider.", err=True)
                click.echo("Please wait a while before trying again.", err=True)
            # Check for API key issues
            elif "authentication" in error_str.lower() or "api key" in error_str.lower():
                click.echo("\nAPI authentication error. Please check your API key in the .env file.", err=True)
                click.echo("1. Make sure your .env file contains a valid API key for your provider.", err=True)
                click.echo(f"2. The expected environment variable is {config['provider']['name'].upper()}_API_KEY", err=True)
                click.echo("3. Get a valid API key from your provider's website.", err=True)
            else:
                click.echo("An unexpected error occurred with the API. You may want to try:", err=True)
                click.echo("1. Using a different model in config.yaml", err=True)
                click.echo("2. Trying again with a smaller code diff", err=True)
                click.echo("3. Checking if your API service is functioning correctly", err=True)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        click.echo("An unexpected error occurred. Please try again later.", err=True)

if __name__ == "__main__":
    cli() 