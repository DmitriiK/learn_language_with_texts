from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.data_classes.bilingual_text import BilingualText
from src.prompts.prompt_reader import read_prompt, PromptName
from src.text_processing.utils import split_to_paragraphs
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
     source_text = "\n\n".join(split_to_paragraphs(source_text, max_length=cfg.max_paragraph_length)) 
     messages = [SystemMessage(content=system_prompt), HumanMessage(content=source_text)]
     print("Invoking LLM ")
     ret = structured_llm.invoke(messages)
     print(ret['raw'].usage_metadata)
     return ret['parsed']

def bilingual_to_html(bilingual, layout='continuous'):
    html = ['<html><head><meta charset="utf-8"><title>Bilingual Text</title><style>\n.syntagma-translation{color:green;}\ntable{border-collapse:collapse;}td,th{border:1px solid #ccc;padding:4px;}\n</style></head><body>']
    if layout == 'continuous':
        for para in bilingual.paragraphs:
            html.append('<div class="paragraph">')
            html.append('<div>')
            for s in para.Sintagmas:
                html.append(f'<span class="syntagma-translation">{s.target_text}</span> | <span>{s.source_text}</span><br>')
            html.append('</div>')
            html.append('<div style="margin-top:0.5em;font-style:italic;">')
            html.append(' '.join(s.source_text for s in para.Sintagmas))
            html.append('</div></div><hr>')
    elif layout == 'side-by-side':
        html.append('<table><tr><th>Source</th><th>Translation</th></tr>')
        for para in bilingual.paragraphs:
            for s in para.Sintagmas:
                html.append(f'<tr><td>{s.source_text}</td><td class="syntagma-translation">{s.target_text}</td></tr>')
        html.append('</table>')
    html.append('</body></html>')
    return '\n'.join(html)