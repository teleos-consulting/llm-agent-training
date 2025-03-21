# Get the key
from . import key

# Get the OpenAI API key
OPENAI_API_KEY = key.OPENAI_API_KEY

# Add the langchain loader for text files
from langchain import hub

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document

docs = [TextLoader("./JC_Wikipedia.md").load(), TextLoader("./JC_Text.txt").load()]

# Chop up the document into smaller pieces the robot can reference
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Split the text into chunks of 1000 characters with 200 characters of overlap.
# This ensures that words we want to look at don't get cut in the middle between two copies
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
processed_documents = text_splitter.split_documents(docs)

# Now we need to put the documents into a file cabinet of sorts
# We do this with a "vector store"
from langchain_core.vectorstores import InMemoryVectorStore

from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=OPENAI_API_KEY)
vector_store = InMemoryVectorStore(embeddings)
_ = vector_store.add_documents(documents=processed_documents)

# Grab a standard prompt to configure this agent
# https://smith.langchain.com/hub/rlm/rag-prompt
prompt = hub.pull("rlm/rag-prompt")

# Structure the state of the agent
from typing_extensions import List, TypedDict
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

# Define a function that will grab information based on the question
def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}

# Define the llm
from langchain.chat_models import init_chat_model
llm = init_chat_model("gpt-4o-mini", model_provider="openai", api_key=OPENAI_API_KEY)

# Define a function that will generate an answer based on the data it received
def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}

# Build the graph with a retrieve & generate sequence
from langgraph.graph import START, StateGraph

graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

response = graph.invoke({"question": "Why makes this play distinctive from other Shakespear plays? Provide a quote from the document supporting your answer."})
print(response["answer"])
