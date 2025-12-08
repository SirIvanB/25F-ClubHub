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
    page_title="Student Demographics",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Demographics Dashboard")
st.markdown("Explore demographic data of the student population")
st.divider()

API_URL = "http://web-api:4000/analytics/demographics"

by_year_df = pd.DataFrame()
by_major_df = pd.DataFrame()
event_pref_df = pd.DataFrame()
underserved_df = pd.DataFrame()

try:
    response = requests.get(f"{API_URL}/by-year")
    if response.status_code == 200:
        year_data = response.json()
        by_year_df = pd.DataFrame(year_data)
    else:
        st.error(f"Failed to fetch demographics summary. Status: {response.status_code}")
        demographics_summary = {}
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching demographics summary: {e}")
    demographics_summary = {}

try:
    response = requests.get(f"{API_URL}/by-major")
    if response.status_code == 200:
        major_data = response.json()
        by_major_df = pd.DataFrame(major_data)
    else:
        st.error(f"Failed to fetch demographics summary. Status: {response.status_code}")
        demographics_summary = {}
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching demographics summary: {e}")
    demographics_summary = {}

try:
    response = requests.get(f"{API_URL}/event-preferences")
    if response.status_code == 200:
        event_pref_data = response.json()
        event_pref_df = pd.DataFrame(event_pref_data)
    else:
        st.error(f"Failed to fetch event preferences. Status: {response.status_code}")
        event_pref_df = pd.DataFrame()
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching event preferences: {e}")
    event_pref_df = pd.DataFrame()

try:
    response = requests.get(f"{API_URL}/underserved")
    if response.status_code == 200:
        underserved_data = response.json()
        underserved_df = pd.DataFrame(underserved_data)
    else:
        st.error(f"Failed to fetch underserved data. Status: {response.status_code}")
        underserved_df = pd.DataFrame()
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching underserved data: {e}")
    underserved_df = pd.DataFrame()

st.subheader("Engagement by Year")
col1, col2 = st.columns(2)
with col1:
    if not by_year_df.empty:
        fig = px.bar(by_year_df, x='year', y='participation_rate', labels={'participation_rate': 'Participation Rate (%)', 'year': 'Year'}, orientation='v')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for student distribution by year.")
with col2:
    if not by_year_df.empty:
        by_year_df = by_year_df.set_index('year')
        st.dataframe(by_year_df)
    else:
        st.info("No data available for student distribution by year.")

st.divider()

st.subheader("Engagement by Major")

if not event_pref_df.empty:
    fig = px.bar(by_major_df, x='major', y='participation_rate', labels={'participation_rate': 'Participation Rate (%)', 'major': 'Major'}, orientation='v')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(by_major_df)
else:
    st.info("No data available for student distribution by major.")

st.divider()
st.subheader("Event Preferences")

if not event_pref_df.empty:
    majors = sorted(event_pref_df['major'].unique())
    selected_major = st.selectbox(
        "Select a major to view their event preferences:",
        options=majors
    )
    
    major_data = event_pref_df[event_pref_df['major'] == selected_major]
    
    if not major_data.empty:
        category_summary = major_data.groupby('category_name').agg({
            'attendance_count': 'sum',
            'unique_students': 'sum'
        }).reset_index()
        
        category_summary = category_summary.sort_values('attendance_count', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pie = px.pie(
                category_summary,
                values='attendance_count',
                names='category_name',
                title=f'{selected_major} Students - Event Category Distribution',
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            fig_bar = px.bar(
                category_summary,
                x='category_name',
                y='attendance_count',
                title=f'{selected_major} Students - Attendance by Category',
                labels={'category_name': 'Event Category', 'attendance_count': 'Total Attendance'},
                color='attendance_count',
                color_continuous_scale='Blues',
                text='attendance_count'
            )
            fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
            fig_bar.update_layout(
                showlegend=False,
                xaxis={'tickangle': -45},
                height=400
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with st.expander(f"📊 See breakdown by year for {selected_major}"):
            st.dataframe(
                major_data,
                column_config={
                    "year": st.column_config.NumberColumn("Year", format="%d"),
                    "category_name": st.column_config.TextColumn("Event Category", width="medium"),
                    "attendance_count": st.column_config.NumberColumn("Attendance", format="%d"),
                    "unique_students": st.column_config.NumberColumn("Unique Students", format="%d")
                },
                hide_index=True,
                use_container_width=True
            )
    else:
        st.info(f"No event attendance data for {selected_major} students")
else:
    st.info("No event preference data available")

st.divider()
st.subheader("Underserved Student Groups")
if not underserved_df.empty:
    st.dataframe(underserved_df, use_container_width=True)
else:
    st.info("No data available for underserved student groups.")