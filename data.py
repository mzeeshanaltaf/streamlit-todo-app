import streamlit as st

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table

TABLE_NAME = "todo_table"
conn = st.connection("todo_db")


@st.cache_resource
def connect_table():
    metadata_obj = MetaData()
    todo_table = Table(
        TABLE_NAME,
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("title", String),
        Column("description", String),
        Column("created_at", Date),
        Column("due_date", Date),
        Column("done", Boolean),
    )
    return metadata_obj, todo_table

# metadata_obj.create_all(bind=conn.engine)