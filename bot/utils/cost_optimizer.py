import re
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import json
import asyncio

logger = logging.getLogger(__name__)

class CostOptimizer:
    def __init__(self):
        self.simple_responses = {
            # 挨拶系
            r'こんにち[はわ]|おはよう|hello|hi': [
                "こんにちは！何かお手伝いできることはありますか？",
                "こんにちは！今日も一日頑張りましょう！",
                "こんにちは！AIアシスタントです。お気軽にお声かけください。"
            ],
            r'さようなら|またね|bye|goodbye': [
                "さようなら！また何かあればお声かけください。",
                "またお会いしましょう！",
                "お疲れさまでした！"
            ],
            r'ありがとう|thank you|thanks': [
                "どういたしまして！",
                "お役に立てて嬉しいです！",
                "いつでもお手伝いします！"
            ],
            r'おやすみ|good night': [
                "おやすみなさい！良い夢を。",
                "ゆっくり休んでくださいね。",
                "おやすみなさい！"
            ],
            # 簡単な質問
            r'元気\?|調子はどう\?|how are you': [
                "元気です！ありがとうございます。",
                "絶好調です！今日も頑張ります。",
                "とても元気です！何かお手伝いできることはありますか？"
            ],
            r'名前は\?|who are you|あなたは誰': [
                "私はAIアシスタントです！",
                "Gemini AIを使ったDiscord Botです。",
                "AIアシスタントとしてお手伝いします！"
            ]
        }
        
        self.api_usage = {
            'daily_requests': 0,
            'daily_tokens': 0,
            'last_reset': datetime.now().date(),
            'quota_limit': 1500,  # Gemini Flash daily free limit
            'token_limit': 1000000  # Daily token limit
        }
        
        self.conversation_summaries = {}  # user_id -> summary
        self.summary_threshold = 10  # Summarize after 10 messages
    
    def check_simple_response(self, message: str) -> Optional[str]:
        """Check if message can be handled with simple response"""
        message_lower = message.lower().strip()
        
        # Skip if message is too long (likely complex)
        if len(message) > 100:
            return None
        
        for pattern, responses in self.simple_responses.items():
            if re.search(pattern, message_lower):
                import random
                return random.choice(responses)
        
        return None
    
    def should_use_ai(self, message: str, user_id: int) -> bool:
        """Determine if AI should be used for this message"""
        # Check daily limits
        if not self.check_daily_limits():
            return False
        
        # Check if simple response is available
        if self.check_simple_response(message):
            return False
        
        # Always use AI for complex queries
        complex_keywords = [
            'explain', 'how to', 'what is', 'why', 'when', 'where',
            'code', 'program', 'music', 'recommend', 'help me',
            '説明', 'どうやって', 'なぜ', 'いつ', 'どこで', 'コード',
            'プログラム', '音楽', '推薦', '手伝って'
        ]
        
        message_lower = message.lower()
        if any(keyword in message_lower for keyword in complex_keywords):
            return True
        
        # Use AI for longer messages
        if len(message) > 50:
            return True
        
        return False
    
    def check_daily_limits(self) -> bool:
        """Check if daily API limits are exceeded"""
        today = datetime.now().date()
        
        # Reset counters if new day
        if self.api_usage['last_reset'] != today:
            self.api_usage['daily_requests'] = 0
            self.api_usage['daily_tokens'] = 0
            self.api_usage['last_reset'] = today
        
        # Check limits
        if self.api_usage['daily_requests'] >= self.api_usage['quota_limit']:
            logger.warning("Daily API request limit exceeded")
            return False
        
        if self.api_usage['daily_tokens'] >= self.api_usage['token_limit']:
            logger.warning("Daily token limit exceeded")
            return False
        
        return True
    
    def record_api_usage(self, tokens_used: int):
        """Record API usage"""
        self.api_usage['daily_requests'] += 1
        self.api_usage['daily_tokens'] += tokens_used
    
    def get_optimized_model(self, query_type: str) -> str:
        """Get optimal model based on query complexity"""
        complex_tasks = [
            'music_analysis', 'code_generation', 'creative_writing',
            'complex_reasoning', 'translation'
        ]
        
        if query_type in complex_tasks:
            return 'gemini-pro'  # Use full model for complex tasks
        else:
            return 'gemini-1.5-flash'  # Use flash model for simple tasks
    
    def should_summarize_conversation(self, user_id: int, message_count: int) -> bool:
        """Check if conversation should be summarized"""
        return message_count >= self.summary_threshold
    
    async def create_conversation_summary(self, messages: List[Dict], gemini_client) -> str:
        """Create conversation summary to reduce token usage"""
        try:
            # Prepare messages for summarization
            conversation_text = "\n".join([
                f"User: {msg['user_message']}\nAI: {msg['ai_response']}"
                for msg in messages[-self.summary_threshold:]
            ])
            
            summary_prompt = f"""
            以下の会話を簡潔に要約してください。重要なポイントと文脈を保持しながら、
            トークン数を削減してください。

            会話:
            {conversation_text}

            要約（200文字以内）:
            """
            
            summary = await gemini_client.generate_response(
                summary_prompt,
                mode='assistant',
                model='gemini-1.5-flash'  # Use flash for summarization
            )
            
            return summary if summary else "会話の要約を作成できませんでした。"
            
        except Exception as e:
            logger.error(f"Error creating conversation summary: {e}")
            return "会話の要約を作成できませんでした。"
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        today = datetime.now().date()
        
        # Reset if new day
        if self.api_usage['last_reset'] != today:
            self.api_usage['daily_requests'] = 0
            self.api_usage['daily_tokens'] = 0
            self.api_usage['last_reset'] = today
        
        return {
            'daily_requests': self.api_usage['daily_requests'],
            'daily_tokens': self.api_usage['daily_tokens'],
            'request_limit': self.api_usage['quota_limit'],
            'token_limit': self.api_usage['token_limit'],
            'requests_remaining': max(0, self.api_usage['quota_limit'] - self.api_usage['daily_requests']),
            'tokens_remaining': max(0, self.api_usage['token_limit'] - self.api_usage['daily_tokens']),
            'usage_percentage': {
                'requests': (self.api_usage['daily_requests'] / self.api_usage['quota_limit']) * 100,
                'tokens': (self.api_usage['daily_tokens'] / self.api_usage['token_limit']) * 100
            }
        }
    
    def is_quota_warning_threshold(self) -> bool:
        """Check if approaching quota limits (80%)"""
        stats = self.get_usage_stats()
        return (stats['usage_percentage']['requests'] >= 80 or 
                stats['usage_percentage']['tokens'] >= 80)
    
    def is_quota_exceeded(self) -> bool:
        """Check if quota is exceeded"""
        return not self.check_daily_limits()

# Global instance
cost_optimizer = CostOptimizer()