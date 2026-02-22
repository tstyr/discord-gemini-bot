import google.generativeai as genai


class AIHandler:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")

    async def generate(self, prompt: str, system_prompt: str) -> tuple[str, int]:
        try:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}"
            response = await self.model.generate_content_async(full_prompt)
            
            tokens = 0
            if response.usage_metadata:
                tokens = response.usage_metadata.total_token_count
            
            return response.text, tokens
        except Exception as e:
            return f"Error: {str(e)}", 0
