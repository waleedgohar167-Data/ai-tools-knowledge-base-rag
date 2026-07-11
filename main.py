import os
from dotenv import load_dotenv
from openai import OpenAI
from search_service import search  # Importing the search function you built yesterday

# Load environment variables
load_dotenv()

# Initialize OpenAI Client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_prompt(user_query, search_results):
    """Constructs the context and the final prompt for the LLM."""
    context = ""
    for res in search_results:
        doc_name = res.payload.get('document_name', 'Unknown Document')
        text = res.payload.get('chunk_text', '')
        context += f"Document: {doc_name}\nContent: {text}\n\n"

    # Strict system instructions enforcing RAG
    system_prompt = (
        "You are a highly professional AI assistant. Answer the user's question strictly "
        "using the provided context. If the answer is not contained in the context, "
        "politely state that you do not have enough information to answer based on the knowledge base."
    )

    user_prompt = f"Context:\n{context}\nQuestion: {user_query}"
    
    return system_prompt, user_prompt

def generate_response(user_query, search_results):
    """Sends the constructed prompt to OpenAI for completion."""
    system_prompt, user_prompt = build_prompt(user_query, search_results)
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo", # You can change this to gpt-4o-mini if preferred
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3 # Low temperature for factual, grounded answers
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred while communicating with the AI: {e}"

def main():
    """Main CLI application loop."""
    print("====================================")
    print(" AI Tools Knowledge Base Assistant  ")
    print("====================================")
    print("Type 'exit' or 'quit' to close the application.\n")

    while True:
        try:
            # Phase 4: Handle invalid or empty user input gracefully
            user_input = input("\nAsk your question: ").strip()
            
            if not user_input:
                print("Please enter a valid question.")
                continue
                
            if user_input.lower() in ['exit', 'quit']:
                print("Shutting down the AI Assistant. Goodbye!")
                break

            # Phase 3, Step 2: Semantic Search
            print("\n🔍 Searching knowledge base...")
            results = search(user_input, limit=5)
            
            # Phase 4: Display a helpful message when no relevant documents are found
            if not results:
                print("No relevant documents found. Please try rephrasing your question.")
                continue

            # Phase 3, Step 3 & 4: Construct Prompt and Generate Response
            print("🧠 Generating response...")
            answer = generate_response(user_input, results)
            
            # Phase 4: Improve response formatting for readability
            print("\n" + "="*50)
            print("📝 AI RESPONSE:")
            print("="*50)
            print(answer)
            
            # Phase 3, Step 5: Display supporting sources
            print("\n" + "-"*50)
            print("📚 SUPPORTING SOURCES:")
            print("-"*50)
            for res in results:
                score = res.score
                doc_name = res.payload.get('document_name', 'Unknown')
                print(f"- {doc_name} (Relevance Score: {score:.3f})")
            print("="*50)

        # Phase 4: Exception handling
        except Exception as e:
            print(f"\n⚠️ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()