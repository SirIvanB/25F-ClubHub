import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="RSVPs - ClubHub",
    page_icon="✅",
    layout="wide")

CLUB_ID = 101  # Latin American Student Union
USER_ID = 98765  # Sofia's user ID

# API Base URL
API_BASE_URL = "http://web-api:4000"

# Sidebar navigation
st.sidebar.title("🎭 Sofia's Pages")
st.sidebar.markdown("**Current:** RSVPs")
st.sidebar.page_link("pages/6_Sofia_My_Events.py", label="My Events")
st.sidebar.page_link("pages/7_Sofia_Create_Event.py", label="Create Event")
st.sidebar.page_link("pages/9_Sofia_Analytics.py", label="Analytics")
st.sidebar.page_link("pages/010_Sofia_Collaborations.py", label="Collaborations")
st.sidebar.divider()
st.sidebar.page_link("Home.py", label="← Back to Home")

# Main page title
st.title("✅ RSVP Management")
st.markdown("View and manage RSVPs with real-time headcount updates")
st.divider()

# Fetch events with RSVP data
@st.cache_data(ttl=30)  # Shorter cache for real-time updates
def fetch_events_with_rsvps(club_id):
    try:
        response = requests.get(f"{API_BASE_URL}/clubs/{club_id}/events/rsvps", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"Could not connect to API: {e}")
        return []

