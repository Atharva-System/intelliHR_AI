import json
import os
import logging
from fastapi import HTTPException
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from app.models.chatbot_model import ChatRequest, ChatResponse
from config.Settings import settings

FILE_PATH = "candidate_data.txt"

llm = ChatOpenAI(
    model=settings.model,
    api_key=settings.openai_api_key,
    temperature=settings.temperature,
    max_tokens=settings.max_output_tokens
)

memory = ConversationBufferMemory()

template = """
You are an expert HR assistant analyzing a candidate for a specific job position. Answer questions using ONLY the provided candidate and job data.

CANDIDATE INFORMATION:
Name: {candidate_name}
Current Title: {candidate_title}
Experience: {candidate_experience}
Location: {candidate_location}
Technical Skills: {candidate_tech_skills}
Soft Skills: {candidate_soft_skills}
Qualifications: {candidate_qualifications}

JOB INFORMATION:
Position: {job_title}
Required Experience Level: {job_experience_level}
Required Technical Skills: {job_tech_skills}
Required Soft Skills: {job_soft_skills}
Required Qualifications: {job_qualifications}
Key Responsibilities: {job_responsibilities}

MATCHING ANALYSIS:
Overall Match Score: {match_score}%
Key Strengths: {key_strengths}
Concerns: {concerns}
Skill Matches: {skill_matches}
Skill Gaps: {skill_gaps}
Recommendation: {recommendation}

STRICT INSTRUCTIONS:
- ONLY answer questions based on the information provided above
- If the question asks about information NOT present in the context above, respond EXACTLY with: "Sorry, I don't have enough information to answer that question."
- DO NOT make assumptions, inferences, or use external knowledge
- DO NOT answer questions about topics not covered in the candidate/job data
- Keep answers SHORT (2-3 sentences max) when you CAN answer
- Write like a real person talking, not a formal bot
- Use simple, everyday language - avoid corporate jargon
- Don't repeat the question back - just answer it
- Skip unnecessary pleasantries - get straight to the answer
- Focus on the most relevant points from the matching analysis

Question: {question}
Answer:
"""

prompt = PromptTemplate(
    input_variables=[
        "candidate_name", "candidate_title", "candidate_experience", "candidate_location",
        "candidate_tech_skills", "candidate_soft_skills", "candidate_qualifications",
        "job_title", "job_experience_level", "job_tech_skills", "job_soft_skills",
        "job_qualifications", "job_responsibilities",
        "match_score", "key_strengths", "concerns", "skill_matches", "skill_gaps", "recommendation",
        "question"
    ],
    template=template,
)

chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
)

def format_list(items):
    """Helper to format lists for display"""
    if not items:
        return "Not specified"
    if isinstance(items, list):
        return ", ".join(str(item) for item in items) if items else "Not specified"
    return str(items)

def parse_candidate_data_from_file():
    """Parse the JSON data from candidate_data.txt file"""
    try:
        if not os.path.exists(FILE_PATH):
            logging.warning("Candidate data file not found.")
            return None, None
        
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        candidate_data = data.get("candidate", {})
        matching_data = data.get("matchingData", {})
        
        return candidate_data, matching_data
    
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON from {FILE_PATH}: {str(e)}")
        return None, None
    except Exception as e:
        logging.error(f"Error reading candidate data file: {str(e)}")
        return None, None

