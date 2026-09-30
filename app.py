import streamlit as st
import requests

st.set_page_config(
    page_title="AI Business Analytics",
    page_icon="📊",
    layout="wide"
)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #000080;
    }
    title {
        color: #c0c0c0;
    }

    subheader {
    color: #fff8dc !important;
    }

    .stButton > button {
    background-color: #4F46E5 !important;
    color: white !important;
    border-radius: 8px;
    border: none;
    }

    .stButton > button:hover {
    background-color: #3730A3 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.title("📊 AI Business Analytics")
st.subheader("Decision Support Dashboard")

st.write(
    "Ask questions about sales, business policies, "
    "or request data-driven recommendations."
)

question = st.text_area(
    "Ask a business question",
    placeholder="Example: Which region generated the highest sales?",
    height=100
)

if st.button("Ask Question"):

    if not question.strip():
        st.warning("Please enter a question.")

    else:

        with st.spinner("Analyzing..."):

            try:

                response = requests.post(
                    "http://127.0.0.1:8000/ask",
                    json={
                        "question": question
                    }
                )

                if response.status_code == 200:

                    data = response.json()

                    st.success("Answer")

                    st.write(data["answer"])

                    st.caption(
                        f"Source: {data.get('source', 'agent')}"
                    )

                else:

                    st.error(
                        f"Error: {response.json().get('detail', 'Unknown error')}"
                    )

            except Exception as e:

                st.error(
                    "Could not connect to the FastAPI backend."
                )