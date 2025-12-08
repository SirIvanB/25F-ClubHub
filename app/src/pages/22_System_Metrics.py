import streamlit as st
import requests

# Page config
st.set_page_config(
    page_title="System Metrics - ClubHub",
    page_icon="📊",
    layout="wide")

# API Base URL
API_BASE_URL = "http://web-api:4000"

# Sidebar navigation
st.sidebar.title("🖥️ David's Pages")
st.sidebar.markdown("**Current:** System Metrics")
st.sidebar.page_link("pages/20_Admin_Home.py", label="Admin Home")
st.sidebar.page_link("pages/23_Audit_Logs.py", label="Audit Logs")
st.sidebar.page_link("pages/24_Alert_Management.py", label="Alert Management")
st.sidebar.page_link("pages/25_Server_Management.py", label="Server Management")
st.sidebar.divider()
st.sidebar.page_link("Home.py", label="← Back to Home")

# Main page title
st.title("📊 System Metrics Dashboard")
st.markdown("Monitor real-time system health and performance")
st.divider()

# Fetch metrics from API
@st.cache_data(ttl=60)  # Cache for 60 seconds
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

# Get metrics
metrics = fetch_metrics()

if metrics:
    # Top row - Key metrics
    st.markdown("### 🖥️ Server Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_servers = int(metrics.get('total_servers', 0))
        st.metric(
            label="Total Servers",
            value=total_servers,
            delta=None
        )

    with col2:
        servers_online = int(metrics.get('servers_online', 0))
        st.metric(
            label="Servers Online",
            value=servers_online,
            delta=None,
            delta_color="normal"
        )

    with col3:
        servers_offline = int(metrics.get('servers_offline', 0))
        delta_color = "inverse" if servers_offline > 0 else "normal"
        st.metric(
            label="Servers Offline",
            value=servers_offline,
            delta=None,
            delta_color=delta_color
        )

    with col4:
        if total_servers > 0:
            uptime_pct = round((servers_online / total_servers) * 100, 1)
        else:
            uptime_pct = 0
        st.metric(
            label="Uptime",
            value=f"{uptime_pct}%",
            delta=None
        )

    st.divider()

    # Log activity section
    st.markdown("### 📋 Log Activity (Last Hour)")
    log_col1, log_col2, log_col3 = st.columns(3)

    with log_col1:
        total_logs = int(metrics.get('total_logs_last_hour', 0))
        st.metric(
            label="Total Logs",
            value=total_logs,
            delta=None
        )

    with log_col2:
        error_logs = int(metrics.get('error_logs_last_hour', 0))
        st.metric(
            label="Error Logs",
            value=error_logs,
            delta=None,
            delta_color="inverse"
        )

    with log_col3:
        error_rate = metrics.get('error_rate_last_hour')
        if error_rate is not None:
            error_rate_pct = round(error_rate * 100, 2)
            st.metric(
                label="Error Rate",
                value=f"{error_rate_pct}%",
                delta=None,
                delta_color="inverse"
            )
        else:
            st.metric(
                label="Error Rate",
                value="N/A",
                delta=None
            )

    st.divider()

    # Refresh button
    col_refresh1, col_refresh2, col_refresh3 = st.columns([1, 1, 2])
    with col_refresh1:
        if st.button("🔄 Refresh Metrics", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # System status indicator
    if servers_offline > 0:
        st.warning(f"⚠️ Warning: {servers_offline} server(s) offline. Check Server Management for details.")
    elif error_rate and error_rate > 0.1:  # More than 10% error rate
        st.warning(f"⚠️ Warning: High error rate detected ({error_rate_pct}%). Check Audit Logs for details.")
    else:
        st.success("✓ All systems operational")

else:
    st.error("Unable to load system metrics. Please check if the API is running.")
    if st.button("Retry"):
        st.cache_data.clear()
        st.rerun()

# Footer
st.divider()
st.markdown("*Metrics are updated every 60 seconds. Click Refresh for latest data.*")
