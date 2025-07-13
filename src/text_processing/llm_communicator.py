from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.data_classes.bilingual_text import BilingualText
from src.prompts.prompt_reader import read_prompt, PromptName
from src.text_processing.nlp import split_to_paragraphs
from src.auth.usage_tracker import usage_tracker
from src import config as cfg


load_dotenv()

llm = ChatGoogleGenerativeAI(model=cfg.LLM_MODEL, temperature=0)


# Invoke the model with a query asking for structured information
def create_bilingual_text(source_text: str, target_language: str,
                          number_of_questions: int = 2,
                          user_name: str = None) -> BilingualText:
    structured_llm = llm.with_structured_output(BilingualText, include_raw=True)
    system_prompt = read_prompt(PromptName.MAKE_BILINGUAL, target_language=target_language, 
                                number_of_questions=number_of_questions)
    
    # Process the source text for LLM input
    processed_text = "\n\n".join(split_to_paragraphs(source_text, max_length=cfg.MAX_PARAGRAPH_LENGTH))
    
    # Log the length of text being sent (before LLM invocation)
    text_length = len(processed_text)
    ost = usage_tracker.get_overall_usage_stats()
    if ost.total_text_length + text_length > cfg.OVERALL_TOTAL_TEXT_LENGTH_QUOTA:
        raise ValueError(f"Total text length quota exceeded: {cfg.OVERALL_TOTAL_TEXT_LENGTH_QUOTA}")
    # TODO - make this at user level
    print(f"Invoking LLM with text length: {text_length}, and system prompt length: {len(system_prompt)} characters")
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=processed_text)]
    ret = structured_llm.invoke(messages)
    # Extract usage metadata
    usage_metadata = ret['raw'].usage_metadata
    input_tokens = usage_metadata.get('input_tokens', 0)
    output_tokens = usage_metadata.get('output_tokens', 0)
    
    # Log usage metrics
    usage_tracker.log_usage(
        text_length=text_length,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        user_name=user_name
    )
    
    print(f"LLM usage: {usage_metadata}")
    return ret['parsed']

