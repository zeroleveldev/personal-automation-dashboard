import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import os
import shutil
import json
from pathlib import Path

# Persistence paths
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
TASKS_FILE = DATA_DIR / "tasks.json"
BUDGET_FILE = DATA_DIR / "budget.csv"

# Load tasks on startup
if 'tasks' not in st.session_state:
    if TASKS_FILE.exists():
        with open(TASKS_FILE, "r") as f:
            st.session_state.tasks = json.load(f)
    else:
        st.session_state.tasks = []

# Function to save tasks whenever they change
def save_tasks():
    with open(TASKS_FILE, "w") as f:
        json.dump(st.session_state.tasks, f, indent=2)

# Page config - must be first command
st.set_page_config(
    page_title="Personal Automation Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title(" 🛠️ Automation Hub")
page = st.sidebar.radio(
    "Navigate",
    options=[
        "🏠 Home",
        "💰 Budget Tracker",
        "📅 Tasks & AI Prioritizer",
        "🌤️ Weather & Quick Widgets",
        "📁 File Organizer",
        "🤖 AI Motivation"
    ],
    index=0 # starts on Home
)

# Main content area
if page == "🏠 Home":
    st.title("🚀 Welcome to Your Personal Automation Dashboard!")
    st.markdown("""
    This is your all-in-one life automation hub built with **Python + Streamlit**.
    
    Features coming up:
    - Auto-organize your download folder
    - Live budget charts & expense tracking
    - Smart task prioritization with local AI
    - Daily weather widget
    - Motivational AI quotes (100% local!)
    """)
    
    with st.expander("Quick About"):
        st.markdown("""
        Built for beginners-to-intermediate coders.
        Runs locally, free AI via Ollama, no cloud costs.
        Deployable to Streamlit Cloud in minutes.
        """)

elif page == "📁 File Organizer":
    st.title("📁 File Organizer Automation")
    st.markdown("Click to auto-sort your **Downloads** folder into categories (Images, Docs, Archives, etc.). Safe — previews first!")
    
    downloads_path = os.path.expanduser("~/Downloads")  # works cross-platform
    if not os.path.exists(downloads_path):
        st.error("Downloads folder not found!")
    else:
        if st.button("Organize Downloads Now!", type="primary"):
            categories = {
                "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
                "Documents": [".pdf", ".doc", ".docx", ".txt", ".csv"],
                "Archives": [".zip", ".rar", ".7z"],
                "Code": [".py", ".js", ".html", ".css"],
                "Others": []  # catch-all
            }
            moved_count = 0
            with st.spinner("Organizing..."):
                for file in os.listdir(downloads_path):
                    file_path = os.path.join(downloads_path, file)
                    if os.path.isfile(file_path):
                        ext = os.path.splitext(file)[1].lower()
                        moved = False
                        for cat, exts in categories.items():
                            if ext in exts or (cat == "Others" and not moved):
                                dest_folder = os.path.join(downloads_path, cat)
                                os.makedirs(dest_folder, exist_ok=True)
                                shutil.move(file_path, os.path.join(dest_folder, file))
                                moved_count += 1
                                moved = True
            st.success(f"Organized {moved_count} files! Refresh folder to see magic. 🚀")

elif page == "💰 Budget Tracker":
    st.title("💰 Budget Tracker with Live Charts")
    st.markdown("Upload or edit your expenses (saved automatically).")
    
    uploaded_file = st.file_uploader("Upload budget CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.to_csv(BUDGET_FILE, index=False) # save it
        st.success("Budget saved!")
        st.rerun()
    
    # Load from saved file if exists
    if BUDGET_FILE.exists():
        df = pd.read_csv(BUDGET_FILE)
        df['Date'] = pd.to_datetime(df['Date'])
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        
        
        # Pie chart: expenses by category
        cat_summary = df.groupby('Category')['Amount'].sum().reset_index()
        fig_pie = px.pie(cat_summary, values='Amount', names='Category', title='Expenses by Category', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Line chart: spending over time
        time_summary = df.groupby(df['Date'].dt.to_period('M'))['Amount'].sum().reset_index()
        time_summary['Date'] = time_summary['Date'].astype(str)
        fig_line = px.line(time_summary, x='Date', y='Amount', title='Monthly Spending Trend', markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
        
        st.dataframe(df.style.format({"Amount": "${:.2f}"}))
    else:
        st.info("No budget data yet - upload a CSV to start tracking!")

elif page == "🌤️ Weather & Quick Widgets":
    st.title("🌤️ Weather + Quick Tasks")
    
    # Weather widget (Open-Meteo - no key needed!)
    st.subheader("Current Weather in Lake Elsinore")
    lat, lon = 33.6681, -117.3270  # Lake Elsinore coords
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code&timezone=America/Los_Angeles"
    try:
        resp = requests.get(url).json()
        current = resp['current']
        temp_c = current['temperature_2m']
        temp_f = (temp_c * 9/5) + 32 # Convet C to F
        hum = current['relative_humidity_2m']
        wcode = current['weather_code']
        
        # Simple emoji map (expand as needed)
        weather_emoji = "☀️" if wcode in [0,1] else "⛅" if wcode in [2,3] else "🌧️" if wcode >= 51 else "❓"
        
        st.metric(label=f"{weather_emoji} Temperature", value=f"{temp_f:.1f}°F")
        st.metric("Humidity", f"{hum}%")
        st.caption(f"Updated: {datetime.now().strftime('%I:%M %p %Z')}")
    except:
        st.error("Weather fetch failed — check connection!")
    
    # Quick Tasks widget
    st.subheader("Quick Tasks")
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []
    
    new_task = st.text_input("Add a task:")
    if st.button("Add Task") and new_task:
        st.session_state.tasks.append({"task": new_task, "done": False})
    
    for i, t in enumerate(st.session_state.tasks):
        col1, col2 = st.columns([8,1])
        done = col1.checkbox(t["task"], value=t["done"], key=f"task_{i}")
        if done != t["done"]:
            st.session_state.tasks[i]["done"] = done
        if col2.button("🗑", key=f"del_{i}"):
            del st.session_state.tasks[i]
            st.rerun()    

elif page == "🤖 AI Motivation":
    st.title("🤖 AI Daily Motivation Generator")
    st.markdown("Powered by local Ollama — 100% free & offline! Get your daily boost.")
    
    if st.button("Generate Motivation Quote", type="primary"):
        with st.spinner("AI thinking..."):
            try:
                import ollama  # ← import HERE, only when needed
                
                user_prompt = (
                    "Give me one short, original, uplifting daily motivation quote or message "
                    "tailored for a Python coder/developer. Keep it 1-3 sentences, energetic, "
                    "positive, and include at least one emoji. Make it feel personal and fun!"
                )

                stream = ollama.chat(
                    model='llama3.2:3b',
                    messages=[{'role': 'user', 'content': user_prompt}],
                    stream=True,
                    options={'temperature': 0.85, 'top_p': 0.92, 'num_predict': 120}
                )

                placeholder = st.empty()
                full_response = ""
                for chunk in stream:
                    if 'message' in chunk and 'content' in chunk['message']:
                        delta = chunk['message']['content']
                        full_response += delta
                        placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                st.balloons()

            except ImportError:
                st.error("Ollama Python library not installed. Run `pip install ollama` locally.")
            except Exception as e:
                st.warning("AI features work best when running locally with Ollama installed and running (`ollama serve` in a terminal).")
                st.info("On this deployed version (Streamlit Cloud), local AI isn't available — try it on your machine for the full experience! 🚀")
                st.caption(f"Error details (for debug): {str(e)}")

elif page == "📅 Tasks & AI Prioritizer":
    st.title("📅 Tasks & AI Prioritizer")
    
    st.subheader("Manage Your Tasks")
    
    # Add new task (clean layout)
    col_input, col_button = st.columns([4, 1])
    new_task = col_input.text_input("Add a new task:", key="new_task_input")
    if col_button.button("Add", use_container_width=True) and new_task.strip():
        st.session_state.tasks.append({"task": new_task.strip(), "done": False})
        save_tasks()
        st.rerun()
    
    if st.session_state.tasks:
        st.markdown("### Your Tasks")
        for i, t in enumerate(st.session_state.tasks):
            col_check, col_text, col_delete = st.columns([1, 6, 1])
            
            # Checkbox (no label, just box)
            done = col_check.checkbox(
                label="",
                value=t["done"],
                key=f"chk_{i}",
                help="Mark as done"
            )
            if done != t["done"]:
                st.session_state.tasks[i]["done"] = done
                save_tasks()
                st.rerun()
            
            # Show task with strikethrough if done
            task_style = f"~~{t['task']}~~" if t["done"] else f"**{t['task']}**"
            col_text.markdown(task_style)
            
            # Delete button
            if col_delete.button("🗑", key=f"del_{i}", help="Delete task"):
                del st.session_state.tasks[i]
                save_tasks()
                st.rerun()
        
        # ───────────────────────────────────────────────
        # AI Prioritize & Summarize button
        # ───────────────────────────────────────────────
        if st.button("✨ AI Prioritize & Summarize", type="primary"):
            with st.spinner("AI analyzing your tasks..."):
                try:
                    import ollama  # lazy import - only runs when button clicked
                    
                    pending_tasks = [t["task"] for t in st.session_state.tasks if not t["done"]]
                    if not pending_tasks:
                        st.info("No pending tasks to prioritize!")
                        st.stop()
                    
                    task_text = "\n".join(f"- {task}" for task in pending_tasks)
                    
                    user_prompt = (
                        f"Here are my current pending tasks:\n{task_text}\n\n"
                        "Summarize them briefly in one sentence, then assign each task a priority: "
                        "High (urgent/important), Medium, or Low. "
                        "Output in clean markdown bullet points with priority labels. "
                        "Be concise, helpful, and encouraging!"
                    )
                    
                    stream = ollama.chat(
                        model='llama3.2:3b',
                        messages=[{'role': 'user', 'content': user_prompt}],
                        stream=True,
                        options={
                            'temperature': 0.7,
                            'top_p': 0.9,
                            'num_predict': 200
                        }
                    )
                    
                    placeholder = st.empty()
                    full_response = ""
                    for chunk in stream:
                        if 'message' in chunk and 'content' in chunk['message']:
                            delta = chunk['message']['content']
                            full_response += delta
                            placeholder.markdown(full_response + "▌")  # typing cursor
                    
                    placeholder.markdown(full_response)
                    st.success("Priorities ready!")
                
                except ImportError:
                    st.error("Ollama library not found. Run `pip install ollama` locally.")
                
                except Exception as e:
                    st.warning(
                        "AI features work best when running **locally** with Ollama installed and running "
                        "(`ollama serve` in a separate terminal)."
                    )
                    st.info(
                        "On this deployed version (Streamlit Cloud), local AI isn't available — "
                        "try it on your machine for the full experience! 🚀"
                    )
                    st.caption(f"Error details (for debug): {str(e)}")
    
    else:
        st.info("No tasks yet — add one above!")
                      
    
# footer
st.markdown("---")
st.caption("Built by ZeroLevel | 2026 Streamlit Tutorial Series")