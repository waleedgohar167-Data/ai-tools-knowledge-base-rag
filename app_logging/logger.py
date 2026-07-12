# app_logging/logger.py
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# 1. Create the dedicated logs/ directory if it doesn't exist
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers if logger is called multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
        )
        
        # 2. Console Handler (for your terminal)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # 3. Daily Rotating File Handler (generates a new file automatically at midnight)
        log_filename = os.path.join(LOG_DIR, "enterprise_rag.log")
        file_handler = TimedRotatingFileHandler(
            log_filename, 
            when="midnight", 
            interval=1, 
            backupCount=30, # Keep logs for 30 days
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
    return logger