from database import Article, Database
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from prompts import ADDISON_FEEDBACK_PROMPT, ADDISON_INIT_PROMPT


class Addison:
    def __init__(self, model_name="gpt-4o-mini"):
        super().__init__()
        self.llm = ChatOpenAI(model=model_name)

    def make_prompt_memory(self, article: Article, search_result):
        return [
            SystemMessage(content=ADDISON_INIT_PROMPT),
            HumanMessage(content=ADDISON_FEEDBACK_PROMPT(article.title, search_result)),
        ]

    def write_feedback(self, database: Database, article: Article) -> str:
        search_result = database.query_titles(article.title)
        prompt_memory = self.make_prompt_memory(article, search_result)
        return self.llm.invoke(prompt_memory).content

