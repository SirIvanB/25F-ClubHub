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
    page_title="Weekly Report",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Weekly Report")
st.markdown("Analyze weekly event data and trends")
st.divider()

API_URL = "http://web-api:4000/analytics/reports"

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

st.subheader("Generate Weekly Report")
if st.button("Generate Report"):
    try:
        response = requests.post(f"{API_URL}")
        response.raise_for_status()
        st.success("Weekly report generated successfully!")
    except requests.exceptions.RequestException as e:
        st.error(f"Error generating report: {e}")
        logger.error(f"Error generating weekly report: {e}")
st.subheader("Weekly Engagement Reports")
if not df.empty:
    fig = px.bar(
        df,
        x='reportPeriodStart',
        y=['totalActiveUsers', 'totalEventsCreated', 'totalRSVPs', 'totalAttendance', 'totalSearches'],
        barmode='group',
        title="Weekly Engagement Metrics"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No report data available.")