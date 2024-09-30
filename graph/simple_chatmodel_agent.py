from IPython.display import Image, display
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key="AIzaSyA1wygPM_ocs4MgCBTu9DZ3-JCcB9jNelc")


# Node
def chat_model_node(state: MessagesState):
    return {"messages": llm.invoke(state["messages"])}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)
memory = MemorySaver()
graph = builder.compile(memory)

# View
display(Image(graph.get_graph().draw_mermaid_png()))


sys_msg = "You are a helpful assitant to help users with their queries."
messages = [SystemMessage(content=sys_msg)]

while True:

    human_input = input("Enter your input")
    config = {"configurable": {"thread_id": "1"}}
    messages = [HumanMessage(content=human_input)]
    output = graph.invoke({'messages': messages}, config)
    for m in output['messages']:
        m.pretty_print()