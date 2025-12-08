import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Analytics - ClubHub",
    page_icon="📈",
    layout="wide")

CLUB_ID = 101  # Latin American Student Union

# API Base URL
API_BASE_URL = "http://web-api:4000"

# Sidebar navigation
st.sidebar.title("🎭 Sofia's Pages")
st.sidebar.markdown("**Current:** Analytics")
st.sidebar.page_link("pages/6_Sofia_My_Events.py", label="My Events")
st.sidebar.page_link("pages/7_Sofia_Create_Event.py", label="Create Event")
st.sidebar.page_link("pages/8_Sofia_RSVPs.py", label="RSVPs")
st.sidebar.page_link("pages/010_Sofia_Collaborations.py", label="Collaborations")
st.sidebar.divider()
st.sidebar.page_link("Home.py", label="← Back to Home")

# Main page title
st.title("📈 Event Analytics")
st.markdown("Understand which event types, times, and formats are most successful")
st.divider()

# Fetch analytics data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_event_analytics(club_id):
    try:
        response = requests.get(f"{API_BASE_URL}/clubs/{club_id}/analytics", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"Could not connect to API: {e}")
        return []

# Get analytics
analytics_data = fetch_event_analytics(CLUB_ID)

if not analytics_data:
    st.info("No past events to analyze yet. Host some events to see analytics!")
