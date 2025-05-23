import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Content Strategist application"""
    
    # Google AI API Key
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # App Configuration
    APP_TITLE = "AI Content Strategist"
    APP_ICON = "🚀"
    
    # Model Configuration
    MODEL_NAME = "gemini-2.0-flash-lite"
    TEMPERATURE = 0.7
    MAX_OUTPUT_TOKENS = 2048
    
    # UI Configuration
    THEME_COLOR = "#FF6B6B"
    SECONDARY_COLOR = "#4ECDC4"
    BACKGROUND_COLOR = "#F8F9FA"
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        return True