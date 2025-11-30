"""
Code Optimizer
Uses LLM (o4-mini) to optimize Python code through variable renaming and nested IF detection.
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


class CodeOptimizer:
    """
    Optimizes Python code using LLM for variable renaming and nested IF detection.
    """
    
    def __init__(self, model: str = "o4-mini", pdf_guidelines: Optional[str] = None):
        """
        Initialize the code optimizer.
        
        Args:
            model: OpenAI model to use (default: o4-mini)
            pdf_guidelines: Optional additional guidelines from PDF
        """
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.pdf_guidelines = pdf_guidelines
        
        # Load system prompt from PDF
        script_dir = os.path.dirname(os.path.abspath(__file__))
        system_prompt_pdf = os.path.join(script_dir, "systemPrompt.pdf")
        
        if os.path.exists(system_prompt_pdf):
            self.system_prompt = self.load_pdf_guidelines(system_prompt_pdf)
            logger.info(f"Loaded system prompt from: {system_prompt_pdf}")
        else:
            logger.warning(f"systemPrompt.pdf not found at {system_prompt_pdf}")
            # Fallback to default prompt
            self.system_prompt = "You are a Python code optimizer. Optimize the provided code."
        
        logger.info(f"Initialized CodeOptimizer with model: {model}")
    
    def load_pdf_guidelines(self, pdf_path: str) -> str:
        """
        Load optimization guidelines from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from PDF
        """
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(pdf_path)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            logger.info(f"Loaded guidelines from PDF: {pdf_path}")
            return text
            
        except ImportError:
            logger.warning("PyPDF2 not installed - cannot load PDF guidelines")
            return ""
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            return ""
    
    def optimize_code(self, code: str) -> Dict[str, Any]:
        """
        Optimize Python code using LLM.
        
        Args:
            code: Python source code to optimize
            
        Returns:
            Dictionary with optimization results
        """
        result = {
            "original_code": code,
            "optimized_code": None,
            "success": False,
            "error": None
        }
        
        try:
            # Build user message
            user_message = f"Optimize the following Python code:\n\n{code}"
            
            logger.info("Sending code to LLM for optimization...")
            
            # Call LLM with loaded system prompt
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=1.0  # o4-mini requires temperature=1.0
            )
            
            # Extract optimized code
            optimized_code = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if optimized_code.startswith("```python"):
                optimized_code = optimized_code.split("```python")[1]
            if optimized_code.startswith("```"):
                optimized_code = optimized_code.split("```")[1]
            if optimized_code.endswith("```"):
                optimized_code = optimized_code.rsplit("```", 1)[0]
            
            optimized_code = optimized_code.strip()
            
            result["optimized_code"] = optimized_code
            result["success"] = True
            
            logger.info("✅ Code optimization completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error optimizing code: {e}")
            result["error"] = str(e)
        
        return result
    
    def analyze_optimization(self, original: str, optimized: str) -> Dict[str, Any]:
        """
        Analyze the differences between original and optimized code.
        
        Args:
            original: Original code
            optimized: Optimized code
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "has_warnings": "WARNING" in optimized,
            "warning_count": optimized.count("WARNING:"),
            "line_count_original": len(original.split('\n')),
            "line_count_optimized": len(optimized.split('\n')),
            "lines_added": 0
        }
        
        # Calculate lines added (warnings)
        analysis["lines_added"] = analysis["line_count_optimized"] - analysis["line_count_original"]
        
        return analysis


# Usage example
if __name__ == "__main__":
    # Example code to optimize
    example_code = """
def calculate_discount(price, customer_type, years):
    '''Calculate discount based on customer type and years'''
    discount = 0
    
    if price > 0:
        if customer_type == "premium":
            if years > 5:
                if price > 1000:
                    discount = 0.30
                else:
                    discount = 0.20
            else:
                discount = 0.15
        else:
            discount = 0.05
    
    return price * (1 - discount)

def process_numbers(data, threshold):
    '''Process a list of numbers'''
    result = []
    total = 0
    
    for num in data:
        if num > threshold:
            total += num
            result.append(num * 2)
    
    average = total / len(result) if result else 0
    return result, average
"""
    
    print("=" * 70)
    print("Code Optimizer - Demo")
    print("=" * 70)
    
    # Initialize optimizer
    optimizer = CodeOptimizer(model="o4-mini")
    
    print("\nOriginal Code:")
    print("-" * 70)
    print(example_code)
    print("-" * 70)
    
    # Optimize code
    print("\nOptimizing code...")
    result = optimizer.optimize_code(example_code)
    
    if result["success"]:
        print("\n✅ Optimized Code:")
        print("-" * 70)
        print(result["optimized_code"])
        print("-" * 70)
        
        # Analyze optimization
        analysis = optimizer.analyze_optimization(
            result["original_code"],
            result["optimized_code"]
        )
        
        print("\nOptimization Analysis:")
        print(f"  Warnings found: {analysis['has_warnings']}")
        print(f"  Warning count: {analysis['warning_count']}")
        print(f"  Lines added: {analysis['lines_added']}")
    else:
        print(f"\n❌ Optimization failed: {result['error']}")
