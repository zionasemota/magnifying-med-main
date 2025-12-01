# Azure OpenAI API Setup Guide

## Understanding the Issue

When you see the error `'>=' not supported between instances of 'NoneType' and 'float'`, it typically means:
1. The Azure API credentials aren't being loaded correctly, OR
2. The LLM is returning `None`/empty responses, which then causes scoring comparisons to fail

This guide will help you verify that all Azure API environment variables are set correctly.

## Your Azure API Information

Based on what you provided:
- **Endpoint**: `https://ziongraceproject2.openai.azure.com/`
- **API Key**: `FyGORcTSbfVCmXawImSsiMCB0AXj2Ti1QX7XPJwSrKHZvnX46RzlJQQJ99BJACHYHv6XJ3w3AAABACOGFV0I`
- **Deployment Name**: `gpt-4.1`
- **API Version**: `2024-02-15-preview`

## Problem with Your Current Approach

When you run this command:
```bash
export AZURE_OPENAI_ENDPOINT="..." && export AZURE_OPENAI_API_KEY="..." && ...
```

This only sets the variables **in the current shell session**. If you:
- Open a new terminal
- Run the Python script in a different way
- The variables might not be available

## How to Set Azure API Variables Correctly

### Option 1: Set for Current Session Only (Temporary)

Run each export separately:
```bash
export AZURE_OPENAI_ENDPOINT="https://ziongraceproject2.openai.azure.com/"
export AZURE_OPENAI_API_KEY="FyGORcTSbfVCmXawImSsiMCB0AXj2Ti1QX7XPJwSrKHZvnX46RzlJQQJ99BJACHYHv6XJ3w3AAABACOGFV0I"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4.1"
export AZURE_OPENAI_API_VERSION="2024-02-15-preview"
```

**Note**: These will only work in the terminal where you run them.

### Option 2: Add to Shell Profile (Permanent - Recommended)

Since you're using `zsh`, add these to your `~/.zshrc` file:

1. Open your `.zshrc` file:
   ```bash
   nano ~/.zshrc
   # or
   code ~/.zshrc
   ```

2. Add these lines at the end:
   ```bash
   # Azure OpenAI Configuration for MagnifyingMed
   export AZURE_OPENAI_ENDPOINT="https://ziongraceproject2.openai.azure.com/"
   export AZURE_OPENAI_API_KEY="FyGORcTSbfVCmXawImSsiMCB0AXj2Ti1QX7XPJwSrKHZvnX46RzlJQQJ99BJACHYHv6XJ3w3AAABACOGFV0I"
   export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4.1"
   export AZURE_OPENAI_API_VERSION="2024-02-15-preview"
   ```

3. Save and reload:
   ```bash
   source ~/.zshrc
   ```

## How to Verify Your API Configuration

### Step 1: Check if Variables are Set

Run this command to verify all variables are set:
```bash
echo "Endpoint: $AZURE_OPENAI_ENDPOINT"
echo "API Key: ${AZURE_OPENAI_API_KEY:0:20}..."  # Only show first 20 chars for security
echo "Deployment: $AZURE_OPENAI_DEPLOYMENT_NAME"
echo "API Version: $AZURE_OPENAI_API_VERSION"
```

Expected output:
```
Endpoint: https://ziongraceproject2.openai.azure.com/
API Key: FyGORcTSbfVCmXawImSi...
Deployment: gpt-4.1
API Version: 2024-02-15-preview
```

### Step 2: Test from Python

Create a test script `test_azure_config.py`:

```python
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
        print("⚠ Warning: Endpoint ends with '/', this is fine but might cause issues")
    
    # Test API version format
    if api_version:
        print(f"✓ API Version format looks correct: {api_version}")
else:
    print("\n✗ Missing required variables!")
    missing = []
    if not endpoint: missing.append("AZURE_OPENAI_ENDPOINT")
    if not api_key: missing.append("AZURE_OPENAI_API_KEY")
    if not deployment: missing.append("AZURE_OPENAI_DEPLOYMENT_NAME")
    if not api_version: missing.append("AZURE_OPENAI_API_VERSION")
    print(f"Missing: {', '.join(missing)}")
```

Run it:
```bash
python test_azure_config.py
```

### Step 3: Test Azure Connection

