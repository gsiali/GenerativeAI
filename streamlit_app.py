"""Streamlit App for Code Generation (Part A) and Code Optimization (Part B)."""

import streamlit as st
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'partA'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'partB'))

from llm_agent import LLMAgent
from rag_system import InMemoryRAG
from optimizer import CodeOptimizer

st.set_page_config(page_title="Python Code Assistant", page_icon="🐍", layout="wide")

# Initialize session state
defaults = {
    'conversation_history': [],
    'generated_code': "",
    'cfg_path': None,
    'dfg_path': None,
    'optimization_result': None,
    'processing': False
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

if 'agent' not in st.session_state:
    st.session_state.agent = LLMAgent()
if 'optimizer' not in st.session_state:
    st.session_state.optimizer = CodeOptimizer()

st.title("🐍 Python Code Assistant")
tab1, tab2 = st.tabs(["💬 Part A: Code Generation Chatbot", "⚡ Part B: Code Optimizer"])

# ===================== TAB 1: Chatbot =====================
with tab1:
    st.header("Code Generation Chatbot")
    col_chat, col_code, col_diagrams = st.columns(3)
    
    with col_chat:
        st.subheader("💬 Conversation")
        chat_container = st.container(height=400)
        with chat_container:
            for msg in st.session_state.conversation_history:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
        
        user_input = st.chat_input("Describe the Python function you want...", disabled=st.session_state.processing)
        
        if st.button("🗑️ Clear", use_container_width=True, disabled=st.session_state.processing):
            st.session_state.conversation_history = []
            st.session_state.generated_code = ""
            st.session_state.cfg_path = None
            st.session_state.dfg_path = None
            st.rerun()
        
        if user_input and not st.session_state.processing:
            st.session_state.processing = True
            st.session_state.conversation_history.append({"role": "user", "content": user_input})
            
            with st.spinner("Processing..."):
                result = st.session_state.agent.chat(
                    user_input,
                    conversation_history=st.session_state.conversation_history[:-1]
                )
                st.session_state.conversation_history.append({"role": "assistant", "content": result["chat_reply"]})
                st.session_state.generated_code = result["generated_code"] or st.session_state.generated_code
                st.session_state.cfg_path = result["cfg_path"] or st.session_state.cfg_path
                st.session_state.dfg_path = result["dfg_path"] or st.session_state.dfg_path
            
            st.session_state.processing = False
            st.rerun()
    
    with col_code:
        st.subheader("📝 Generated Code")
        with st.container(height=500):
            if st.session_state.generated_code:
                st.code(st.session_state.generated_code, language="python")
            else:
                st.info("Generated code will appear here...")
        if st.session_state.generated_code:
            st.download_button("📥 Download Code", st.session_state.generated_code, "generated_code.py", use_container_width=True)
    
    with col_diagrams:
        st.subheader("📊 Diagrams")
        with st.container(height=500):
            if st.session_state.cfg_path or st.session_state.dfg_path:
                if st.session_state.cfg_path and os.path.exists(st.session_state.cfg_path):
                    st.markdown("**Control Flow Graph (CFG)**")
                    st.image(st.session_state.cfg_path, use_container_width=True)
                if st.session_state.dfg_path and os.path.exists(st.session_state.dfg_path):
                    st.markdown("**Data Flow Graph (DFG)**")
                    st.image(st.session_state.dfg_path, use_container_width=True)
            else:
                st.info("CFG/DFG diagrams will appear here...")

# ===================== TAB 2: Optimizer =====================
with tab2:
    st.header("Code Optimizer")
    col_input, col_output = st.columns(2)
    
    with col_input:
        st.subheader("📥 Input Code")
        
        # File uploader
        uploaded_file = st.file_uploader("Upload a Python file (optional):", type=["py"])
        
        default_code = '''def check_conditions(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                if x > y:
                    if y > z:
                        return "All positive and descending"
    return "Conditions not met"'''
        
        # If file uploaded, use its content, otherwise use text area value
        if uploaded_file is not None:
            input_code = uploaded_file.read().decode("utf-8")
            st.text_area("Uploaded code:", value=input_code, height=400, disabled=True)
        else:
            input_code = st.text_area("Or paste your Python code:", value=default_code, height=400)
        
        if st.button("⚡ Optimize Code", type="primary", use_container_width=True):
            if input_code.strip():
                with st.spinner("Optimizing..."):
                    st.session_state.optimization_result = st.session_state.optimizer.optimize_code(input_code)
    
    with col_output:
        st.subheader("📤 Optimized Code")
        result = st.session_state.optimization_result
        if result:
            if result["success"]:
                st.code(result["optimized_code"], language="python")
                st.download_button("📥 Download", result["optimized_code"], "optimized_code.py", use_container_width=True)
            else:
                st.error(f"Optimization failed: {result['error']}")
        else:
            st.info("Optimized code will appear here...")

