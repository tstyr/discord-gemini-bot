import os
import logging
from typing import List, Dict, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=api_key)
        
        # Initialize model - use gemini-2.0-flash (latest free model)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # AI mode configurations
        # Note: Music playback requests are handled by main.py before reaching Gemini
        self.modes = {
            'standard': {
                'system_instruction': """あなたは親切なAIアシスタントです。明確で正確、フレンドリーな応答を提供してください。日本語で応答してください。

重要: ユーザーが「曲流して」「音楽かけて」「〇〇聞きたい」など音楽再生をリクエストした場合は、説明せずに「🎵 音楽を再生しますね！」と短く応答してください。音楽の再生方法の説明は不要です。""",
                'temperature': 0.7,
            },
            'creative': {
                'system_instruction': """あなたは創造的なAIアシスタントです。想像力豊かで芸術的、型にはまらない発想をしながらも役立つ応答をしてください。日本語で応答してください。

重要: ユーザーが音楽再生をリクエストした場合は、説明せずに「🎵 音楽を再生しますね！」と短く応答してください。""",
                'temperature': 0.9,
            },
            'coder': {
                'system_instruction': "あなたはプログラミングの専門家です。正確で、よくドキュメント化されたコードソリューションと説明を提供してください。ベストプラクティスとクリーンなコードに焦点を当ててください。",
                'temperature': 0.3,
            },
            'assistant': {
                'system_instruction': """あなたはプロフェッショナルなアシスタントです。フォーマルで正確、生産性と整理整頓に焦点を当ててください。日本語で応答してください。

重要: ユーザーが音楽再生をリクエストした場合は、説明せずに「🎵 音楽を再生しますね！」と短く応答してください。""",
                'temperature': 0.5,
            },
            'music_dj': {
                'system_instruction': """あなたは音楽に詳しいDJ AIです。音楽ジャンル、アーティスト、録音品質について深い知識を持っています。ユーザーの気分に合った曲を推薦してください。日本語で応答してください。

重要: ユーザーが「曲流して」「音楽かけて」など音楽再生をリクエストした場合は、長い説明をせずに「🎵 いい曲見つけました！再生しますね！」と短く応答してください。""",
                'temperature': 0.8,
            }
        }
        
        # Simple responses for cost optimization
        self.simple_responses = {
            'こんにちは': 'こんにちは！何かお手伝いできることはありますか？',
            'hello': 'こんにちは！何かお手伝いできることはありますか？',
            'hi': 'こんにちは！何かお手伝いできることはありますか？',
            'おはよう': 'おはようございます！今日も一日頑張りましょう！',
            'ありがとう': 'どういたしまして！他に何かあればお気軽にどうぞ。',
            'thanks': 'どういたしまして！他に何かあればお気軽にどうぞ。',
        }
        
        # Usage tracking
        self.daily_requests = 0
        self.daily_tokens = 0
        
        logger.info("GeminiClient initialized successfully")
    
    async def generate_response(
        self, 
        prompt: str, 
        history: Optional[List[Dict]] = None,
        mode: str = 'standard',
        model: Optional[str] = None
    ) -> Optional[str]:
        """Generate AI response"""
        try:
            # Check for simple responses first (cost optimization)
            prompt_lower = prompt.lower().strip()
            for key, response in self.simple_responses.items():
                if key in prompt_lower and len(prompt) < 20:
                    logger.info(f"Using simple response for: {prompt}")
                    return response
            
            mode_config = self.modes.get(mode, self.modes['standard'])
            
            # Build the full prompt with system instruction
            full_prompt = f"{mode_config['system_instruction']}\n\nユーザー: {prompt}"
            
            # Add history context if available
            if history and len(history) > 0:
                history_text = "\n".join([
                    f"ユーザー: {h.get('user_message', '')}\nAI: {h.get('ai_response', '')}"
                    for h in history[-3:]  # Only last 3 messages for context
                ])
                full_prompt = f"{mode_config['system_instruction']}\n\n過去の会話:\n{history_text}\n\nユーザー: {prompt}"
            
            logger.info(f"Generating response for prompt: {prompt[:50]}...")
            
            # Generate response using async method
            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=mode_config['temperature'],
                    max_output_tokens=1024,
                )
            )
            
            if response and response.text:
                self.daily_requests += 1
                self.daily_tokens += len(prompt.split()) + len(response.text.split())
                logger.info(f"Response generated successfully: {response.text[:50]}...")
                return response.text
            else:
                logger.warning("Empty response from Gemini API")
                return None
            
        except Exception as e:
            logger.error(f'Error generating response: {e}')
            import traceback
            traceback.print_exc()
            return None
    
    async def get_available_modes(self) -> Dict[str, str]:
        """Get available AI modes"""
        return {
            mode: config['system_instruction'] 
            for mode, config in self.modes.items()
        }
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation"""
        return int(len(text.split()) * 1.3)
    
    def get_usage_stats(self) -> Dict:
        """Get current API usage statistics"""
        return {
            'daily_requests': self.daily_requests,
            'daily_tokens': self.daily_tokens,
            'request_limit': 1500,
            'token_limit': 1000000,
            'requests_remaining': max(0, 1500 - self.daily_requests),
            'tokens_remaining': max(0, 1000000 - self.daily_tokens),
            'usage_percentage': {
                'requests': (self.daily_requests / 1500) * 100,
                'tokens': (self.daily_tokens / 1000000) * 100
            }
        }