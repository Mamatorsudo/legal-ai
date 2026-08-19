import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load API key from environment or Streamlit secrets
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Missing GEMINI_API_KEY. Please add it to your .env file or Streamlit Secrets.")
    st.stop()

# Initialize Gemini client
client = genai.Client(api_key=api_key)

# Page Configuration
st.set_page_config(page_title="Judicial AI Assistant", page_icon="⚖️", layout="centered")
st.title("⚖️ Judicial & Legal AI Assistant")
st.caption("Powered by Gemini • For legal research and statutory analysis")

# Define Judicial System Instructions
SYSTEM_INSTRUCTION = """
You are an expert Judicial and Legal AI Assistant.
When answering legal questions:
1. Provide structured analysis: Issue, Applicable Law, Legal Analysis, and Conclusion.
2. Reference statutory frameworks and case precedents clearly.
3. If specific jurisdictions are specified (e.g., Ghana, UK, US), tailor analysis to those rules.
4. Always conclude with a disclaimer that answers serve as research aids, not formal legal advice.
"""

# Initialize Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask a legal or judicial question..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI Response with Streaming (Fast Response)
    with st.chat_message("assistant"):
        try:
            # Build conversation history
            contents = [
                types.Content(
                    role=m["role"],
                    parts=[types.Part.from_text(text=m["content"])]
                ) for m in st.session_state.messages
            ]

            # Stream response chunks directly as they arrive
            response_stream = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2,
                )
            )

            # Render text in real time
            full_response = st.write_stream(chunk.text for chunk in response_stream)

            # Save assistant response to memory
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error generating response: {e}")