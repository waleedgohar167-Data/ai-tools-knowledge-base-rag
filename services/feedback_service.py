# services/feedback_service.py
import os
import csv
from datetime import datetime
from config.settings import FEEDBACK_FILE
from app_logging.logger import get_logger

logger = get_logger("Feedback_Service")

def save_feedback(query: str, answer: str, is_helpful: bool, comment: str):
    """Saves user feedback into a dedicated CSV database."""
    file_exists = os.path.isfile(FEEDBACK_FILE)
    try:
        with open(FEEDBACK_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write the header if the file is brand new
            if not file_exists:
                writer.writerow(["Timestamp", "Rating", "Comments", "Original Question", "Generated Answer"])
            
            rating = "Helpful" if is_helpful else "Not Helpful"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            writer.writerow([timestamp, rating, comment, query, answer])
        logger.info("User feedback successfully logged to CSV database.")
    except Exception as e:
        logger.error(f"Failed to save user feedback: {e}", exc_info=True)