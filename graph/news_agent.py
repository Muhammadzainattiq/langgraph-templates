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

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key="AIzaSyA1wygPM_ocs4MgCBTu9DZ3-JCcB9jNelc")

class State(MessagesState):
  summary:str

def call_model(state: State):
    
    # Get summary if it exists
    summary = state.get("summary", "")

    # If there is summary, then we add it
    if summary:
        
        # Add summary to system message
        system_message = f"Summary of conversation earlier: {summary}"

        # Append summary to any newer messages
        messages = [SystemMessage(content=system_message)] + state["messages"]
    
    else:
        messages = state["messages"]
    
    response = llm.invoke(messages)
    return {"messages": response}

def summarize_conversation(state: State):
    
    # First, we get any existing summary
    summary = state.get("summary", "")

    # Create our summarization prompt 
    if summary:
        
        # A summary already exists
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
        
    else:
        summary_message = "Create a summary of the conversation above:"

    # Add prompt to our history
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = llm.invoke(messages)
    
    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}

def should_generate_summary(state:State):
  if len(state['messages']) > 16:
    return "summarize_conversation"
  else:
    return END


from IPython.display import Image, display
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START

# Define a new graph
workflow = StateGraph(State)
workflow.add_node("conversation", call_model)
workflow.add_node(summarize_conversation)

# Set the entrypoint as conversation
workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", should_generate_summary)
workflow.add_edge("summarize_conversation", END)

# Compile
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
display(Image(graph.get_graph().draw_mermaid_png()))
os.environ['TAVILY_API_KEY'] = "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"
def fetch_news(
               q: str, 
               sort_by: str = "publishedAt", 
               from_date: str = None, 
               to_date: str = None, 
               language: str = None, 
               page_size: int = 50, 
               page: int = 1) -> dict:
    """
    Fetches news based on the parameters.

    Parameters:
    - q (str): The query keywords or phrases.
    - sort_by (str): The sorting parameter. Options: 'relevancy', 'popularity', 'publishedAt'.
    - from_date (str): Starting date for articles (ISO format).
    - to_date (str): End date for articles (ISO format).
    - language (str): Language code for articles (ISO 639-1).
    - page_size (int): Number of articles per page.
    - page (int): The page number.
        
    Returns:
    - A JSON response containing the fetched articles in the following format:
    
    {
      'status': 'ok',
      'totalResults': <int>, 
      'articles': [
          {
              'source': {'id': <str or None>, 'name': <str>},
              'author': <str or None>,
              'title': <str>,
              'description': <str>,
              'url': <str>,
              'urlToImage': <str or None>,
              'publishedAt': <str in ISO 8601 format>,
              'content': <str truncated to 200 chars or None>
          },
          ...
      ]
    }

    Example output:
    {
      'status': 'ok',
      'totalResults': 83,
      'articles': [
        {
          'source': {'id': None, 'name': 'NDTV News'},
          'author': 'NDTV Sports Desk',
          'title': '"Yaari With Umpires": Babar\'s Teammate Hints At Officials Giving Favours',
          'description': 'The Pakistan star said that at the domestic level umpires have an understanding with the players...',
          'url': 'https://sports.ndtv.com/...',
          'urlToImage': 'https://c.ndtvimg.com/...',
          'publishedAt': '2024-09-21T11:26:09Z',
          'content': 'Pakistan cricket team star Faheem Ashraf...'
        },
        ...
      ]
    }
    """
    
    # Base URL for the News API
    base_url = "https://newsapi.org/v2/everything?apiKey=a754c2e1ba5643cba3006160d24802a5"
    
    # URL-encode the query
    encoded_query = urllib.parse.quote(q)
    
    # Create a dictionary of all the parameters
    params = {
        "q": encoded_query,
        "sortBy": sort_by,
        "pageSize": page_size,
        "page": page
    }
    
    # Add optional parameters if they are provided
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    if language:
        params["language"] = language

    # Make the API request
    response = requests.get(base_url, params=params)

    # Return the response in JSON format
    return response.json()

def fetch_news_from_web()

sys_msg = SystemMessage(content="""You are a news assistant designed to help users find articles and information based on their interests. Your primary task is to respond to user queries by fetching relevant news articles using the News API. You should provide users with detailed summaries of the articles, including key parameters such as:

- Title of the article
- Author
- Source of the article
- Description or snippet
- Direct URL to the article
- Publication date
- Image URL (if available)
- Content preview

You have access to the following tool to assist in fulfilling this task:

1. **fetch_news**: This tool allows you to retrieve articles from the News API based on user-defined keywords or phrases. You can use various parameters such as:
   - Keywords (supporting advanced search with AND, OR, NOT operators)
   - Language preferences
   - Sort order (by relevancy, popularity, or publication date)
   - Date range for filtering articles

Use this tool effectively to provide users with the most relevant and up-to-date news articles based on their interests and queries.""")

    
# Define the LLM with tools
search = TavilySearchResults(tavily_api_key="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")
tools = [search]
llm_with_tools = llm.bind_tools(tools)

# Node definition
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

memory = MemorySaver()
agent = builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1234"}}
while True:
  inp = input("Enter the query:")
  messages = [HumanMessage(content=f"{inp}")]
  messages = agent.invoke({"messages": messages}, config)
  print("Message>>>", messages)
  for m in messages['messages']:
      m.pretty_print()