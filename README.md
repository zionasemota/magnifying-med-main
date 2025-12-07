# Quick Start Guide

## Running MagnifyingMed

### Option 1: Direct Run (Recommended)

1. **Set your Azure OpenAI credentials:**
```bash
export AZURE_OPENAI_ENDPOINT='https://ziongraceproject2.openai.azure.com/'
export AZURE_OPENAI_API_KEY='FyGORcTSbfVCmXawImSsiMCB0AXj2Ti1QX7XPJwSrKHZvnX46RzlJQQJ99BJACHYHv6XJ3w3AAABACOGFV0I'
export AZURE_OPENAI_DEPLOYMENT_NAME='gpt-4.1'
export AZURE_OPENAI_API_VERSION='2024-02-15-preview'
```

3. **Run the application:**
```bash
python -m magnifying-med-main 
```

## Verify Configuration

Check your setup:
```bash
python diagnose_llm.py