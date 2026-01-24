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
        
        # AI mode configurations - will be used to create models dynamically
        self.modes = {
            'standard': {
                'system_instruction': """あなたは親切で柔軟なAIアシスタントです。

性格:
- フレンドリーで親しみやすい
- 会話の流れを自然に継続
- ユーザーの意図を柔軟に理解
- 話題が変わっても自然に対応
- 短く簡潔に、でも温かみのある応答

応答スタイル:
- 1-3文程度の簡潔な応答
- 絵文字を適度に使用（多用しない）
- 前の会話を覚えて文脈を理解
- 質問には直接的に答える
- 不要な説明は省く

日本語で応答してください。""",
                'temperature': 0.8,
            },
            'creative': {
                'system_instruction': """あなたは創造的で自由な発想のAIです。

性格:
- 想像力豊かで芸術的
- 型にはまらない発想
- 遊び心がある
- でも役立つ情報も提供

応答スタイル:
- 創造的で面白い表現
- 比喩や例えを使う
- 短く印象的に

日本語で応答してください。""",
                'temperature': 0.95,
            },
            'coder': {
                'system_instruction': """あなたはプログラミングの専門家です。

性格:
- 技術的に正確
- 実用的なアドバイス
- ベストプラクティス重視

応答スタイル:
- コード例を含める
- 簡潔な説明
- 実装可能な解決策

日本語で応答してください。""",
                'temperature': 0.3,
            },
            'assistant': {
                'system_instruction': """あなたはプロフェッショナルなアシスタントです。

性格:
- 丁寧でフォーマル
- 効率的で整理された
- 生産性重視

応答スタイル:
- 明確で構造化された応答
- 箇条書きを活用
- 実用的な提案

日本語で応答してください。""",
                'temperature': 0.5,
            },
            'music_dj': {
                'system_instruction': """あなたは音楽に詳しいDJ AIです。

性格:
- 音楽への情熱がある
- トレンドに敏感
- ユーザーの気分を理解

応答スタイル:
- 音楽の話題で盛り上がる
- おすすめを自然に提案
- 短く楽しく

日本語で応答してください。""",
                'temperature': 0.85,
            }
        }
        
        # Cache for models with different system instructions
        self.model_cache = {}
        
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
    
    def get_model(self, mode: str = 'standard'):
        """Get or create model with system instruction for the given mode"""
        if mode not in self.model_cache:
            mode_config = self.modes.get(mode, self.modes['standard'])
            self.model_cache[mode] = genai.GenerativeModel(
                'gemini-2.0-flash',
                system_instruction=mode_config['system_instruction']
            )
        return self.model_cache[mode]
        
        # AI mode configurations
        # Note: Music playback requests are handled by main.py before reaching Gemini
        self.modes = {
            'standard': {
                'system_instruction': """あなたは親切で柔軟なAIアシスタントです。

性格:
- フレンドリーで親しみやすい
- 会話の流れを自然に継続
- ユーザーの意図を柔軟に理解
- 話題が変わっても自然に対応
- 短く簡潔に、でも温かみのある応答

応答スタイル:
- 1-3文程度の簡潔な応答
- 絵文字を適度に使用（多用しない）
- 前の会話を覚えて文脈を理解
- 質問には直接的に答える
- 不要な説明は省く

日本語で応答してください。""",
                'temperature': 0.8,
            },
            'creative': {
                'system_instruction': """あなたは創造的で自由な発想のAIです。

性格:
- 想像力豊かで芸術的
- 型にはまらない発想
- 遊び心がある
- でも役立つ情報も提供

応答スタイル:
- 創造的で面白い表現
- 比喩や例えを使う
- 短く印象的に

日本語で応答してください。""",
                'temperature': 0.95,
            },
            'coder': {
                'system_instruction': """あなたはプログラミングの専門家です。

性格:
- 技術的に正確
- 実用的なアドバイス
- ベストプラクティス重視

応答スタイル:
- コード例を含める
- 簡潔な説明
- 実装可能な解決策

日本語で応答してください。""",
                'temperature': 0.3,
            },
            'assistant': {
                'system_instruction': """あなたはプロフェッショナルなアシスタントです。

性格:
- 丁寧でフォーマル
- 効率的で整理された
- 生産性重視

応答スタイル:
- 明確で構造化された応答
- 箇条書きを活用
- 実用的な提案

日本語で応答してください。""",
                'temperature': 0.5,
            },
            'music_dj': {
                'system_instruction': """あなたは音楽に詳しいDJ AIです。

性格:
- 音楽への情熱がある
- トレンドに敏感
- ユーザーの気分を理解

応答スタイル:
- 音楽の話題で盛り上がる
- おすすめを自然に提案
- 短く楽しく

日本語で応答してください。""",
                'temperature': 0.85,
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
            
            # Get model with system instruction for this mode
            model = self.get_model(mode)
            
            # Build conversation history for context
            conversation_history = []
            if history and len(history) > 0:
                # Use last 5 messages for better context
                for h in history[-5:]:
                    conversation_history.append({
                        'role': 'user',
                        'parts': [h.get('user_message', '')]
                    })
                    conversation_history.append({
                        'role': 'model',
                        'parts': [h.get('ai_response', '')]
                    })
            
            logger.info(f"Generating response for prompt: {prompt[:50]}... (mode: {mode})")
            
            # Create chat session with history
            chat = model.start_chat(history=conversation_history)
            
            # Generate response using async method
            response = await chat.send_message_async(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=mode_config['temperature'],
                    max_output_tokens=512,  # Shorter responses
                    top_p=0.95,
                    top_k=40,
                ),
                safety_settings={
                    'HARASSMENT': 'BLOCK_NONE',
                    'HATE_SPEECH': 'BLOCK_NONE',
                    'SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'DANGEROUS_CONTENT': 'BLOCK_NONE',
                }
            )
            
            if response and response.text:
                self.daily_requests += 1
                self.daily_tokens += len(prompt.split()) + len(response.text.split())
                
                # Clean up response
                result = response.text.strip()
                
                logger.info(f"Response generated successfully: {result[:50]}...")
                return result
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