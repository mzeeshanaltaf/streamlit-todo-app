import streamlit as st
from streamlit.connections import SQLConnection
from datetime import date
from typing import Optional
from dataclasses import dataclass

import sqlalchemy as sa
from sqlalchemy.engine import Row
from sqlalchemy import Table

from data import *

@dataclass
class Todo:
    id: Optional[int] = None
    title: str = ""
    description: Optional[str] = None
    created_at: Optional[date] = None
    due_date: Optional[date] = None
    done: bool = False

    @classmethod
    def from_row(cls, row: Row):
        if row:
            return cls(**row._mapping)
        return None

def create_todo_callback(connection:SQLConnection, table: Table):
    title = st.session_state["new_todo_form_title"]
    description = st.session_state["new_todo_form_description"]
    due_date = st.session_state["new_todo_form_due_date"]

    new_todo = {
        "title": title,
        "description": description,
        "created_at": date.today(),
        "due_date": due_date,
        "done": False,
    }

    stmt = table.insert().values(**new_todo)
    with connection.session as session:
        session.execute(stmt)
        session.commit()
    st.session_state["todo_data"] = load_all_todos(connection, table)

def load_all_todos(connection:SQLConnection, table: Table):
    stmt = sa.select(table).order_by(table.c.id)
    with connection.session as session:
        result = session.execute(stmt)
        all_todos = [Todo.from_row(row) for row in result]
        return {todo.id: todo for todo in all_todos}

def load_todos(connection:SQLConnection, table: Table, todo_id: int):
    stmt = sa.select(table).where(table.c.id == todo_id)
    with connection.session as session:
        result = session.execute(stmt)
        row = result.first()
        todo = Todo.from_row(row)
        return todo

def mark_done_callback(connection:SQLConnection, table: Table, todo_id: int):
    done_status = st.session_state['todo_data'][todo_id].done

    stmt = table.update().where(table.c.id == todo_id).values(done = not done_status)
    with connection.session as session:
        session.execute(stmt)
        session.commit()
    st.session_state["todo_data"][todo_id] = load_todos(connection, table, todo_id)

def switch_edit_callback(todo_id: int):
    st.session_state[f"currently_editing_{todo_id}"] = not st.session_state[f"currently_editing_{todo_id}"]

def update_todo_callback(connection:SQLConnection, table: Table, todo_id: int):
    updated_values = {
        "title": st.session_state[f"edit_todo_form_{todo_id}_title"],
        "description": st.session_state[f"edit_todo_form_{todo_id}_description"],
        "due_date": st.session_state[f"edit_todo_form_{todo_id}_due_date"],
    }
    stmt = table.update().where(table.c.id == todo_id).values(**updated_values)
    with connection.session as session:
        session.execute(stmt)
        session.commit()

    st.session_state["todo_data"][todo_id] = load_todos(connection, table, todo_id)
    switch_edit_callback(todo_id)

def delete_todo_callback(connection:SQLConnection, table: Table, todo_id: int):
    stmt = table.delete().where(table.c.id == todo_id)
    with connection.session as session:
        session.execute(stmt)
        session.commit()

    st.session_state["todo_data"] = load_all_todos(connection, table)

@st.fragment
def view_todo(todo_id: int, todo_table: Table):
    if f"currently_editing_{todo_id}" not in st.session_state:
        st.session_state[f"currently_editing_{todo_id}"] = False

    todo = st.session_state["todo_data"][todo_id]

    currently_editing = st.session_state[f"currently_editing_{todo_id}"]

    if not currently_editing:
        with st.container(border=True):
            st.subheader(todo.title)
            st.markdown(todo.description)
            st.markdown(todo.due_date)
            st.markdown(todo.done)

            done_col, edit_col, delete_col = st.columns(3)
            done_col.button("Done",
                            key=f"view_todo_{todo_id}_done",
                            use_container_width=True,
                            icon=":material/check_circle:",
                            type="primary",
                            on_click=mark_done_callback,
                            args=(conn, todo_table, todo_id))
            edit_col.button("Edit",
                            key=f"view_todo_{todo_id}_edit",
                            use_container_width=True,
                            icon=":material/edit:",
                            on_click=switch_edit_callback,
                            args=(todo_id,))
            if delete_col.button("Delete",
                              key=f"view_todo_{todo_id}_delete",
                              use_container_width=True,
                              icon=":material/delete:",
                            ):
                delete_todo_callback(conn, todo_table, todo_id)
                st.rerun(scope="app")
    if currently_editing:
        with st.form(f"update_{todo_id}"):
            st.subheader(f":material/edit: Editing Todo {todo.title}")
            st.text_input("Todo Title", key=f"edit_todo_form_{todo_id}_title", value=todo.title)
            st.text_area("Todo Description", key=f"edit_todo_form_{todo_id}_description", value=todo.description)
            st.date_input("Due Date", key=f"edit_todo_form_{todo_id}_due_date", value=todo.due_date)

            submit_col, cancel_col = st.columns(2)
            submit_col.form_submit_button("Edit Todo",
                                          type="primary",
                                          use_container_width=True,
                                          on_click=update_todo_callback,
                                          args=(conn, todo_table, todo_id))
            cancel_col.form_submit_button("Cancel",
                                          use_container_width=True,
                                          on_click=switch_edit_callback,
                                          args=(todo_id,))

