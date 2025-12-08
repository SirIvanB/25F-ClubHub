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
    page_title="Club Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Club Analytics")
st.markdown("Analyze club event performance and member engagement")
st.divider()

API_URL = "http://web-api:4000/clubs/performance"

try:
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching data: {e}")
    logger.error(f"Error fetching data from API: {e}")
    df = pd.DataFrame()

if not df.empty:
    df = df.sort_values('avg_attendance_per_event', ascending=True)
    fig = px.bar(
        df,
        x='avg_attendance_per_event',
        y='club_name',
        title='Club Performance Leaderboard',
        labels={'club_name': 'Club Name', 'avg_attendance_per_event': 'Average Attendance per Event'},
        orientation='h'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.divider()
    df = df.sort_values('avg_attendance_per_event', ascending=False)
    st.subheader("All Clubs Performance Data")
    st.dataframe(df)
    st.divider()
    df['avg_attendance_per_event'] = pd.to_numeric(df['avg_attendance_per_event'], errors='coerce')
    avg_attendance = df['avg_attendance_per_event'].mean()
    st.subheader("Clubs Performing Below Average Attendance")
    below_avg_df = df[df['avg_attendance_per_event'] < avg_attendance]
    st.dataframe(below_avg_df)
else:
    st.info("No data available to display charts.")