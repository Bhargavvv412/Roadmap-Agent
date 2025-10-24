from agno.agent import Agent
from agno.models.google import Gemini
import json
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") 
if not api_key:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    exit()

class GoalParserAgent:
    def __init__(self):
        # Pass the API key to the model
        self.agent = Agent(
            model=Gemini(api_key=api_key), 
            name="Goal Parser Agent",
            description="Extracts core learning goal and key skills."
        )

    def parse_goal(self, user_goal: str):
        prompt = f"""
            User Goal: {user_goal}
            Extract the main career path and list 5 core subskills.
            Respond ONLY with the raw JSON object, without markdown code fences (```), 
            or any other explanatory text.
            The JSON structure must be:
            {{
                "goal": "....",
                "core_skills": ["", "", "", "", ""]
            }}
        """
        
        try:
            result = self.agent.run(prompt)
            raw_content = result.content
            
            start_index = raw_content.find('{')
            end_index = raw_content.rfind('}')
            
            if start_index != -1 and end_index != -1 and end_index > start_index:
                json_string = raw_content[start_index : end_index + 1]
                return json_string
            else:
                # If no JSON object is found, return the problematic content for debugging
                print("Error: Could not find valid JSON object in agent response.")
                return raw_content

        except Exception as e:
            print(f"An error occurred during agent run: {e}")
            return None
    

if __name__ == "__main__":
    parser = GoalParserAgent()
    example_user_goal = "I want to become a successful ai ml who can build scalable and secure applications from scratch."
    
    print("--- Sending Goal to Agent ---")
    json_result_string = parser.parse_goal(example_user_goal)
    
    if json_result_string:
        print("\n--- Agent's Cleaned Output (JSON String) ---")
        print(json_result_string)
        
        try:
            # This should now succeed
            data = json.loads(json_result_string)
            print("\n--- Parsed Python Dictionary (Success!) ---")
            print(json.dumps(data, indent=4))
        except json.JSONDecodeError as e:
            print(f"\nError: Still failed to parse JSON. Details: {e}")
            print("This can happen if the agent's output is not valid JSON (e.g., missing comma, trailing comma).")
    else:
        print("\nError: Did not receive any content from the agent.")