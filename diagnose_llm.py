#!/usr/bin/env python3
"""
Diagnostic script to identify which LLM configuration is being used
and help troubleshoot 404 errors.
"""

import os
from config import (
    OPENAI_API_KEY, OPENAI_MODEL,
    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME
)

def diagnose_llm_config():
    """Print diagnostic information about LLM configuration"""
    print("=" * 60)
    print("LLM Configuration Diagnostic")
    print("=" * 60)
    
    # Check Azure OpenAI configuration
    print("\n1. Azure OpenAI Configuration:")
    print(f"   AZURE_OPENAI_ENDPOINT: {AZURE_OPENAI_ENDPOINT if AZURE_OPENAI_ENDPOINT else 'NOT SET'}")
    print(f"   AZURE_OPENAI_API_KEY: {'SET' if AZURE_OPENAI_API_KEY else 'NOT SET'}")
    print(f"   AZURE_OPENAI_DEPLOYMENT_NAME: {AZURE_OPENAI_DEPLOYMENT_NAME if AZURE_OPENAI_DEPLOYMENT_NAME else 'NOT SET'}")
    print(f"   AZURE_OPENAI_API_VERSION: {AZURE_OPENAI_API_VERSION if AZURE_OPENAI_API_VERSION else 'NOT SET'}")
    
    # Check standard OpenAI configuration
    print("\n2. Standard OpenAI Configuration:")
    print(f"   OPENAI_API_KEY: {'SET' if OPENAI_API_KEY else 'NOT SET'}")
    print(f"   OPENAI_MODEL: {OPENAI_MODEL}")
    
    # Determine which will be used
    print("\n3. Active Configuration:")
    if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY:
        print("   ✓ Using: Azure OpenAI")
        deployment = AZURE_OPENAI_DEPLOYMENT_NAME or OPENAI_MODEL
        print(f"   Deployment Name: {deployment}")
        print(f"   Endpoint: {AZURE_OPENAI_ENDPOINT}")
        print(f"   API Version: {AZURE_OPENAI_API_VERSION}")
        print(f"\n   ⚠️  If you're getting a 404 error:")
        print(f"      - Verify the deployment '{deployment}' exists in your Azure OpenAI resource")
        print(f"      - Check that the endpoint URL is correct")
        print(f"      - Ensure the API version is correct")
    else:
        print("   ✓ Using: Standard OpenAI")
        print(f"   Model: {OPENAI_MODEL}")
        print(f"\n   ⚠️  If you're getting a 404 error:")
        print(f"      - Verify the model '{OPENAI_MODEL}' exists and is available")
        print(f"      - Check that your API key has access to this model")
        print(f"      - Some models may require a specific OpenAI plan")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    diagnose_llm_config()

