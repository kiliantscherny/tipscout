import streamlit as st
import pandas as pd
import duckdb
import numpy as np
import altair as alt
import os

st.set_page_config(layout="wide")

st.title("tipscout Statistics")


def fetch_data(db_path):
    conn = duckdb.connect(db_path, read_only=True)
    try:
        tables = conn.execute("SHOW TABLES").fetchall()
        if not tables:
            return None, "No tables found in the database."

        table_name = tables[0][0]

        query = f"""
        SELECT
            *,
            sold + remaining AS total_available,
            remaining / (sold + remaining) AS remaining_percent,
            old_price - new_price AS discount_absolute,
            (old_price - new_price) / old_price AS discount_percent
        FROM
            {table_name}
        QUALIFY ROW_NUMBER() OVER (PARTITION BY deal_id ORDER BY inserted_at DESC) = 1
        """
        df = conn.execute(query).df()

        return df, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


# Sidebar for user input
# Determine if running in Docker
if os.path.exists("/.dockerenv"):
    st.sidebar.image("/app/images/tipscout-logo.png", use_column_width=True)
    db_path = st.sidebar.text_input(
        "Database Path", value="/app/data/tipsterdeals.duckdb"
    )
else:
    st.sidebar.image("images/tipscout-logo.png", use_column_width=True)
    db_path = st.sidebar.text_input(
        "Database Path", value="airflow/data/tipsterdeals.duckdb"
    )
refresh_button = st.sidebar.button("Refresh Data")

