from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import GoogleGenerativeAI
from config.Settings import settings
from langchain.memory import ConversationBufferMemory
from agents.types import AskAI
key = settings.api_key
model = settings.model

llm = GoogleGenerativeAI(model=model,google_api_key=key,temperature=0.2,max_output_tokens=10000)

memory = ConversationBufferMemory()

template = """
    You are a helpful chatbot.  
    You have the following information about the user:  
    {user_detail}

    The user will ask you a question.  
    Use the given user detail to provide the best possible answer.  
    If the answer is not in the user detail, politely say you don’t know.

    Question: {question}
    Answer:
    """
parser = PydanticOutputParser(pydantic_object=AskAI)

prompt = PromptTemplate(
    input_variables=["user_detail", "question"],
    template=template
)

chain = LLMChain(llm=llm,prompt=prompt,verbose=True,output_parser=parser,verbose=True,memory=memory)

def ask_ai(user_detail,question):
    raw_output = chain.invoke({"user_detail":user_detail,"question":question})
    if isinstance(raw_output, dict) and "text" in raw_output:
        parsed = raw_output["text"]
    else:
        parsed = raw_output
    return parsed





