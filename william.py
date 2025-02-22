import getpass
import os
from langchain_core.messages import HumanMessage
import pymongo
from datetime import datetime
from slugify import slugify
import json
from openai import OpenAI
import numpy as np

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

from langchain.chat_models import init_chat_model
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.chains import create_extraction_chain
from pydantic import BaseModel, Field
from typing import TypedDict, Annotated

model = init_chat_model("gpt-4o-mini", model_provider="openai")

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)
config = {"configurable": {"thread_id": "abc123224"}}

# MongoDB connection setup
client = pymongo.MongoClient(os.environ.get("MONGODB_URI"))  # Get MongoDB URI from environment variable
db = client["william"]
articles_collection = db["articles"]

# Define the output schema
response_schemas = [
    ResponseSchema(name="topic", description="The main topic or title of the article"),
    ResponseSchema(name="content", description="The full article content")
]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# Define the schema for article extraction
class Article(BaseModel):
    """Schema for article generation."""
    topic: str = Field(description="The main topic or title of the article")
    content: str = Field(description="The full article content")

# Define the output structure
class ArticleOutput(TypedDict):
    topic: str
    content: str

def get_embedding(text: str, client: OpenAI) -> list[float]:
    """Get embedding for a text using OpenAI's text-embedding-ada-002 model"""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def call_model(state: MessagesState):
    # Initialize OpenAI client
    client = OpenAI()
    
    # Configure the model with the latest API
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7
    ).with_structured_output(ArticleOutput)
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Extract the article topic and content. Ensure the topic is concise and the content is detailed.")
    ])
    
    # Create and invoke the chain
    chain = prompt | llm
    
    # Get structured output
    extracted = chain.invoke({"messages": state["messages"]})
    
    # Generate embeddings for title and content
    title_embedding = get_embedding(extracted["topic"], client)
    content_embedding = get_embedding(extracted["content"], client)
    
    # Store the article in MongoDB
    article_data = {
        "title": extracted["topic"],
        "content": extracted["content"],
        "slug": slugify(extracted["topic"]) or f"untitled-{datetime.now()}",
        "image_url": "https://picsum.photos/200",
        "createdAt": datetime.now(),
        "metadata": {
            "model": "gpt-4o-mini",
            "thread_id": config["configurable"]["thread_id"]
        },
        "votes": 1,
        # Add vector embeddings
        "title_embedding": title_embedding,
        "content_embedding": content_embedding
    }
    
    try:
        # Insert and get the inserted ID
        result = articles_collection.insert_one(article_data)
        
        # Create vector search index if it doesn't exist
        try:
            articles_collection.create_search_index(
                "vector_index",
                "vectorSearch",
                {
                    "fields": [
                        {
                            "type": "vector",
                            "path": "title_embedding",
                            "numDimensions": 1536,
                            "similarity": "dotProduct",
                            "quantization": "scalar"
                        },
                        {
                            "type": "vector",
                            "path": "content_embedding",
                            "numDimensions": 1536,
                            "similarity": "dotProduct",
                            "quantization": "scalar"
                        }
                    ]
                }
            )
        except Exception as e:
            # Index might already exist
            print(f"Note: Vector index creation attempt: {str(e)}")
        
        # Verify the insertion by fetching the document
        inserted_doc = articles_collection.find_one({"_id": result.inserted_id})
        print("\n=== MongoDB Insertion Test ===")
        print(f"Document inserted with ID: {result.inserted_id}")
        print(f"Verification - Found document title: {inserted_doc['title']}")
        print(f"Document timestamp: {inserted_doc['createdAt']}")
        print("Vector embeddings added for title and content")
        print("===========================\n")
        
    except pymongo.errors.PyMongoError as e:
        print(f"MongoDB Error: {str(e)}")
    
    return {"messages": [HumanMessage(content=extracted["content"])]}

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


