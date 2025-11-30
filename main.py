"""
Main Application
Unified chatbot application integrating code generation (Part A) and optimization (Part B).
Provides both FastAPI backend and Streamlit frontend.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import json
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import Part A components
try:
    from partA.rag_system import InMemoryRAG
    from partA.llm_agent import LLMAgent
    logger.info("✅ Part A components loaded successfully")
except ImportError as e:
    logger.error(f"❌ Error importing Part A components: {e}")
    raise

# Import Part B components
try:
    from partB.optimizer import CodeOptimizer
    logger.info("✅ Part B components loaded successfully")
except ImportError as e:
    logger.error(f"❌ Error importing Part B components: {e}")
    raise


class ChatbotSession:
    """
    Manages a chatbot session with conversation history.
    """
    
    def __init__(self, session_id: str):
        """Initialize a new session."""
        self.session_id = session_id
        self.created_at = datetime.now()
        self.conversation_history = []
        self.generated_codes = []
        self.artifacts = {}  # Store CFGs, DFGs, etc.
        
    def add_interaction(self, user_input: str, response: Dict[str, Any]):
        """Add an interaction to the conversation history."""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "response": response
        }
        self.conversation_history.append(interaction)
    
    def to_dict(self) -> Dict:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "conversation_history": self.conversation_history,
            "generated_codes": self.generated_codes,
            "artifacts": self.artifacts
        }


class CodeGenerationPipeline:
    """
    Part A: Code generation pipeline with RAG, CFG, and DFG.
    """
    
    def __init__(self):
        """Initialize the code generation pipeline."""
        logger.info("Initializing Code Generation Pipeline (Part A)...")
        
        # Define paths
        kb_path = "partA/knowledge_base/functions.txt"
        emb_path = "partA/knowledge_base/embeddings.json"
        
        # Initialize components
        self.rag = InMemoryRAG(knowledge_base_path=kb_path, embeddings_path=emb_path)
        self.llm_agent = LLMAgent(model="o4-mini", temperature=1.0)
        
        # Initialize RAG system
        try:
            logger.info("Initializing RAG system...")
            self.rag.initialize()
            logger.info("✅ Code Generation Pipeline initialized")
        except Exception as e:
            logger.error(f"❌ Error initializing RAG: {e}")
            raise
    
    def generate_code(self, description: str, use_rag: bool = True) -> Dict[str, Any]:
        """
        Generate code from natural language description.
        
        Args:
            description: Natural language description
            use_rag: Whether to use RAG for context retrieval
            
        Returns:
            Dictionary with generated code and metadata
        """
        result = {
            "description": description,
            "code": None,
            "context_functions": [],
            "cfg_paths": {},
            "dfg_paths": {},
            "errors": []
        }
        
        try:
            # Step 1: Retrieve relevant functions using RAG
            context_functions = []
            if use_rag:
                logger.info("Retrieving relevant functions from knowledge base...")
                try:
                    rag_results = self.rag.retrieve_relevant_functions(description, top_k=3)
                    # Extract text from RAG results (returns list of dicts)
                    context_functions = [r["text"] for r in rag_results]
                    result["context_functions"] = context_functions
                    logger.info(f"Retrieved {len(context_functions)} relevant functions")
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {e}")
                    result["errors"].append(f"RAG retrieval: {str(e)}")
            
            # Step 2: Generate code using LLM agent (automatically generates CFG/DFG)
            logger.info("Generating code with LLM agent...")
            try:
                code_result = self.llm_agent.generate_code(
                    user_description=description,
                    context_functions=context_functions,
                    auto_visualize=True
                )
                
                if code_result["code"]:
                    result["code"] = code_result["code"]
                    result["is_valid"] = True  # LLM agent validates internally
                    result["cfg_paths"] = code_result.get("cfg_paths", {})
                    result["dfg_paths"] = code_result.get("dfg_paths", {})
                    
                    logger.info(f"✅ Generated code with {len(result['cfg_paths'])} CFG(s) and {len(result['dfg_paths'])} DFG(s)")
                    
                    if code_result.get("errors"):
                        result["errors"].extend(code_result["errors"])
                else:
                    result["errors"].append("Code generation failed: No code produced")
                    return result
                    
            except Exception as e:
                logger.error(f"Code generation failed: {e}")
                result["errors"].append(f"Code generation: {str(e)}")
                return result
            
            logger.info("✅ Code generation pipeline completed")
            return result
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            result["errors"].append(f"Pipeline: {str(e)}")
            return result


class CodeOptimizationPipeline:
    """
    Part B: Code optimization pipeline using LLM.
    """
    
    def __init__(self):
        """Initialize the code optimization pipeline."""
        logger.info("Initializing Code Optimization Pipeline (Part B)...")
        
        self.optimizer = CodeOptimizer(model="o4-mini")
        
        logger.info("✅ Code Optimization Pipeline initialized")
    
    def optimize_code(self, code: str) -> Dict[str, Any]:
        """
        Optimize code using LLM for variable renaming and nested IF detection.
        
        Args:
            code: Python source code
            
        Returns:
            Dictionary with optimization results
        """
        result = {
            "original_code": code,
            "optimized_code": None,
            "success": False,
            "analysis": {},
            "errors": []
        }
        
        try:
            logger.info("Optimizing code with LLM...")
            
            # Call optimizer
            opt_result = self.optimizer.optimize_code(code)
            
            if opt_result["success"]:
                result["optimized_code"] = opt_result["optimized_code"]
                result["success"] = True
                
                # Analyze the optimization
                analysis = self.optimizer.analyze_optimization(
                    opt_result["original_code"],
                    opt_result["optimized_code"]
                )
                result["analysis"] = analysis
                
                if analysis["has_warnings"]:
                    logger.info(f"⚠️  Found {analysis['warning_count']} nested IF warning(s)")
                else:
                    logger.info("✅ No nested IF violations found")
                
                logger.info("✅ Code optimization completed successfully")
            else:
                result["errors"].append(opt_result.get("error", "Unknown error"))
                logger.error("❌ Code optimization failed")
            
            return result
            
        except Exception as e:
            logger.error(f"Optimization pipeline error: {e}")
            result["errors"].append(f"Pipeline: {str(e)}")
            return result


class ChatbotApplication:
    """
    Main chatbot application orchestrating Part A and Part B.
    """
    
    def __init__(self):
        """Initialize the chatbot application."""
        logger.info("=" * 70)
        logger.info("Initializing Chatbot Application")
        logger.info("=" * 70)
        
        # Create output directories
        os.makedirs("generated_artifacts/cfg", exist_ok=True)
        os.makedirs("generated_artifacts/dfg", exist_ok=True)
        os.makedirs("sessions", exist_ok=True)
        
        # Initialize pipelines
        self.generation_pipeline = CodeGenerationPipeline()
        self.optimization_pipeline = CodeOptimizationPipeline()
        
        # Session management
        self.sessions = {}
        
        logger.info("=" * 70)
        logger.info("✅ Chatbot Application Ready")
        logger.info("=" * 70)
    
    def create_session(self) -> str:
        """Create a new session and return its ID."""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        self.sessions[session_id] = ChatbotSession(session_id)
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ChatbotSession]:
        """Get a session by ID."""
        return self.sessions.get(session_id)
    
    def save_session(self, session_id: str):
        """Save session to disk."""
        session = self.get_session(session_id)
        if session:
            session_file = f"sessions/{session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)
            logger.info(f"Session saved: {session_file}")
    
    def generate_code_endpoint(self, description: str, session_id: Optional[str] = None,
                               use_rag: bool = True) -> Dict[str, Any]:
        """
        Part A: Generate code from description.
        
        Args:
            description: Natural language description
            session_id: Optional session ID
            use_rag: Whether to use RAG
            
        Returns:
            Generation results
        """
        # Create session if needed
        if not session_id:
            session_id = self.create_session()
        
        session = self.get_session(session_id)
        if not session:
            return {"error": "Invalid session ID"}
        
        # Generate code
        result = self.generation_pipeline.generate_code(description, use_rag=use_rag)
        result["session_id"] = session_id
        
        # Add to session history
        session.add_interaction(description, result)
        if result.get("code"):
            session.generated_codes.append(result["code"])
        
        # Save session
        self.save_session(session_id)
        
        return result
    
    def optimize_code_endpoint(self, code: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Part B: Optimize code.
        
        Args:
            code: Python source code
            session_id: Optional session ID
            
        Returns:
            Optimization results
        """
        # Create session if needed
        if not session_id:
            session_id = self.create_session()
        
        session = self.get_session(session_id)
        if not session:
            return {"error": "Invalid session ID"}
        
        # Optimize code
        result = self.optimization_pipeline.optimize_code(code)
        result["session_id"] = session_id
        
        # Add to session history
        session.add_interaction("optimize_code", result)
        
        # Save session
        self.save_session(session_id)
        
        return result


