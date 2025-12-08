
##################################################
# This is the main/entry-point file for the 
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
from modules.nav import SideBarLinks

# Page config
st.set_page_config(
    page_title="ClubHub",
    page_icon="🎓",
    layout="wide"
)

# If a user is at this page, we assume they are not 
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false. 
st.session_state['authenticated'] = False

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel. 
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)

# ***************************************************
#    The major content of this page
# ***************************************************

# set the title of the page and provide a simple prompt. 
logger.info("Loading the Home page of the app")
# Title
st.title("🎓 Welcome to ClubHub!")
st.markdown("### Centralized Campus Event Management Platform")
st.divider()

#introduction
st.markdown("""
ClubHub is a platform that connects students, club organizers, administrators, and data analysts 
to make campus life more organized and engaging.
""")

st.divider()
st.write('#### HI! As which user would you like to log in?')

# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user 
# can click to MIMIC logging in as that mock user. 

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### 🎒 Student")
    st.markdown("**Ruth Doe**")
    st.markdown("*New Student*")
    st.markdown("""
    - Discover events
    - Compare clubs
    - Manage schedule
    - Invite friends
    """)
    if st.button("Enter as Ruth", use_container_width=True):
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'student'
        st.session_state['first_name'] = 'Ruth'
        logger.info("Logging in as Student Persona")
        st.switch_page("pages/1_Ruth_Event_Discovery.py")

with col2:
    st.markdown("### 📋 Event Coordinator")
    st.markdown("**Sofia Martinez**")
    st.markdown("*Club Leader*")
    st.markdown("""
    - Publish events
    - Manage RSVPs
    - Track attendance
    - View analytics
    """)
    if st.button("Enter as Sofia", use_container_width=True):
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'event_coordinator'
        st.session_state['first_name'] = 'Sofia'
        logger.info("Logging in as Event Coordinator Persona")
        st.switch_page("pages/6_Sofia_My_Events.py")


with col3:
    st.markdown("### 🔧 Server Admin")
    st.markdown("**David Kim**")
    st.markdown("*IT Administrator*")
    st.markdown("""
    - Monitor system
    - View audit logs
    - Manage alerts
    - Check metrics
    """)
    if st.button("Enter as David", use_container_width=True):
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'administrator'
        st.session_state['first_name'] = 'David'
        logger.info("Logging in as System Administrator Persona")
        st.switch_page("pages/20_Admin_Home.py")

with col4:
    st.markdown("### 📊 Data Analyst")
    st.markdown("**Marcus Rodriguez**")
    st.markdown("*Student Affairs*")
    st.markdown("""
    - View engagement
    - Analyze searches
    - Track demographics
    - Generate reports
    """)
    if st.button("Enter as Marcus", use_container_width=True):
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'data_analyst'
        st.session_state['first_name'] = 'Marcus'
        logger.info("Logging in as Data Analyst Persona")
        st.switch_page("pages/41_Engagement_Overview.py")
# ON TOP IS ORIGINAL HOME PAGE! HERE IS A NEW ONE!

st.divider()

# Footer
st.markdown("""
---
**CS 3200 - Database Design Project | Team: Everett and Friends**
""")


