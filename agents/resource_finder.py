import json
from agno.agent import Agent
from agno.models.google import Gemini
import os
from dotenv import load_dotenv
import time # Import time for rate limiting

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") 
if not api_key:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    exit()

class ResourceFinderAgent:
    """
    Finds specific learning resources for a list of topics
    by calling an agent for each topic individually and respecting
    API rate limits.
    """
    def __init__(self):
        # FIX 1: You must pass the api_key to the model
        self.agent = Agent(
            model=Gemini(api_key=api_key),
            name="Resource Finder Agent",
            description="Finds one YouTube, course, and GitHub resource for a topic."
        )
        
    def _find_single_resource(self, topic: str):
        """
        Private helper method to find resources for *one* topic.
        This is more reliable than batching.
        """
        
        # This prompt is hyper-focused on one topic and demands JSON.
        prompt = f"""
        Find the best beginner-friendly resources for this single topic: "{topic}"
        
        Suggest exactly:
        1. One high-quality YouTube tutorial or channel (just the name).
        2. One comprehensive online course (e.g., Udemy, Coursera, or official docs).
        3. One practical GitHub project or repository (just the name or "user/repo").
        
        Respond ONLY with the raw JSON object, without markdown code fences (```)
        or any other explanatory text. The format must be:
        {{
            "topic": "{topic}",
            "youtube": "...",
            "course": "...",
            "github": "..."
        }}
        """
        try:
            result = self.agent.run(prompt)
            raw_content = result.content
            
            # Clean the JSON output from the agent
            start_index = raw_content.find('{')
            end_index = raw_content.rfind('}')
            
            if start_index != -1 and end_index != -1 and end_index > start_index:
                json_string = raw_content[start_index : end_index + 1]
                
                # FIX 2: Add extra error handling for bad agent JSON
                # This fixes your "Expecting ',' delimiter" error
                try:
                    return json.loads(json_string) # Return the parsed dictionary
                except json.JSONDecodeError as e:
                    print(f"Error: Agent returned invalid JSON for '{topic}'. Error: {e}")
                    print(f"Raw output: {raw_content}")
                    return None
            else:
                print(f"Error: Could not find JSON in response for '{topic}'")
                return None
                
        except Exception as e:
            # This catches API errors like the 429
            print(f"Agent API error for '{topic}': {e}")
            return None

    def find_resources(self, roadmap_json: str):
        """
        Iterates through the roadmap and finds resources for each topic.
        """
        try:
            roadmap = json.loads(roadmap_json)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid roadmap JSON provided to find_resources. {e}")
            return json.dumps({"error": "Invalid input JSON"}, indent=2)
            
        topics = [r["topic"] for r in roadmap.get("roadmap", [])]
        
        if not topics:
            print("No topics found in roadmap.")
            return json.dumps({"resources": []}, indent=2)
            
        all_resources = []
        
        print(f"--- Finding resources for {len(topics)} topics (with 5 sec delay) ---")
        for i, topic in enumerate(topics):
            print(f"Searching for: '{topic}' ({i+1}/{len(topics)})...")
            
            resource_data = self._find_single_resource(topic)
            
            if resource_data:
                all_resources.append(resource_data)
                
            # FIX 3: Change sleep time to 5 seconds
            # The free tier limit is 15 req/min (4s/req). 5s is safer.
            time.sleep(5) 
            
        print("--- Resource finding complete ---")
        return json.dumps({"resources": all_resources}, indent=2)