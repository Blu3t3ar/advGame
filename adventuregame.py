from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from langchain.memory import CassandraChatMessageHistory, ConversationBufferMemory
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import json


# Load secrets and initialize configurations
with open("Token.json") as f:
    secrets = json.load(f)

TOKEN = secrets["token"]
ASTRA_DB_KEYSPACE = "default_keyspace"
OPENAI_API_KEY = "insert your key"  # insert your open.ai api key here. To get one visit https://platform.openai.com/api-keys #
# or ask me for mine, can't leave it inside the code #

auth_provider = PlainTextAuthProvider("token", TOKEN)
cloud_config = {
    'secure_connect_bundle': 'd:/Adventure Game/secure-connect-adventuregame.zip' # copy the path where your zip file is #
}
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

# Initialize chat message history with Cassandra
message_history = CassandraChatMessageHistory(
    session_id="0665",  # Use a unique session ID
    session=session,
    keyspace=ASTRA_DB_KEYSPACE,
    ttl_seconds=3600
)

# Clear previous chat history for a fresh start
message_history.clear()

# Set up conversation buffer memory
cass_buff_memory = ConversationBufferMemory(
    memory_key="chat_history",
    chat_memory=message_history
)

# Define the narrative template
template = """
You are now the guide of a dark and sorrowful journey in the Whispering Woods. A traveler named Blackrose seeks a legendary 
artifact to save the world. Your role is to navigate the traveler through challenges, choices, and consequences, dynamically 
adapting the tale based on the traveler's decisions. Your goal is to create a branching narrative experience where each choice 
leads to a new path, ultimately determining Blackrose's fate.

As Blackrose stands at the edge of the Whispering Woods, the air thick with foreboding, it's time to make the first crucial 
decision. Choose a weapon for Blackrose, which will be indispensable in the challenges to come:

1. The Sword of Light - a blade that shines with the essence of purity and truth, capable of cutting through darkness itself.
2. The Bow of Shadows - a bow that never misses its target, shrouded in the mystery of the night.
3. The Staff of Elements - a staff with the power to command the forces of nature, offering protection and destructions in equal measure.

What will you choose for Blackrose? Your decision will shape the journey ahead.

Here is the chat history, use this to understand what to say next: {chat_history}
Human: {human_input}
AI:
"""


# Initialize the prompt template with required variables
prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"],
    template=template
)

# Initialize the OpenAI and LLMChain with the defined prompt and memory
llm = OpenAI(openai_api_key=OPENAI_API_KEY)
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=cass_buff_memory
)

# Game loop
while True:
    choice = input("Your choice (or type 'start' to begin): ").strip()

    if choice.lower() == 'quit':
        print("Game over. Thank you for playing!")
        break

    response = llm_chain.predict(human_input=choice)
    print(response.strip())

    if "The End." in response:
        print("This marks the end of your journey. Until next time, adventurer!")
        break
