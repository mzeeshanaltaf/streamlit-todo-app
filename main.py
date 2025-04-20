import streamlit as st
from todo import *
from data import *

st.title("Todo App")
metadata_obj, todo_table = connect_table()

if "todo_data" not in st.session_state:
    st.session_state["todo_data"] = load_all_todos(conn, todo_table)

for todo_id in st.session_state["todo_data"].keys():
    view_todo(todo_id, todo_table)

with st.form("add_todo", clear_on_submit=True):
    st.subheader(":material/add_circle: Create Todo")
    st.text_input("Todo Title", key="new_todo_form_title")
    st.text_area("Todo Description", key="new_todo_form_description")
    st.date_input("Due Date", key="new_todo_form_due_date")
    st.form_submit_button("Create Todo", type="primary", on_click=create_todo_callback, args=(conn, todo_table))
