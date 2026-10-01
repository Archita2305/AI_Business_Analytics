import streamlit as st
import pandas as pd
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

                    # Answer
                    st.success("Answer")
                    st.write(data["answer"])

                    # Chart
                    if data.get("chart_data"):

                            st.subheader("📊 Visualization")

                            chart_df = pd.DataFrame(data["chart_data"])

                            chart_type = data.get("chart_type")

                            # BAR
                            if chart_type == "bar":

                                st.bar_chart(
                                    chart_df.set_index("category")
                                )

                            # LINE
                            elif chart_type == "line":

                                chart_df["date"] = pd.to_datetime(chart_df["date"])

                                chart_df = chart_df.set_index("date")

                                st.line_chart(chart_df["value"])

                            # PIE
                            elif chart_type == "pie":

                                import matplotlib.pyplot as plt

                                fig, ax = plt.subplots()

                                ax.pie(
                                    chart_df["value"],
                                    labels=chart_df["category"],
                                    autopct="%1.1f%%",
                                    startangle=90
                                )

                                ax.set_title(data.get("chart_title", ""))

                                st.pyplot(fig)

                            # SCATTER
                            elif chart_type == "scatter":

                                st.scatter_chart(
                                    chart_df,
                                    x="quantity",
                                    y="sales"
                                )
                else:

                    st.error(
                        f"Error: {response.json().get('detail', 'Unknown error')}"
                    )

            except Exception:

                st.error(
                    "Could not connect to the FastAPI backend."
                )
