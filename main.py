import sys
from services.search_service import search
from services.llm_service import generate_response
from app_logging.logger import get_logger

logger = get_logger("Main_Application")

def main():
    """Main CLI application loop."""
    print("=====================================================")
    print(" 🚀 Enterprise AI Tools Knowledge Base Assistant ")
    print("=====================================================")
    print("Type 'exit' or 'quit' to close the application.\n")

    while True:
        try:
            # Handle user input gracefully
            user_input = input("\nAsk your question: ").strip()
            
            if not user_input:
                print("⚠️ Please enter a valid question.")
                continue
                
            if user_input.lower() in ['exit', 'quit']:
                print("Shutting down the AI Assistant. Goodbye!")
                sys.exit(0)

            # Route to Search Service
            print("\n🔍 Searching vector database...")
            results = search(user_input, limit=5)
            
            if not results:
                print("⚠️ No relevant documents found. Please try rephrasing your question.")
                continue

            # Route to LLM Service
            print("🧠 Generating grounded response...")
            answer = generate_response(user_input, results)
            
            # Display perfectly formatted output
            print("\n" + "="*50)
            print("📝 AI RESPONSE")
            print("="*50)
            print(answer)
            
            print("\n" + "-"*50)
            print("📚 SUPPORTING SOURCES")
            print("-"*50)
            for res in results:
                doc_name = res.payload.get('document_name', 'Unknown')
                print(f"- {doc_name} (Confidence Score: {res.score:.3f})")
            print("="*50)

        except KeyboardInterrupt:
            print("\nShutting down the AI Assistant. Goodbye!")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Application error: {str(e)}", exc_info=True)
            print("\n⚠️ An unexpected error occurred. Please check the system logs.")

if __name__ == "__main__":
    main()