import streamlit as st
import requests
from datetime import datetime, date, time

# Page config
st.set_page_config(
    page_title="Create Event - ClubHub",
    page_icon="➕",
    layout="wide")

CLUB_ID = 101  # Latin American Student Union
USER_ID = 98765  # Sofia's user ID

# API Base URL
API_BASE_URL = "http://web-api:4000"

# Sidebar navigation
st.sidebar.title("🎭 Sofia's Pages")
st.sidebar.markdown("**Current:** Create Event")
st.sidebar.page_link("pages/6_Sofia_My_Events.py", label="My Events")
st.sidebar.page_link("pages/8_Sofia_RSVPs.py", label="RSVPs")
st.sidebar.page_link("pages/9_Sofia_Analytics.py", label="Analytics")
st.sidebar.page_link("pages/010_Sofia_Collaborations.py", label="Collaborations")
st.sidebar.divider()
st.sidebar.page_link("Home.py", label="← Back to Home")

# Main page title
st.title("➕ Create New Event")
st.markdown("Publish your event to the centralized platform")
st.divider()

# Fetch conflicting events
@st.cache_data(ttl=60)
def fetch_conflicting_events(start_dt, end_dt, club_id):
    try:
        response = requests.get(
            f"{API_BASE_URL}/events/conflicts",
            params={
                "start_datetime": start_dt,
                "end_datetime": end_dt,
                "exclude_club_id": club_id
            },
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        return []

# Form
with st.form("create_event_form"):
    st.markdown("### 📝 Event Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        event_name = st.text_input("Event Title*", placeholder="e.g., Spring Networking Mixer")
        event_description = st.text_area("Description*", placeholder="Describe your event...", height=100)
        
        event_type = st.selectbox(
            "Event Type*",
            ["Social", "Cultural", "Academic", "Professional", "Service", "Sports", "Arts"]
        )
        
        category = st.text_input("Category", placeholder="e.g., Networking, Performance, Workshop")
    
    with col2:
        event_date = st.date_input("Event Date*", min_value=date.today())
        
        col_time1, col_time2 = st.columns(2)
        with col_time1:
            start_time = st.time_input("Start Time*", value=time(18, 0))
        with col_time2:
            end_time = st.time_input("End Time*", value=time(21, 0))
        
        capacity = st.number_input("Capacity*", min_value=1, value=50, step=1)
    
    st.divider()
    st.markdown("### 📍 Location")
    
    col3, col4 = st.columns(2)
    
    with col3:
        location = st.text_input("Venue Name*", placeholder="e.g., Student Union Ballroom")
        building_name = st.text_input("Building", placeholder="e.g., Student Union")
    
    with col4:
        room_number = st.text_input("Room Number", placeholder="e.g., 200A")
    
    st.divider()
    st.markdown("### 🏷️ Tags & Settings")
    
    col5, col6 = st.columns(2)
    
    with col5:
        tags = st.multiselect(
            "Tags",
            ["latin", "culture", "music", "food", "networking", "professional", "social", "community"]
        )
        
    with col6:
        require_rsvp = st.checkbox("Require RSVP", value=True)
        enable_checkin = st.checkbox("Enable Check-in", value=True)
        limit_attendees = st.checkbox("Limit Attendees", value=True)
        open_to_all = st.checkbox("Open to All Students", value=True)
    
    st.divider()
    
    # Submit buttons
    col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 2])
    
    with col_submit1:
        submit_draft = st.form_submit_button("💾 Save as Draft", use_container_width=True)
    
    with col_submit2:
        submit_publish = st.form_submit_button("📢 Publish Event", type="primary", use_container_width=True)

# Handle form submission
if submit_draft or submit_publish:
    # Validation
    if not event_name or not event_description or not location:
        st.error("⚠️ Please fill in all required fields (marked with *)")
    else:
        # Combine date and time
        start_datetime = datetime.combine(event_date, start_time)
        end_datetime = datetime.combine(event_date, end_time)
        
        # Check for conflicts
        conflicts = fetch_conflicting_events(
            start_datetime.isoformat(),
            end_datetime.isoformat(),
            CLUB_ID
        )
        
        if conflicts:
            st.warning(f"⚠️ Warning: {len(conflicts)} conflicting events found at the same time")
            
            with st.expander("View Conflicting Events", expanded=True):
                for conflict in conflicts:
                    st.markdown(f"**{conflict.get('name')}** - {conflict.get('club_name')}")
                    st.markdown(f"📍 {conflict.get('location')} | 👥 {conflict.get('expected_attendance', 'N/A')} expected")
                    st.divider()
        
        # Create event data
        event_data = {
            "club_id": CLUB_ID,
            "event_name": event_name,
            "event_description": event_description,
            "event_type": event_type,
            "category": category,
            "start_datetime": start_datetime.isoformat(),
            "end_datetime": end_datetime.isoformat(),
            "location": location,
            "building_name": building_name,
            "room_number": room_number,
            "capacity": capacity,
            "created_by_user_id": USER_ID,
            "tags": ",".join(tags),
            "require_rsvp": require_rsvp,
            "enable_checkin": enable_checkin,
            "status": "published" if submit_publish else "draft"
        }
        
        # Submit to API
        try:
            response = requests.post(
                f"{API_BASE_URL}/events",
                json=event_data,
                timeout=5
            )
            
            if response.status_code == 201:
                if submit_publish:
                    st.success("🎉 Event published successfully!")
                    st.balloons()
                else:
                    st.success("💾 Event saved as draft!")
                
                st.cache_data.clear()
                
                if st.button("← Back to My Events"):
                    st.switch_page("pages/6_Sofia_My_Events.py")
            else:
                st.error(f"Failed to create event: {response.status_code}")
                st.code(response.text) 
                st.json(response.json() if response.text else {})
                
        except Exception as e:
            st.error(f"Could not connect to API: {e}")

# Footer
st.divider()
st.markdown("*All fields marked with * are required*")