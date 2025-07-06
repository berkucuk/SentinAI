# utils.py

import os
import subprocess
import google.generativeai as genai
from dotenv import load_dotenv

def initialize_gemini():
    """
    Loads environment variables and configures the Gemini API.
    Returns the generative model instance.
    Raises ValueError if API key is not found.
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Error: GOOGLE_API_KEY not found. Please check your .env file.")
    print(api_key)
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    return model

def check_tool_installed(tool_name):
    """Checks if a command-line tool is installed and available in PATH."""
    try:
        subprocess.run([tool_name, "--help"], check=True, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False