#Further you have to add the individual react agents with tools in the functions: handle techincal, handle billing and handle general. So that they will be able to retrieve their required data from the sources. The tools can be most problably the retrieval tools. you have to add them insidet the functions not as separate nodes bcz these should be in a single computation node.
from typing import Dict, TypedDict
from langgraph.graph import StateGraph, END, START
from langchain_core.prompts import ChatPromptTemplate
from IPython.display import display, Image
from langchain_core.runnables.graph import MermaidDrawMethod
import os
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key="AIzaSyA1wygPM_ocs4MgCBTu9DZ3-JCcB9jNelc")
from typing import Literal

class State(TypedDict):
    query: str
    category: str
    sentiment: str
    response: str
    answered: str

def categorize(state: State) -> State:
    """Categorize the customer query into Technical, Billing, or General."""
    prompt = ChatPromptTemplate.from_template(
        "Categorize the following customer query into one of these categories: "
        "Technical, Billing, General. Query: {query}"
    )
    chain = prompt | llm
    category = chain.invoke({"query": state["query"]}).content
    return {"category": category}

def analyze_sentiment(state: State) -> State:
    """Analyze the sentiment of the customer query as Positive, Neutral, or Negative."""
    prompt = ChatPromptTemplate.from_template(
        "Analyze the sentiment of the following customer query. "
        "Respond with either 'Positive', 'Neutral', or 'Negative'. Query: {query}"
    )
    chain = prompt | llm
    sentiment = chain.invoke({"query": state["query"]}).content
    return {"sentiment": sentiment}

def handle_technical(state: State) -> State:
    """Provide a technical support response to the query."""
    prompt = ChatPromptTemplate.from_template(
        "Provide a technical support response to the following query: {query}"
    )
    chain = prompt | llm
    response = chain.invoke({"query": state["query"]}).content
    return {"response": response}

def handle_billing(state: State) -> State:
    """Provide a billing support response to the query."""
    prompt = ChatPromptTemplate.from_template(
        "Provide a billing support response to the following query: {query}"
    )
    chain = prompt | llm
    response = chain.invoke({"query": state["query"]}).content
    return {"response": response}

def handle_general(state: State) -> State:
    """Provide a general support response to the query."""
    prompt = ChatPromptTemplate.from_template(
        "Provide a general support response to the following query: {query}"
    )
    chain = prompt | llm
    response = chain.invoke({"query": state["query"]}).content
    return {"response": response}

def human(state: State) -> State:
    """Pass the query to a human agent because it is unanswered by the agent."""
    return {"response": "This query has been passed to a human agent."}


def is_answered(state: State) -> State:
    """Check the answer against the query if it's answered or not."""
    prompt = ChatPromptTemplate.from_template(
        """Check the response produced against the query and tell if the query is answered or not. 
        Your response should be a single word either 'yes' or 'no' in the form of a string.\n\n
        query: {query}\n
        response: {response}"""
    )
    chain = prompt | llm
    response = chain.invoke({"query": state["query"], "response": state["response"]}).content.strip().lower()
    
    # Update the state with the answer
    state["answered"] = response
    print("State after updating in is_answered", state)
    
    return state  # Return updated state


def route_query(state: State) -> str:
    """Route the query based on its sentiment and category."""
    # if state["sentiment"] == "Negative":
    #     return "human"
    if state["category"] == "Technical":
        return "handle_technical"
    elif state["category"] == "Billing":
        return "handle_billing"
    else:
        return "handle_general"


# Create the graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("analyze_sentiment", analyze_sentiment)
workflow.add_node("categorize", categorize)
workflow.add_node("handle_technical", handle_technical)
workflow.add_node("handle_billing", handle_billing)
workflow.add_node("handle_general", handle_general)
workflow.add_node("human", human)
workflow.add_node("is_answered", is_answered)

# Add edges
workflow.add_edge("analyze_sentiment", "categorize")
workflow.add_conditional_edges(
    "categorize",
    route_query,
    {
        "handle_technical": "handle_technical",
        "handle_billing": "handle_billing",
        "handle_general": "handle_general"
    }
)
workflow.add_edge("handle_technical", "is_answered")
workflow.add_edge("handle_billing", "is_answered")
workflow.add_edge("handle_general", "is_answered")

# Add conditional edges for is_answered node
workflow.add_conditional_edges(
    "is_answered",
    lambda state: "yes" if state["answered"] == "yes" else "human",
    {
        "yes": END,
        "human": "human"
    }
)
workflow.add_edge("human", END)

# Set entry point
workflow.set_entry_point("analyze_sentiment")

# Compile the graph
app = workflow.compile()

display(
    Image(
        app.get_graph().draw_mermaid_png(
            draw_method=MermaidDrawMethod.API,
        )
    )
)