st.sidebar.markdown(
    """
    <style>
        /* Target only the links inside the sidebar */
        section[data-testid="stSidebar"] a {
            color: white !important;
            font-weight: bold;
            text-decoration: none;
            text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
        }
        /* Override visited and active link colors */
        section[data-testid="stSidebar"] a:link,
        section[data-testid="stSidebar"] a:visited,
        section[data-testid="stSidebar"] a:hover,
        section[data-testid="stSidebar"] a:active {
            color: white !important;
        }
    </style>
    <a href="https://github.com/kiliantscherny/tipscout" target="_blank">
        <img src="https://cdn-icons-png.flaticon.com/128/5968/5968866.png" width="25" style="margin-right: 10px;">
        tipscout GitHub Repo
    </a> <br>
    <a href="https://www.linkedin.com/in/kiliantscherny" target="_blank">
        <img src="https://cdn-icons-png.flaticon.com/128/3536/3536505.png" width="25" style="margin-right: 10px;">
        Find me on LinkedIn
    </a>
    """,
    unsafe_allow_html=True,
)


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
    # Check if not running in Docker and display a warning box
    if not os.path.exists("/.dockerenv"):
        st.warning("⚠️ Heads up: This data is not updated in real-time.")

    # Filter for active deals
    active_deals_df = st.session_state.data[st.session_state.data["status"] == "ACTIVE"]

    if not active_deals_df.empty:
        st.subheader("Active Deals")
        # Create a new DataFrame with deal_id, merchant name, number remaining, number sold, total available, discount percentage, remaining percentage, and full_url as a link
        active_deals_display = active_deals_df[
            [
                "deal_id",
                "merchant_name",
                "total_available",
                "sold",
                "remaining",
                "remaining_percent",
                "discount_percent",
                "full_url",
            ]
        ].copy()

        # Convert discount_percent and remaining_percent to percentage format
        active_deals_display["discount_percent"] = (
            active_deals_display["discount_percent"] * 100
        )
        active_deals_display["discount_percent"] = active_deals_display[
            "discount_percent"
        ].map("{:.2f}%".format)

        # Apply color based on remaining_percent before converting to string
        def color_remaining(val):
            color = "red" if val <= 0.2 else "orange" if val <= 0.5 else "green"
            return f"background-color: {color}"

        # Apply color based on discount_percent before converting to string
        def color_discount(val):
            color = "green" if val >= 50 else "orange" if val >= 20 else "red"
            return f"background-color: {color}"

        active_deals_display["remaining_percent"] = (
            active_deals_display["remaining_percent"] * 100
        )
        active_deals_display["remaining_percent"] = active_deals_display[
            "remaining_percent"
        ].map("{:.2f}%".format)

        active_deals_display["full_url"] = active_deals_display.apply(
            lambda row: f'<a href="{row["full_url"]}" target="_blank">{row["full_url"]}</a>',
            axis=1,
        )

        # Clean up column names
        active_deals_display.columns = [
            "Deal ID",
            "Merchant Name",
            "Total Available",
            "Sold",
            "Remaining",
            "Remaining Percent",
            "Discount Percent",
            "Link to Deal",
        ]

        # Apply color formatting
        styled_df = active_deals_display.style.applymap(
            lambda x: color_remaining(float(x.strip("%")) / 100) if "%" in x else "",
            subset=["Remaining Percent"],
        ).applymap(
            lambda x: color_discount(float(x.strip("%"))) if "%" in x else "",
            subset=["Discount Percent"],
        )

        # Display the DataFrame with links and color formatting
        st.write(
            styled_df.to_html(escape=False, index=False),
            unsafe_allow_html=True,
        )
    else:
        st.warning("No active deals found.")

    # Active, expired, and sold out deals
    st.subheader("Deal Status Overview")
    if "status" in st.session_state.data.columns:
        status_counts = st.session_state.data["status"].value_counts()
        active_deals = status_counts.get("ACTIVE", 0)
        expired_deals = status_counts.get("EXPIRED", 0)
        sold_out_deals = status_counts.get("SOLD OUT", 0)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Active Deals", value=active_deals)
        with col2:
            st.metric(label="Expired Deals", value=expired_deals)
        with col3:
            st.metric(label="Sold Out Deals", value=sold_out_deals)
    else:
        st.warning("Column 'status' is required to calculate deal status overview.")

    # Display metrics
    st.subheader("Metrics")

    # Average saving as a percentage
    col1, col2, col3, col4 = st.columns(4)

    # Count of unique deal IDs
    with col1:
        if "date_added" in st.session_state.data.columns:
            # Ensure date_added is in datetime format
            st.session_state.data["date_added"] = pd.to_datetime(
                st.session_state.data["date_added"]
            )

            # Get the latest month and the previous month
            latest_month = st.session_state.data["date_added"].dt.to_period("M").max()
            previous_month = latest_month - 1

            # Count unique deals for the latest month
            latest_month_data = st.session_state.data[
                st.session_state.data["date_added"].dt.to_period("M") == latest_month
            ]
            unique_deals_latest_month = latest_month_data["deal_id"].nunique()

            # Count unique deals for the previous month
            previous_month_data = st.session_state.data[
                st.session_state.data["date_added"].dt.to_period("M") == previous_month
            ]
            unique_deals_previous_month = previous_month_data["deal_id"].nunique()

            # Calculate the difference
            difference = unique_deals_latest_month - unique_deals_previous_month
            delta = f"{difference} deals"

            # Display the metric with the difference
            st.metric(
                label="Unique Deals Latest Month",
                value=unique_deals_latest_month,
                delta=delta,
            )
        else:
            st.warning(
                "Column 'date_added' is required to calculate unique deals per month."
            )

    with col2:
        if (
            "old_price" in st.session_state.data.columns
            and "new_price" in st.session_state.data.columns
            and "date_added" in st.session_state.data.columns
        ):
            # Ensure date_added is in datetime format
            st.session_state.data["date_added"] = pd.to_datetime(
                st.session_state.data["date_added"]
            )

            # Get the latest month and the previous month
            latest_month = st.session_state.data["date_added"].dt.to_period("M").max()
            previous_month = latest_month - 1

            # Calculate average saving percentage for the latest month
            latest_month_data = st.session_state.data[
                st.session_state.data["date_added"].dt.to_period("M") == latest_month
            ]
            latest_month_avg_saving = latest_month_data["discount_percent"].mean()

            # Calculate average saving percentage for the previous month
            previous_month_data = st.session_state.data[
                st.session_state.data["date_added"].dt.to_period("M") == previous_month
            ]
            previous_month_avg_saving = previous_month_data["discount_percent"].mean()

            # Calculate the difference
            difference = latest_month_avg_saving - previous_month_avg_saving
            delta = f"{difference*100:.2f}%"

            # Display the metric with the difference
            st.metric(
                label="Avg Saving Latest Month (%)",
                value=f"{latest_month_avg_saving*100:.2f}%",
                delta=delta,
            )
        else:
            st.warning(
                "Columns 'old_price', 'new_price', and 'date_added' are required to calculate the average saving percentages."
            )

    with col3:
        if (
            "old_price" in st.session_state.data.columns
            and "date_added" in st.session_state.data.columns
        ):
            # Ensure date_added is in datetime format
            st.session_state.data["date_added"] = pd.to_datetime(
                st.session_state.data["date_added"]
            )

            # Get the latest month and the previous month
            latest_month = st.session_state.data["date_added"].dt.to_period("M").max()
            previous_month = latest_month - 1

            # Calculate average old price for the latest month
            latest_month_data = st.session_state.data[
                st.session_state.data["date_added"].dt.to_period("M") == latest_month
            ]
            latest_month_avg_old_price = latest_month_data["old_price"].mean()

            # Calculate average old price for the previous month
            previous_month_data = st.session_state.data[
                st.session_state.data["date_added"].dt.to_period("M") == previous_month
            ]
            previous_month_avg_old_price = previous_month_data["old_price"].mean()

            # Calculate the difference
            difference = latest_month_avg_old_price - previous_month_avg_old_price
            delta = f"{difference:.2f} DKK"

            # Display the metric with the difference
            st.metric(
                label="Average Old Price",
                value=f"{latest_month_avg_old_price:.2f} DKK",
                delta=delta,
                delta_color="inverse",
            )
        else:
            st.warning(
                "Columns 'old_price' and 'date_added' are required to calculate the average old price."
            )

    with col4:
        if (
            "new_price" in st.session_state.data.columns
            and "date_added" in st.session_state.data.columns
        ):
            # Ensure date_added is in datetime format
            st.session_state.data["date_added"] = pd.to_datetime(
                st.session_state.data["date_added"]
            )

            # Get the latest month and the previous month
            latest_month = st.session_state.data["date_added"].dt.to_period("M").max()
            previous_month = latest_month - 1

            # Calculate average new price for the latest month
            latest_month_data = st.session_state.data[
                st.session_state.data["date_added"].dt.to_period("M") == latest_month
            ]
            latest_month_avg_new_price = latest_month_data["new_price"].mean()

            # Calculate average new price for the previous month
            previous_month_data = st.session_state.data[
                st.session_state.data["date_added"].dt.to_period("M") == previous_month
            ]
            previous_month_avg_new_price = previous_month_data["new_price"].mean()

            # Calculate the difference
            difference = latest_month_avg_new_price - previous_month_avg_new_price
            delta = f"{difference:.2f} DKK"

            # Display the metric with the difference
            st.metric(
                label="Average New Price",
                value=f"{latest_month_avg_new_price:.2f} DKK",
                delta=delta,
                delta_color="inverse",
            )
        else:
            st.warning(
                "Columns 'new_price' and 'date_added' are required to calculate the average new price."
            )

    # Deals added each month with data labels
    col5, col6 = st.columns(2)

    with col5:
        st.subheader("Unique Deals Added Each Month")
        unique_deals_per_month = (
            st.session_state.data.groupby(
                st.session_state.data["date_added"].dt.to_period("M")
            )["deal_id"]
            .nunique()
            .reset_index(name="unique_deals")
        )

        # Convert Period to datetime for Altair
        unique_deals_per_month["date_added"] = unique_deals_per_month[
            "date_added"
        ].dt.to_timestamp()

        # Plotting with points and data labels
        unique_deals_chart = (
            alt.Chart(unique_deals_per_month)
            .mark_line()
            .encode(
                x=alt.X("date_added:T", title="Month", axis=alt.Axis(format="%b %Y")),
                y=alt.Y("unique_deals:Q", title="Number of Unique Deals"),
            )
            .properties(title="Unique Deals Added Each Month")
        )

        points = unique_deals_chart.mark_point().encode(
            tooltip=["date_added:T", "unique_deals:Q"]
        )

        labels = unique_deals_chart.mark_text(
            align="left", baseline="middle", dx=5
        ).encode(text="unique_deals:Q")

        st.altair_chart(unique_deals_chart + points + labels, use_container_width=True)

    with col6:
        # Average saving percentage per month with data labels
        st.subheader("Average Saving Percentage Per Month")
        avg_saving_per_month = (
            st.session_state.data.groupby(
                st.session_state.data["date_added"].dt.to_period("M")
            )["discount_percent"]
            .mean()
            .reset_index(name="avg_saving")
        )

        # Convert Period to datetime for Altair
        avg_saving_per_month["date_added"] = avg_saving_per_month[
            "date_added"
        ].dt.to_timestamp()

        # Plotting with points and data labels
        avg_saving_chart = (
            alt.Chart(avg_saving_per_month)
            .mark_line()
            .encode(
                x=alt.X("date_added:T", title="Month", axis=alt.Axis(format="%b %Y")),
                y=alt.Y(
                    "avg_saving:Q",
                    title="Average Saving (%)",
                    axis=alt.Axis(format="%"),
                ),
            )
            .properties(title="Average Saving Percentage Per Month")
        )

        points = avg_saving_chart.mark_point().encode(
            tooltip=[
                alt.Tooltip("date_added:T", title="Month"),
                alt.Tooltip("avg_saving:Q", title="Average Saving (%)", format=".2%"),
            ]
        )

        labels = avg_saving_chart.mark_text(
            align="left", baseline="middle", dx=5
        ).encode(text=alt.Text("avg_saving:Q", format=".2%"))

        st.altair_chart(avg_saving_chart + points + labels, use_container_width=True)

    # Top merchants by number of deals and merchants with highest average savings
    col7, col8 = st.columns(2)

    with col7:
        st.subheader("Top Merchants by Number of Deals")
        top_merchants = (
            st.session_state.data["merchant_name"].value_counts().head(10).reset_index()
        )
        top_merchants.columns = ["merchant_name", "deal_count"]

        # Convert deal_count to integers
        top_merchants["deal_count"] = top_merchants["deal_count"].astype(int)

        # Create a horizontal bar chart using Altair
        top_merchants_chart = (
            alt.Chart(top_merchants)
            .mark_bar()
            .encode(
                x=alt.X(
                    "deal_count:Q", title="Number of Deals", axis=alt.Axis(format="d")
                ),
                y=alt.Y("merchant_name:N", sort="-x", title="Merchant Name"),
                tooltip=["merchant_name:N", "deal_count:Q"],
            )
            .properties(title="Top Merchants by Number of Deals")
        )

        st.altair_chart(top_merchants_chart, use_container_width=True)

    with col8:
        st.subheader("Merchants with Highest Average Savings")
        avg_saving_by_merchant = (
            st.session_state.data.groupby("merchant_name")["discount_percent"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        # Create a horizontal bar chart using Altair with adjusted x-axis scale
        avg_saving_by_merchant_chart = (
            alt.Chart(avg_saving_by_merchant)
            .mark_bar()
            .encode(
                x=alt.X(
                    "discount_percent:Q",
                    title="Average Saving (%)",
                    axis=alt.Axis(format="%"),
                ),
                y=alt.Y("merchant_name:N", sort="-x", title="Merchant Name"),
                tooltip=[
                    alt.Tooltip("merchant_name:N", title="Merchant Name"),
                    alt.Tooltip(
                        "discount_percent:Q", title="Average Saving (%)", format=".2%"
                    ),
                ],
            )
            .properties(title="Merchants with Highest Average Savings")
        )

        st.altair_chart(avg_saving_by_merchant_chart, use_container_width=True)

    # Current status of deals
    st.subheader("Current Status of Deals")
    deal_status_counts = st.session_state.data["status"].value_counts()
    st.bar_chart(deal_status_counts)

    st.write(f"Displaying {len(st.session_state.data)} rows from the database:")

    # Display the data in a dataframe
    st.dataframe(st.session_state.data, use_container_width=True)
