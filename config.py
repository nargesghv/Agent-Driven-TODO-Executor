"""
Configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
# Get your API key from: https://platform.openai.com/api-keys
# IMPORTANT: Set your API key in the .env file or as an environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# If no API key is found, show a helpful error message
if not OPENAI_API_KEY:
    print("=" * 60)
    print(" WARNING: OPENAI_API_KEY not found")
    print("=" * 60)
    print("Please set your API key in one of these ways:")
    print("1. Create a .env file with: OPENAI_API_KEY=your-key-here")
    print("2. Set environment variable: export OPENAI_API_KEY=your-key-here")
    print("=" * 60)

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "")

# Agent Configuration
MAX_RETRIES = 3
TEMPERATURE = 0.7
MAX_TOKENS = 4000
