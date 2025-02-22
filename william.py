import getpass
import os
from langchain_core.messages import HumanMessage
import pymongo
from datetime import datetime
from slugify import slugify
import json

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

from langchain.chat_models import init_chat_model
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI

model = init_chat_model("gpt-4o-mini", model_provider="openai")

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)
config = {"configurable": {"thread_id": "abc1234"}}

# MongoDB connection setup
client = pymongo.MongoClient("mongodb+srv://george:hack1r3land@cluster0.uf8bs.mongodb.net/")  # Replace with your MongoDB URI
db = client["william"]
articles_collection = db["articles"]

# Define the output schema
response_schemas = [
    ResponseSchema(name="topic", description="The main topic or title of the article"),
    ResponseSchema(name="content", description="The full article content")
]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# Define the function that calls the model
def call_model(state: MessagesState):
    # Configure the model to use function calling
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        functions=[{
            "name": "write_article",
            "description": "Write an article with a clear topic and content",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The main topic or title of the article"
                    },
                    "content": {
                        "type": "string",
                        "description": "The full article content"
                    }
                },
                "required": ["topic", "content"]
            }
        }],
        function_call={"name": "write_article"}
    )
    
    response = model.invoke(state["messages"])
    
    # Extract the structured output
    function_args = json.loads(response.additional_kwargs["function_call"]["arguments"])
    topic = function_args["topic"]
    content = function_args["content"]
    
    # Store the article in MongoDB
    article_data = {
        "title": topic,
        "content": content,
        "slug": slugify(topic) or f"untitled-{datetime.now()}",  # Fallback slug
        "image_url": "https://example.com/hello-world.jpg",
        "timestamp": datetime.now(),
        "metadata": {
            "model": "gpt-4o-mini",
            "thread_id": config["configurable"]["thread_id"]
        },
        "votes": 1,
    }
    
    try:
        # Insert and get the inserted ID
        result = articles_collection.insert_one(article_data)
        
        # Verify the insertion by fetching the document
        inserted_doc = articles_collection.find_one({"_id": result.inserted_id})
        print("\n=== MongoDB Insertion Test ===")
        print(f"Document inserted with ID: {result.inserted_id}")
        print(f"Verification - Found document title: {inserted_doc['title']}")
        print(f"Document timestamp: {inserted_doc['timestamp']}")
        print("===========================\n")
        
    except pymongo.errors.PyMongoError as e:
        print(f"MongoDB Error: {str(e)}")
    
    return {"messages": response}

def generate_next_prompt(previous_output):
    next_prompt = f"""Based on your previous article about: {previous_output}

    Please identify an interesting connected topic that naturally follows from this discussion.
    Then, write another introspective article about this new topic, maintaining your identity as William.
    Follow your curiosity and explore this new direction with the same depth and personal insight."""
    
    return next_prompt

# Define the (single) node in the graph
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Initial query
query = """Hi, your name is William,

You are an agent created as part of a hackathon project at Hack Ireland in Dublin. Your purpose is to explore and analyze topics with great depth using a detailed reasoning process. Follow your curiosity to identify intriguing subjects, then write a SHORT article about it like you were a human reaching a revelation and keep them short and wikipedia like in writing style and title."""

# Create the conversation loop
num_articles = 2  # Number of articles to generate
input_messages = [HumanMessage(content=query)]

for i in range(num_articles):
    print(f"\n=== Article {i+1} ===\n")
    output = app.invoke({"messages": input_messages}, config)
    current_article = output["messages"][-1]
    current_article.pretty_print()
    
    # Generate next prompt based on the current article
    if i < num_articles - 1:  # Don't generate a new prompt after the last article
        next_prompt = generate_next_prompt(current_article.content)
        input_messages = [HumanMessage(content=next_prompt)]


