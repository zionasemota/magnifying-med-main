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

2. **Navigate to the project directory:**
```bash
cd /Users/graceajibola/magnifying-med-main
```

3. **Run the application:**
```bash
python main.py
```

### Option 2: Using the Helper Script

1. **Set your Azure OpenAI credentials** (same as above)

2. **Run the script:**
```bash
./run_with_azure.sh
```

### Option 3: All in One Command

```bash
cd /Users/graceajibola/magnifying-med-main && \
export AZURE_OPENAI_ENDPOINT='https://ziongraceproject2.openai.azure.com/' && \
export AZURE_OPENAI_API_KEY='FyGORcTSbfVCmXawImSsiMCB0AXj2Ti1QX7XPJwSrKHZvnX46RzlJQQJ99BJACHYHv6XJ3w3AAABACOGFV0I' && \
export AZURE_OPENAI_DEPLOYMENT_NAME='gpt-4.1' && \
export AZURE_OPENAI_API_VERSION='2024-02-15-preview' && \
python main.py
```

## Make Credentials Permanent

To avoid setting these every time, add them to your `~/.zshrc`:

```bash
echo 'export AZURE_OPENAI_ENDPOINT="https://ziongraceproject2.openai.azure.com/"' >> ~/.zshrc
echo 'export AZURE_OPENAI_API_KEY="FyGORcTSbfVCmXawImSsiMCB0AXj2Ti1QX7XPJwSrKHZvnX46RzlJQQJ99BJACHYHv6XJ3w3AAABACOGFV0I"' >> ~/.zshrc
echo 'export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4.1"' >> ~/.zshrc
echo 'export AZURE_OPENAI_API_VERSION="2024-02-15-preview"' >> ~/.zshrc
source ~/.zshrc
```

## Verify Configuration

Check your setup:
```bash
python diagnose_llm.py
```

