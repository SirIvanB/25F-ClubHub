import streamlit as st
import requests
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Event Discovery - ClubHub",
    page_icon="🎉",
    layout="wide")

# API Base URL
API_BASE_URL = "http://web-api:4000"

# Sidebar navigation
st.sidebar.title("🎒 Ruth's Pages")
st.sidebar.markdown("**Current:** Event Discovery")
st.sidebar.page_link("pages/2_Ruth_Club_Comparison.py", label="Club Comparison")
st.sidebar.page_link("pages/3_Ruth_My_Schedule.py", label="My Schedule")
st.sidebar.page_link("pages/4_Ruth_Friends_Invites.py", label="Friends & Invites")
st.sidebar.page_link("pages/5_Ruth_Club_Rankings.py", label="Club Rankings")
st.sidebar.divider()
st.sidebar.page_link("Home.py", label="← Back to Home")

# Main page title
st.title("🎉 Event Discovery")
st.markdown("Find events happening on campus")
st.divider()

# Search bar
search_query = st.text_input("🔍 Search events by name...", placeholder="Type to search...")

# Filter row
col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    date_filter = st.selectbox("📅 Date", ["All Dates", "Today", "This Week", "This Month"])

with col2:
    category_filter = st.selectbox("🏷️ Category", ["All Categories", "Academic", "Social", "Sports", "Arts"])

with col3:
    club_filter = st.selectbox("🎯 Club", ["All Clubs", "CS Club", "Latin Union", "Board Games", "Business Club"])

with col4:
    st.markdown("<br>", unsafe_allow_html=True)  # spacing
    if st.button("Clear Filters", use_container_width=True):
        st.rerun()

st.divider()

# Fetch events from API
@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_events():
    try:
        response = requests.get(f"{API_BASE_URL}/events", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"Could not connect to API: {e}")
        return []

# Get events
events = fetch_events()

# Filter events based on search
if search_query:
    events = [e for e in events if search_query.lower() in e.get('name', '').lower()]

# Display events in grid
if not events:
    st.info("No events found. Try adjusting your filters!")
else:
    st.markdown(f"**Showing {len(events)} events**")
    
    # Create grid layout (2 columns)
    cols = st.columns(2)
    
    for idx, event in enumerate(events):
        with cols[idx % 2]:
            with st.container(border=True):
                # Event name
                st.markdown(f"### {event.get('name', 'Untitled Event')}")
                
                # Club name
                st.markdown(f"**🎭 {event.get('club_name', 'Unknown Club')}**")
                
                # Date and time
                start_time = event.get('startDateTime', '')
                if start_time:
                    try:
                        dt = datetime.fromisoformat(str(start_time))
                        formatted_date = dt.strftime("%b %d, %I:%M %p")
                        st.markdown(f"📅 {formatted_date}")
                    except:
                        st.markdown(f"📅 {start_time}")
                
                # Location
                location = event.get('location', 'TBD')
                st.markdown(f"📍 {location}")
                
                # Capacity
                capacity = event.get('capacity')
                if capacity:
                    st.markdown(f"👥 Capacity: {capacity}")
                
                # Action buttons
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("RSVP", key=f"rsvp_{event.get('eventID')}", use_container_width=True):
                        st.success("RSVP submitted! ✓")
                        st.balloons()
                with col_b:
                    if st.button("Details →", key=f"details_{event.get('eventID')}", use_container_width=True):
                        st.session_state['selected_event'] = event
                        st.info(f"Viewing details for: {event.get('name')}")

# Footer
st.divider()
st.markdown("*Events are updated in real-time from the ClubHub database*")