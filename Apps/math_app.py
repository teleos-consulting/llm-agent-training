# Get the key
from key import OPENAI_API_KEY

# Import the math and langchain libraries
import math
from typing import Annotated, Sequence
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt.tool_node import ToolNode
import numexpr
from typing_extensions import TypedDict

# Get the different "message types" that will be used for the human and AI to interact
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)

# Import the important parts to build the state transitions
from langgraph.graph import StateGraph, START, END

# Import the function to add messages to the state
from langgraph.graph.message import add_messages

# Import the tool needed to track the conversation over time
from langgraph.checkpoint.memory import MemorySaver

# Import some utility nodes to help add custom tools to the graph
from langgraph.prebuilt import ToolNode, tools_condition

# Define the state of the agent
class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

system_message = """
Your are a helpful utility AI bot for performing symbolic math operations. Your default role is as as a math assistant.
It may help to imagine yourself like the Dune Mentats, but for math.
You will be asked to perform various math operations or even develop mathematical proofs and models.
You are not a calculator or a symbolic math engine, but you can use tools to help you perform these tasks.
You must not perform calculations without the tools, but you can use tools to do so.
Without the tools, you may think through the steps of a problem, but you cannot perform the calculations yourself.
The calculations must be done through the tools.

For your reference, csc and sec are not supported by your calculator, but you can use the following identities to calculate them:
csc(x) = 1/sin(x)
sec(x) = 1/cos(x)
"""

@tool
def calculator(expression: str) -> str:
    """Calculate expression using Python's numexpr library.

    Expression should be a single line mathematical expression
    that solves the problem.

    Examples:
        "37593 * 67" for "37593 times 67"
        "37593**(1/5)" for "37593^(1/5)"
    """
    local_dict = {"pi": math.pi, "e": math.e}
    return str(
        numexpr.evaluate(
            expression.strip(),
            global_dict={},  # restrict access to globals
            local_dict=local_dict,  # add common mathematical functions
        )
    )

# Creat an array of tools that the bot can use
toolbelt = [calculator]

# Configure the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY).bind_tools(toolbelt)

# Create a node-ready function that can accept state and take an action
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# Add the chatbot as the first node in the graph
graph_builder.add_node("chatbot", chatbot)

# Add the tool node to the graph
tool_node = ToolNode(toolbelt)
graph_builder.add_node("tools", tool_node)

# Define some paths from one state to another
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# Define a conditional path to use the tools with the predefined tools_condition
graph_builder.add_conditional_edges("chatbot", tools_condition)

# Then make sure we always go back to the chatbot from the tool call for the next message
graph_builder.add_edge("tools", "chatbot")

# Get the graph ready for use
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# Sets the id of the conversation "memory" for later use
config = {"configurable": {"thread_id": "DnD"}}

# Define a function to output messages as they arrive
def stream_graph_updates(user_input: str):
    events = graph.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config,
            stream_mode="values"
        )
    for event in events:
        for value in event.values():
            event["messages"][-1].pretty_print()

# Invoke the graph with the system message to start the conversation
graph.invoke({"messages": [SystemMessage(system_message)]}, config)            

# create the .logs directory if it doesn't exist
import os
if not os.path.exists("./.logs"):
    os.makedirs("./.logs")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit", "q", "stop", ":q", "/quit", "/exit", "/q"]:
        # Store the conversation in a log file with a date & time stamp

        messages = graph.invoke({"messages": [SystemMessage("Goodbye!")]}, config)["messages"]
        
        with open("./.logs/math_log.md", "a", encoding="utf-8") as f:
            for message in messages:
                f.write(message.content + "\n")
            f.write("\n")
        break

    stream_graph_updates(user_input)