import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Server Management - ClubHub",
    page_icon="🖥️",
    layout="wide")

# API Base URL
API_BASE_URL = "http://web-api:4000"

# Sidebar navigation
st.sidebar.title("🖥️ David's Pages")
st.sidebar.markdown("**Current:** Server Management")
st.sidebar.page_link("pages/20_Admin_Home.py", label="Admin Home")
st.sidebar.page_link("pages/22_System_Metrics.py", label="System Metrics")
st.sidebar.page_link("pages/23_Audit_Logs.py", label="Audit Logs")
st.sidebar.page_link("pages/24_Alert_Management.py", label="Alert Management")
st.sidebar.divider()
st.sidebar.page_link("Home.py", label="← Back to Home")

# Main page title
st.title("🖥️ Server Management")
st.markdown("Monitor individual server health and activity")
st.divider()

# Fetch audit logs to get server information
@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_audit_logs():
    try:
        response = requests.get(f"{API_BASE_URL}/admin/audit-logs", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"Could not connect to API: {e}")
        return []

# Fetch metrics to get server counts
@st.cache_data(ttl=60)
def fetch_metrics():
    try:
        response = requests.get(f"{API_BASE_URL}/admin/metrics", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Could not connect to API: {e}")
        return None

# Get data
logs = fetch_audit_logs()
metrics = fetch_metrics()

if logs or metrics:
    # Summary from metrics
    if metrics:
        st.markdown("### 📊 Server Overview")
        col1, col2, col3 = st.columns(3)

        with col1:
            total_servers = int(metrics.get('total_servers', 0))
            st.metric("Total Servers", total_servers)

        with col2:
            servers_online = int(metrics.get('servers_online', 0))
            st.metric("Online", servers_online, delta=None, delta_color="normal")

        with col3:
            servers_offline = int(metrics.get('servers_offline', 0))
            st.metric("Offline", servers_offline, delta=None, delta_color="inverse")

        st.divider()

    # Process logs to get server information
    if logs:
        df = pd.DataFrame(logs)

        # Get unique servers
        if 'serverID' in df.columns:
            # Group by server to get latest info
            server_info = df.groupby('serverID').agg({
                'ipAddress': 'first',
                'serverStatus': 'first',
                'serverLastUpdated': 'first',
                'logID': 'count'  # Count logs per server
            }).reset_index()
            server_info.columns = ['Server ID', 'IP Address', 'Status', 'Last Updated', 'Log Count']

            # Sort by Server ID
            server_info = server_info.sort_values('Server ID')

            st.divider()

            # Server details table
            st.markdown(f"### 📋 Server Details ({len(server_info)} servers)")
            st.markdown("Complete list of all servers and their current status")

            # Format the dataframe for display
            display_df = server_info.copy()

            # Color code status
            def highlight_status(row):
                if row['Status'] == 'online':
                    return ['background-color: #d4edda'] * len(row)
                else:
                    return ['background-color: #f8d7da'] * len(row)

            # Display styled dataframe
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

            # Export functionality
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Server Report",
                data=csv,
                file_name=f"server_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

        else:
            st.info("No server information available in audit logs")

    st.divider()

    # Refresh button
    if st.button("🔄 Refresh Server Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # Warnings
    if metrics:
        servers_offline = int(metrics.get('servers_offline', 0))
        if servers_offline > 0:
            st.warning(f"⚠️ Warning: {servers_offline} server(s) currently offline. Check server status above for details.")

else:
    st.error("Unable to load server information. Please check if the API is running.")
    if st.button("Retry"):
        st.cache_data.clear()
        st.rerun()

# Footer
st.divider()
st.markdown("*Server data is cached for 60 seconds. Click Refresh for latest information.*")
