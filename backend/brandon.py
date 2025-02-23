from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List

from prompts import BRANDON_INIT_PROMPT

class IdentifyBacklinks(BaseModel):
    """Identify potential backlink opportunities in the article content."""
    backlinks: List[str] = Field(..., description="List of strings in the article that are suitable for backlinks.")

class Brandon:
    def __init__(self, model_name="gpt-4o-mini", temperature=0.7):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

        self.response_schemas = [
            ResponseSchema(
                name="backlinks", description="List of strings suitable for backlinks"
            ),
        ]
        self.output_parser = StructuredOutputParser.from_response_schemas(
            self.response_schemas
        )

        self.llm = self.llm.bind_tools([IdentifyBacklinks], tool_choice="any")

    def identify_backlinks(self, article_content: str) -> List[str]:
        response = self.llm.invoke([
            SystemMessage(content=BRANDON_INIT_PROMPT),
            HumanMessage(content=article_content)
        ])
        tool_calls = response.tool_calls
        for call in tool_calls:
            if call["name"] == "IdentifyBacklinks":
                return call["args"]["backlinks"]
        return []