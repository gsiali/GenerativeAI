"""
LLM Agent with Function Calling
Uses OpenAI's function calling to generate code and automatically create CFG/DFG
"""

import os
import sys
import json
import ast
import logging
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from partA.cfg_generator import CFGGenerator
from partA.dfg_generator import DFGGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


class LLMAgent:
    """
    LLM Agent that uses function calling to generate code and create visualizations
    """
    
    def __init__(self, model: str = "o4-mini", temperature: float = 1.0):
        """
        Initialize the LLM agent
        
        Args:
            model: OpenAI model to use (default: o4-mini)
            temperature: Sampling temperature (default: 1.0 for o4-mini)
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        
        # Initialize generators
        self.cfg_generator = CFGGenerator(output_dir="generated_artifacts/cfg")
        self.dfg_generator = DFGGenerator(output_dir="generated_artifacts/dfg")
        
        # Define available tools
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "generate_cfg",
                    "description": "Generate Control Flow Graph (CFG) visualization for Python code. Creates a PNG image showing the control flow structure of the function.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The complete Python code containing the function to visualize"
                            },
                            "function_name": {
                                "type": "string",
                                "description": "The name of the function to generate CFG for"
                            }
                        },
                        "required": ["code", "function_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_dfg",
                    "description": "Generate Data Flow Graph (DFG) visualization for Python code. Creates a PNG image showing variable definitions and usage patterns.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The complete Python code containing the function to visualize"
                            },
                            "function_name": {
                                "type": "string",
                                "description": "The name of the function to generate DFG for"
                            }
                        },
                        "required": ["code", "function_name"]
                    }
                }
            }
        ]
        
        logger.info(f"Initialized LLMAgent with model: {model}")
    
    def _execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a function call from the LLM
        
        Args:
            function_name: Name of the function to execute
            arguments: Function arguments
            
        Returns:
            Result dictionary
        """
        try:
            if function_name == "generate_cfg":
                code = arguments.get("code", "")
                func_name = arguments.get("function_name", "")
                
                logger.info(f"Generating CFG for function: {func_name}")
                cfg_paths = self.cfg_generator.generate_cfg(code)
                
                if func_name in cfg_paths:
                    return {
                        "success": True,
                        "function": func_name,
                        "cfg_path": cfg_paths[func_name],
                        "message": f"CFG generated successfully at {cfg_paths[func_name]}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to generate CFG for function '{func_name}'. Available functions: {list(cfg_paths.keys())}"
                    }
            
            elif function_name == "generate_dfg":
                code = arguments.get("code", "")
                func_name = arguments.get("function_name", "")
                
                logger.info(f"Generating DFG for function: {func_name}")
                dfg_path = self.dfg_generator.generate_dfg(code, func_name)
                
                if dfg_path:
                    return {
                        "success": True,
                        "function": func_name,
                        "dfg_path": dfg_path,
                        "message": f"DFG generated successfully at {dfg_path}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to generate DFG for function '{func_name}'"
                    }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown function: {function_name}"
                }
                
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_function_names(self, code: str) -> List[str]:
        """
        Extract function names from Python code
        
        Args:
            code: Python code string
            
        Returns:
            List of function names
        """
        try:
            tree = ast.parse(code)
            return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        except:
            return []
    
    def generate_code(
        self,
        user_description: str,
        context_functions: Optional[List[str]] = None,
        auto_visualize: bool = True
    ) -> Dict[str, Any]:
        """
        Generate Python code using LLM with automatic CFG/DFG generation
        
        Args:
            user_description: Natural language description of desired functionality
            context_functions: List of relevant function descriptions from RAG
            auto_visualize: Whether to automatically generate CFG/DFG (default: True)
            
        Returns:
            Dictionary containing:
                - code: Generated Python code
                - function_names: List of functions in generated code
                - cfg_paths: Dict of function_name -> CFG image path
                - dfg_paths: Dict of function_name -> DFG image path
                - tool_calls: List of tool calls made by LLM
                - errors: List of any errors encountered
        """
        result = {
            "code": None,
            "function_names": [],
            "cfg_paths": {},
            "dfg_paths": {},
            "tool_calls": [],
            "errors": []
        }
        
        try:
            # Build system message with context
            system_content = """You are an expert Python programmer.

Generate clean, executable Python code with:
1. Proper error handling
2. Type hints for all parameters and return values
3. Comprehensive docstrings (Google style)
4. PEP 8 style compliance

Return ONLY valid Python code. No markdown blocks, no explanations, no tool calls in your code.
Just pure Python code that can be directly executed.

After generating code, you have access to tools to generate Control Flow Graphs (CFG) and Data Flow Graphs (DFG).
When asked to generate visualizations, you MUST call BOTH generate_cfg AND generate_dfg for EVERY function."""
            
            # Add RAG context if provided
            if context_functions:
                system_content += f"\n\nRELEVANT FUNCTION EXAMPLES:\n{chr(10).join(context_functions)}"
            
            # Initial request to LLM
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_description}
            ]
            
            # Make API call WITHOUT tools first to get code
            logger.info(f"Generating code for: {user_description[:100]}...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=messages
            )
            
            # Process response
            assistant_message = response.choices[0].message
            
            # Extract generated code from content
            code = None
            if assistant_message.content:
                code = assistant_message.content.strip()
                
                # Remove markdown code blocks if present
                if code.startswith("```python"):
                    code = code.split("```python", 1)[1]
                    code = code.rsplit("```", 1)[0].strip()
                elif code.startswith("```"):
                    code = code.split("```", 1)[1]
                    code = code.rsplit("```", 1)[0].strip()
                
                # Remove any tool call syntax that LLM might have included
                import re
                # Remove XML-style tool calls
                code = re.sub(r'<tool\s+[^>]*\s*/>', '', code, flags=re.MULTILINE)
                # Remove JSON-style tool calls
                code = re.sub(r'\{"name":\s*"[^"]*",\s*"arguments":\s*\{[^}]*\}\}', '', code, flags=re.MULTILINE)
                # Remove Python-style function call patterns like generate_cfg(...) or generate_dfg(...)
                code = re.sub(r'^generate_(cfg|dfg)\([^)]*\)\s*$', '', code, flags=re.MULTILINE)
                code = code.strip()
                
                result["code"] = code
                result["function_names"] = self._extract_function_names(code)
                
                # Validate code
                try:
                    ast.parse(code)
                    logger.info("✅ Generated code is syntactically valid")
                except SyntaxError as e:
                    result["errors"].append(f"Syntax error in generated code: {e}")
                    logger.error(f"Syntax error: {e}")
            else:
                logger.warning("No code content in response")
                result["errors"].append("LLM did not return code")
                return result
            
            # Now ask LLM to generate visualizations using tools
            if auto_visualize and result["code"] and result["function_names"]:
                logger.info("Requesting LLM to generate visualizations...")
                
                # Add code generation to conversation
                messages.append({"role": "assistant", "content": result["code"]})
                messages.append({
                    "role": "user", 
                    "content": f"""You MUST now generate BOTH CFG (Control Flow Graph) AND DFG (Data Flow Graph) visualizations for EVERY function in the code.

The functions in the code are: {', '.join(result['function_names'])}

For EACH function, you MUST call:
1. generate_cfg(code, function_name)
2. generate_dfg(code, function_name)

Start by calling these tools now for all functions. This is required - do not skip the DFG generation."""
                })
                
                # Request with tools enabled
                tool_response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=self.temperature,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto"
                )
                
                assistant_message = tool_response.choices[0].message
            
            # Handle function calls
            if auto_visualize and assistant_message.tool_calls:
                messages.append(assistant_message)
                
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"LLM called tool: {function_name}")
                    result["tool_calls"].append({
                        "function": function_name,
                        "arguments": arguments
                    })
                    
                    # Execute the function
                    function_result = self._execute_function(function_name, arguments)
                    
                    # Store results
                    if function_result.get("success"):
                        if function_name == "generate_cfg":
                            result["cfg_paths"][function_result["function"]] = function_result["cfg_path"]
                        elif function_name == "generate_dfg":
                            result["dfg_paths"][function_result["function"]] = function_result["dfg_path"]
                    else:
                        result["errors"].append(function_result.get("error"))
                    
                    # Add function result to conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps(function_result)
                    })
                
                # Continue conversation to let LLM know tools were executed
                logger.info("Continuing conversation after tool execution...")
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=self.temperature,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto"
                )
                
                # Check for additional tool calls
                final_message = final_response.choices[0].message
                if final_message.tool_calls:
                    messages.append(final_message)
                    
                    for tool_call in final_message.tool_calls:
                        function_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)
                        
                        logger.info(f"LLM called additional tool: {function_name}")
                        result["tool_calls"].append({
                            "function": function_name,
                            "arguments": arguments
                        })
                        
                        function_result = self._execute_function(function_name, arguments)
                        
                        if function_result.get("success"):
                            if function_name == "generate_cfg":
                                result["cfg_paths"][function_result["function"]] = function_result["cfg_path"]
                            elif function_name == "generate_dfg":
                                result["dfg_paths"][function_result["function"]] = function_result["dfg_path"]
                        else:
                            result["errors"].append(function_result.get("error"))
            
            # If LLM didn't call tools, manually generate visualizations
            elif auto_visualize and result["code"] and result["function_names"]:
                logger.info("LLM didn't call tools, generating visualizations manually...")
                
                for func_name in result["function_names"]:
                    # Generate CFG
                    cfg_result = self._execute_function("generate_cfg", {
                        "code": result["code"],
                        "function_name": func_name
                    })
                    if cfg_result.get("success"):
                        result["cfg_paths"][func_name] = cfg_result["cfg_path"]
                    
                    # Generate DFG
                    dfg_result = self._execute_function("generate_dfg", {
                        "code": result["code"],
                        "function_name": func_name
                    })
                    if dfg_result.get("success"):
                        result["dfg_paths"][func_name] = dfg_result["dfg_path"]
            
            return result
            
        except Exception as e:
            logger.error(f"Error in code generation: {e}")
            result["errors"].append(str(e))
            return result


