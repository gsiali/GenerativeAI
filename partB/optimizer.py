"""Code Optimizer - LLM-based Python code optimization with nested IF detection."""

import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader

load_dotenv()
logging.getLogger("openai").setLevel(logging.DEBUG)


class CodeOptimizer:
    def __init__(self, model: str = "o4-mini"):
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from PDF."""
        pdf_path = os.path.join(os.path.dirname(__file__), "systemPrompt.pdf")
        return "".join(page.extract_text() for page in PdfReader(pdf_path).pages)
    
    def optimize_code(self, code: str) -> Dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Optimize the following Python code. Return ONLY the optimized code without any markdown formatting or code fences:\n\n{code}"}
                ]
            )
            
            optimized_code = response.choices[0].message.content.strip()
            
            return {"original_code": code, "optimized_code": optimized_code, "success": True, "error": None}
        except Exception as e:
            return {"original_code": code, "optimized_code": None, "success": False, "error": str(e)}


if __name__ == "__main__":
    code = "def f(x,y):\n    if x>0:\n        if y>0:\n            if x>y:\n                if y>10:\n                    return x\n    return 0"
    result = CodeOptimizer().optimize_code(code)
    print(f"Success: {result['success']} | Warnings: {result['optimized_code'].count('WARNING:')}\n\n{result['optimized_code']}")
