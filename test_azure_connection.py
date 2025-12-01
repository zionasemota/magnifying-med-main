#!/usr/bin/env python3
"""
Test script to verify Azure OpenAI connection
This will actually try to connect to Azure and make a test API call.
"""

import os
from openai import OpenAI

# Get config from environment
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

print("Testing Azure OpenAI Connection...")
print("=" * 50)

if not all([endpoint, api_key, deployment, api_version]):
    print("ERROR: Missing required environment variables!")
    missing = []
    if not endpoint: missing.append("AZURE_OPENAI_ENDPOINT")
    if not api_key: missing.append("AZURE_OPENAI_API_KEY")
    if not deployment: missing.append("AZURE_OPENAI_DEPLOYMENT_NAME")
    if not api_version: missing.append("AZURE_OPENAI_API_VERSION")
    print(f"Missing: {', '.join(missing)}")
    print("\nPlease set them first, then run this script again.")
    exit(1)

# Create client
base_url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}"

print(f"Endpoint: {endpoint}")
print(f"Deployment: {deployment}")
print(f"API Version: {api_version}")
print(f"Base URL: {base_url}")
print()

try:
    print("Creating OpenAI client...")
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        default_query={"api-version": api_version}
    )
    
    print("Sending test message to Azure OpenAI...")
    print("-" * 50)
    
    # Test with a simple prompt
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Connection successful!' if you can read this."}
        ],
        max_tokens=50
    )
    
    print("-" * 50)
    print("✓ Connection successful!")
    print(f"Response: {response.choices[0].message.content}")
    print("\n" + "=" * 50)
    print("Your Azure OpenAI configuration is working correctly!")
    print("You can now run the main application.")
    
except Exception as e:
    print("-" * 50)
    print(f"✗ Connection failed!")
    print(f"Error: {str(e)}")
    print("\n" + "=" * 50)
    print("Troubleshooting:")
    print("1. Check that your API key is correct and active")
    print("2. Verify the endpoint URL is correct")
    print("3. Ensure the deployment name exists in Azure Portal")
    print("4. Check your Azure subscription status and quota")
    print("5. Verify the API version is supported by your deployment")
    print("6. Check network connectivity to Azure")
    exit(1)

