"""
Model client for OpenAI LLM interactions.
"""
import openai
import os
from dotenv import load_dotenv
load_dotenv()



class OpenAIClient:
    """OpenAI API client"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4o-mini"
        self.temperature = 0.7
        self.max_tokens = 2000
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a chat completion using OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content


def create_model():
    """Create OpenAI client"""
    return OpenAIClient()
