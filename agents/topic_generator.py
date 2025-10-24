from agno.agent import Agent
from agno.models.google import Gemini
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") 
if not api_key:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    exit()

class TopicGeneratorAgent:
    def __init__(self):
        self.agent = Agent(model=Gemini(api_key=api_key),
                    name= "Topic Generator Agent"
                    )
        
    def generate_topics(self,skills_json: str):
        skills = json.load(skills_json)
        goal = skills['goal']
        skill_list = skills["core_skills"]

        propmt = """
        Create a structured roadmap for becoming a {goal}.
        Divide each skill into weekly topics with short descriptions.
        Output in JSON:
        {{
            "roadmap": [
                {{"week": 1, "topic": "Python Basics", "description": "..." }},
                ...
            ]
        }}
        """
        result = self.agent.run(propmt)
        return result.content
    
