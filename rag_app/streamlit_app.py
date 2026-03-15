"""Streamlit UI for the RAG Intent Classifier."""

import requests
import streamlit as st

st.set_page_config(
    page_title="RAG Intent Classifier",
    page_icon="🔍",
    layout="wide",
)

# Sidebar configuration
st.sidebar.title("Settings")

api_url = st.sidebar.text_input(
    "FastAPI Backend URL",
    value="http://localhost:8000",
    help="URL of the FastAPI backend service",
)

top_k = st.sidebar.slider(
    "Top K Documents to Retrieve",
    min_value=1,
    max_value=20,
    value=1,
    step=1,
    help="Number of top matching utterances to retrieve using hybrid search (BM25 + Vector)",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **About**

    This application uses a **Hybrid RAG** approach combining:
    - **BM25** (keyword-based retrieval)
    - **Vector Search** (semantic similarity via ChromaDB)

    The system searches utterances and returns the most likely **intent**
    using an LLM (Gemini Flash / OpenAI GPT).
    """
)

# Main content
st.title("Hybrid RAG Intent Classifier")
st.markdown(
    "Enter a query below to classify its intent using hybrid search "
    "(BM25 + Vector similarity) over utterance-intent pairs."
)

# Query input
user_query = st.text_input(
    "Enter your query:",
    placeholder="e.g., I want to check how much money is in my account",
)

if st.button("Classify Intent", type="primary", disabled=not user_query):
    if not user_query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Classifying intent..."):
            try:
                response = requests.post(
                    f"{api_url.rstrip('/')}/classify",
                    json={"query": user_query, "top_k": top_k},
                    timeout=30,
                )

                if response.status_code == 200:
                    data = response.json()

                    # Display predicted intent
                    st.success(f"**Predicted Intent:** `{data['predicted_intent']}`")

                    # Display retrieved utterances
                    st.subheader(f"Top {data['top_k']} Retrieved Utterance(s)")

                    for i, item in enumerate(data["retrieved_utterances"], 1):
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{i}.** {item['utterance']}")
                            with col2:
                                st.markdown(f"Intent: `{item['intent']}`")
                else:
                    st.error(
                        f"API Error (HTTP {response.status_code}): "
                        f"{response.json().get('detail', 'Unknown error')}"
                    )
            except requests.exceptions.ConnectionError:
                st.error(
                    f"Cannot connect to the API at `{api_url}`. "
                    "Make sure the FastAPI backend is running."
                )
            except requests.exceptions.Timeout:
                st.error("Request timed out. Please try again.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# Example queries section
with st.expander("Example Queries"):
    examples = [
        "I want to check how much money is in my account",
        "Can you help me cancel my recent purchase?",
        "My app keeps crashing, what should I do?",
        "I'd like to schedule a meeting for tomorrow",
        "Hello, how are you doing today?",
        "I need to get my money back for this order",
        "Where is my package right now?",
        "I forgot my login password",
        "Tell me about the products you sell",
        "I'm really unhappy with your service",
    ]
    for ex in examples:
        st.code(ex, language=None)
