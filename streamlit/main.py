import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(layout="wide")

st.title("Database Content Viewer")


# Function to fetch data from the database
def fetch_data(db_path, row_limit):
    conn = duckdb.connect(db_path)
    try:
        # Get table names
        tables = conn.execute("SHOW TABLES").fetchall()
        if not tables:
            return None, "No tables found in the database."

        # Assume we're interested in the first table
        table_name = tables[0][0]

        # Fetch data
        query = f"SELECT * FROM {table_name} LIMIT {row_limit}"
        df = conn.execute(query).df()

        return df, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


# Sidebar for user input
st.sidebar.header("Settings")
db_path = st.sidebar.text_input("Database Path", value="/app/data/deals.db")
row_limit = st.sidebar.number_input("Number of Rows to Display", min_value=1, value=10)
refresh_button = st.sidebar.button("Refresh Data")

# Main content area
if refresh_button or "data" not in st.session_state:
    data, error = fetch_data(db_path, row_limit)
    if error:
        st.error(f"Error: {error}")
    else:
        st.session_state.data = data

if "data" in st.session_state and st.session_state.data is not None:
    st.write(f"Displaying {len(st.session_state.data)} rows from the database:")

    # Display the data
    st.dataframe(st.session_state.data, use_container_width=True)

    # Display summary statistics
    st.subheader("Summary Statistics")
    st.write(st.session_state.data.describe())

    # Display column information
    st.subheader("Column Information")
    column_info = pd.DataFrame(
        {
            "Column Name": st.session_state.data.columns,
            "Data Type": st.session_state.data.dtypes,
            "Non-Null Count": st.session_state.data.count(),
            "Null Count": st.session_state.data.isnull().sum(),
        }
    )
    st.table(column_info)

else:
    st.info("No data to display. Please check the database path and try refreshing.")
