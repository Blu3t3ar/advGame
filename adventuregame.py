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
OPENAI_API_KEY = "instert your key"  # insert your open.ai api key here. To get one visit https://platform.openai.com/api-keys #
# or ask me for mine, can't leave it inside the code #

auth_provider = PlainTextAuthProvider("token", TOKEN)
cloud_config = {
    'secure_connect_bundle': 'secure-connect-adventuregame.zip' 
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
Before the darkness consumed Gloomhaven, you were Blackrose, a guardian of the realm known for your unmatched skill and bravery. 
Legends spoke of your battles, your victories against the forces that sought to plunge the world into eternal night. Yet, as the shadows grew, 
so did the tales fade, until you became but a whisper, a shadow among shadows.

Your quest for the Nightshade Amulet is more than a journey; it's a redemption, a chance to restore the light that once was. The amulet, lost to 
the ages, is said to hold the power to dispel the darkness, to return hope to Gloomhaven. It's the reason you stand at the edge of the Forbidden 
Forest, the reason you must face the nightmares that await.

With a heart heavy with the memories of a brighter past and a resolve steeled by the promise of a future, you must choose your companion for the 
journey ahead:

1. The Cursed Blade - Once your trusted ally in countless battles, its thirst for the blood of the wicked is unquenched.
2. The Shadowcloak - A relic from your days as a guardian, offering protection and camouflage in the shadows you now call home.
3. The Orb of Torment - Discovered in the ruins of an ancient battleground, its power resonates with your own sorrow and strength.

This choice marks the first of many you will face in the Forbidden Forest. Remember, Blackrose, the path to salvation is fraught with peril, but 
it is also paved with hope. Your history, your battles, have prepared you for this moment. Will you emerge from the darkness as the savior of 
Gloomhaven, or will you be consumed by the very shadows you seek to vanquish?

Here are some rules to follow:

1. Given Blackrose's current situation, offer a hint or suggestion on what they might do next to advance their quest for the Nightshade Amulet.
2. Your goal is to create a branching narrative experience where each choice leads to a new path, ultimately determining Blackrose's fate. 


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

choices_made = 0  # Initialize a counter for the choices made by the player

# Start the game loop with the enhanced narrative
while True:
    if choices_made == 0:
        print("As Blackrose, your journey through the dark heart of Gloomhaven begins, driven by a quest for redemption and the hope of restoring light to the realm.")
        # Print the initial weapon choice prompt with added context about the player's history
        print(template)  # Assuming template includes the narrative with player history and weapon choices
    
    choice = input("Your choice: ").strip()

    if choice.lower() == 'quit':
        print("Game over. Thank you for playing!")
        break

    # Predict and print the AI-generated response based on the player's choice and history
    response = llm_chain.predict(human_input=choice)
    print(response.strip())

    choices_made += 1  # Increment the choice count

    # Implement the death condition and check for victory after a minimum of 40 choices
    if "You have died." in response and choices_made < 40:
        print("Alas, your journey ends here, not with the redemption you sought, but with the shadows claiming one of their own.")
        break
    elif choices_made >= 40:
        print("Through the darkness, you've carried the light of your past, Blackrose, facing each challenge with the courage of a true guardian. The Nightshade Amulet is yours, and with it, the promise of a new dawn for Gloomhaven.")
        print("Congratulations, Blackrose! You have reclaimed your legend and brought hope back to the realm.")
        break  # End the game after 40 choices with a victory message