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
                "include_citations": include_citations,
                "user_id": "test-user"  # Required field
            }
        )
        if response.status_code == 200 or response.status_code == 202:
            job_id = response.json()["job_id"]
            st.success(f"Job submitted! Job ID: {job_id}")
            st.write("Polling for results...")

            while True:
                status_response = requests.get(
                    f"http://localhost:8000/api/v1/research/{job_id}/status"
                )
                data = status_response.json()
                st.write(f"Status: {data['status']}")
                if data["status"] == "completed":
                    # Fetch full job details (not just status) to get summary/citations
                    full_response = requests.get(f"http://localhost:8000/api/v1/research/{job_id}")
                    if full_response.status_code == 200:
                        full = full_response.json()
                        st.success("Research complete!")
                        st.write("### Summary")
                        st.write(full.get("summary") or full.get("report_data", {}).get("executive_summary", "No summary available."))
                        if full.get("google_doc_url"):
                            st.markdown(f"[View Google Doc]({full.get('google_doc_url')})")
                        if full.get("report_data") and full.get("report_data").get("citations"):
                            st.write("### Citations")
                            for i, citation in enumerate(full.get("report_data").get("citations"), 1):
                                st.write(f"{i}. {citation.get('title', '')} ({citation.get('url', '')})")
                    else:
                        st.error("Failed to fetch full job results")
                    break
                elif data["status"] == "failed":
                    st.error(f"Error: {data.get('error_message', 'Unknown error')}")
                    break
                time.sleep(3)
        else:
            st.error("Failed to submit research job. Please check your backend server.")

st.info("Make sure your backend is running at http://localhost:8000")
