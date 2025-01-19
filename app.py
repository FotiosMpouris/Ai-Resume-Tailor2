# app.py

import streamlit as st
from main_functions import dummy_function

# Set the page configuration
st.set_page_config(page_title="AI Resume Tailor 2", page_icon="📄", layout="centered")

# Display a title
st.title("AI Resume Tailor 2")

# Display a simple test message
st.write("Testing the UI.")

# Call the dummy function and display its return value
st.write(dummy_function())
