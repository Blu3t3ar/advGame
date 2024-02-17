from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from langchain.memory import CassandraChatMessageHistory, ConversationBufferMemory
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from astrapy.db import AstraDB # not sure what to do here check the video #
import json

# run the env.bat and install everything like in the tutorial , if its not working properly do the code line by line #

cloud_config= {
  'secure_connect_bundle': 'secure-connect-adventuregame.zip' 
}

with open("Token.json") as f:
    secrets = json.load(f)

TOKEN = secrets["token"]
ASTRA_DB_KEYSPACE = "default_keyspace"
OPENAI_API_KEY = "instert kez"  # insert your open.ai api key here. To get one visit https://platform.openai.com/api-keys #
# or ask me for mine, can't leave it inside the code #

auth_provider = PlainTextAuthProvider("token", TOKEN)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

message_history = CassandraChatMessageHistory(
    session_id="15022024", # this session id can be anything #
    session=session,
    keyspace=ASTRA_DB_KEYSPACE,
    ttl_seconds=3600
)

message_history.clear()

cass_buff_memory = ConversationBufferMemory(
    memory_key="chat_history",
    chat_memory=message_history
)

# can be changed freely #
template = """ 
You are now the the guide of a dark and sorrowful journey in the Whispering Woods. 
A traveler named Blackrose seeks a legendary artifact to save the world. 
You must navigate the traveler through challenges, choices, and consequences, 
dynamically adapting the tale based on the traveler's decisions. 
Your goal is to create a branching narrative experience where each choice 
leads to a new path, ultimately determining Blackrose's fate. 

Here are some rules to follow:

1. Start by asking human_input to choose some kind of weapons to Blackrose that will be used later in the game,
wait for the choice by human_input .
2. As you progress the story, at every step wait for human_input to make a decision
3. Have at least 30 different and interesting paths that leads to success
4. Have some paths that lead to death. If the user dies generate a response that explains the death and ends in the text: "The End.", I will search for this text to end the game

Here is the chat history, use this to understand what to say next: {chat_history}
Human: {human_input}
AI:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"],
    template=template
)

llm = OpenAI(openai_api_key=OPENAI_API_KEY)
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=cass_buff_memory
)

choice = "start"

while True:
    response = llm_chain.predict(human_input=choice)
    print(response.strip())

    if "The End." in response:
        break

    choice = input("Your reply: ")
