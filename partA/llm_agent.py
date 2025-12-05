"""LLM Agent for code generation with CFG/DFG diagram tools."""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from openai import OpenAI
import graphviz
from rag_system import InMemoryRAG

load_dotenv()
logging.getLogger("openai").setLevel(logging.INFO)


class LLMAgent:
    def __init__(self, model: str = "o4-mini"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.output_dir = "diagrams"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize RAG system
        self.rag_system = InMemoryRAG()
        self.rag_system.initialize()
        
        # Define the function schema that the LLM will use to structure its responses
        # This tells the LLM: "Always respond using this format with these fields"
        self.tools = [{
            "type": "function",
            "function": {
                "name": "respond",
                "description": "Returns a chat response and optionally generated code with diagrams.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "chat_reply": {"type": "string", "description": "Conversational response to the user."},
                        "generated_code": {"type": "string", "description": "Python code if requested. Null if no code needed."},
                        "cfg_dot": {"type": "string", "description": "Control Flow Graph in Graphviz DOT format (only if code generated)."},
                        "dfg_dot": {"type": "string", "description": "Data Flow Graph in Graphviz DOT format (only if code generated)."}
                    },
                    "required": ["chat_reply"]
                }
            }
        }]
    
    def _render_diagram(self, dot_string: str, diagram_type: str) -> Optional[str]:
        """Render a DOT string to PNG and return the file path."""
        if not dot_string:
            return None
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(self.output_dir, f"{diagram_type}_{timestamp}")
            graphviz.Source(dot_string).render(filepath, format="png", cleanup=True)
            return f"{filepath}.png"
        except Exception as e:
            logging.error(f"Error rendering {diagram_type}: {e}")
            return None
    
    def chat(self, user_message: str, conversation_history: Optional[List[Dict]] = None) -> Dict:
        """Send a message to the LLM and get a structured response."""
        
        # Step 1: Retrieve RAG context
        relevant = self.rag_system.retrieve_relevant_embeddings(user_message, top_k=3)
        rag_context = [{"text": r["text"], "score": r["score"]} for r in relevant]
        logging.info("RAG context: %s", [{"score": r["score"], "text": r["text"][:200]} for r in relevant])
        
        # Step 2: Build the conversation messages
        messages = [{"role": "system", "content": self._build_system_prompt(rag_context)}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        # Step 3: Call OpenAI API with function calling
        # tool_choice forces the LLM to ALWAYS use the "respond" function format
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice={"type": "function", "function": {"name": "respond"}}
        )
        
        # Step 4: Extract the function call arguments from LLM response
        tool_call = response.choices[0].message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        
        # Step 5: Process and return the structured result
        return self._process_llm_response(args)
    
    def _build_system_prompt(self, rag_context: List[Dict]) -> str:
        """Build the system prompt with RAG context."""
        rag_context_str = " | ".join([f"[Score: {item['score']:.4f}] {item['text']}" for item in rag_context])
        
        return f"""You are a helpful Python programming assistant.
If the user asks for code, generate the Python code, a Control Flow Graph (CFG) in DOT format, and a Data Flow Graph (DFG) in DOT format.
Otherwise, strictly provide a conversational reply.

IMPORTANT: When generating code, check the RAG context provided below.
- If the RAG context contains relevant specifications (score > 0.5), implement the code STRICTLY according to those specifications and mention in your chat_reply that the code was "generated based on knowledge base specifications".
- If the RAG context is not relevant (score <= 0.5 or doesn't match the request), generate code using your own logic and mention in your chat_reply that the code was "generated using general programming knowledge".

RAG CONTEXT:
{rag_context_str}"""
    
    def _process_llm_response(self, args: Dict) -> Dict:
        """Process the LLM function call arguments and render diagrams."""
        result = {
            "chat_reply": args.get("chat_reply", ""),
            "generated_code": None,
            "cfg_path": None,
            "dfg_path": None
        }
        
        if generated_code := args.get("generated_code"):
            result["generated_code"] = generated_code.strip()
        
        if cfg_dot := args.get("cfg_dot"):
            result["cfg_path"] = self._render_diagram(cfg_dot, "cfg")
        
        if dfg_dot := args.get("dfg_dot"):
            result["dfg_path"] = self._render_diagram(dfg_dot, "dfg")
        
        return result