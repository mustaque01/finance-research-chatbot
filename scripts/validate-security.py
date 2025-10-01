#!/usr/bin/env python3
"""
Security validation script for API key configurations
This script ensures all API keys are properly configured and secured
"""

import os
import re
from pathlib import Path

def check_api_keys():
    """Check that all API keys are properly configured"""
    
    # Define expected API keys with their patterns
    api_patterns = {
        'OPENAI_API_KEY': r'^sk-proj-[A-Za-z0-9_-]{120,}$',
        'TAVILY_API_KEY': r'^tvly-[A-Za-z0-9_-]+$',
        'ALPHA_VANTAGE_API_KEY': r'^[A-Z0-9]{16}$',
        'PINECONE_API_KEY': r'^pcsk_[A-Za-z0-9_-]+$'
    }
    
    # Check each service's .env file
    services = ['agents', 'backend', '.']
    
    for service in services:
        env_path = Path(service) / '.env'
        if env_path.exists():
            print(f"\n🔍 Checking {env_path}...")
            
            with open(env_path, 'r') as f:
                content = f.read()
                
            for key, pattern in api_patterns.items():
                # Extract the value for this API key
                match = re.search(f'{key}=(.+)', content)
                if match:
                    value = match.group(1).strip()
                    
                    # Skip placeholder values
                    if value in ['demo-key-replace-with-real-key', 'your_openai_api_key_here', 
                                'your_tavily_api_key_here', 'your_alpha_vantage_key_here',
                                'your_pinecone_api_key_here']:
                        print(f"   ⚠️  {key}: Using placeholder value")
                        continue
                    
                    # Validate the API key format
                    if re.match(pattern, value):
                        print(f"   ✅ {key}: Valid format")
                    else:
                        print(f"   ❌ {key}: Invalid format or missing")
                else:
                    print(f"   ❌ {key}: Not found")
        else:
            print(f"   ❌ {env_path}: File not found")

def check_gitignore():
    """Ensure .env files are properly ignored by git"""
    
    print(f"\n🔒 Checking .gitignore security...")
    
    services = ['agents', 'backend', 'frontend', '.']
    
    for service in services:
        gitignore_path = Path(service) / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                content = f.read()
                
            if '.env' in content:
                print(f"   ✅ {gitignore_path}: .env files properly ignored")
            else:
                print(f"   ❌ {gitignore_path}: .env files NOT ignored")
        else:
            print(f"   ⚠️  {gitignore_path}: .gitignore not found")

def main():
    """Main security validation"""
    print("🛡️  API Key Security Validation")
    print("=" * 50)
    
    check_api_keys()
    check_gitignore()
    
    print("\n✅ Security validation complete!")
    print("\nIMPORTANT REMINDERS:")
    print("- Never commit .env files to version control")
    print("- Keep API keys secure and rotate them regularly")
    print("- Use different keys for development and production")
    print("- Monitor API usage for unusual activity")

if __name__ == "__main__":
    main()