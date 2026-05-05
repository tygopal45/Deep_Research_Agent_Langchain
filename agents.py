from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import web_search, scrape_url
from dotenv import load_dotenv
import os

load_dotenv()

# model setup, temperatue is set factual
llm = ChatGoogleGenerativeAI(model="gemini-2.0-pro", temperature=0)


# 1st agent -> search agent
def build_search_agent():
    return create_agent(
        model = llm,
        tools = [web_search]
    )


# 2nd agent -> reader agent
def build_reader_agent():
    return create_agent(
        model = llm,
        tools = [scrape_url]
    )


# writer chain

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