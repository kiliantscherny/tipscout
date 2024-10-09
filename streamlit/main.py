import streamlit as st
import pandas as pd
import duckdb
import numpy as np

st.set_page_config(layout="wide")

st.title("Database Content Viewer")


def fetch_data(db_path):
    conn = duckdb.connect(db_path)
    try:
        tables = conn.execute("SHOW TABLES").fetchall()
        if not tables:
            return None, "No tables found in the database."
        
        table_name = tables[0][0]
        
        query = f"""
        SELECT
            *,
            sold + remaining AS total_available,
            remaining / (sold + remaining) AS left_percent,
            old_price - new_price AS discount_absolute,
            (old_price - new_price) / old_price AS discount_percent
        FROM
            {table_name}
        """
        df = conn.execute(query).df()

        return df, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


# Sidebar for user input
st.sidebar.header("Settings")
db_path = st.sidebar.text_input("Database Path", value="/app/data/tipsterdeals.duckdb")
refresh_button = st.sidebar.button("Refresh Data")

# Main content area
if refresh_button or "data" not in st.session_state:
    # Fetch data from the database if the refresh button is pressed or if data is not already in session state
    data, error = fetch_data(db_path)
    if error:
        st.error(f"Error: {error}")
    else:
        # Store the fetched data in session state
        st.session_state.data = data

# Check if data is available in session state
if "data" in st.session_state and st.session_state.data is not None:
    st.write(f"Displaying {len(st.session_state.data)} rows from the database:")

    # Display the data in a dataframe
    st.dataframe(st.session_state.data, use_container_width=True)

    # Display metrics
    st.subheader("Metrics")

    # Average saving as a percentage
    col1, col2, col3, col4 = st.columns(4)

    # Count of unique deal IDs
    with col1:
        unique_deal_ids = st.session_state.data["deal_id"].nunique()
        st.metric(label="Unique deals", value=unique_deal_ids)

    with col2:
        if (
            "old_price" in st.session_state.data.columns
            and "new_price" in st.session_state.data.columns
        ):
            average_saving_percentage = st.session_state.data["discount_percent"].mean()
            st.metric(
                label="Average Saving (%)",
                value=f"{average_saving_percentage*100:.2f}%",
            )
        else:
            st.warning(
                "Columns 'old_price' and 'new_price' are required to calculate the average saving percentage."
            )

    with col3:
        # Average old price
        # st.subheader("Average Old Price")
        avg_old_price = st.session_state.data["old_price"].mean()
        st.metric(label="Average Old Price", value=f"{avg_old_price:.2f} DKK")

    with col4:
        # Average new price
        # st.subheader("Average New Price")
        avg_new_price = st.session_state.data["new_price"].mean()
        st.metric(label="Average New Price", value=f"{avg_new_price:.2f} DKK")

    # Deals added each month
    st.subheader("Deals Added Each Month")
    deals_per_month = st.session_state.data.groupby(
        st.session_state.data["date_added"].dt.to_period("M")
    ).size()
    st.line_chart(deals_per_month)

    # Average saving percentage per month
    st.subheader("Average Saving Percentage Per Month")
    avg_saving_per_month = st.session_state.data.groupby(
        st.session_state.data["date_added"].dt.to_period("M")
    )["discount_percent"].mean()
    st.line_chart(avg_saving_per_month)

    # Top merchants by number of deals
    st.subheader("Top Merchants by Number of Deals")
    top_merchants = st.session_state.data["merchant_name"].value_counts().head(10)
    st.bar_chart(top_merchants)

    # Merchants with highest average savings
    st.subheader("Merchants with Highest Average Savings")
    avg_saving_by_merchant = (
        st.session_state.data.groupby("merchant_name")["discount_percent"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )
    st.bar_chart(avg_saving_by_merchant)

    # Distribution of savings percentages
    st.subheader("Distribution of Savings Percentages")
    hist_values, bin_edges = np.histogram(
        st.session_state.data["discount_percent"].dropna(), bins=20
    )
    st.bar_chart(pd.DataFrame({"count": hist_values}, index=bin_edges[:-1]))

    # Current status of deals
    st.subheader("Current Status of Deals")
    deal_status_counts = st.session_state.data["status"].value_counts()
    st.bar_chart(deal_status_counts)

    # Top locations by number of deals
    st.subheader("Top Locations by Number of Deals")
    top_locations = st.session_state.data["location"].value_counts().head(10)
    st.bar_chart(top_locations)

    # Average saving percentage by location
    st.subheader("Average Saving Percentage by Location")
    avg_saving_by_location = (
        st.session_state.data.groupby("location")["discount_percent"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )
    st.bar_chart(avg_saving_by_location)

    # Average time to sell out
    st.subheader("Average Time to Sell Out")
    if "sold_out_date" in st.session_state.data.columns:
        st.session_state.data["days_to_sell_out"] = (
            st.session_state.data["sold_out_date"] - st.session_state.data["date"]
        ).dt.days
        avg_days_to_sell_out = st.session_state.data["days_to_sell_out"].mean()
        st.metric(
            label="Average Days to Sell Out", value=f"{avg_days_to_sell_out:.2f} days"
        )
    else:
        st.warning(
            "Column 'sold_out_date' is required to calculate the average time to sell out."
        )
