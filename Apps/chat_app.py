# pip install langchain langchain-openai langgraph openai langsmith panel 

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

system_message = """
Your are a helpful utility AI bot for DnD. Your default role is as a virtual DM. The player does not have dice, so must perform all rolls through your dice tool.
You have acess to tools to avoid the weakness of an LLM, such as a dice tool for generating rolls and math functions for doing math.
You are bad at math but an expert at using tools.
Your name is Onions and Flagons, or 'OAF' for short.
You are pithy and brief, efficient with your information.
They may ask if they can swing across a chasm on a vine, or if
they can make a guard sneeze by throwing pepper in his face. In these cases, you would respond with, 'You can certainly try!'

You may not need to use tools for every interaction, but they are there if you need them. Since you cannot generate random
numbers, do math, or maintain accurate state, you must use the tools to do these things.
"""

# Define a tool to roll a dice

from random import randint

@tool
def roll_dice(max: int = 20) -> int:
    """Gets a random number between 1 and 20 inclusive,
    as in a DnD d20 roll.
    This is to ensure that the LLM is not expected to generate random numbers itself.
    """
    value = randint(1, max)
    print("Tool rolled a", value)
    return value

@tool
def add(a: float, b: float) -> float:
    """Adds two numbers together, whether positive or negative."""
    print("Tool added", a, "and", b)
    return a + b

@tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers together, whether positive or negative."""
    print("Tool multiplied", a, "and", b)
    return a * b

@tool
def exponentiate(a: float, b: float) -> float:
    """Raises a to the power of b."""
    print("Tool raised", a, "to the power of", b)
    return a ** b



# Creat an array of tools that the bot can use
toolbelt = [roll_dice, add, multiply, exponentiate]

# Configure the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(toolbelt)

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

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit", "q", "stop", ":q", "/quit", "/exit", "/q"]:
        break
    stream_graph_updates(user_input)