# ============================================================================
# CLI Interface
# ============================================================================

def run_cli():
    """Run command-line interface."""
    print("=" * 70)
    print("AI Code Assistant - CLI Mode")
    print("=" * 70)
    
    chatbot = ChatbotApplication()
    session_id = chatbot.create_session()
    
    while True:
        print("\nOptions:")
        print("1. Generate Code (Part A)")
        print("2. Optimize Code (Part B)")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            description = input("\nEnter code description: ").strip()
            if description:
                print("\nGenerating code...")
                result = chatbot.generate_code_endpoint(description, session_id)
                if result.get("code"):
                    print("\n" + "=" * 70)
                    print("Generated Code:")
                    print("=" * 70)
                    print(result["code"])
                    print("\n" + "=" * 70)
                    
                    if result.get("cfg_paths"):
                        print(f"✅ CFG saved: {len(result['cfg_paths'])} file(s)")
                    if result.get("dfg_paths"):
                        print(f"✅ DFG saved: {len(result['dfg_paths'])} file(s)")
                else:
                    print("\n❌ Code generation failed")
                    if result.get("errors"):
                        for error in result["errors"]:
                            print(f"  - {error}")
                    
        elif choice == "2":
            print("\nEnter Python code (end with a line containing only 'END'):")
            lines = []
            while True:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
            
            code = '\n'.join(lines)
            if code.strip():
                print("\nOptimizing code...")
                result = chatbot.optimize_code_endpoint(code, session_id)
                
                if result.get("success"):
                    print("\n" + "=" * 70)
                    print("Optimized Code:")
                    print("=" * 70)
                    print(result["optimized_code"])
                    print("\n" + "=" * 70)
                    
                    analysis = result.get("analysis", {})
                    if analysis.get("has_warnings"):
                        print(f"⚠️  Found {analysis['warning_count']} nested IF warning(s)")
                    else:
                        print("✅ No nested IF violations detected")
                else:
                    print("\n❌ Optimization failed")
                    if result.get("errors"):
                        for error in result["errors"]:
                            print(f"  Error: {error}")
            else:
                print("\n❌ No code provided")
                
        elif choice == "3":
            print("\nGoodbye!")
            break
        else:
            print("\n❌ Invalid choice")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "cli":
        run_cli()
    else:
        # Default: Show usage
        print("AI Code Assistant")
        print("=" * 70)
        print("\nUsage:")
        print("  python main.py cli              # Run CLI interface")
        print("  streamlit run streamlit_app.py  # Run Streamlit UI")
        print("  python demo.py                  # Run demo")
        print("\nDefaulting to CLI mode...\n")
        run_cli()
