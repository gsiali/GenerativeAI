"""
Streamlit Web Application
Interactive UI for AI Code Assistant chatbot
"""

import streamlit as st
import sys
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main import ChatbotApplication

# Page configuration
st.set_page_config(
    page_title="AI Code Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chatbot' not in st.session_state:
    with st.spinner("🚀 Initializing AI models... Please wait..."):
        try:
            st.session_state.chatbot = ChatbotApplication()
            st.session_state.session_id = st.session_state.chatbot.create_session()
            st.session_state.initialized = True
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {e}")
            st.stop()

if 'generation_history' not in st.session_state:
    st.session_state.generation_history = []

if 'optimization_history' not in st.session_state:
    st.session_state.optimization_history = []

# Header
st.markdown('<div class="main-header">🤖 AI Code Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Generate and optimize Python code with AI-powered analysis</div>', unsafe_allow_html=True)

# Main content - Tabs
tab1, tab2, tab3 = st.tabs([
    "📝 Code Generation (Part A)",
    "⚙️ Code Optimization (Part B)",
    "📜 History"
])

# ============================================================================
# Tab 1: Code Generation
# ============================================================================
with tab1:
    st.header("Generate Python Code")
    st.markdown("Describe what you want to code, and AI will generate it with analysis.")
    
    description = st.text_area(
        "Code Description",
        placeholder="Example: Create a function to implement binary search on a sorted array",
        height=150,
        key="gen_description"
    )
    
    # Always use RAG for Part A
    use_rag = True
    
    col1, col2 = st.columns([3, 1])
    with col1:
        generate_btn = st.button("🚀 Generate Code", type="primary", width="stretch")
    with col2:
        if st.button("🔄 Clear", width="stretch"):
            st.rerun()
    
    if generate_btn:
        if not description.strip():
            st.warning("⚠️ Please enter a code description")
        else:
            with st.spinner("🔄 Generating code... This may take a moment..."):
                try:
                    result = st.session_state.chatbot.generate_code_endpoint(
                        description=description,
                        session_id=st.session_state.session_id,
                        use_rag=use_rag
                    )
                    
                    # Store in history
                    st.session_state.generation_history.append({
                        "description": description,
                        "result": result
                    })
                    
                    if result.get("code"):
                        st.success("✅ Code generated successfully!")
                        
                        # Display generated code
                        st.subheader("Generated Code")
                        st.code(result["code"], language="python", line_numbers=True)
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Code",
                            data=result["code"],
                            file_name="generated_code.py",
                            mime="text/x-python"
                        )
                        
                        # Display context functions
                        if result.get("context_functions"):
                            with st.expander("📚 Retrieved Context Functions from RAG", expanded=False):
                                st.write(f"Found {len(result['context_functions'])} relevant functions:")
                                for i, func in enumerate(result["context_functions"], 1):
                                    st.text_area(f"Function {i}", func, height=100, key=f"ctx_{i}")
                        
                        # Display CFGs and DFGs
                        if result.get("cfg_paths") or result.get("dfg_paths"):
                            st.subheader("📊 Visual Analysis")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if result.get("cfg_paths"):
                                    st.write("**Control Flow Graphs**")
                                    for func_name, path in result["cfg_paths"].items():
                                        try:
                                            st.image(path, caption=f"CFG: {func_name}", width="stretch")
                                        except Exception as e:
                                            st.error(f"Error displaying CFG: {e}")
                            
                            with col2:
                                if result.get("dfg_paths"):
                                    st.write("**Data Flow Graphs**")
                                    for func_name, path in result["dfg_paths"].items():
                                        try:
                                            st.image(path, caption=f"DFG: {func_name}", width="stretch")
                                        except Exception as e:
                                            st.error(f"Error displaying DFG: {e}")
                        
                        # Display errors/warnings
                        if result.get("errors"):
                            with st.expander("⚠️ Warnings", expanded=False):
                                for error in result["errors"]:
                                    st.warning(error)
                    else:
                        st.error("❌ Failed to generate code")
                        if result.get("errors"):
                            for error in result["errors"]:
                                st.error(error)
                
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ============================================================================
# Tab 2: Code Optimization
# ============================================================================
with tab2:
    st.header("Optimize Python Code")
    st.markdown("Upload or paste Python code to optimize it with AI-powered analysis.")
    
    # Input method selection
    input_method = st.radio(
        "Input Method",
        ["📝 Paste Code", "📁 Upload File"],
        horizontal=True,
        key="input_method"
    )
    
    code_input = None
    
    if input_method == "📝 Paste Code":
        code_input = st.text_area(
            "Python Code",
            placeholder="Paste your Python code here...",
            height=300,
            key="opt_code_input"
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload Python File",
            type=["py"],
            key="uploaded_file"
        )
        if uploaded_file:
            code_input = uploaded_file.read().decode("utf-8")
            with st.expander("📄 Uploaded Code", expanded=True):
                st.code(code_input, language="python", line_numbers=True)
    
    st.divider()
    
    # Action buttons
    col1, col2 = st.columns([3, 1])
    with col1:
        optimize_btn = st.button("⚙️ Optimize Code", type="primary", width="stretch")
    with col2:
        if st.button("🔄 Clear", width="stretch", key="opt_clear"):
            st.rerun()
    
    if optimize_btn:
        if not code_input or not code_input.strip():
            st.warning("⚠️ Please provide Python code to optimize")
        else:
            with st.spinner("⚙️ Optimizing code with AI... This may take a moment..."):
                try:
                    result = st.session_state.chatbot.optimize_code_endpoint(
                        code=code_input,
                        session_id=st.session_state.session_id
                    )
                    
                    # Store in history
                    st.session_state.optimization_history.append({
                        "original": code_input,
                        "result": result
                    })
                    
                    if result.get("success"):
                        st.success("✅ Code optimization completed!")
                        
                        # Display side-by-side comparison
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Original Code")
                            st.code(result["original_code"], language="python", line_numbers=True)
                        
                        with col2:
                            st.subheader("Optimized Code")
                            st.code(result["optimized_code"], language="python", line_numbers=True)
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Optimized Code",
                            data=result["optimized_code"],
                            file_name="optimized_code.py",
                            mime="text/x-python"
                        )
                        
                        # Analysis
                        analysis = result.get("analysis", {})
                        
                        st.subheader("📊 Optimization Analysis")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                "Warnings Found",
                                analysis.get("warning_count", 0),
                                delta="Issues" if analysis.get("has_warnings") else "Clean"
                            )
                        with col2:
                            st.metric(
                                "Lines Added",
                                analysis.get("lines_added", 0),
                                delta="Modified"
                            )
                        with col3:
                            st.metric(
                                "Original Lines",
                                analysis.get("line_count_original", 0)
                            )
                        
                        # Show warnings if any
                        if analysis.get("has_warnings"):
                            st.warning(f"⚠️ Found {analysis['warning_count']} nested IF statement(s) exceeding depth limit of 3")
                            st.info("💡 **Tip:** Consider refactoring deep nesting using early returns, guard clauses, or extracting methods.")
                        else:
                            st.success("✅ No code quality issues detected!")
                        
                        # Display errors
                        if result.get("errors"):
                            with st.expander("⚠️ Warnings/Errors", expanded=False):
                                for error in result["errors"]:
                                    st.warning(error)
                    else:
                        st.error("❌ Optimization failed")
                        if result.get("errors"):
                            for error in result["errors"]:
                                st.error(error)
                
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())

