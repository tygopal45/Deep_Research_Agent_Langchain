import streamlit as st
from pipeline import run_research_pipeline

# Page configuration
st.set_page_config(page_title="AI Research Assistant", page_icon="🔍", layout="wide")

def main():
    st.title("🔍 Multi-Agent Research System")
    st.markdown("Enter a topic below to trigger the specialized agentic workflow.")

    # Sidebar for configuration or info
    with st.sidebar:
        st.header("About")
        st.info(
            "This system utilizes a multi-agent pipeline:\n"
            "1. **Search Agent**: Finds reliable sources.\n"
            "2. **Reader Agent**: Scrapes deep content.\n"
            "3. **Writer Agent**: Drafts the structured report.\n"
            "4. **Critic Agent**: Provides quality feedback."
        )

    # User Input
    topic = st.text_input("What would you like me to research?", placeholder="e.g., The impact of quantum computing on cybersecurity")
    
    if st.button("Start Research"):
        if not topic:
            st.warning("Please enter a topic first.")
            return

        # Initialize progress tracking
        with st.status("Researching...", expanded=True) as status:
            
            # Step 1: Search
            st.write("Step 1: Search Agent is working...")
            # We will call the function but modify how we display progress
            # For a better UI, we might want to refactor run_research_pipeline 
            # to yield updates, but for now, we'll run it and display results.
            
            try:
                results = run_research_pipeline(topic)
                status.update(label="Research Complete!", state="complete", expanded=False)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                return

        # --- Displaying Results ---
        
        # 1. Final Report (Primary Output)
        st.header("📋 Final Research Report")
        st.markdown(results['report'])
        
        st.divider()

        # 2. Critic Feedback
        with st.expander("⭐ Critic Evaluation"):
            st.markdown(results['feedback'])

        # 3. Technical Logs (Research Data)
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