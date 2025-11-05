import json
import os
import logging
from fastapi import HTTPException
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from app.models.chatbot_model import ChatRequest, ChatResponse
from config.Settings import settings

FILE_PATH = "candidate_data.txt"

from config.Settings import api_key, settings
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel(settings.model)

llm = GoogleGenerativeAI(
    model=settings.model,
    google_api_key=api_key,
    temperature=settings.temperature,
    max_output_tokens=settings.max_output_tokens
)

memory = ConversationBufferMemory()

template = """
You are an HR assistant chatbot. You have access to candidate profile data and job matching information.

Available candidate data:
{user_detail}

Instructions:
- Use the candidate data to answer questions about the candidate's profile, skills, experience, or job matching
- For questions not related to the candidate data or general HR topics, provide helpful responses as an HR assistant
- If the answer cannot be found in the candidate data, politely state that you don't have that specific information
- Maintain a professional and helpful tone
- Do not assume the user is the candidate - treat this as a general HR inquiry system
- Keep responses clear and concise

Question: {question}
Answer:
"""

prompt = PromptTemplate(
    input_variables=["user_detail", "question"],
    template=template,
)

chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
)

def ask_ai(question: str):
    try:
        if not os.path.exists(FILE_PATH):
            logging.warning("Candidate data file not found.")
            user_detail = "data not found"
        else:
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                user_detail = f.read()

        chain = prompt | llm
        response = chain.invoke({
            "user_detail": user_detail, 
            "question": question
        })
        
        return response

    except Exception as e:
        logging.error(f"Error in ask_ai: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in AI processing: {str(e)}")