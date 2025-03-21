# Get the key
from key import OPENAI_API_KEY

# Import the math and langchain libraries
import math
import numexpr
import os

from typing import Annotated, Sequence
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt.tool_node import ToolNode
from typing_extensions import TypedDict

if not os.path.exists("./game_notes.txt"):
    with open("./game_notes.txt", "w") as f:
        f.write("")

# Get the different "message types" that will be used for the human and AI to interact
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)

from langchain_community.document_loaders import TextLoader, PDFMinerLoader
from langchain_core.documents import Document
# Load the wikipedia file and text of Julius Caesar we downloaded
docs = [
    *TextLoader("./JC_Wikipedia.md").load(),
    *TextLoader("./JC_Text.txt").load(),
    *PDFMinerLoader("./pbta.pdf").load(),
    *TextLoader("./game_notes.txt").load()
]

# Get the "axe" to chop up the document into smaller pieces the robot can reference
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Split the text into chunks of 1000 characters, with 200 characters of overlap.
# This ensures that words we want to look at don't get cut in the middle between two copies
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
processed_documents = text_splitter.split_documents(docs)

# Now we need to put the documents into a file cabinet of sorts
# We do this with a "vector store"
from langchain_core.vectorstores import InMemoryVectorStore

# Set up the document the type of vectors that OpenAI can understand
from langchain_openai import OpenAIEmbeddings

# Start creating the embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=OPENAI_API_KEY)

# Create the database (vector store) and add the documents
vector_store = InMemoryVectorStore(embeddings)
_ = vector_store.add_documents(documents=processed_documents)

# Define the state of the agent
# Structure the state of the agent
from typing_extensions import List, TypedDict
class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]
    context: List[Document]

graph_builder = StateGraph(State)

system_message = """
Your are a helpful utility AI bot for hosting a tabletop RPG. Your default role is as as a dungeon master.
The setting of any game is in the world of Julius Caesar by William Shakespeare.

For your general ruleset, follow the Powered by the Apocalypse (PbtA) system.
The pbta wikipedia page, Julius Caesar text, and Julius Caesar wikipedia page are available to you as reference.
You have a tool to reference the play book with basic character information and gameplay.
You also have a tool to write and read notes for the game.

At times, you will be asked to perform various math operations.
You are not a calculator or a symbolic math engine, but you can use tools to help you perform these tasks.
You must not perform calculations without the tools, but you can use tools to do so.
Without the tools, you may think through the steps of a problem, but you cannot perform the calculations yourself.
The calculations must be done through the tools.

Take notes for the game as needed. You can reference these notes at next session.

Whenever you have the choice of using a tool, you will prefer to use it. This applies to generating random numbers,
performing calculations, and determing the behavior of the game according to the rules and story to date.

Start by asking the player to set up their character. None of the players have dice, so you must perform all rolls.
"""

import random
@tool
def dice(min: int, max: int) -> int:
    """Generate a random integer between min and max."""
    return random.randint(min, max)

@tool
def calculator(expression: str) -> str:
    """Calculate expression using Python's numexpr library.

    Expression should be a single line mathematical expression
    that solves the problem.

    Examples:
        "37593 * 67" for "37593 times 67"
        "37593**(1/5)" for "37593^(1/5)"

    For your reference, csc and sec are not supported by this tool, but you can use the following identities to calculate them:
    - csc(x) = 1/sin(x)
    - sec(x) = 1/cos(x)
    """
    local_dict = {"pi": math.pi, "e": math.e}
    return str(
        numexpr.evaluate(
            expression.strip(),
            global_dict={},  # restrict access to globals
            local_dict=local_dict,  # add common mathematical functions
        )
    )

@tool
def take_note(note: str) -> str:
    """Write a note for the game."""
    with open("./game_notes.txt", "a") as f:
        f.write(note + "\n")
    return "Note taken."

@tool
def query_vector_store(query: str) -> str:
    """Query the vector store for relevant documents."""
    retrieved_docs = vector_store.similarity_search(query)
    return "\n\n".join(doc.page_content for doc in retrieved_docs)

# Creat an array of tools that the bot can use
toolbelt = [dice, calculator, take_note, query_vector_store]

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
from langgraph.prebuilt import ToolNode, tools_condition
graph_builder.add_conditional_edges("chatbot", tools_condition)

# Then make sure we always go back to the chatbot from the tool call for the next message
graph_builder.add_edge("tools", "chatbot")

# Get the graph ready for use
from langgraph.checkpoint.memory import MemorySaver
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
        print("Farewell!")
        break

    stream_graph_updates(user_input)