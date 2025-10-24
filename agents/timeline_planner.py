import json

class TimelinePlannerAgent:
    def plan_timeline(self, roadmap_json: str, total_weeks: int = 12):
        roadmap = json.loads(roadmap_json)
        step = len(roadmap["roadmap"]) // total_weeks or 1
        timeline = []
        for i, r in enumerate(roadmap["roadmap"], 1):
            week = (i - 1) // step + 1
            timeline.append({"week": week, "topic": r["topic"], "description": r["description"]})
        return json.dumps({"timeline": timeline}, indent=2)
