from langchain_core.messages import HumanMessage
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

def run_research_pipeline(topic: str) -> dict:
    state = {}

    print("\n" + "="*50)
    print("Step 1: Search Agent is working ...")
    print("="*50)

    search_agent = build_search_agent()
    
    # Use HumanMessage object instead of a tuple to satisfy Pylance
    search_result = search_agent.invoke({
        "messages": [
            HumanMessage(content=f"Find recent, reliable and detailed information on the topic: {topic}")
        ]
    })
    
    state['search_result'] = search_result['messages'][-1].content

    print("\n search result: \n", state['search_result'])

    # step 2: reader agent
    print("\n" + "="*50)
    print("Step 2: Reader Agent is scraping the resources ...")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [
            HumanMessage(content=f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_result'][:800]}")
        ]
    })

    state['scraped_content'] = reader_result['messages'][-1].content

    print("\nscraped content: \n", state['scraped_content'])


    # step 3: writer chain
    print("\n" + "="*50)
    print("Step 3: Writer Chain is drafting the report ...")
    print("="*50)

    # combining search and reader results for the writer chain
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


    # step 4: critic report
    print("\n" + "="*50)
    print("Step 4: Critic Chain is evaluating the report ...")
    print("="*50)

    critic_result = critic_chain.invoke({
        "report": state['report']
    })

    state['feedback'] = critic_result
    print("\nCritic Evaluation: \n", state['feedback'])


    return state



if __name__ == "__main__":
    topic = input("Enter the research topic: ")
    run_research_pipeline(topic)


