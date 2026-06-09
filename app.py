import streamlit as st
import io
import contextlib
import sys
from rich.console import Console

# Import your existing main logic
from main import main as run_oba_analysis

# Page Config
st.set_page_config(page_title="OBA Core — 10 Modules Terminal View", layout="wide")

# Custom CSS to make it look like a gorgeous developer terminal
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    .terminal-container {
        background-color: #000000;
        color: #ffffff;
        font-family: 'Courier New', Courier, monospace;
        padding: 25px;
        border-radius: 8px;
        border: 1px solid #333;
        white-space: pre-wrap;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Control Panel
with st.sidebar:
    st.title("🧠 OBA Core Engine")
    st.markdown("Horquva Workforce Intelligence Platform")
    st.info("Status: 10 Modules Deployed Successfully.")
    
    # Simple Trigger Button
    run_btn = st.button("🚀 Run Live Engine Simulation", type="primary", use_container_width=True)

st.title("🖥️ OBA Core Live Terminal Interface")
st.markdown("Click the sidebar button to execute the 10-module graph validation live for **Sunrise Care**.")

if run_btn:
    with st.spinner("Analyzing AI Agent Architecture, Cascade Risks & Knowledge Preservation..."):
        # Catch all the terminal output (including ANSI colors from Rich)
        output_buffer = io.StringIO()
        
        # Force Rich to render in HTML/ANSI instead of dropping styles
        console = Console(file=output_buffer, force_terminal=True, color_system="truecolor", width=120)
        
        # Monkeypatch the terminal printer temporarily
        import main
        original_console = main.console
        main.console = console
        
        try:
            with contextlib.redirect_stdout(output_buffer):
                run_oba_analysis()
        except Exception as e:
            st.error(f"Execution Error: {str(e)}")
        finally:
            # Restore original state
            main.console = original_console
        
        # Fetch the formatted string
        raw_output = output_buffer.getvalue()
        
        # Convert ANSI terminal colors into clean HTML tags for Streamlit display
        import re
        def ansi_to_html(text):
            # Simple escape for safety
            text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            # Basic map for ANSI color codes from Rich logger
            ansi_codes = {
                r'\x1b\[31m': '<span style="color:#ff5555; font-weight:bold;">', # Red
                r'\x1b\[32m': '<span style="color:#50fa7b; font-weight:bold;">', # Green
                r'\x1b\[33m': '<span style="color:#f1fa8c;">', # Yellow
                r'\x1b\[34m': '<span style="color:#bd93f9;">', # Blue/Purple
                r'\x1b\[36m': '<span style="color:#8be9fd;">', # Cyan
                r'\x1b\[1m': '<span style="font-weight:bold;">',  # Bold
                r'\x1b\[0m': '</span>',                          # Reset
                r'\x1b\[39m': '</span>',
                r'\x1b\[49m': '</span>'
            }
            # Clean up unwanted control codes that muddy the UI
            text = re.sub(r'\x1b\[[0-9;]*m', '', raw_output) 
            return text

        clean_html_output = ansi_to_html(raw_output)
        
        # Render the beautiful terminal look
        st.markdown(f'<div class="terminal-container">{clean_html_output}</div>', unsafe_allow_html=True)
        st.balloons()
