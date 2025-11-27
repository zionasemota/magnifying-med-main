#!/bin/bash
# Quick script to run MagnifyingMed with Azure OpenAI
# Make sure to set your Azure credentials as environment variables first

# Navigate to project directory
cd "$(dirname "$0")"

# Check if Azure credentials are set
if [ -z "$AZURE_OPENAI_ENDPOINT" ] || [ -z "$AZURE_OPENAI_API_KEY" ]; then
    echo "Error: Azure OpenAI credentials not set!"
    echo ""
    echo "Please set these environment variables first:"
    echo "  export AZURE_OPENAI_ENDPOINT='your-endpoint'"
    echo "  export AZURE_OPENAI_API_KEY='your-key'"
    echo "  export AZURE_OPENAI_DEPLOYMENT_NAME='your-deployment'"
    echo "  export AZURE_OPENAI_API_VERSION='2024-02-15-preview'"
    exit 1
fi

# Set default API version if not set
if [ -z "$AZURE_OPENAI_API_VERSION" ]; then
    export AZURE_OPENAI_API_VERSION='2024-02-15-preview'
    echo "Using default API version: $AZURE_OPENAI_API_VERSION"
fi

# Run the application
echo "Starting MagnifyingMed with Azure OpenAI..."
echo "Endpoint: $AZURE_OPENAI_ENDPOINT"
echo "Deployment: ${AZURE_OPENAI_DEPLOYMENT_NAME:-gpt-4.1}"
echo ""

python -m magnifying_med

