# Get the key
from key import OPENAI_API_KEY

# Import the math and langchain libraries
import math                                           # Surprise! This is a math library
from typing import Annotated, Sequence
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool                 # This lets us mark functions as tools
from langchain_openai import ChatOpenAI               # This saves us a bunch of work from before
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt.tool_node import ToolNode     # A new type of grpah node for using tools
from typing_extensions import TypedDict

# Get the different "message types" that will be used for the human and AI to interact
from langchain_core.messages import (
    HumanMessage,   # For humans
    AIMessage,      # AI responses
    SystemMessage,  # Communicatinos from the host app to the AI (including tools)
    ToolMessage,    # Instructs the host program to use a tool
)

# Import the important parts to build the state transitions
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

# Define the state of the agent
class State(TypedDict):
    messages: Annotated[list, add_messages]

workflow = StateGraph(State)

#### First Tool #################################

#### End First Tool #############################

#### Section A #################################

#### End Section A #############################

#### Toolbelt #################################
toolbelt = []
#### Toolbelt #################################

# Now back to setting up our LLM
# Notice we're using OpenAI chat directly rather than the LangChain wrapper
# Also see how we stuck some tools to it at the end
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY).bind_tools(toolbelt)

# Create a node-ready function that can accept state and take an action
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


#### Section B #################################

#### End Section B #############################

# Let's set up "state management" so LangGraph can keep track of the conversation
# for us. Import the MemorySaver tool.
from langgraph.checkpoint.memory import MemorySaver

# Now get some helpful nodes we can use to build a conversation graph
from langgraph.graph import (
    StateGraph,     # The graph that tracks the conversation
    START,          # The entry point to the graph
    MessagesState,  # The messages that are passed around the graph
)

# We're going to create a little utility that helps LangGraph keep track of the conversation
from langgraph.graph import add_messages    # A function that automatically adds messages to the list
from typing import Annotated                #
from typing_extensions import TypedDict     # This is for building a lookup table

# Define the state of the agent
class State(TypedDict):
    # Messages are in a list. The `add_messages` function (from langgraph)
    # will automatically add new messages to the conversation so far.
    # 'Annotated' basically just means this is a list with some extra information
    # about each message.
    messages: Annotated[list, add_messages]

# Now create a python function that calls the model with the messages we've tracked
def chatbot(state: MessagesState):
    # Call the model with the messages we've tracked so far and collect the response
    response_messages = {"messages": [llm.invoke(state["messages"])]}

    # Return the whole conversation so far, including the new response
    return response_messages

# Now we need to help it remember
memory = MemorySaver()

# Configure the memory to label this conversation "My first chat"
config = {"configurable": {"thread_id": "MathChat"}}

# Put it all together and what have you got?
app = workflow.compile(checkpointer=memory)

#### Initial Prompt #################################

inital_prompt = """
"""

# Send the robot that message.
app.invoke({"messages": [SystemMessage(content=inital_prompt)]}, config)

#### End Initial Prompt #################################

# Loop until we quit
while True:
    # Wait for user input in the console
    user_input = input("You: ")

    # Check if the user wants to quit, then leave.
    if user_input.lower() in ["exit", "quit", "q", "stop", ":q", "/quit", "/exit", "/q"]:
        break # get outta here
     # . . .
    # Create a user message
    user_message = HumanMessage(content=user_input)
   
    # Pass the list-of-one message to the model. LangGraph will add
    # it to the conversation for us. Note: You could pass more than
    # one message if you wanted to.
    output = app.invoke({"messages": [user_message]}, config=config)

    # Show the output in the console
    print("Chatbot: " + output["messages"][-1].content)
