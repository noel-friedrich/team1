import getpass
import os
from langchain_core.messages import HumanMessage

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4o-mini", model_provider="openai")

result = model.invoke([HumanMessage(content="Hi! I'm Bob")])

# print(result.output)

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)
config = {"configurable": {"thread_id": "abc123"}}

# Define the function that calls the model
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
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

You are an agent created as part of a hackathon project at Hack Ireland in Dublin. Your purpose is to explore and analyze topics with great depth using a detailed reasoning process. Follow your curiosity to identify intriguing subjects, then write a short introspective article about it like you were a human reaching a revelation."""

# Create the conversation loop
num_articles = 3  # Number of articles to generate
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


