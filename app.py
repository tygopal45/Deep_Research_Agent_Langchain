# The front door. Streamlit turns this plain Python script into a web app —
# no HTML or JavaScript needed. All the heavy lifting lives in pipeline.py.
import streamlit as st
from pipeline import run_research_pipeline

# Title, icon and a wide layout so the report has room to breathe.
st.set_page_config(page_title="AI Research Assistant", page_icon="🔍", layout="wide")

def main():
    st.title("🔍 Multi-Agent Research System")
    st.markdown("Enter a topic below to trigger the specialized agentic workflow.")

    # A little "how it works" panel on the left so users know what's happening.
    with st.sidebar:
        st.header("About")
        st.info(
            "This system utilizes a multi-agent pipeline:\n"
            "1. **Search Agent**: Finds reliable sources.\n"
            "2. **Reader Agent**: Scrapes deep content.\n"
            "3. **Writer Agent**: Drafts the structured report.\n"
            "4. **Critic Agent**: Provides quality feedback."
        )

    # The one input the whole app revolves around.
    topic = st.text_input("What would you like me to research?", placeholder="e.g., The impact of quantum computing on cybersecurity")

    if st.button("Start Research"):
        # Don't bother running the pipeline on an empty box — just nudge the user.
        if not topic:
            st.warning("Please enter a topic first.")
            return

        # st.status gives us a live "Researching..." box. We hand the pipeline a
        # tiny progress() callback so each stage can report in as it starts —
        # that way the updates are real, not just decorative.
        with st.status("Researching...", expanded=True) as status:

            def progress(message: str):
                st.write(message)

            # The pipeline touches the network and the LLM, so anything can go
            # wrong (bad key, rate limit, dead link). Catch it and show a friendly
            # error instead of a scary stack trace / blank screen.
            try:
                results = run_research_pipeline(topic, progress=progress)
                status.update(label="Research Complete!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="Research Failed", state="error")
                st.error(f"An error occurred: {e}")
                return

        # --- Show everything the pipeline gave us ---

        # The report is the star of the show, so it goes up top in full.
        st.header("📋 Final Research Report")
        st.markdown(results['report'])

        st.divider()

        # The critique is secondary — tuck it in a collapsible expander.
        with st.expander("⭐ Critic Evaluation"):
            st.markdown(results['feedback'])

        # The raw research data, for the curious. Two columns side by side so you
        # can peek at exactly what the search and reader agents pulled in.
        st.subheader("🛠️ Research Logs")
        col1, col2 = st.columns(2)

        with col1:
            with st.expander("Raw Search Results"):
                st.write(results['search_result'])

        with col2:
            with st.expander("Scraped Content"):
                st.write(results['scraped_content'])

if __name__ == "__main__":
    main()