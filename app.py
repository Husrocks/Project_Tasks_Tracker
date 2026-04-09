import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from tracker_logic import Project, Task
from database_setup import create_tables  # <-- ADDED IMPORT

# ================= CONFIGURATION =================
st.set_page_config(page_title="TaskTracker Pro", page_icon="☑️", layout="wide")

# ================= INITIALIZE DATABASE =================
create_tables()  # <-- ADDED INITIALIZATION: Ensures DB exists before app runs

# ================= PROFESSIONAL CSS =================
st.markdown("""
    <style>
    /* 1. Global clean font & background */
    .stApp {
        background-color: #0e1117;
    }

    /* 2. Professional Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #1a1c24;
        border: 1px solid #2b2d3e;
        padding: 15px;
        border-radius: 8px;
        color: white;
        overflow-wrap: break-word;
    }
    [data-testid="stMetricLabel"] { color: #9ca3af !important; font-size: 0.9rem; }
    [data-testid="stMetricValue"] { color: #f3f4f6 !important; font-size: 1.8rem; }

    /* 3. Task Cards */
    .task-card {
        background-color: #1a1c24;
        border: 1px solid #2b2d3e;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    /* 4. Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        background-color: #1a1c24;
        border-radius: 4px;
        color: #9ca3af;
        border: 1px solid #2b2d3e;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
        border: none;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ================= HELPER FUNCTIONS =================
def get_priority_color(priority):
    if priority == "High": return "red"
    if priority == "Medium": return "orange"
    return "green"

def get_status_color(status, due_date_str):
    if status == "Completed": return "green"
    if due_date_str:
        try:
            due = date.fromisoformat(due_date_str)
            if due < date.today(): return "red"
        except:
            pass
    return "blue"

# ================= SIDEBAR =================
st.sidebar.header("TaskTracker")

projects = Project.get_all()
if not projects:
    st.warning("No projects found.")
    new_p = st.text_input("Create Project Name")
    if st.button("Create Project"):
        Project(new_p).save()
        st.rerun()
    st.stop()

project_dict = {name: pid for pid, name in projects}
selected_project_name = st.sidebar.selectbox("Select Project", list(project_dict.keys()))
current_project_id = project_dict[selected_project_name]

with st.sidebar.expander("Manage Projects"):
    new_p_name = st.text_input("New Project Name")
    if st.button("Create"):
        Project(new_p_name).save()
        st.success("Created!")
        st.rerun()
    
    if st.button("Delete Current Project", type="primary"):
        Project.delete(current_project_id)
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("v2.1 Enterprise Edition")

# ================= MAIN CONTENT =================
st.title(selected_project_name)

# 1. Fetch Data
tasks = Task.get_by_project(current_project_id)
df = pd.DataFrame(tasks, columns=['ID', 'Task', 'Description', 'Status', 'Priority', 'Due Date'])

# 2. Top Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Tasks", len(df))
m2.metric("Pending", len(df[df['Status']=='Pending']))
m3.metric("Completed", len(df[df['Status']=='Completed']))
m4.metric("High Priority", len(df[df['Priority']=='High']))

st.markdown("<br>", unsafe_allow_html=True)

# 3. Main Tabs
tab_add, tab_list, tab_analytics = st.tabs(["➕ Add Task", "📋 Task List", "📊 Analytics"])

# --- TAB 1: ADD TASK ---
with tab_add:
    st.markdown("##### New Task Details")
    with st.form("add_task_form", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        name = c1.text_input("Task Title")
        priority = c2.selectbox("Priority", ["High", "Medium", "Low"])
        
        desc = st.text_area("Description (Optional)")
        due_date = st.date_input("Due Date", value=date.today())
        
        if st.form_submit_button("Create Task", type="primary", use_container_width=True):
            if name:
                Task(current_project_id, name, desc, "Pending", priority, due_date).save()
                st.success("Task added successfully")
                st.rerun()
            else:
                st.error("Task title is required")

# --- TAB 2: PROFESSIONAL TASK LIST ---
with tab_list:
    # Filter Toolbar
    c1, c2, c3 = st.columns([2, 1, 1])
    search = c1.text_input("Search", placeholder="Filter by name...", label_visibility="collapsed")
    filter_status = c2.selectbox("Status", ["All", "Pending", "Completed"], label_visibility="collapsed")
    
    csv = df.to_csv(index=False).encode('utf-8')
    c3.download_button("📥 Export CSV", csv, "tasks.csv", "text/csv", use_container_width=True)

    filtered_df = df.copy()
    if search: filtered_df = filtered_df[filtered_df['Task'].str.contains(search, case=False)]
    if filter_status != "All": filtered_df = filtered_df[filtered_df['Status'] == filter_status]

    st.markdown("---")

    if not filtered_df.empty:
        for idx, row in filtered_df.iterrows():
            
            # EDIT MODE
            if st.session_state.get('edit_id') == row['ID']:
                with st.container():
                    with st.form(key=f"edit_form_{row['ID']}"):
                        st.subheader(f"Editing: {row['Task']}")
                        c_edit_1, c_edit_2 = st.columns([3, 1])
                        
                        new_name = c_edit_1.text_input("Task Name", value=row['Task'])
                        new_priority = c_edit_2.selectbox("Priority", ["High", "Medium", "Low"], 
                                                        index=["High", "Medium", "Low"].index(row['Priority']))
                        
                        new_desc = st.text_area("Description", value=row['Description'] if row['Description'] else "")
                        
                        try:
                            curr_date = date.fromisoformat(str(row['Due Date']))
                        except:
                            curr_date = date.today()
                        new_date = st.date_input("Due Date", value=curr_date)
                        
                        b_save, b_cancel = st.columns(2)
                        if b_save.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                            Task.update_details(row['ID'], new_name, new_desc, new_priority, new_date)
                            del st.session_state['edit_id']
                            st.rerun()
                            
                        if b_cancel.form_submit_button("❌ Cancel", use_container_width=True):
                            del st.session_state['edit_id']
                            st.rerun()
                st.divider()

            # VIEW MODE
            else:
                with st.container():
                    c_status, c_details, c_meta, c_actions = st.columns([0.2, 4, 1.5, 2.5])
                    
                    color = get_status_color(row['Status'], row['Due Date'])
                    c_status.markdown(f"""
                        <div style="height: 80px; width: 6px; background-color: {color}; border-radius: 3px;"></div>
                    """, unsafe_allow_html=True)

                    with c_details:
                        st.markdown(f"**{row['Task']}**")
                        if row['Description']:
                            st.caption(row['Description'])
                    
                    with c_meta:
                        st.caption(f"📅 {row['Due Date']}")
                        p_color = get_priority_color(row['Priority'])
                        st.markdown(f"<span style='color:{p_color}'>●</span> {row['Priority']}", unsafe_allow_html=True)

                    with c_actions:
                        b1, b2, b3 = st.columns(3)
                        
                        if row['Status'] == 'Pending':
                            if b1.button("Done", key=f"btn_c_{row['ID']}", use_container_width=True):
                                Task.update_status(row['ID'], "Completed")
                                st.rerun()
                        else:
                            if b1.button("Undo", key=f"btn_o_{row['ID']}", use_container_width=True):
                                Task.update_status(row['ID'], "Pending")
                                st.rerun()
                        
                        if b2.button("Edit", key=f"btn_e_{row['ID']}", use_container_width=True):
                            st.session_state['edit_id'] = row['ID']
                            st.rerun()

                        if b3.button("Del", key=f"btn_d_{row['ID']}", use_container_width=True):
                            Task.delete(row['ID'])
                            st.rerun()
                st.divider()
    else:
        st.info("No tasks found matching your filters.")

# --- TAB 3: ANALYTICS ---
with tab_analytics:
    if not df.empty:
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("##### Priority Breakdown")
            fig = px.pie(df, names='Priority', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown("##### Progress Status")
            status_count = df['Status'].value_counts().reset_index()
            status_count.columns = ['Status', 'Count']
            fig2 = px.bar(status_count, x='Status', y='Count', color='Status', 
                          color_discrete_map={'Pending':'#3b82f6', 'Completed':'#10b981'})
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Analytics will appear here once you create tasks.")