from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    trim_messages,
    RemoveMessage
)
from langchain_google_genai import ChatGoogleGenerativeAI
from IPython.display import Image, display
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
# Nodes
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key="AIzaSyA1wygPM_ocs4MgCBTu9DZ3-JCcB9jNelc")

def filter_messages(state: MessagesState):
    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"messages": delete_messages}

def chat_model_node(state: MessagesState):    
    return {"messages": [llm.invoke(state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("filter", filter_messages)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "filter")
builder.add_edge("filter", "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()

# View
display(Image(graph.get_graph().draw_mermaid_png()))

messages = [AIMessage("Hi. How I can help you today?", name="Bot", id="1")]
messages.append(HumanMessage("Hi.", name="Lance", id="2"))
# messages.append(AIMessage("So you said you were researching ocean mammals?", name="Bot", id="3"))
# messages.append(HumanMessage("Yes, I know about whales. But what others should I learn about?", name="Lance", id="4"))

# Invoke
while True:
    human_input = input("Enter your query: ")
    id = str(int(id) + 1)
    messages.append(HumanMessage(content=human_input, id = f"{id}"))
    print("messages>>", messages)
    output = graph.invoke({'messages': messages})
    for m in output['messages']:
        m.pretty_print()