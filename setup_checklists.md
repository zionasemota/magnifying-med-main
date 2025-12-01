# MagnifyingMed Setup Checklist

## Required Setup

### ✅ 1. Python Environment
- **Python Version**: Python 3.8+ (you have Python 3.12.7 ✓)
- **Virtual Environment**: Recommended but not required

### ✅ 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `openai>=1.0.0` - For LLM API calls
- `requests>=2.31.0` - For research paper APIs (PubMed, OpenAlex, arXiv)
- `matplotlib>=3.7.0` - For visualizations
- `numpy>=1.24.0` - For data processing

### ✅ 3. Set OpenAI API Key (REQUIRED)
This is the **only required configuration** for basic usage.

**Quick setup:**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

**Permanent setup:**
```bash
./setup_api_key.sh
```

Get your API key from: https://platform.openai.com/api-keys

## Optional Configuration

### Optional: Change Default Model
If you want to use a different OpenAI model:
```bash
export OPENAI_MODEL='gpt-4-turbo'  # or any other model name
```

### Optional: Use Azure OpenAI Instead
If you prefer Azure OpenAI, set these instead:
```bash
export AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'
export AZURE_OPENAI_API_KEY='your-azure-key'
export AZURE_OPENAI_DEPLOYMENT_NAME='your-deployment-name'
export AZURE_OPENAI_API_VERSION='2024-02-15-preview'
```

## No Additional Setup Needed

The following work automatically without any configuration:
- ✅ **Research Paper APIs**: PubMed, OpenAlex, and arXiv are public APIs (no keys needed)
- ✅ **Visualization**: Works out of the box with matplotlib
- ✅ **Scoring & Analysis**: All logic is built-in

## Verify Your Setup

Run the diagnostic script:
```bash
python diagnose_llm.py
```

This will show:
- Which LLM provider you're using
- Which model/deployment is configured
- Any missing configuration

## Quick Test

After setup, test the application:
```bash
python -m magnifying_med
```

Or:
```bash
python main.py
```

## Summary

**Minimum Required:**
1. ✅ Python 3.8+ installed
2. ✅ Dependencies installed (`pip install -r requirements.txt`)
3. ✅ OpenAI API key set (`export OPENAI_API_KEY='...'`)

That's it! Everything else is optional.

