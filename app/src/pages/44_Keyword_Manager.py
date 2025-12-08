import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
from modules.nav import SideBarLinks
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px

SideBarLinks()

st.set_page_config(
    page_title="Keyword Manager",
    page_icon="🔑",
    layout="wide"
)

st.title("🔑 Keyword Manager")
st.markdown("Manage and analyze keywords for content optimization")

st.divider()

API_URL = "http://web-api:4000/events"

df = pd.DataFrame()
try:
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching data: {e}")
    logger.error(f"Error fetching data from API: {e}")
    df = pd.DataFrame()

st.subheader("Event Keyword Editor")
if not df.empty:
    events = df['name'].unique()
    selected_event = st.selectbox("Select Event to View Keywords", events)
    event_id = df[df['name'] == selected_event]['eventID'].values[0]
    
    keywords_df = pd.DataFrame()
    try:
        response = requests.get(f"{API_URL}/{event_id}/keywords")
        response.raise_for_status()
        keywords_data = response.json()
        keywords_df = pd.DataFrame(keywords_data)
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching keywords: {e}")
        logger.error(f"Error fetching keywords for event {event_id}: {e}")
        keywords_df = pd.DataFrame()

    if not keywords_df.empty:
        for index, row in keywords_df.iterrows():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**{row['keyword']}**")
            with col2:
                st.write(f"Searches: {row['search_count']}")
            with col3:
                if st.button("🗑️ Remove", key=f"remove_{row['keywordID']}"):
                    response = requests.delete(
                        f"{API_URL}/{event_id}/keywords?keyword_id={row['keywordID']}"
                    )
                    if response.status_code == 200:
                        st.success("Keyword removed!")
                        st.cache_data.clear()
                        st.experimental_rerun()
                    else:
                        st.error("Failed to remove keyword")
    
    new_keyword = st.text_input("Add New Keyword")
    if st.button("➕ Add Keyword"):
        if new_keyword.strip() == "":
            st.error("Keyword cannot be empty")
        else:
            response = requests.post(
                f"{API_URL}/{event_id}/keywords",
                json={"keyword": new_keyword.strip()}
            )
            if response.status_code == 201:
                st.success("Keyword added!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Failed to add keyword")
else:
    st.info("No events available to manage keywords.")