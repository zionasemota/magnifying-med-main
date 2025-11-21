"""
Main CLI interface for MagnifyingMed
"""

import sys
import os
from .conversation_handler import ConversationHandler


def main():
    """Main entry point for the CLI"""
    print("=" * 60)
    print("MagnifyingMed - Racial Bias Analysis for Medical AI Research")
    print("=" * 60)
    print()
    
    # Check for API key (either OpenAI or Azure OpenAI)
    has_openai_key = os.getenv("OPENAI_API_KEY")
    has_azure_key = os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_ENDPOINT")
    
    if not has_openai_key and not has_azure_key:
        print("Warning: No API credentials found.")
        print("Please set either:")
        print("  - OPENAI_API_KEY for standard OpenAI, or")
        print("  - AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY for Azure OpenAI")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Initialize handler
    try:
        handler = ConversationHandler()
    except Exception as e:
        print(f"Error initializing handler: {str(e)}")
        return
    
    # Show greeting
    print(handler.get_greeting())
    print()
    
    # Main conversation loop
    print("Type 'quit' or 'exit' to end the conversation.")
    print("Type 'reset' to start a new conversation.")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nThank you for using MagnifyingMed. Goodbye!")
                break
            
            if user_input.lower() == 'reset':
                handler.reset()
                print("\nConversation reset. Starting fresh...\n")
                continue
            
            # Get response
            response = handler.handle_message(user_input)
            print(f"\nMagnifyingMed: {response}\n")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")


if __name__ == "__main__":
    main()

