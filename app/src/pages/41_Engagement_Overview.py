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
    page_title="Engagement Overview",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Engagement Metrics Dashboard")
st.markdown("Comprehensive view of platform engagement metrics")

st.divider()

#API endpoint
API_URL = "http://web-api:4000/analytics/engagement"

events, rsvps, checkins, active_users = 0, 0, 0, 0
past_events, past_rsvps, past_checkins, past_active_users = 0, 0, 0, 0
engagement = 0
events_by_month_df = pd.DataFrame()
top_clubs_df = pd.DataFrame()

try:
    response = requests.get(f"{API_URL}/current-metrics")
    if response.status_code == 200:
        current_metrics = response.json()
        events = current_metrics.get("total_events", 0)
        rsvps = current_metrics.get("total_rsvps", 0)
        checkins = current_metrics.get("total_checkins", 0)
        active_users = current_metrics.get("active_users", 0)
    else:
        st.error("Failed to fetch current period metrics.")
        current_metrics = {}
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching current period metrics: {e}")
    current_metrics = {}


try:
    response = requests.get(f"{API_URL}/previous-metrics")
    if response.status_code == 200:
        previous_metrics = response.json()
        past_events = previous_metrics.get("total_events", 0)
        past_rsvps = previous_metrics.get("total_rsvps", 0)
        past_checkins = previous_metrics.get("total_checkins", 0)
        past_active_users = previous_metrics.get("active_users", 0)
    else:
        st.error(f"Failed to fetch previous metrics. Status: {response.status_code}")
        previous_metrics = {}
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching previous metrics: {e}")
    previous_metrics = {}

try:
    response = requests.get(f"{API_URL}/events-by-month")
    if response.status_code == 200:
        events_by_month_data = response.json()
        if events_by_month_data:
            # Store as DataFrame
            events_by_month_df = pd.DataFrame(events_by_month_data)
        else:
            st.info("No event data available")
    else:
        st.error("Failed to fetch events by month.")
        events_by_month_data = {}
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching events by month: {e}")
    events_by_month_data = {}

try:
    response = requests.get(f'{API_URL}/top-clubs')
    if response.status_code == 200:
        top_clubs_data = response.json()
        if top_clubs_data:
            top_clubs_df = pd.DataFrame(top_clubs_data)
        else:
            st.info("No top clubs data available")
    else:
        st.error("Failed to fetch top clubs data.")
        top_clubs_data = {}
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching top clubs data: {e}")
    top_clubs_data = {}

try:
    response = requests.get(f'{API_URL}/engagement-rate')
    if response.status_code == 200:
        engagement_rate = response.json()
        if engagement_rate:
            engagement = engagement_rate.get("engagement_rate", 0)
        else:
            st.info("No engagement trends data available")
    else:
        st.error("Failed to fetch engagement trends data.")
        engagement_trends_data = {}
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching engagement trends data: {e}")
    engagement_trends_data = {}

if past_events == 0:
    past_events = 1
if past_rsvps == 0:
    past_rsvps = 1
if past_checkins == 0:
    past_checkins = 1
if past_active_users == 0:
    past_active_users = 1

events_diff = 100 * (events / past_events)
events_diff_symbol = "▲" if events_diff >= 100 else "▼"
if events_diff > 100:
    events_diff -= 100
else:
    events_diff = 100 - events_diff

rsvps_diff = 100 * (rsvps / past_rsvps)
rsvps_diff_symbol = "▲" if rsvps_diff >= 100 else "▼"
if rsvps_diff > 100:
    rsvps_diff -= 100
else:
    rsvps_diff = 100 - rsvps_diff

checkins_diff = 100 * (checkins / past_checkins)
checkins_diff_symbol = "▲" if checkins_diff >= 100 else "▼"
if checkins_diff > 100:
    checkins_diff -= 100
else:
    checkins_diff = 100 - checkins_diff

active_users_diff = 100 * (active_users / past_active_users)
active_users_diff_symbol = "▲" if active_users_diff >= 100 else "▼"
if active_users_diff > 100:
    active_users_diff -= 100
else:
    active_users_diff = 100 - active_users_diff

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("Total Events")
    st.metric("Events", events, delta=events - past_events)
    st.markdown(f"Change: {events_diff_symbol} {events_diff:.2f}%")

with col2:
    st.markdown("Total RSVPs")
    st.metric("RSVPs", rsvps, delta=rsvps - past_rsvps)
    st.markdown(f"Change: {rsvps_diff_symbol} {rsvps_diff:.2f}%")

with col3:
    st.markdown("Total Check-ins")
    st.metric("Check-ins", checkins, delta=checkins - past_checkins)
    st.markdown(f"Change: {checkins_diff_symbol} {checkins_diff:.2f}%")

with col4:
    st.markdown("Active Users")
    st.metric("Active Users", active_users, delta=active_users - past_active_users)
    st.markdown(f"Change: {active_users_diff_symbol} {active_users_diff:.2f}%")

st.divider()

fig = px.bar(events_by_month_df, x='month', y='event_count',
             title='Events Created by Month',
             labels={'month': 'Month', 'event_count': 'Number of Events'},
             template='plotly_white')

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Top Clubs by Engagement")
    st.dataframe(top_clubs_df, use_container_width=True)

st.divider()

engagement = float(engagement)
st.subheader("Overall Engagement Rate")
st.markdown(f'The overall engagement rate is **{engagement:.2f}%** based on current user interactions with events and clubs.')