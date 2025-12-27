import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/query"

st.set_page_config(
    page_title="Legal GraphRAG – GDPR",
    layout="centered"
)

st.title("⚖️ Legal GraphRAG – GDPR Explorer")
st.markdown(
    "Ask questions about the **GDPR** using a **Graph + Vector RAG** system."
)

query = st.text_area(
    "Enter your legal question:",
    placeholder="Ex: Qu’est-ce qu’une donnée à caractère personnel ?",
    height=120
)

if st.button("Ask"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Querying knowledge graph and documents..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"query": query},
                    timeout=60
                )
                response.raise_for_status()
                answer = response.json()["answer"]

                st.success("Answer")
                st.write(answer)

            except Exception as e:
                st.error(f"Error: {e}")