else:
    df = pd.DataFrame(analytics_data)
    
    # Overall metrics
    st.markdown("### 📊 Overall Performance")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_events = len(df)
    total_rsvps = df['total_rsvps'].sum() if 'total_rsvps' in df.columns else 0
    total_attendance = df['actual_attendance'].sum() if 'actual_attendance' in df.columns else 0
    avg_attendance_rate = df['attendance_rate'].mean() if 'attendance_rate' in df.columns else 0
    avg_capacity_util = df['capacity_utilization'].mean() if 'capacity_utilization' in df.columns else 0
    
    with col1:
        st.metric("Total Events", total_events)
    
    with col2:
        st.metric("Total RSVPs", int(total_rsvps))
    
    with col3:
        st.metric("Total Attendance", int(total_attendance))
    
    with col4:
        st.metric("Avg Attendance Rate", f"{avg_attendance_rate:.1f}%")
    
    with col5:
        st.metric("Avg Capacity Used", f"{avg_capacity_util:.1f}%")
    
    st.divider()
    
    # Visualizations
    col_viz1, col_viz2 = st.columns(2)
    
    with col_viz1:
        st.markdown("### 📅 Attendance Over Time")
        if 'start_datetime' in df.columns and 'actual_attendance' in df.columns:
            # Prepare data for time series
            df_time = df.copy()
            df_time['date'] = pd.to_datetime(df_time['start_datetime']).dt.date
            df_time = df_time.sort_values('date')
            
            fig_time = px.line(
                df_time,
                x='date',
                y='actual_attendance',
                title='Attendance Trend',
                markers=True,
                labels={'actual_attendance': 'Attendance', 'date': 'Event Date'}
            )
            fig_time.update_traces(line_color='#1f77b4', line_width=3)
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("No time series data available")
    
    with col_viz2:
        st.markdown("### 🎯 Attendance Rate vs Capacity")
        if 'attendance_rate' in df.columns and 'capacity_utilization' in df.columns:
            fig_scatter = px.scatter(
                df,
                x='attendance_rate',
                y='capacity_utilization',
                size='actual_attendance',
                hover_data=['event_name', 'event_type'],
                title='Performance Matrix',
                labels={
                    'attendance_rate': 'Attendance Rate (%)',
                    'capacity_utilization': 'Capacity Utilization (%)'
                }
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("No performance data available")
    
    st.divider()
    
    # Event type analysis
    col_type1, col_type2 = st.columns(2)
    
    with col_type1:
        st.markdown("### 📂 Performance by Event Type")
        if 'event_type' in df.columns:
            type_stats = df.groupby('event_type').agg({
                'event_id': 'count',
                'actual_attendance': 'mean',
                'attendance_rate': 'mean',
                'capacity_utilization': 'mean'
            }).round(1).reset_index()
            
            type_stats.columns = ['Event Type', 'Count', 'Avg Attendance', 'Avg Rate (%)', 'Avg Capacity (%)']
            
            fig_type = px.bar(
                type_stats,
                x='Event Type',
                y='Avg Attendance',
                title='Average Attendance by Type',
                color='Avg Rate (%)',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_type, use_container_width=True)
            
            st.dataframe(type_stats, use_container_width=True, hide_index=True)
        else:
            st.info("No event type data available")
    
    with col_type2:
        st.markdown("### 🏆 Top Performing Events")
        if 'event_name' in df.columns and 'attendance_rate' in df.columns:
            top_events = df.nlargest(5, 'attendance_rate')[
                ['event_name', 'actual_attendance', 'attendance_rate', 'capacity_utilization', 'event_type']
            ].copy()
            
            top_events.columns = ['Event Name', 'Attendance', 'Rate (%)', 'Capacity (%)', 'Type']
            
            for idx, event in top_events.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{event['Event Name']}**")
                    st.markdown(f"*{event['Type']}*")
                    
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    with metric_col1:
                        st.metric("Attendance", int(event['Attendance']))
                    with metric_col2:
                        st.metric("Rate", f"{event['Rate (%)']:.1f}%")
                    with metric_col3:
                        st.metric("Capacity", f"{event['Capacity (%)']:.1f}%")
        else:
            st.info("No event ranking data available")
    
    st.divider()
    
    # Detailed event list
    st.markdown("### 📋 All Past Events")
    
    # Add filters
    col_filter1, col_filter2 = st.columns([2, 2])
    
    with col_filter1:
        if 'event_type' in df.columns:
            type_options = ['All Types'] + sorted(df['event_type'].unique().tolist())
            selected_type = st.selectbox("Filter by Type", type_options)
        else:
            selected_type = 'All Types'
    
    with col_filter2:
        sort_options = {
            'Most Recent': 'start_datetime',
            'Highest Attendance': 'actual_attendance',
            'Best Attendance Rate': 'attendance_rate',
            'Best Capacity Use': 'capacity_utilization'
        }
        selected_sort = st.selectbox("Sort By", list(sort_options.keys()))
    
    # Apply filters
    filtered_df = df.copy()
    if selected_type != 'All Types':
        filtered_df = filtered_df[filtered_df['event_type'] == selected_type]
    
    # Sort
    sort_col = sort_options[selected_sort]
    if sort_col in filtered_df.columns:
        filtered_df = filtered_df.sort_values(sort_col, ascending=False)
    
    # Display events
    for idx, event in filtered_df.iterrows():
        with st.container(border=True):
            col_event1, col_event2 = st.columns([2, 1])
            
            with col_event1:
                st.markdown(f"### {event.get('event_name', 'Untitled Event')}")
                st.markdown(f"**📂 {event.get('event_type', 'N/A')}**")
                
                start_time = event.get('start_datetime', '')
                if start_time:
                    try:
                        dt = pd.to_datetime(start_time)
                        formatted_date = dt.strftime("%b %d, %Y")
                        st.markdown(f"📅 {formatted_date}")
                    except:
                        st.markdown(f"📅 {start_time}")
            
            with col_event2:
                # Metrics
                rsvps = int(event.get('total_rsvps', 0))
                attendance = int(event.get('actual_attendance', 0))
                rate = event.get('attendance_rate', 0)
                capacity_used = event.get('capacity_utilization', 0)
                
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric("RSVPs", rsvps)
                    st.metric("Rate", f"{rate:.1f}%")
                with metric_col2:
                    st.metric("Attended", attendance)
                    st.metric("Capacity", f"{capacity_used:.1f}%")

# Export and refresh
st.divider()
col_action1, col_action2, col_action3 = st.columns([1, 1, 2])

with col_action1:
    if st.button("🔄 Refresh Analytics", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col_action2:
    if analytics_data:
        csv = pd.DataFrame(analytics_data).to_csv(index=False)
        st.download_button(
            label="📥 Download Report",
            data=csv,
            file_name=f"event_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# Footer
st.divider()
st.markdown("*Analytics are based on completed events. Attendance rate = (Actual Attendance / Total RSVPs) × 100*")