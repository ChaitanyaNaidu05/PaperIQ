import os
import logging
from google import genai
from google.genai import types
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_client():
    """
    Initialize and return the Gemini API client.
    """
    api_key = None
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    elif os.environ.get("GEMINI_API_KEY"):
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        logger.error("Gemini API key not found in secrets or environment variables.")
        return None
    
    return genai.Client(api_key=api_key)

def get_chat_response(context: str, chat_history: list, user_message: str):
    """
    Generate a chat response using the new Google GenAI SDK based on the document context and chat history.
    """
    client = get_client()
    if not client:
        return "Error: Gemini API key is missing. Please configure it in .streamlit/secrets.toml or as an environment variable."

    try:
        system_instruction = f"""
You are an expert AI research assistant named PaperIQ. 
Your goal is to answer the user's questions strictly based on the provided document context. 
If the answer is not contained within the document, state that clearly instead of guessing.

--- DOCUMENT CONTEXT ---
{context}
--- END CONTEXT ---
"""
        # Format history for the new SDK
        # The new SDK expects a list of types.Content objects or equivalent dicts
        history = []
        for msg in chat_history:
            role = "user" if msg["role"] == "user" else "model"
            history.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
        
        # Create a chat session with the system instruction
        chat = client.chats.create(
            model='gemini-3-flash-preview',
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
            ),
            history=history
        )
        
        response = chat.send_message(user_message)
        return response.text

    except Exception as e:
        logger.error(f"Error communicating with Gemini API: {e}")
        return f"Error connecting to Gemini API: {str(e)}"
