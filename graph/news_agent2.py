import requests
from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langgraph.graph import MessagesState
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    trim_messages,
)
import requests
import urllib.parse
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from IPython.display import Image, display
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langchain_community.document_loaders import WebBaseLoader
os.environ['TAVILY_API_KEY'] = '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'
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key="AIzaSyA1wygPM_ocs4MgCBTu9DZ3-JCcB9jNelc")

#define tools
#________________________________________________________________
def web_search(query: str):
    """
    Perform a web search for news articles based on the user's query.

    This function utilizes the TavilySearchResults tool to search for news articles 
    related to the given query. It retrieves up to 5 results and returns the relevant 
    information, including article content, images, and additional context where available.

    Args:
        query (str): The search query input provided by the user, representing the topic 
        or keywords for which news articles are being requested.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary contains information 
        about a single news article. The details may include the article content, any 
        associated images, and additional contextual information (if available).
    """
    tool = TavilySearchResults(
        max_results=10,
        include_answer=True,
        include_raw_content=True,
        include_images=True,
    )
    response = tool.invoke({'query': query})
    return response

def individual_article_retriever(url: str):
    """
    Retrieve the full content of a web page, article, or blog post from the given URL.

    This function uses the WebBaseLoader to fetch and extract the entire content of the web 
    page specified by the provided URL. It returns the textual content of the page, which can 
    be a news article, blog post, or any other web-based document.

    Args:
        url (str): The URL of the web page, article, or blog post from which the content 
        will be retrieved.

    Returns:
        str: The full text content of the web page. This includes the main body of the page,
        excluding any extraneous elements like navigation menus or advertisements.
    """
    loader = WebBaseLoader(url)
    data = loader.load()
    return data[0].page_content

#________________________________________________________________

#define the system message to the llm
sys_msg = """Your name is Headline AI. You are a assistant to help users with news related queries. Users will ask you about different news about any domain and you will call the tools to fetch those news and answer them with the related news articles and information about the news by fetching them. If the user query is vague you can ask for clearance like what types of news the user actually want. Must access the following tools for news fetching:
- web_search
- individual_article_retriever
Your response should be news articles in a well ordered way and list all of them with long descriptions."""

#binding tools with the llm
tools = [web_search, individual_article_retriever]
llm_with_tools = llm.bind_tools(tools)

#defining assistant it will call the llm_with_tools with the last 10 messages
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"][-10:])]}

#defining the nodes and edges of the graph
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

#here is the graph's memory
memory = MemorySaver()

#building up the graph
agent = builder.compile(checkpointer=memory)


config = {"configurable": {"thread_id": "123"}}
while True:
  inp = input("Enter you news realted query:")
  messages = [HumanMessage(content=f"{inp}")]
  messages = agent.invoke({"messages": messages}, config)
  print("Message>>>", messages)
  for m in messages['messages']:
      m.pretty_print()