import streamlit as st
import duckdb

st.title("Database Content Checker")

conn = duckdb.connect('/app/data/deals.db')

st.write("Tables in the database:")
tables = conn.execute("SHOW TABLES").fetchall()
st.write(tables)

if tables:
    for table in tables:
        st.write(f"Contents of {table[0]}:")
        data = conn.execute(f"SELECT * FROM {table[0]} LIMIT 5").fetchall()
        st.write(data)
else:
    st.write("No tables found in the database.")

conn.close()