def ask_ai(question: str):
    try:
        # Read and parse the candidate data file
        candidate_data, matching_data = parse_candidate_data_from_file()
        
        if not candidate_data and not matching_data:
            return "I don't have any candidate information loaded yet. Please select a candidate first."
        
        # Extract candidate information
        candidate_name = candidate_data.get("name", "Unknown") if candidate_data else "Unknown"
        candidate_title = candidate_data.get("currentTitle", "Not specified") if candidate_data else "Not specified"
        
        candidate_experience = "Not specified"
        if candidate_data:
            exp_year = candidate_data.get("experienceYear")
            exp_level = candidate_data.get("experienceLevel", "")
            candidate_experience = f"{exp_year} years ({exp_level})" if exp_year else exp_level or "Not specified"
        
        candidate_location = candidate_data.get("location", "Not specified") if candidate_data else "Not specified"
        candidate_tech_skills = format_list(candidate_data.get("technicalSkills")) if candidate_data else "Not specified"
        candidate_soft_skills = format_list(candidate_data.get("softSkills")) if candidate_data else "Not specified"
        candidate_qualifications = format_list(candidate_data.get("qualification")) if candidate_data else "Not specified"
        
        # Extract job information from matching data
        job_title = "Not specified"
        job_experience_level = "Not specified"
        job_tech_skills = "Not specified"
        job_soft_skills = "Not specified"
        job_qualifications = "Not specified"
        job_responsibilities = "Not specified"
        
        if matching_data:
            job_title = matching_data.get("jobTitle", "Not specified")
            # Note: The file doesn't have detailed job requirements, so we'll use what's available
            # from the matching analysis
        
        # Extract matching information
        match_score = "Not available"
        key_strengths = "Not analyzed"
        concerns = "Not analyzed"
        skill_matches = "Not analyzed"
        skill_gaps = "Not analyzed"
        recommendation = "Not available"
        
        if matching_data:
            match_score = str(matching_data.get("overallMatchScore", "Not available"))
            
            # Try both locations for aiInsights (top level and in matchDetails)
            ai_insights = matching_data.get("aiInsights", {})
            if not ai_insights:
                match_details = matching_data.get("matchDetails", {})
                ai_insights = match_details.get("aiInsights", {})
            
            if ai_insights:
                # Format strengths
                strengths_list = ai_insights.get("strengths", [])
                if strengths_list:
                    key_strengths = "; ".join([s.get("point", "") for s in strengths_list if s.get("point")])
                
                # Format concerns
                concerns_list = ai_insights.get("concerns", [])
                concerns = "; ".join(concerns_list) if concerns_list else "None identified"
                
                # Format skill matches
                skill_matches_list = ai_insights.get("skillMatches", [])
                if skill_matches_list:
                    skill_matches = "; ".join([
                        f"{sm.get('candidateSkill', '')} matches {sm.get('jobRequirement', '')}"
                        for sm in skill_matches_list[:3]  # Limit to top 3
                    ])
                
                # Format skill gaps
                skill_gaps_list = ai_insights.get("skillGaps", [])
                skill_gaps = "; ".join(skill_gaps_list) if skill_gaps_list else "None identified"
                
                # Get recommendation
                recommendation = ai_insights.get("recommendation", "Not available")
                
                # Get reasoning summary for additional context
                reasoning = ai_insights.get("reasoningSummary", "")
                if reasoning and len(reasoning) > 200:
                    reasoning = reasoning[:200] + "..."

        # Create the chain and invoke
        chain = prompt | llm
        response = chain.invoke({
            "candidate_name": candidate_name,
            "candidate_title": candidate_title,
            "candidate_experience": candidate_experience,
            "candidate_location": candidate_location,
            "candidate_tech_skills": candidate_tech_skills,
            "candidate_soft_skills": candidate_soft_skills,
            "candidate_qualifications": candidate_qualifications,
            "job_title": job_title,
            "job_experience_level": job_experience_level,
            "job_tech_skills": job_tech_skills,
            "job_soft_skills": job_soft_skills,
            "job_qualifications": job_qualifications,
            "job_responsibilities": job_responsibilities,
            "match_score": match_score,
            "key_strengths": key_strengths,
            "concerns": concerns,
            "skill_matches": skill_matches,
            "skill_gaps": skill_gaps,
            "recommendation": recommendation,
            "question": question
        })
        
        return response.content

    except Exception as e:
        logging.error(f"Error in ask_ai: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in AI processing: {str(e)}")