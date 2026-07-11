# This file is the "brains" of the project: the shared LLM, the two tool-using
# agents (search + reader), and the two text-only chains (writer + critic).
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import web_search, scrape_url
from dotenv import load_dotenv
import os

load_dotenv()

# Same idea as in tools.py — bail out early with a clear message if the key is missing.
if not os.getenv("GOOGLE_API_KEY"):
    raise EnvironmentError(
        "GOOGLE_API_KEY is not set. Add it to your .env file "
        "(get a key at https://aistudio.google.com/apikey)."
    )

# One LLM instance shared by every agent and chain below.
# temperature=0 -> deterministic, factual answers. We want reliable research,
# not creative writing, so we turn the "creativity" dial all the way down.
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)


# --- Agents (they can DECIDE to call a tool) ---

# Agent #1: the searcher. Give it only the web_search tool so it stays focused
# on one job — finding sources — and can't accidentally do anything else.
def build_search_agent():
    return create_agent(
        model = llm,
        tools = [web_search]
    )


# Agent #2: the reader. Only gets the scrape_url tool. Same idea: one tool,
# one responsibility. It reads a page; it doesn't search.
def build_reader_agent():
    return create_agent(
        model = llm,
        tools = [scrape_url]
    )


# --- Chains (fixed prompt -> LLM -> text, no tools needed) ---

# The writer just turns the gathered research into a report — pure text work,
# so a simple chain is a better fit than a full agent here.
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

    Topic: {topic}

    Research Gathered:
    {research}

    Structure the report as:
    - Introduction
    - Key Findings (minimum 3 well-explained points)
    - Conclusion
    - Sources (list all URLs found in the research)

    Be detailed, factual and professional."""),
])

# Read the "|" like a pipe: fill the prompt -> send to the LLM -> parse the
# reply down to a plain string. This is LangChain's LCEL syntax.
writer_chain = writer_prompt | llm | StrOutputParser()


# The critic is our quality check — a second pair of eyes that scores the draft.
# We ask for a strict, fixed format so the output is predictable and easy to read.
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

    Report:
    {report}

    Respond in this exact format:

    Score: X/10

    Strengths:
    - ...
    - ...

    Areas to Improve:
    - ...
    - ...

    One line verdict:
    ..."""),
])

# Same pipe pattern as the writer.
critic_chain = critic_prompt | llm | StrOutputParser()


# results = writer_chain.invoke({
#     "topic": "The impact of AI on the job market",
#     "research": """1. "AI and the Future of Work" - A comprehensive article from MIT Technology Review discussing how AI is transforming the job market.
# 2. "The State of AI in the Workplace" - A report from McKinsey & Company analyzing the impact of AI on various industries.
# 3. "AI and Employment: A Double-Edged Sword" - An article from Harvard Business Review exploring both the opportunities and challenges of AI in the workforce."""
# })

# print("Generated Report:\n", results)