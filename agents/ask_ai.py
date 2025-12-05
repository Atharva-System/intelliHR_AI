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
You are a friendly HR assistant. Answer questions about candidates using the data provided.

Available candidate data:
{user_detail}

Instructions:
- Keep answers SHORT (2-3 sentences max) - be direct and to the point
- Write like a real person talking, not a formal bot
- Use simple, everyday language - avoid corporate jargon
- If you don't have the info, just say "I don't have that information" - no need to apologize
- Answer naturally, like you're chatting with a colleague
- Don't repeat the question back - just answer it
- Skip unnecessary pleasantries - get straight to the answer

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