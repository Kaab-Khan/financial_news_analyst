import logging

# Create a custom logger
logger = logging.getLogger("financial_news_analyst")
logger.setLevel(logging.DEBUG)  # Set the level for your application

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

# Suppress logs from other libraries
logging.getLogger("watchdog").setLevel(logging.WARNING)
logging.getLogger("streamlit").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)