Create a simple connection test `test_azure_connection.py`:

```python
import os
from openai import OpenAI

# Get config from environment
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

if not all([endpoint, api_key, deployment, api_version]):
    print("ERROR: Missing required environment variables!")
    exit(1)

# Create client
base_url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}"

print(f"Testing Azure OpenAI connection...")
print(f"Endpoint: {endpoint}")
print(f"Deployment: {deployment}")
print(f"Base URL: {base_url}")
print()

try:
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        default_query={"api-version": api_version}
    )
    
    # Test with a simple prompt
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Connection successful!' if you can read this."}
        ],
        max_tokens=50
    )
    
    print("✓ Connection successful!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"✗ Connection failed: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Check that your API key is correct")
    print("2. Verify the endpoint URL is correct")
    print("3. Ensure the deployment name exists in Azure")
    print("4. Check your Azure subscription status")
```

Run it:
```bash
python test_azure_connection.py
```

## Common Issues and Solutions

### Issue 1: Variables Not Persisting

**Symptom**: Variables are set but disappear when you open a new terminal.

**Solution**: Use Option 2 (add to `.zshrc`) or Option 3 (setup script).

### Issue 2: Variables Not Available to Python

**Symptom**: Variables show up in `echo` but Python shows `None`.

**Solution**: 
- Make sure you're running Python from the same terminal where you set the variables
- If using an IDE, restart it after setting variables
- Check if Python is using a virtual environment that needs variables

### Issue 3: Endpoint URL Format

**Symptom**: Connection errors about malformed URLs.

**Solution**: 
- Endpoint should be: `https://ziongraceproject2.openai.azure.com/`
- With or without trailing `/` should work, but be consistent
- The code will construct: `{endpoint}/openai/deployments/{deployment}`

### Issue 4: API Version Mismatch

**Symptom**: Errors about unsupported API version.

**Solution**:
- Your version `2024-02-15-preview` should work
- If not, try: `2023-12-01-preview` or `2024-05-01-preview`
- Check Azure portal for supported versions

### Issue 5: Deployment Name Not Found

**Symptom**: Errors about model/deployment not found.

**Solution**:
- Verify the deployment name in Azure Portal
- It should match exactly (case-sensitive)
- Common names: `gpt-4`, `gpt-4-turbo`, `gpt-35-turbo`, etc.

## How the Application Loads Configuration

Looking at `config.py`, the application loads variables like this:

```python
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
```

If these are empty strings (`""`), the code will try to use standard OpenAI instead, which might cause the error you're seeing.

In `llm_client.py`, it checks:
```python
if azure_endpoint and azure_api_key:
    # Use Azure OpenAI
else:
    # Use standard OpenAI (which will fail if no OPENAI_API_KEY is set)
```

## Recommended Setup Process

1. **Add variables to `.zshrc`** (most permanent):
   ```bash
   nano ~/.zshrc
   # Add your export statements
   # Save and exit
   source ~/.zshrc
   ```

2. **Verify they're loaded**:
   ```bash
   python test_azure_config.py
   ```

3. **Test connection**:
   ```bash
   python test_azure_connection.py
   ```

4. **Run your application**:
   ```bash
   python -m magnifying_med
   # or
   ./run_with_azure.sh
   ```

## Quick Reference Checklist

Before running your application, verify:

- [ ] `AZURE_OPENAI_ENDPOINT` is set to your endpoint URL
- [ ] `AZURE_OPENAI_API_KEY` is set (and is the full key)
- [ ] `AZURE_OPENAI_DEPLOYMENT_NAME` matches your Azure deployment exactly
- [ ] `AZURE_OPENAI_API_VERSION` is set to a supported version
- [ ] Variables are available in the same terminal where you run Python
- [ ] Your Azure subscription is active and has quota
- [ ] The deployment exists and is accessible

## Next Steps After Setup

Once your Azure API is configured correctly, the error about `NoneType` and `float` should be resolved because:

1. The LLM calls will succeed and return proper data
2. The scoring system will receive valid data structures
3. Comparisons like `>=` will work with actual numbers instead of `None`

If you still see errors after verifying your setup, it might indicate:
- API rate limits
- Invalid responses from the LLM
- Network connectivity issues

In those cases, the error messages will be different and more specific about the actual problem.

