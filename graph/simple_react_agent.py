import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
os.environ["TAVILY_API_KEY"] = "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"
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage, AIMessage
from langchain_community.tools.tavily_search import TavilySearchResults

search = TavilySearchResults(max_results=2)

tools = [search]

model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key="AIzaSyA1wygPM_ocs4MgCBTu9DZ3-JCcB9jNelc")

agent_executor = create_react_agent(model, tools)

response = agent_executor.invoke({"messages": [HumanMessage(content="tell me about the champions cup 2024 pakistan")]})

res = response["messages"][3].content

print("Response: ", res)