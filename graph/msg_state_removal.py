from langchain_core.messages import RemoveMessage
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage

messages = [AIMessage("msg 1.", name="Bot", id="1")]
messages.append(HumanMessage("msg 2", name="Lance", id="2"))
messages.append(AIMessage("msg 3", name="Bot", id="3"))
messages.append(HumanMessage("msg 4", name="Lance", id="4"))

delete_messages = [RemoveMessage(id=m.id) for m in messages[:-2]]
print("delete_messages", delete_messages)
print("Messages before deletion:", messages )
final_messages = add_messages(messages, delete_messages)
print("Messages after deletion:", final_messages)