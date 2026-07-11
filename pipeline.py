# The conductor. This file doesn't do any "thinking" itself — it just runs the
# four stages in order and passes each stage's output along to the next one.
from langchain_core.messages import HumanMessage
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

def run_research_pipeline(topic: str, progress=None) -> dict:
    """Run the 4-stage research pipeline.

    Args:
        topic: The research topic.
        progress: Optional callback ``progress(message: str)`` invoked before
            each stage so a UI can display real-time status. Defaults to no-op.
    """
    # If nobody passed a progress callback (e.g. running from the terminal),
    # swap in a do-nothing function so the calls below don't crash.
    if progress is None:
        progress = lambda _msg: None

    # One plain dict carries everything forward: each stage writes its result
    # here and later stages read from it. Simple and easy to inspect.
    state = {}

    # --- Step 1: find sources ---
    progress("Step 1: Search Agent is working...")
    print("\n" + "="*50)
    print("Step 1: Search Agent is working ...")
    print("="*50)

    search_agent = build_search_agent()

    # Kick off the agent with the user's topic. We wrap the text in a HumanMessage
    # object (rather than a plain tuple) so the types line up and Pylance stays happy.
    search_result = search_agent.invoke({
        "messages": [
            HumanMessage(content=f"Find recent, reliable and detailed information on the topic: {topic}")
        ]
    })

    # The agent hands back its whole message history; [-1] is its final answer.
    state['search_result'] = search_result['messages'][-1].content

    print("\n search result: \n", state['search_result'])

    # --- Step 2: read the best source in depth ---
    progress("Step 2: Reader Agent is scraping the resources...")
    print("\n" + "="*50)
    print("Step 2: Reader Agent is scraping the resources ...")
    print("="*50)

    reader_agent = build_reader_agent()
    # We only feed it the first 800 chars of the search results — that's plenty
    # for it to pick a good URL, and it keeps the prompt short.
    reader_result = reader_agent.invoke({
        "messages": [
            HumanMessage(content=f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_result'][:800]}")
        ]
    })

    state['scraped_content'] = reader_result['messages'][-1].content

    print("\nscraped content: \n", state['scraped_content'])


    # --- Step 3: write the report ---
    progress("Step 3: Writer Chain is drafting the report...")
    print("\n" + "="*50)
    print("Step 3: Writer Chain is drafting the report ...")
    print("="*50)

    # Hand the writer both the search summary AND the deep-scraped page, clearly
    # labelled so it knows which is which.
    research_combined = (
        f"SEARCH RESULTS:\n{state['search_result']}\n\n"
        f"DETAILED SCRAPEd CONTENT:\n{state['scraped_content']}\n\n"
    )

    report = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    state['report'] = report

    print("\nFinal Report: \n", state['report'])


    # --- Step 4: grade the report ---
    progress("Step 4: Critic Chain is evaluating the report...")
    print("\n" + "="*50)
    print("Step 4: Critic Chain is evaluating the report ...")
    print("="*50)

    # The critic only needs the finished report — not the raw research.
    critic_result = critic_chain.invoke({
        "report": state['report']
    })

    state['feedback'] = critic_result
    print("\nCritic Evaluation: \n", state['feedback'])


    # Everything the UI needs (report, critique, and the raw logs) lives in state.
    return state



# Lets you run the whole thing straight from the terminal for a quick test,
# without needing to spin up the Streamlit app.
if __name__ == "__main__":
    topic = input("Enter the research topic: ")
    run_research_pipeline(topic)


