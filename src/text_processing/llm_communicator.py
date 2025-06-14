from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.data_classes.bilingual_text import BilingualText
from src.prompts.prompt_reader import read_prompt, PromptName
from src import config as cfg


load_dotenv()

llm = ChatGoogleGenerativeAI(model=cfg.llm_model, temperature=0)

# Invoke the model with a query asking for structured information
def create_bilingual_text(
    source_text: str, target_language: str
) -> BilingualText: # Note: The return type of the function itself might need adjustment if you want to return usage info too
     # Key change: Add include_raw=True
     structured_llm = llm.with_structured_output(BilingualText, include_raw=True)
     system_prompt = read_prompt(PromptName.MAKE_BILINGUAL, target_language=target_language)

     # Pass both system prompt and user message as a list of messages using LangChain message classes
     messages = [SystemMessage(content=system_prompt), HumanMessage(content=source_text)]
     print("Invoking LLM ")
     ret = structured_llm.invoke(messages)
     print(ret['raw'].usage_metadata)
     return ret['parsed']