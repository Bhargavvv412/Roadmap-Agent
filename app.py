import streamlit as st
import json
from agents.goal_parser import GoalParserAgent
from agents.topic_generator import TopicGeneratorAgent
from agents.resource_finder import ResourceFinderAgent
from agents.timeline_planner import TimelinePlannerAgent

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="AI Learning Roadmap Generator")
st.title("🎯 AI Learning Roadmap Generator")

# --- Agent Initialization ---
# We can cache these agents to make the app more efficient
@st.cache_resource
def load_agents():
    """Loads all agents once and caches them."""
    return {
        "goal_parser": GoalParserAgent(),
        "topic_gen": TopicGeneratorAgent(),
        "resource_finder": ResourceFinderAgent(),
        "timeline_planner": TimelinePlannerAgent()
    }

try:
    agents = load_agents()
except Exception as e:
    st.error(f"Error loading agents. Did you set your GOOGLE_API_KEY? Error: {e}")
    st.stop()

# --- User Input ---
user_goal = st.text_input(
    "Enter your learning goal:", 
    placeholder="e.g., Become a Data Scientist"
)

# --- Main App Logic ---
if st.button("Generate My Roadmap", type="primary"):
    if not user_goal:
        st.error("Please enter a learning goal.")
    else:
        # This will hold the final roadmap data
        st.session_state.final_roadmap = None 
        
        try:
            # --- STEP 1: Parse Goal ---
            st.info("Step 1/4: Analyzing your goal...")
            skills_json = None
            with st.spinner("Agent is identifying core skills..."):
                skills_json = agents["goal_parser"].parse_goal(user_goal)
            
            if not skills_json:
                st.error("Step 1 Failed: Could not parse goal. Please try a different prompt.")
                st.stop() # Halt execution
            
            st.success("Step 1 Complete: Goal and skills identified.")

            # --- STEP 2: Generate Topics ---
            st.info("Step 2/4: Generating a detailed topic roadmap...")
            roadmap_json = None
            with st.spinner("Agent is planning a comprehensive curriculum..."):
                roadmap_json = agents["topic_gen"].generate_topics(skills_json)

            if not roadmap_json:
                st.error("Step 2 Failed: Could not generate topics.")
                st.stop()

            st.success("Step 2 Complete: Topic roadmap created.")

            # --- STEP 3: Find Resources (The Slow Step) ---
            st.info("Step 3/4: Finding learning resources... (This may take several minutes!)")
            resources_json = None
            with st.spinner("Agent is searching for YouTube, courses, and GitHub repos..."):
                # This is the long-running process
                resources_json = agents["resource_finder"].find_resources(roadmap_json)
            
            if not resources_json:
                st.error("Step 3 Failed: Could not find resources. This might be an API limit.")
                st.stop()

            st.success("Step 3 Complete: Resources found.")

            # --- STEP 4: Plan Timeline ---
            st.info("Step 4/4: Compressing roadmap into a 12-week timeline...")
            timeline_json = None
            with st.spinner("Agent is scheduling your weeks..."):
                # This one is local and fast
                timeline_json = agents["timeline_planner"].plan_timeline(roadmap_json)
            
            if not timeline_json:
                st.error("Step 4 Failed: Could not plan timeline.")
                st.stop()

            st.success("Step 4 Complete: Final timeline created.")

            # --- Final Assembly ---
            st.balloons()
            st.header("🎉 Your Learning Roadmap is Ready!")
            
            # Safely parse all JSON strings
            skills_data = json.loads(skills_json)
            timeline_data = json.loads(timeline_json)
            resources_data = json.loads(resources_json)

            st.session_state.final_roadmap = {
                "goal": skills_data.get("goal", user_goal),
                "skills": skills_data.get("core_skills", []),
                "timeline": timeline_data.get("timeline", []),
                "resources": resources_data.get("resources", [])
            }

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            st.exception(e) # Show full traceback in the app


# --- Display the final roadmap (if it exists in session state) ---
if "final_roadmap" in st.session_state and st.session_state.final_roadmap:
    
    roadmap = st.session_state.final_roadmap
    
    st.divider()
    
    st.subheader(f"Your Goal: {roadmap['goal']}")
    st.write("### Core Skills to Master:")
    st.markdown(
        "\n".join(f"- **{skill}**" for skill in roadmap['skills'])
    )

    # Use columns for a clean layout
    col1, col2 = st.columns(2)

    with col1:
        st.write("### 🗓️ Your Weekly Timeline")
        
        # Group timeline by week
        weeks = {}
        for item in roadmap['timeline']:
            week_num = item['week']
            if week_num not in weeks:
                weeks[week_num] = []
            weeks[week_num].append(item)
        
        # Display timeline in expanders
        for week, items in sorted(weeks.items()):
            with st.expander(f"**Week {week}**"):
                for item in items:
                    st.markdown(f"**{item['topic']}**")
                    st.caption(item['description'])

    with col2:
        st.write("### 📚 Learning Resources")
        
        # Display resources in expanders
        for res in roadmap['resources']:
            with st.expander(f"**{res['topic']}**"):
                st.markdown(f"**YouTube:** {res['youtube']}")
                st.markdown(f"**Course:** {res['course']}")
                st.markdown(f"**GitHub:** {res['github']}")

 