import streamlit as st
import requests

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="To-Do List", page_icon="📝", layout="centered")

st.title("📝 To-Do List App (FastAPI + Streamlit)")

# ---------- Add Task ----------
st.header("➕ Add a New Task")
with st.form("add_task_form"):
    title = st.text_input("Title")
    description = st.text_area("Description")
    submitted = st.form_submit_button("Add Task")
    if submitted:
        if title.strip():
            response = requests.post(f"{API_URL}/tasks/", json={"title": title, "description": description})
            if response.status_code == 200:
                st.success("Task added successfully!")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        else:
            st.warning("Title cannot be empty.")

# ---------- Get Tasks ----------
st.header("📋 Current Tasks")
response = requests.get(f"{API_URL}/tasks/")
if response.status_code == 200:
    tasks = response.json()
    if not tasks:
        st.info("No tasks yet. Add one above!")
    for task in tasks:
        with st.expander(f"{'✅' if task['completed'] else '⬜'} {task['title']}"):
            st.write(f"**Description:** {task['description'] or 'No description'}")
            st.write(f"**Completed:** {task['completed']}")

            # Update Task
            new_title = st.text_input(f"Edit Title {task['id']}", task["title"], key=f"title_{task['id']}")
            new_desc = st.text_area(f"Edit Description {task['id']}", task["description"] or "", key=f"desc_{task['id']}")
            new_status = st.checkbox("Completed", value=task["completed"], key=f"status_{task['id']}")
            if st.button("Update Task", key=f"update_{task['id']}"):
                update_payload = {"title": new_title, "description": new_desc, "completed": new_status}
                r = requests.put(f"{API_URL}/tasks/{task['id']}", json=update_payload)
                if r.status_code == 200:
                    st.success("Task updated! Refresh to see changes.")
                else:
                    st.error("Failed to update task.")

            # Delete Task
            if st.button("🗑️ Delete Task", key=f"delete_{task['id']}"):
                r = requests.delete(f"{API_URL}/tasks/{task['id']}")
                if r.status_code == 200:
                    st.success("Task deleted! Refresh to see changes.")
                else:
                    st.error("Failed to delete task.")
else:
    st.error("Could not fetch tasks from API.")
