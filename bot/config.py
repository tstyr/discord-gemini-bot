"""Bot設定ファイル"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Bot設定クラス"""
    
    # Discord設定
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    
    # Gemini API設定
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # データベース設定
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")
    
    # API設定
    API_HOST = os.getenv("API_HOST", "localhost")
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_SECRET_KEY = os.getenv("API_SECRET_KEY", "your-secret-key-here")
    
    # ログ設定
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """必須設定の検証"""
        required_vars = ["DISCORD_TOKEN", "GEMINI_API_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True