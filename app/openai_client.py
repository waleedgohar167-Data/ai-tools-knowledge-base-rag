import os
import sys
import logging
from typing import Optional
from openai import OpenAI, AuthenticationError, APIConnectionError, RateLimitError
from dotenv import load_dotenv

# Configure enterprise-grade logging for production monitoring
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("OpenAI_Client_Service")

class OpenAIIntegration:
    """
    Enterprise-grade client manager for OpenAI API integration.
    Handles secure authentication, connection pooling, and structured error handling.
    """
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initializes the OpenAI client with secure environment variable loading.
        """
        load_dotenv()
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self._api_key:
            logger.critical("OPENAI_API_KEY is missing from environment variables.")
            raise ValueError("System configuration error: OPENAI_API_KEY must be provided in the .env file.")
            
        # Initialize the reusable client
        self.client = OpenAI(api_key=self._api_key)

    def test_connection(self) -> bool:
        """
        Validates API connectivity and authentication using the highly cost-efficient gpt-5.4-mini model.
        Returns True if successful, False otherwise.
        """
        logger.info("Initiating OpenAI API connection test using gpt-5.4-mini...")
        try:
            response = self.client.chat.completions.create(
                model="gpt-5.4-mini", 
                messages=[
                    {"role": "system", "content": "You are a backend diagnostic service for a RAG pipeline."},
                    {"role": "user", "content": "Acknowledge connection successfully established."}
                ],
                max_completion_tokens=20, # <-- Updated parameter for newer models
                temperature=0.0 # Deterministic output for testing
            )
            
            output = response.choices[0].message.content.strip()
            logger.info(f"SUCCESS! API Connection Verified. Response: {output}")
            return True
            
        except AuthenticationError as auth_err:
            logger.error(f"Authentication failed. Please verify your API key: {auth_err}")
        except RateLimitError as rate_err:
            logger.warning(f"Rate limit exceeded. Check OpenAI account billing and limits: {rate_err}")
        except APIConnectionError as conn_err:
            logger.error(f"Network connectivity issue reaching OpenAI servers: {conn_err}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during API validation: {str(e)}", exc_info=True)
            
        return False

if __name__ == "__main__":
    # Instantiate the service and execute the connection test
    openai_service = OpenAIIntegration()
    success = openai_service.test_connection()
    
    # Exit with standard OS status codes (0 for success, 1 for failure)
    if not success:
        sys.exit(1)