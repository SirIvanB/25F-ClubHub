import json
import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
import pandas as pd

SideBarLinks()

st.write("Accessing REST API from within Streamlit")

try:
    response = requests.get('http://web-api:4000/analytics/analytics/engagement')
    st.write(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        st.write(f"Response type: {type(data)}")
        st.write(f"Number of records: {len(data)}")
        
        if data:
            st.write("### Engagement Metrics (Last 30 Days)")
            
            # Show raw JSON
            st.json(data)
            
            # Convert to DataFrame and display as table
            df = pd.DataFrame(data)
            st.dataframe(df)
        else:
            st.warning("API returned empty array []")
            st.write("Debugging: Check if the query is returning data")
    else:
        st.error(f"API Error: {response.status_code}")
        st.code(response.text)
        
except Exception as e:
    st.error(f"Error: {e}")
    import traceback
    st.code(traceback.format_exc())



