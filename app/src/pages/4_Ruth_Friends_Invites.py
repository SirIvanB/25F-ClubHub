import streamlit as st
import requests

# Page config
st.set_page_config(
    page_title="Friends & Invites - ClubHub",
    page_icon="👥",
    layout="wide")

# API Base URL
API_BASE_URL = "http://web-api:4000"

# TODO: REPLACE WITH REAL AUTHENTICATION!
# Hardcoded student ID for testing - MUST update this when adding login system
# Should be: STUDENT_ID = st.session_state.get('user_id')
STUDENT_ID = 1  # ⚠️ TEMPORARY - COME BACK TO THIS!

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
st.title("👥 Friends & Invitations")
st.markdown("Invite others to events and manage your invitations")
st.divider()

# Fetch incoming invitations
def fetch_invitations():
    try:
        response = requests.get(
            f"{API_BASE_URL}/students/{STUDENT_ID}/invitations",
            timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"Could not fetch invitations: {e}")
        return []

# Fetch my RSVPs
@st.cache_data(ttl=30)
def fetch_my_events():
    try:
        response = requests.get(
            f"{API_BASE_URL}/students/{STUDENT_ID}/rsvps", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        return []

# Fetch all students (for suggested students dropdown)
@st.cache_data(ttl=60)
def fetch_all_students():
    try:
        response = requests.get(f"{API_BASE_URL}/students", timeout=5)
        if response.status_code == 200:
            students = response.json()
            # Filter out current user
            return [s for s in students if s.get('studentID') != STUDENT_ID]
        else:
            return []
    except Exception as e:
        return []

# Update invitation status
def update_invitation(invitation_id, new_status):
    try:
        response = requests.put(
            f"{API_BASE_URL}/students/{STUDENT_ID}/invitations/{invitation_id}",
            json={"status": new_status},
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error updating invitation: {e}")
        return False

# Send invitation
def send_invitation(event_id, recipient_id):
    try:
        response = requests.post(
            f"{API_BASE_URL}/invitations",
            json={
                "event_id": event_id,
                "sender_student_id": STUDENT_ID,
                "recipient_student_id": recipient_id
            },
            timeout=5)
        return response.status_code == 201
    except Exception as e:
        st.error(f"Error sending invitation: {e}")
        return False

# Get data
invitations = fetch_invitations()
my_events = fetch_my_events()
all_students = fetch_all_students()

# Section 1: Incoming Invitations
st.markdown("### 📬 Incoming Invitations")

pending_invitations = [inv for inv in invitations if inv.get('invitation_status') == 'pending']

if not pending_invitations:
    st.info("No pending invitations at the moment.")
else:
    st.markdown(f"You have **{len(pending_invitations)}** pending invitation(s)")

    for invitation in pending_invitations:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
    
            with col1:
                sender_name = f"{invitation.get('sender_first_name', '')} {invitation.get('sender_last_name', '')}"
                event_name = invitation.get('event_name', 'Unknown Event')
                event_date = invitation.get('start_datetime', '')
                
                st.markdown(f"**{sender_name}** invited you to:")
                st.markdown(f"🎉 **{event_name}**")
                if event_date:
                    st.markdown(f"📅 {event_date}")

            with col2:
                if st.button("✅ Accept", key=f"accept_{invitation.get('invitation_id')}", use_container_width=True):
                    if update_invitation(invitation.get('invitation_id'), 'accepted'):
                        st.success("Accepted!")
                        st.cache_data.clear()
                        st.rerun()
                
                if st.button("❌ Decline", key=f"decline_{invitation.get('invitation_id')}", use_container_width=True):
                    if update_invitation(invitation.get('invitation_id'), 'declined'):
                        st.warning("Declined")
                        st.cache_data.clear()
                        st.rerun()

st.divider()

# Section 2: Send Invitations
st.markdown("### 🎯 Invite Someone to Your Events")

if not my_events:
    st.info("You haven't RSVP'd to any events yet. RSVP to events first, then you can invite others!")
    if st.button("Browse Events", use_container_width=True):
        st.switch_page("pages/1_Ruth_Event_Discovery.py")
else:
    # Select event to invite people to
    event_options = {f"{e.get('event_name')} - {e.get('start_datetime', '')}": e.get('event_id') 
                     for e in my_events}
    
    selected_event_name = st.selectbox(
        "Select an event you're attending:",
        options=list(event_options.keys()))

    if selected_event_name:
        selected_event_id = event_options[selected_event_name]
        
        # Select student to invite
        if not all_students:
            st.warning("No other students found in the database.")
        else:
            student_options = {f"{s.get('firstName', '')} {s.get('lastName', '')} ({s.get('email', '')})": s.get('studentID') 
                              for s in all_students}
            
            selected_student_name = st.selectbox(
                "Select a student to invite:",
                options=list(student_options.keys()),
                help="These are suggested students based on campus activity")
            
            if selected_student_name:
                selected_student_id = student_options[selected_student_name]
                
                col_send, col_cancel = st.columns([1, 1])
                
                with col_send:
                    if st.button("📧 Send Invitation", type="primary", use_container_width=True):
                        if send_invitation(selected_event_id, selected_student_id):
                            st.success(f"Invitation sent to {selected_student_name.split('(')[0].strip()}!")
                            st.balloons()
                            st.cache_data.clear()
                        else:
                            st.error("Failed to send invitation. Please try again.")
                
                with col_cancel:
                    if st.button("Cancel", use_container_width=True):
                        st.rerun()

st.divider()

# Section 3: Invitation History
st.markdown("### 🗣️ Invitation History")

accepted_invitations = [inv for inv in invitations if inv.get('invitation_status') == 'accepted']
declined_invitations = [inv for inv in invitations if inv.get('invitation_status') == 'declined']

col_a, col_b = st.columns(2)

with col_a:
    st.markdown(f"**Accepted ({len(accepted_invitations)})**")
    if accepted_invitations:
        for inv in accepted_invitations[:5]:  # Show max 5
            st.markdown(f"✅ {inv.get('event_name', 'Event')}")
    else:
        st.caption("No accepted invitations")

with col_b:
    st.markdown(f"**Declined ({len(declined_invitations)})**")
    if declined_invitations:
        for inv in declined_invitations[:5]:  # Show max 5
            st.markdown(f"❌ {inv.get('event_name', 'Event')}")
    else:
        st.caption("No declined invitations")

# Footer
st.divider()
st.markdown("*Invite friends to events and build your campus community!*")