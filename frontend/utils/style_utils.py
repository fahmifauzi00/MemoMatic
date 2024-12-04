import os
import streamlit as st

def load_css():
    """Load and inject CSS styles into Streamlit"""
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'css', 'styles.css')
    if not os.path.exists(css_file):
        raise FileNotFoundError(f"CSS file not found at {css_file}")
        
    with open(css_file, 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)