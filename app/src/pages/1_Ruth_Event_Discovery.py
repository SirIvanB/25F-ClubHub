import streamlit as st
import requests
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Event Discovery - ClubHub",
    page_icon="🔎",
    layout="wide")

STUDENT_ID = 10000001 

if 'clear_trigger' not in st.session_state:
    st.session_state.clear_trigger = 0

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
st.title("🔎 Event Discovery")
st.markdown("Find events happening on campus")
st.divider()

# Search bar
search_query = st.text_input("🔍 Search events by name...", placeholder="Type to search...")

# Filter row
col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    date_filter = st.selectbox("📅 Date", ["All Dates", "Today", "This Week", "This Month"], 
                            key=f"date_{st.session_state.clear_trigger}")

with col2:
    type_filter = st.selectbox("📂 Type", ["All Types", "Academic", "Arts", "Professional", "Sports", "Social", "Service"],
                            key=f"type_{st.session_state.clear_trigger}")

with col3:
    club_filter = st.selectbox("🎯 Club", ["All Clubs", "Husky Hackers", "Dance Collective", "Investment Club", 
                                    "Environmental Action Group", "Debate Society", "Soccer League", 
                                    "Photography Club", "Pre-Med Society", "ISA", "Robotics Team"],
                            key=f"club_{st.session_state.clear_trigger}")

with col4:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Clear Filters", use_container_width=True):
        st.session_state.clear_trigger += 1
        st.rerun()
        
st.divider()

# RSVP function
def create_rsvp(event_id, event_name):
    try:
        response = requests.post(
            f"{API_BASE_URL}/students/{STUDENT_ID}/rsvps",
            json={"event_id": event_id},
            timeout=5
        )
        if response.status_code == 201:
            return True
        return False
    except:
        return False

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

# Apply all filters
filtered_events = events.copy()

# Search filter
if search_query:
    filtered_events = [e for e in filtered_events if search_query.lower() in e.get('name', '').lower()]

# Date filter
if date_filter != "All Dates":
    today = datetime.now().date()
    temp_events = []
    for event in filtered_events:
        try:
            # Handle both string and datetime objects
            dt_str = str(event.get('startDateTime'))
            if 'GMT' in dt_str:
                # Remove timezone info if present
                dt_str = dt_str.split(' GMT')[0]
            event_date = datetime.strptime(dt_str, "%a, %d %b %Y %H:%M:%S").date()
            days_diff = (event_date - today).days
            
            if date_filter == "Today" and days_diff == 0:
                temp_events.append(event)
            elif date_filter == "This Week" and 0 <= days_diff <= 7:
                temp_events.append(event)
            elif date_filter == "This Month" and 0 <= days_diff <= 30:
                temp_events.append(event)
        except:
            pass
    filtered_events = temp_events

# Club filter
if club_filter != "All Clubs":
    filtered_events = [e for e in filtered_events if club_filter.lower() in e.get('club_name', '').lower()]

# Type filter
if type_filter != "All Types":
    filtered_events = [e for e in filtered_events if e.get('club_type', '') == type_filter]

# Use filtered_events instead of events from here on
events = filtered_events

# Display events in grid
if not events:
    st.info("No events found so far 😢. Try adjusting your filters!")
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
                    if st.button("RSVP", key=f"rsvp_{event.get('eventID')}", use_container_width=True, type="primary"):
                        if create_rsvp(event.get('eventID'), event.get('name')):
                            st.success(f"✓ RSVP'd to {event.get('name')}!")
                            st.balloons()
                            st.cache_data.clear()
                        else:
                            st.error("Failed to RSVP. Try again.")
                with col_b:
                    if st.button("Details →", key=f"details_{event.get('eventID')}", use_container_width=True):
                        st.session_state[f'show_details_{event.get("eventID")}'] = True
                        st.rerun()

                    # Show details if toggled
                    if st.session_state.get(f'show_details_{event.get("eventID")}', False):
                        with st.expander("📋 Full Details", expanded=True):
                            st.markdown(f"**Description:** {event.get('description', 'No description')}")
                            st.markdown(f"**Building:** {event.get('buildingName', 'N/A')}")
                            st.markdown(f"**Room:** {event.get('roomNumber', 'N/A')}")
                            if st.button("Close", key=f"close_{event.get('eventID')}"):
                                st.session_state[f'show_details_{event.get("eventID")}'] = False
                                st.rerun()

# Footer
st.divider()
st.markdown("*Events are updated in real-time from the ClubHub database*")