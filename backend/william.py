from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.chains import create_extraction_chain
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import START, MessagesState, StateGraph
from pydantic import BaseModel, Field

from database import Article
from typing import TypedDict
from prompts import WILLIAM_INIT_PROMPT, WILLIAM_WRITE_MORE_PROMPT

class write_article(BaseModel):
    """Write a new article and upload it to the Williampedia"""

    title: str = Field(..., description="title text of the article")
    content: str = Field(..., description="body text of the article")

class William:

    def __init__(self, model_name="gpt-4o-mini", history_size=10):
        super().__init__()

        self.llm = ChatOpenAI(model=model_name)

        self.response_schemas = [
            ResponseSchema(name="topic", description="The main topic or title of the article"),
            ResponseSchema(name="content", description="The full article content")
        ]
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)

        self.history_size = history_size
        self.message_history = []
        
        self.llm = self.llm.bind_tools([write_article], tool_choice="any")

    def produce_article(self, messages) -> Article:
        response = self.llm.invoke(messages)
        self.add_to_memory(response)
        tool_calls = response.tool_calls
        for call in tool_calls:
            if call["name"] == "write_article":
                article = Article(call["args"]["title"], call["args"]["content"])
                
                # openai forces us to supply toolmessage after an aimessage that uses
                # a tool, hence we manually insert an answer into memory
                tool_message = ToolMessage(
                    role='tool',
                    content='{"result":"success"}',
                    name=call["name"],
                    tool_call_id=call["id"]
                )
                self.add_to_memory(tool_message)

                return article

    def update_memory(self):
        while len(self.message_history) > self.history_size:
            self.message_history.pop(0)

        self.memory = [
            SystemMessage(content=WILLIAM_INIT_PROMPT),
            *self.message_history
        ]

    def add_to_memory(self, message):
        self.message_history.append(message)
        self.update_memory()

    def generate_new_article_prompt(self, feedback: str) -> str:
        return WILLIAM_WRITE_MORE_PROMPT(feedback)

    def write_new_article(self, feedback: str):
        # add prompt containing feedback and direction if we got feedback
        if feedback is not None:
            article_prompt = self.generate_new_article_prompt(feedback)
            self.add_to_memory(HumanMessage(content=article_prompt))
        else:
            self.update_memory()

        return self.produce_article(self.memory)