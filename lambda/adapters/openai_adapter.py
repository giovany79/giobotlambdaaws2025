from openai import OpenAI

from domain.interfaces import AIServiceInterface


class OpenAIAdapter(AIServiceInterface):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self._client = OpenAI(api_key=api_key)
        self._model = model
    
    def generate_response(self, message: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": message}],
                max_tokens=200,
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")