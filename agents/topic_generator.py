from agno.agent import Agent
from agno.models.google import Gemini
import json
import os
from dotenv import load_dotenv

# --- API Key Setup ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") 
if not api_key:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    exit()

# --- Agent Definition ---
class TopicGeneratorAgent:
    """
    An agent that takes a JSON string containing a career goal and
    a list of core skills, then generates a structured weekly
    learning roadmap as a new JSON string.
    """
    def __init__(self):
        self.agent = Agent(
            model=Gemini(api_key=api_key),
            name="Topic Generator Agent",
            description="Generates a weekly learning roadmap from a goal and skill list."
        )
        
    def generate_topics(self, skills_json: str):
        """
        Parses the input JSON, sends the goal and skills to the 
        Gemini model, and returns a JSON string of the roadmap.
        """
        
        try:
            skills_data = json.loads(skills_json)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid input JSON. Could not parse. Details: {e}")
            return None

        goal = skills_data.get('goal', 'the specified goal')
        skill_list = skills_data.get('core_skills', [])

        if not skill_list:
            print("Error: No 'core_skills' found in the input JSON.")
            return None

        skills_str = ", ".join(skill_list)

        prompt = f"""
        You are an expert curriculum planner. Your task is to create a detailed, 
        structured weekly roadmap for a student trying to achieve the following goal:
        
        GOAL: "{goal}"
        
        The student needs to master these CORE SKILLS:
        {skills_str}
        
        Create a logical, week-by-week roadmap. Break down EACH core skill into 
        specific weekly topics with a short, clear description for each topic. 
        The plan should be comprehensive and flow logically.
        
        Respond ONLY with the raw JSON object, without markdown code fences (```)
        or any other explanatory text. The JSON format must be:
        {{
            "roadmap": [
                {{"week": 1, "skill_focus": "Name of Core Skill", "topic": "Specific Topic", "description": "Brief one-sentence description..." }},
                {{"week": 2, "skill_focus": "Name of Core Skill", "topic": "Next Topic", "description": "..." }},
                ...
            ]
        }}
        """
        
        try:
            result = self.agent.run(prompt)
            raw_content = result.content
            
            # --- Proactive JSON Cleaning ---
            # Add the same robust cleaning to extract the JSON object
            start_index = raw_content.find('{')
            end_index = raw_content.rfind('}')
            
            if start_index != -1 and end_index != -1 and end_index > start_index:
                json_string = raw_content[start_index : end_index + 1]
                return json_string
            else:
                print("Error: Could not find valid JSON object in agent response.")
                return raw_content # Return for debugging

        except Exception as e:
            print(f"An error occurred during agent run: {e}")
            return None