# ============================================================================
# Tab 3: History
# ============================================================================
with tab3:
    st.header("📋 Session History")
    
    # Session info and controls at the top
    info_col, btn_col = st.columns([3, 1])
    with info_col:
        st.info(f"🔑 **Session ID:** `{st.session_state.session_id}`")
    with btn_col:
        if st.button("🗑️ Clear History", width="stretch", type="secondary"):
            st.session_state.generation_history = []
            st.session_state.optimization_history = []
            st.success("History cleared!")
            st.rerun()
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Code Generations")
        if st.session_state.generation_history:
            for i, item in enumerate(reversed(st.session_state.generation_history), 1):
                with st.expander(f"Generation {len(st.session_state.generation_history) - i + 1}: {item['description'][:50]}...", expanded=False):
                    st.write("**Description:**")
                    st.info(item['description'])
                    
                    if item['result'].get('code'):
                        st.write("**Generated Code:**")
                        st.code(item['result']['code'], language="python")
                        
                        if item['result'].get('cfg_paths'):
                            st.write(f"**CFG:** {', '.join(item['result']['cfg_paths'].keys())}")
                        if item['result'].get('dfg_paths'):
                            st.write(f"**DFG:** {', '.join(item['result']['dfg_paths'].keys())}")
        else:
            st.info("No code generations yet. Go to the Code Generation tab to get started!")
    
    with col2:
        st.subheader("⚙️ Code Optimizations")
        if st.session_state.optimization_history:
            for i, item in enumerate(reversed(st.session_state.optimization_history), 1):
                with st.expander(f"Optimization {len(st.session_state.optimization_history) - i + 1}", expanded=False):
                    if item['result'].get('success'):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write("**Original:**")
                            st.code(item['original'][:200] + "..." if len(item['original']) > 200 else item['original'], language="python")
                        with col_b:
                            st.write("**Optimized:**")
                            st.code(item['result']['optimized_code'][:200] + "..." if len(item['result']['optimized_code']) > 200 else item['result']['optimized_code'], language="python")
                        
                        analysis = item['result'].get('analysis', {})
                        if analysis.get('has_warnings'):
                            st.warning(f"Found {analysis['warning_count']} warning(s)")
        else:
            st.info("No code optimizations yet. Go to the Code Optimization tab to get started!")
    
    st.divider()
    
    # Export options
    st.subheader("💾 Export Session")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Download Session JSON", width="stretch"):
            import json
            session = st.session_state.chatbot.get_session(st.session_state.session_id)
            if session:
                session_json = json.dumps(session.to_dict(), indent=2)
                st.download_button(
                    label="Download",
                    data=session_json,
                    file_name=f"session_{st.session_state.session_id}.json",
                    mime="application/json"
                )
    
    with col2:
        if st.button("🔄 Start New Session", width="stretch"):
            st.session_state.session_id = st.session_state.chatbot.create_session()
            st.session_state.generation_history = []
            st.session_state.optimization_history = []
            st.success("New session started!")
            st.rerun()
