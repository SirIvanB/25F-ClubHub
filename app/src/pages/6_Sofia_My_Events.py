import streamlit as st
import requests
from datetime import datetime

# Page config
st.set_page_config(
    page_title="My Events - ClubHub",
    page_icon="📅",
    layout="wide")

CLUB_ID = 101  # Latin American Student Union
USER_ID = 98765  # Sofia's user ID

# API Base URL
API_BASE_URL = "http://web-api:4000"

# Sidebar navigation
st.sidebar.title("🎭 Sofia's Pages")
st.sidebar.markdown("**Current:** My Events")
st.sidebar.page_link("pages/7_Sofia_Create_Event.py", label="Create Event")
st.sidebar.page_link("pages/8_Sofia_RSVPs.py", label="RSVPs")
st.sidebar.page_link("pages/9_Sofia_Analytics.py", label="Analytics")
st.sidebar.page_link("pages/010_Sofia_Collaborations.py", label="Collaborations")
st.sidebar.divider()
st.sidebar.page_link("Home.py", label="← Back to Home")

# Main page title
st.title("📅 My Events")
st.markdown("Manage your club's events")
st.divider()

# Tabs for upcoming vs past events
tab1, tab2 = st.tabs(["📆 Upcoming Events", "📜 Past Events"])

# Fetch events from API
@st.cache_data(ttl=60)
def fetch_club_events(club_id):
    try:
        response = requests.get(f"{API_BASE_URL}/clubs/{club_id}/events", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"Could not connect to API: {e}")
        return []

# Delete event function
def delete_event(event_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/events/{event_id}", timeout=5)
        return response.status_code == 200
    except:
        return False

# Get events
events = fetch_club_events(CLUB_ID)

# Split into upcoming and past
now = datetime.now()
upcoming_events = []
past_events = []

for event in events:
    try:
        start_dt_str = str(event.get('startDateTime', ''))
        if 'GMT' in start_dt_str:
            start_dt_str = start_dt_str.split(' GMT')[0]
        event_date = datetime.strptime(start_dt_str, "%a, %d %b %Y %H:%M:%S")
        
        if event_date >= now:
            upcoming_events.append(event)
        else:
            past_events.append(event)
    except:
        upcoming_events.append(event)

with tab1:
    if not upcoming_events:
        st.info("No upcoming events. Create your first event!")
        if st.button("➕ Create New Event", type="primary"):
            st.switch_page("pages/7_Sofia_Create_Event.py")
    else:
        st.markdown(f"**{len(upcoming_events)} upcoming events**")
        
        for event in upcoming_events:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {event.get('name', 'Untitled Event')}")
                    
                    # Date and time
                    start_time = event.get('startDateTime', '')
                    end_time = event.get('endDateTime', '')
                    if start_time:
                        try:
                            dt_start = datetime.fromisoformat(str(start_time))
                            dt_end = datetime.fromisoformat(str(end_time)) if end_time else None
                            formatted_start = dt_start.strftime("%b %d, %Y at %I:%M %p")
                            formatted_end = dt_end.strftime("%I:%M %p") if dt_end else "TBD"
                            st.markdown(f"📅 {formatted_start} - {formatted_end}")
                        except:
                            st.markdown(f"📅 {start_time}")
                    
                    # Location
                    location = event.get('location', 'TBD')
                    building = event.get('buildingName', '')
                    room = event.get('roomNumber', '')
                    location_str = f"{location}"
                    if building:
                        location_str += f" - {building}"
                    if room:
                        location_str += f", Room {room}"
                    st.markdown(f"📍 {location_str}")
                    
                    # Capacity
                    capacity = event.get('capacity')
                    if capacity:
                        st.markdown(f"👥 Capacity: {capacity}")
                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("📊 View RSVPs", key=f"rsvp_{event.get('eventID')}", use_container_width=True):
                        st.session_state['selected_event'] = event.get('eventID')
                        st.switch_page("pages/8_Sofia_RSVPs.py")
                    
                    if st.button("✏️ Edit", key=f"edit_{event.get('eventID')}", use_container_width=True):
                        st.info("Edit functionality coming soon!")
                    
                    if st.button("🗑️ Delete", key=f"delete_{event.get('eventID')}", use_container_width=True):
                        if delete_event(event.get('eventID')):
                            st.success("Event deleted!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("Failed to delete event")

with tab2:
    if not past_events:
        st.info("No past events yet")
    else:
        st.markdown(f"**{len(past_events)} past events**")
        
        for event in past_events:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {event.get('name', 'Untitled Event')}")
                    
                    # Date
                    start_time = event.get('startDateTime', '')
                    if start_time:
                        try:
                            dt = datetime.fromisoformat(str(start_time))
                            formatted_date = dt.strftime("%b %d, %Y")
                            st.markdown(f"📅 {formatted_date}")
                        except:
                            st.markdown(f"📅 {start_time}")
                    
                    # Location
                    location = event.get('location', 'TBD')
                    st.markdown(f"📍 {location}")
                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("📈 View Analytics", key=f"analytics_{event.get('eventID')}", use_container_width=True):
                        st.session_state['selected_event'] = event.get('eventID')
                        st.switch_page("pages/9_Sofia_Analytics.py")

# Footer
st.divider()
if st.button("➕ Create New Event", type="primary", use_container_width=True):
    st.switch_page("pages/7_Sofia_Create_Event.py")

st.markdown("*Events are updated in real-time from the ClubHub database*")