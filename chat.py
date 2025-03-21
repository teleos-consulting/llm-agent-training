# Get your API key like before


# Grab some LangChain tools...
# First, the tool that lets us use the OpenAI chat model


# Second, two types of messages that LangChain can track for us


# Let's set up the OpenAI chat model


#### Section A #################################

# Call OpenAI with an introduction to yourself

# Now let's ask it a question...

#### End Section A #############################


#### Section B #################################

# This time, let's send it a whole conversation

#### End Section B #############################


#### Section C #################################

# Let's set up "state management" so LangGraph can keep track of the conversation
# for us. Import the MemorySaver tool.

# Now get some helpful nodes we can use to build a conversation graph


# We're going to create a little utility that helps LangGraph keep track of the conversation


# Define the state of the agent


# Now create a python function that calls the model with the messages we've tracked

# Let's create an empty graph that tracks the conversation as we talk


# Add nodes and edges to the workflow


# Now we need to help it remember

# Configure the memory to label this conversation "My first chat"


# Put it all together and what have you got?


# Loop until we quit


#### End Section C #############################
