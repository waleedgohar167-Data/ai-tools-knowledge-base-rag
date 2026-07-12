# main.py
import sys
from services.search_service import search
from services.llm_service import generate_response
from services.analytics_service import record_transaction
from services.feedback_service import save_feedback
from app_logging.logger import get_logger

# Instantiate the globally centralized application logger
logger = get_logger("Main_Application")

def main():
    """Main CLI application loop with comprehensive enterprise monitoring."""
    # Log absolute application startup sequences across production files
    logger.info("==================================================")
    logger.info("Enterprise AI Knowledge Base Application Started.")
    logger.info("==================================================")
    
    print("=====================================================")
    print(" 🚀 Enterprise AI Tools Knowledge Base Assistant ")
    print("=====================================================")
    print("Type 'exit' or 'quit' to close the application.\n")

    while True:
        try:
            # Handle incoming user interaction securely
            user_input = input("\nAsk your question: ").strip()
            
            if not user_input:
                # Log formal WARNING level metadata when empty criteria are submitted
                logger.warning("User submitted an empty question string slot.")
                print("⚠️ Please enter a valid question.")
                continue
                
            if user_input.lower() in ['exit', 'quit']:
                # Log clean application shutdown states
                logger.info("User initiated application shutdown sequence.")
                print("Shutting down the AI Assistant. Goodbye!")
                break

            # Log every valid operational user query processed by the engine
            logger.info(f"New User Request received: '{user_input}'")

            print("\n🔍 Searching vector database...")
            # Unpack both the dense vector matches and the precise retrieval latency delta
            results, retrieval_time = search(user_input, limit=5)
            
            if not results:
                # Log formal WARNING level events when search returns empty states
                logger.warning(f"Vector search returned zero results for query: '{user_input}'")
                print("⚠️ No relevant documents found. Please try rephrasing your question.")
                record_transaction(success=False, retrieval_time=retrieval_time)
                continue

            print("🧠 Generating grounded response...")
            # Unpack response text, generation runtime metrics, and final token distributions
            answer, gen_time, tokens = generate_response(user_input, results)
            
            # Display beautifully formatted markdown layouts to the end user
            print("\n" + "="*50)
            print("📝 AI RESPONSE")
            print("="*50)
            print(answer)
            
            print("\n" + "-"*50)
            print("📚 SUPPORTING SOURCES")
            print("-"*50)
            
            citations = []
            for res in results:
                payload = getattr(res, 'payload', {}) or {}
                doc_name = payload.get('tool', payload.get('document_name', 'Unknown'))
                citations.append(f"- {doc_name} (Confidence Score: {res.score:.3f})")
            
            # Output clean source validation listings
            for citation in citations:
                print(citation)
            print("="*50)

            # --- PHASE 3: USER FEEDBACK SYSTEM ---
            print("\n" + "-"*50)
            feedback_input = input("Was this answer helpful? (y/n): ").strip().lower()
            is_helpful = feedback_input == 'y'
            comment = input("Optional comments (press Enter to skip): ").strip()
            
            save_feedback(user_input, answer, is_helpful, comment)
            print("✅ Thank you! Your feedback has been securely recorded.")
            print("-" * 50)
            # -------------------------------------

            # Record successfully compiled execution performance metrics to the analytics layer
            record_transaction(success=True, retrieval_time=retrieval_time, generation_time=gen_time, tokens=tokens)
            logger.info("Transaction successfully processed and application analytics updated.")

        except KeyboardInterrupt:
            logger.info("User interrupted application execution loop via KeyboardInterrupt.")
            print("\nShutting down the AI Assistant. Goodbye!")
            break
        except Exception as e:
            # Record critical system vulnerabilities with comprehensive trace metrics
            logger.critical(f"Critical application error encountered: {str(e)}", exc_info=True)
            record_transaction(success=False)
            print("\n⚠️ An unexpected error occurred. Please check the system logs.")

    # Log absolute application termination metrics
    logger.info("==================================================")
    logger.info("Enterprise AI Knowledge Base Application Shutdown.")
    logger.info("==================================================")

if __name__ == "__main__":
    main()