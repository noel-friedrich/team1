from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.chains import create_extraction_chain
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, MessagesState, StateGraph
from pydantic import BaseModel, Field

from database import Article, Database
from prompts import ADDISON_INIT_PROMPT, ADDISON_FEEDBACK_PROMPT

class Addison:

    def __init__(self, model_name="gpt-4o-mini"):
        super().__init__()
        self.llm = ChatOpenAI(model=model_name)

    def make_prompt_memory(self, article: Article, search_result):
        return [
            SystemMessage(content=ADDISON_INIT_PROMPT),
            HumanMessage(content=ADDISON_FEEDBACK_PROMPT(
                article.title, search_result
            ))
        ]

    def write_feedback(self, database: Database, article: Article) -> str:
        search_result = database.query_titles(article.title)
        prompt_memory = self.make_prompt_memory(article, search_result)
        return self.llm.invoke(prompt_memory).content