import streamlit as st
import requests
from datetime import datetime

# Page config
st.set_page_config(
    page_title="My Schedule - ClubHub",
    page_icon="📅",
    layout="wide"
)

# API Base URL
API_BASE_URL = "http://web-api:4000"

# Hardcoded student ID (will come from auth later)
STUDENT_ID = 10000001

# Sidebar navigation
st.sidebar.title("🎒 Ruth's Pages")
st.sidebar.page_link("pages/1_Ruth_Event_Discovery.py", label="Event Discovery")
st.sidebar.page_link("pages/2_Ruth_Club_Comparison.py", label="Club Comparison")
st.sidebar.markdown("**Current:** My Schedule")
st.sidebar.page_link("pages/4_Ruth_Friends_Invites.py", label="Friends & Invites")
st.sidebar.page_link("pages/5_Ruth_Club_Rankings.py", label="Club Rankings")
st.sidebar.divider()
st.sidebar.page_link("Home.py", label="← Back to Home")

# Main page title
st.title("📅 My Schedule")
st.divider()

# Fetch user's RSVPs
@st.cache_data(ttl=30)  # Cache for 30 seconds (shorter since this changes often)
def fetch_my_rsvps():
    try:
        response = requests.get(
            f"{API_BASE_URL}/students/students/{STUDENT_ID}/rsvps", 
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"Could not connect to API: {e}")
        return []

# Get RSVPs
my_events = fetch_my_rsvps()

## Check for recent updates (events that were recently updated)
#recent_updates = [e for e in my_events if e.get('last_updated')]
#if recent_updates:
#    st.markdown("### 🔔 Recent Updates")
#    for event in recent_updates[:3]:  # Show max 3 updates
#        st.info(f"⚠️ **{event.get('event_name')}** was recently updated")
#    st.divider()

# Display events
if not my_events:
    st.info("📭 No upcoming events yet! Browse events to add to your schedule.")
    
    # Button to go to Event Discovery
    if st.button("Browse Events", type="primary", use_container_width=True):
        st.switch_page("pages/1_Ruth_Event_Discovery.py")
else:
    st.markdown(f"### Upcoming Events ({len(my_events)})")
    st.divider()
    
    # Group events by date
    today = datetime.now().date()
    
    for event in my_events:
        with st.container(border=True):
            # Event name
            st.markdown(f"## {event.get('event_name', 'Untitled Event')}")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Club name
                st.markdown(f"**⏰ {event.get('club_name', 'Unknown Club')}**")
                
                # Date and time
                start_time = event.get('start_datetime', '')
                if start_time:
                    try:
                        dt = datetime.fromisoformat(str(start_time))
                        
                        # Calculate relative date
                        event_date = dt.date()
                        days_until = (event_date - today).days
                        
                        if days_until == 0:
                            date_label = "🔥 Today"
                        elif days_until == 1:
                            date_label = "📅 Tomorrow"
                        elif days_until < 7:
                            date_label = f"📅 In {days_until} days"
                        else:
                            date_label = f"📅 {dt.strftime('%B %d')}"
                        
                        formatted_time = dt.strftime("%I:%M %p")
                        st.markdown(f"{date_label} at **{formatted_time}**")
                    except:
                        st.markdown(f"📅 {start_time}")
                
                # Location
                location = event.get('location', 'TBD')
                st.markdown(f"📍 {location}")
            
            with col2:
                # Action buttons
                if st.button("🗺️ Get Directions", key=f"dir_{event.get('event_id')}", use_container_width=True):
                    st.info(f"Directions to: {location}")
                    # In real app, this would show a map or navigation
                
                if st.button("❌ Cancel RSVP", key=f"cancel_{event.get('rsvp_id')}", use_container_width=True):
                    rsvp_id = event.get('rsvp_id')
                    try:
                        resp = requests.delete(
                            f"{API_BASE_URL}/students/students/{STUDENT_ID}/rsvps/{rsvp_id}", timeout=5)
                        if resp.status_code == 200:
                            st.success("RSVP cancelled.")
                            st.cache_data.clear()
                            st.rerun()
                        elif resp.status_code == 404:
                            st.error("RSVP not found. It may have already been cancelled.")
                        else:
                            st.error(f"Failed to cancel RSVP (status {resp.status_code}).")
                    except Exception as e:
                        st.error(f"Failed to cancel RSVP: {e}")
        
        st.markdown("")  # Spacing between events

# Footer
st.divider()

col_a, col_b = st.columns(2)

with col_a:
    if st.button("🔍 Browse More Events", use_container_width=True):
        st.switch_page("pages/1_Ruth_Event_Discovery.py")

with col_b:
    if st.button("🔄 Refresh Schedule", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("*Your schedule syncs automatically with ClubHub*")