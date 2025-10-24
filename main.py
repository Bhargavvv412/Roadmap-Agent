from agents.goal_parser import GoalParserAgent
from agents.topic_generator import TopicGeneratorAgent
from agents.resource_finder import ResourceFinderAgent
from agents.timeline_planner import TimelinePlannerAgent
import json

def generate_roadmap(user_goal):
    goal_parser = GoalParserAgent()
    topic_gen = TopicGeneratorAgent()
    resource_finder = ResourceFinderAgent()
    timeline_planner = TimelinePlannerAgent()

    skills = goal_parser.parse_goal(user_goal)
    roadmap = topic_gen.generate_topics(skills)
    resources = resource_finder.find_resources(roadmap)
    timeline = timeline_planner.plan_timeline(roadmap)

    final_output = {
        "goal": json.loads(skills)["goal"],
        "skills": json.loads(skills)["core_skills"],
        "timeline": json.loads(timeline)["timeline"],
        "resources": json.loads(resources)["resources"]
    }
    return final_output

if __name__ == "__main__":
    goal = input("🎯 Enter your learning goal: ")
    roadmap = generate_roadmap(goal)
    print(json.dumps(roadmap, indent=2))
