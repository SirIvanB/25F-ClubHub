import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Audit Logs - ClubHub",
    page_icon="📋",
    layout="wide")

# API Base URL
API_BASE_URL = "http://web-api:4000"

# Sidebar navigation
st.sidebar.title("🖥️ David's Pages")
st.sidebar.markdown("**Current:** Audit Logs")
st.sidebar.page_link("pages/20_Admin_Home.py", label="Admin Home")
st.sidebar.page_link("pages/22_System_Metrics.py", label="System Metrics")
st.sidebar.page_link("pages/24_Alert_Management.py", label="Alert Management")
st.sidebar.page_link("pages/25_Server_Management.py", label="Server Management")
st.sidebar.divider()
st.sidebar.page_link("Home.py", label="← Back to Home")

# Main page title
st.title("📋 Audit Logs Viewer")
st.markdown("Review system authentication, event activity, and system action logs")
st.divider()

# Fetch audit logs from API
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

# Get logs
logs = fetch_audit_logs()

if logs:
    # Convert to DataFrame
    df = pd.DataFrame(logs)

    # Filter row
    st.markdown("### 🔍 Filters")
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    # Get unique values for filters
    severities = ['All Severities'] + sorted(df['severity'].dropna().unique().tolist()) if 'severity' in df.columns else ['All Severities']
    statuses = ['All Statuses'] + sorted(df['status'].dropna().unique().tolist()) if 'status' in df.columns else ['All Statuses']
    server_ids = ['All Servers'] + sorted([str(x) for x in df['serverID'].dropna().unique().tolist()]) if 'serverID' in df.columns else ['All Servers']

    with col1:
        severity_filter = st.selectbox("⚠️ Severity", severities)

    with col2:
        status_filter = st.selectbox("📊 Status", statuses)

    with col3:
        server_filter = st.selectbox("🖥️ Server", server_ids)

    with col4:
        st.markdown("<br>", unsafe_allow_html=True)  # spacing
        if st.button("Clear Filters", use_container_width=True):
            st.rerun()

    # Search bar
    search_query = st.text_input("🔍 Search logs...", placeholder="Search by any field...")

    st.divider()

    # Apply filters
    filtered_df = df.copy()

    if severity_filter != 'All Severities':
        filtered_df = filtered_df[filtered_df['severity'] == severity_filter]

    if status_filter != 'All Statuses':
        filtered_df = filtered_df[filtered_df['status'] == status_filter]

    if server_filter != 'All Servers':
        filtered_df = filtered_df[filtered_df['serverID'].astype(str) == server_filter]

    if search_query:
        # Search across all columns
        mask = filtered_df.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
        filtered_df = filtered_df[mask]

    # Display summary
    st.markdown(f"### 📊 Showing {len(filtered_df)} of {len(df)} logs")

    # Summary metrics
    if len(filtered_df) > 0:
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

        with metric_col1:
            error_count = len(filtered_df[filtered_df['severity'] == 'ERROR']) if 'severity' in filtered_df.columns else 0
            st.metric("Error Logs", error_count)

        with metric_col2:
            warning_count = len(filtered_df[filtered_df['severity'] == 'WARNING']) if 'severity' in filtered_df.columns else 0
            st.metric("Warning Logs", warning_count)

        with metric_col3:
            info_count = len(filtered_df[filtered_df['severity'] == 'INFO']) if 'severity' in filtered_df.columns else 0
            st.metric("Info Logs", info_count)

        with metric_col4:
            unique_servers = filtered_df['serverID'].nunique() if 'serverID' in filtered_df.columns else 0
            st.metric("Unique Servers", unique_servers)

        st.divider()

        # Display logs
        st.markdown("### 📜 Log Entries")

        # Sort by timestamp descending
        if 'logTimestamp' in filtered_df.columns:
            filtered_df = filtered_df.sort_values('logTimestamp', ascending=False)

        # Display each log entry
        for idx, log in filtered_df.iterrows():
            with st.container(border=True):
                # Header row with severity badge
                col_a, col_b = st.columns([3, 1])

                with col_a:
                    severity = log.get('severity', 'UNKNOWN')
                    status = log.get('status', 'UNKNOWN')

                    # Color code severity
                    if severity == 'ERROR':
                        severity_color = "🔴"
                    elif severity == 'WARNING':
                        severity_color = "🟡"
                    elif severity == 'INFO':
                        severity_color = "🟢"
                    else:
                        severity_color = "⚪"

                    st.markdown(f"**{severity_color} {severity}** | Status: {status}")

                with col_b:
                    log_id = log.get('logID', 'N/A')
                    st.markdown(f"*Log ID: {log_id}*")

                # Timestamp
                timestamp = log.get('logTimestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
                        formatted_time = dt.strftime("%Y-%m-%d %I:%M:%S %p")
                        st.markdown(f"🕐 **Time:** {formatted_time}")
                    except:
                        st.markdown(f"🕐 **Time:** {timestamp}")

                # Server information
                server_id = log.get('serverID', 'N/A')
                ip_address = log.get('ipAddress', 'N/A')
                server_status = log.get('serverStatus', 'N/A')

                st.markdown(f"🖥️ **Server:** ID {server_id} | IP: {ip_address} | Status: {server_status}")

                # Server last updated
                server_updated = log.get('serverLastUpdated', '')
                if server_updated:
                    try:
                        dt_updated = datetime.fromisoformat(str(server_updated).replace('Z', '+00:00'))
                        formatted_updated = dt_updated.strftime("%Y-%m-%d %I:%M:%S %p")
                        st.markdown(f"📅 **Server Last Updated:** {formatted_updated}")
                    except:
                        st.markdown(f"📅 **Server Last Updated:** {server_updated}")

    else:
        st.info("No logs match the selected filters")

    st.divider()

    # Export and refresh buttons
    export_col1, export_col2, export_col3 = st.columns([1, 1, 2])

    with export_col1:
        if st.button("🔄 Refresh Logs", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    with export_col2:
        # Convert to CSV for download
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

else:
    st.error("Unable to load audit logs. Please check if the API is running.")
    if st.button("Retry"):
        st.cache_data.clear()
        st.rerun()

# Footer
st.divider()
st.markdown("*Logs are cached for 60 seconds. Click Refresh for latest data.*")
