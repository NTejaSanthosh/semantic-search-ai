
import streamlit as st

st.set_page_config(
    page_title="Semantic Search AI",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 Semantic Search AI")
st.write("Search your knowledge base and upload documents.")

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Search", "Upload Documents"]
)

if page == "Home":
    st.header("Welcome")
    st.info("Your Semantic Search AI interface is running.")
    st.write("Use the sidebar to navigate between pages.")

elif page == "Search":
    st.header("Ask a Question")
    question = st.text_area(
        "Enter your question",
        placeholder="Ask something about your documents..."
    )

    if st.button("Search", type="primary"):
        if question.strip():
            st.warning(
                "The interface is ready. "
                "Backend search connection still needs to be configured."
            )
        else:
            st.error("Please enter a question.")

elif page == "Upload Documents":
    st.header("Upload Documents")
    files = st.file_uploader(
        "Select PDF, DOCX, or TXT files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

    if files:
        st.write(f"Selected {len(files)} file(s).")
        for file in files:
            st.write(f"📄 {file.name}")

st.divider()
st.caption("Semantic Search AI | Streamlit")
