import streamlit as st
import requests
import time

st.title("LangChain Research Agent")

query = st.text_input("Enter your research question:")
max_results = st.slider("Number of results", 1, 20, 5)
include_citations = st.checkbox("Include citations", value=True)

if st.button("Start Research"):
    with st.spinner("Submitting your research job..."):
        response = requests.post(
            "http://localhost:8000/api/v1/research",
            json={
                "query": query,
                "max_results": max_results,
                "include_citations": include_citations
            }
        )
        if response.status_code == 200 or response.status_code == 202:
            job_id = response.json()["job_id"]
            st.success(f"Job submitted! Job ID: {job_id}")
            st.write("Polling for results...")

            while True:
                status_response = requests.get(
                    f"http://localhost:8000/api/v1/research/{job_id}"
                )
                data = status_response.json()
                st.write(f"Status: {data['status']}")
                if data["status"] == "completed":
                    st.success("Research complete!")
                    st.write("### Summary")
                    st.write(data.get("summary", "No summary available."))
                    if "google_doc_url" in data and data["google_doc_url"]:
                        st.markdown(f"[View Google Doc]({data['google_doc_url']})")
                    if "citations" in data and data["citations"]:
                        st.write("### Citations")
                        for i, citation in enumerate(data["citations"], 1):
                            st.write(f"{i}. {citation.get('title', '')} ({citation.get('url', '')})")
                    break
                elif data["status"] == "failed":
                    st.error(f"Error: {data.get('error_message', 'Unknown error')}")
                    break
                time.sleep(3)
        else:
            st.error("Failed to submit research job. Please check your backend server.")

st.info("Make sure your backend is running at http://localhost:8000")
