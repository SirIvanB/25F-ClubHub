import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
from modules.nav import SideBarLinks
from datetime import datetime, timedelta
import pandas as pd

SideBarLinks()

st.set_page_config(
    page_title="Search Insights",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Search Insights Dashboard")
st.markdown("Analyze user search behavior and popular keywords")

st.divider()

#API endpoint
API_URL = "http://web-api:4000/analytics/search"

no_result_searches = 0
total_searches = 0
unique_queries = 0
try:
    response = requests.get(f"{API_URL}/summary")
    if response.status_code == 200:
        search_summary = response.json()
        total_searches = search_summary.get("total_searches", 0)
        no_result_searches = search_summary.get("no_result_searches", 0)
        unique_queries = search_summary.get("unique_queries", 0)
    else:
        st.error(f"Failed to fetch summary data. Status: {response.status_code}")
        search_summary = {}
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching summary data: {e}")
    search_summary = {}

top_keywords_df = pd.DataFrame()

try:
    response = requests.get(f"{API_URL}/top-keywords")
    if response.status_code == 200:
        top_keywords_data = response.json()
        top_keywords_df = pd.DataFrame(top_keywords_data)
    else:
        st.error(f"Failed to fetch top keywords. Status: {response.status_code}")
        top_keywords_df = pd.DataFrame()
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching top keywords: {e}")
    top_keywords_df = pd.DataFrame()

no_results_df = pd.DataFrame()
try:
    response = requests.get(f'{API_URL}/no-results')
    if response.status_code == 200:
        no_results_data = response.json()
        no_results_df = pd.DataFrame(no_results_data)
    else:
        st.error(f"Failed to fetch no-results searches. Status: {response.status_code}")
        no_results_df = pd.DataFrame()
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching no-results searches: {e}")
    no_results_df = pd.DataFrame()

st.subheader("Search Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total Searches", total_searches)
col2.metric("No Result Searches", no_result_searches)
col3.metric("Unique Queries", unique_queries)

st.divider()

st.subheader("Top Search Keywords")
if not top_keywords_df.empty:
    st.dataframe(top_keywords_df)
else:
    st.info("No top keywords data available.")
st.divider()

st.subheader("Searches with No Results")
if not no_results_df.empty:
    st.dataframe(no_results_df)
else:
    st.info("No no-results search data available.")
st.divider()