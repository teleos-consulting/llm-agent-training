# pip install --upgrade --no-deps --force-reinstall panel holoviews

import panel as pn
from panel.chat import ChatInterface
pn.extension()

openai_key_env = 'OPENAI_API_KEY'

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage, HumanMessage
import getpass
import os

from random import randint

if not os.environ.get(openai_key_env):
    os.environ[openai_key_env] = getpass.getpass("Enter API key for OpenAI: ")

@tool
def roll_dice(max: int = 20) -> int:
    """Gets a random number between 1 and 20 inclusive,
    as in a DnD d20 roll.
    """
    value = randint(1, max)
    print("Tool rolled a", value)
    return value

toolbelt = [roll_dice]

model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(toolbelt)

system_message = """
Your are a helpful utility AI bot for DnD.
Your name is 'OAF' which stands for Onions and Flagons.
You are pithy and brief, efficient with your information.
Whenever a player asks if the player can do something, your response is, 'You can certainly try!'
If they are simply asking for information or providing an instruction, you don't need to use the catch phrase.
That's only for when they are trying to do something that may or may not work.
"""

messages = [
    SystemMessage(system_message),
]

ai_message = model.invoke(messages)

messages.append(ai_message)

def response_callback(input_message: str, input_user: str, instance: ChatInterface):
    messages.append(HumanMessage(input_message))

    r = None
    try:
        r = model.invoke(messages)
        messages.append(r)
        
        if len(r.tool_calls) > 0:
            for tool_call in r.tool_calls:
                selected_tool = {"roll_dice": roll_dice}[tool_call["name"].lower()]
                tool_msg = selected_tool.invoke(tool_call)
                messages.append(tool_msg)
            r = model.invoke(messages)
            
            messages.append(r)
    except:
        pass

    return r.content

ChatInterface(callback=response_callback).servable()

