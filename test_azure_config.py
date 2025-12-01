#!/usr/bin/env python3
"""
Test script to verify Azure OpenAI configuration
Run this to check if all required environment variables are set correctly.
"""

import os

print("Checking Azure OpenAI Configuration...")
print("=" * 50)

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

print(f"AZURE_OPENAI_ENDPOINT: {endpoint or 'NOT SET'}")
print(f"AZURE_OPENAI_API_KEY: {'SET' if api_key else 'NOT SET'} ({len(api_key) if api_key else 0} chars)")
print(f"AZURE_OPENAI_DEPLOYMENT_NAME: {deployment or 'NOT SET'}")
print(f"AZURE_OPENAI_API_VERSION: {api_version or 'NOT SET'}")

if all([endpoint, api_key, deployment, api_version]):
    print("\n✓ All Azure OpenAI variables are set!")
    
    # Test endpoint format
    if endpoint.endswith('/'):
        print("✓ Endpoint ends with '/', this is fine")
    
    if not endpoint.startswith('http'):
        print("⚠ Warning: Endpoint should start with 'https://'")
    
    # Test API version format
    if api_version:
        print(f"✓ API Version format looks correct: {api_version}")
    
    # Check deployment name
    if deployment:
        print(f"✓ Deployment name: {deployment}")
    
    print("\n" + "=" * 50)
    print("Configuration looks good! Try running test_azure_connection.py next.")
else:
    print("\n✗ Missing required variables!")
    missing = []
    if not endpoint: missing.append("AZURE_OPENAI_ENDPOINT")
    if not api_key: missing.append("AZURE_OPENAI_API_KEY")
    if not deployment: missing.append("AZURE_OPENAI_DEPLOYMENT_NAME")
    if not api_version: missing.append("AZURE_OPENAI_API_VERSION")
    print(f"Missing: {', '.join(missing)}")
    print("\nTo set them, run:")
    print("  export AZURE_OPENAI_ENDPOINT='your-endpoint'")
    print("  export AZURE_OPENAI_API_KEY='your-key'")
    print("  export AZURE_OPENAI_DEPLOYMENT_NAME='your-deployment'")
    print("  export AZURE_OPENAI_API_VERSION='your-version'")
    print("\nOr add them to your ~/.zshrc file for permanent setup.")