if __name__ == "__main__":
    # Test the LLM agent
    agent = LLMAgent()
    
    test_description = "Create a function to calculate the nth Fibonacci number using iteration"
    
    print(f"\n🤖 Testing LLM Agent")
    print(f"📝 Request: {test_description}\n")
    
    result = agent.generate_code(test_description)
    
    print("=" * 70)
    print("RESULTS:")
    print("=" * 70)
    
    if result["code"]:
        print("\n✅ Generated Code:")
        print(result["code"])
        
        print(f"\n📊 Functions found: {', '.join(result['function_names'])}")
        
        if result["cfg_paths"]:
            print(f"\n🔀 CFG paths:")
            for func, path in result["cfg_paths"].items():
                print(f"  - {func}: {path}")
        
        if result["dfg_paths"]:
            print(f"\n📊 DFG paths:")
            for func, path in result["dfg_paths"].items():
                print(f"  - {func}: {path}")
        
        if result["tool_calls"]:
            print(f"\n🔧 Tool calls made: {len(result['tool_calls'])}")
            for call in result["tool_calls"]:
                print(f"  - {call['function']}({call['arguments']['function_name']})")
    
    if result["errors"]:
        print(f"\n⚠️ Errors:")
        for error in result["errors"]:
            print(f"  - {error}")