# Fetch detailed RSVPs for an event
@st.cache_data(ttl=30)
def fetch_event_rsvps(event_id):
    try:
        response = requests.get(f"{API_BASE_URL}/events/{event_id}/rsvps", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        return []

# Check in student
def check_in_student(event_id, student_id):
    try:
        response = requests.post(
            f"{API_BASE_URL}/events/{event_id}/attendance",
            json={
                "student_id": student_id,
                "checked_in_by_user_id": USER_ID
            },
            timeout=5
        )
        return response.status_code == 201
    except:
        return False

# Get events
events_data = fetch_events_with_rsvps(CLUB_ID)

if not events_data:
    st.info("No events found or no RSVPs yet")
else:
    # Filter to upcoming events only
    upcoming_events = []
    now = datetime.now()
    
    for event in events_data:
        try:
            start_dt_str = str(event.get('start_datetime', ''))
            if 'GMT' in start_dt_str:
                start_dt_str = start_dt_str.split(' GMT')[0]
            event_date = datetime.strptime(start_dt_str, "%a, %d %b %Y %H:%M:%S")
            
            if event_date >= now:
                upcoming_events.append(event)
        except:
            upcoming_events.append(event)
    
    if not upcoming_events:
        st.info("No upcoming events with RSVPs")
    else:
        # Event selector
        event_options = {f"{e.get('event_name')} - {e.get('start_datetime', 'TBD')}": e.get('event_id') 
                        for e in upcoming_events}
        
        selected_event_name = st.selectbox("📅 Select Event", list(event_options.keys()))
        selected_event_id = event_options[selected_event_name]
        
        # Get selected event data
        selected_event = next((e for e in upcoming_events if e.get('event_id') == selected_event_id), None)
        
        if selected_event:
            st.divider()
            
            # Summary metrics
            st.markdown("### 📊 RSVP Summary")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            total_rsvps = int(selected_event.get('total_rsvps', 0))
            confirmed = int(selected_event.get('confirmed_count', 0))
            waitlist = int(selected_event.get('waitlist_count', 0))
            capacity = int(selected_event.get('capacity', 0))
            remaining = int(selected_event.get('remaining_capacity', 0))
            
            with col1:
                st.metric("Total RSVPs", total_rsvps)
            
            with col2:
                st.metric("Confirmed", confirmed, delta_color="normal")
            
            with col3:
                st.metric("Waitlisted", waitlist, delta_color="off")
            
            with col4:
                st.metric("Capacity", capacity)
            
            with col5:
                delta_color = "normal" if remaining > 0 else "inverse"
                st.metric("Remaining", remaining, delta_color=delta_color)
            
            # Capacity bar
            if capacity > 0:
                fill_percentage = min((total_rsvps / capacity) * 100, 100)
                st.progress(fill_percentage / 100)
                
                if fill_percentage >= 100:
                    st.warning("🚨 Event is at full capacity!")
                elif fill_percentage >= 80:
                    st.info("⚠️ Event is nearly full")
            
            st.divider()
            
            # Detailed RSVP list
            st.markdown("### 📋 RSVP List")
            
            rsvps = fetch_event_rsvps(selected_event_id)
            
            if not rsvps:
                st.info("No RSVPs for this event yet")
            else:
                # Create tabs for different statuses
                tab1, tab2 = st.tabs([f"✅ Confirmed ({confirmed})", f"⏳ Waitlist ({waitlist})"])
                
                with tab1:
                    confirmed_rsvps = [r for r in rsvps if r.get('status') == 'confirmed']
                    
                    if not confirmed_rsvps:
                        st.info("No confirmed RSVPs yet")
                    else:
                        # Display as table with check-in option
                        for rsvp in confirmed_rsvps:
                            with st.container(border=True):
                                col_a, col_b, col_c = st.columns([2, 2, 1])
                                
                                with col_a:
                                    student_name = rsvp.get('student_name', 'Unknown Student')
                                    student_id = rsvp.get('student_id', 'N/A')
                                    st.markdown(f"**{student_name}**")
                                    st.markdown(f"*ID: {student_id}*")
                                
                                with col_b:
                                    rsvp_time = rsvp.get('rsvp_datetime', '')
                                    if rsvp_time:
                                        try:
                                            dt = datetime.fromisoformat(str(rsvp_time))
                                            formatted_time = dt.strftime("%b %d, %I:%M %p")
                                            st.markdown(f"📅 RSVP'd: {formatted_time}")
                                        except:
                                            st.markdown(f"📅 RSVP'd: {rsvp_time}")
                                    
                                    checked_in = rsvp.get('checked_in', False)
                                    if checked_in:
                                        st.success("✅ Checked In")
                                
                                with col_c:
                                    if not checked_in:
                                        if st.button("Check In", key=f"checkin_{student_id}", use_container_width=True):
                                            if check_in_student(selected_event_id, student_id):
                                                st.success("Checked in!")
                                                st.cache_data.clear()
                                                st.rerun()
                                            else:
                                                st.error("Check-in failed")
                
                with tab2:
                    waitlist_rsvps = [r for r in rsvps if r.get('status') == 'waitlisted']
                    
                    if not waitlist_rsvps:
                        st.info("No one on waitlist")
                    else:
                        for rsvp in waitlist_rsvps:
                            with st.container(border=True):
                                student_name = rsvp.get('student_name', 'Unknown Student')
                                student_id = rsvp.get('student_id', 'N/A')
                                st.markdown(f"**{student_name}** - ID: {student_id}")
                                
                                rsvp_time = rsvp.get('rsvp_datetime', '')
                                if rsvp_time:
                                    try:
                                        dt = datetime.fromisoformat(str(rsvp_time))
                                        formatted_time = dt.strftime("%b %d, %I:%M %p")
                                        st.markdown(f"📅 Waitlisted: {formatted_time}")
                                    except:
                                        st.markdown(f"📅 Waitlisted: {rsvp_time}")
            
            st.divider()
            
            # Export and refresh buttons
            col_action1, col_action2, col_action3 = st.columns([1, 1, 2])
            
            with col_action1:
                if st.button("🔄 Refresh Data", use_container_width=True):
                    st.cache_data.clear()
                    st.rerun()
            
            with col_action2:
                if rsvps:
                    df = pd.DataFrame(rsvps)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"rsvps_{selected_event_id}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

# Footer
st.divider()
st.markdown("*RSVP data updates every 30 seconds. Use check-in to track attendance digitally.*")