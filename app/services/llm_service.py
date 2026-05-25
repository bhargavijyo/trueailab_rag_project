import os
import google.generativeai as genai
from typing import List, Dict, Tuple
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class LLMService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_response(self, messages: List[Dict[str, str]]) -> Tuple[str, int]:
        try:
            gemini_messages = []
            system_prompt = ""
            for msg in messages:
                if msg["role"] == "system":
                    system_prompt += msg["content"] + "\n\n"
                elif msg["role"] == "user":
                    gemini_messages.append({"role": "user", "parts": [msg["content"]]})
                elif msg["role"] == "assistant":
                    gemini_messages.append({"role": "model", "parts": [msg["content"]]})
            
            if system_prompt and gemini_messages:
                gemini_messages[0]["parts"][0] = f"System Instruction:\n{system_prompt}\n{gemini_messages[0]['parts'][0]}"
            
            response = self.model.generate_content(
                gemini_messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                )
            )
            
            reply = response.text
            tokens_used = 0
            if response.usage_metadata:
                tokens_used = response.usage_metadata.total_token_count
                
            logger.info(f"LLM Response generated. Tokens used: {tokens_used}")
            return reply, tokens_used
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise e
