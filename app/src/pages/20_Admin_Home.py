import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests

# Page config
st.set_page_config(
    page_title="Admin Home - ClubHub",
    page_icon="🖥️",
    layout="wide")

# API Base URL
API_BASE_URL = "http://web-api:4000"

# Sidebar navigation
st.sidebar.title("🖥️ David's Pages")
st.sidebar.markdown("**Current:** Admin Home")
st.sidebar.page_link("pages/26_Admin_Demo.py", label="🎯 Demo & Pitch", icon="🎯")
st.sidebar.divider()
st.sidebar.page_link("pages/22_System_Metrics.py", label="System Metrics")
st.sidebar.page_link("pages/23_Audit_Logs.py", label="Audit Logs")
st.sidebar.page_link("pages/24_Alert_Management.py", label="Alert Management")
st.sidebar.page_link("pages/25_Server_Management.py", label="Server Management")
st.sidebar.divider()
st.sidebar.page_link("Home.py", label="← Back to Home")

# Main page
st.title('🖥️ System Admin Dashboard')
st.markdown("Welcome, David! Monitor and manage the ClubHub platform.")
st.divider()

# Fetch metrics for dashboard
@st.cache_data(ttl=60)
def fetch_metrics():
    try:
        response = requests.get(f"{API_BASE_URL}/admin/metrics", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        logger.error(f"Could not connect to metrics API: {e}")
        return None

# Fetch alerts for dashboard
@st.cache_data(ttl=60)
def fetch_alerts():
    try:
        response = requests.get(f"{API_BASE_URL}/admin/alerts", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        logger.error(f"Could not connect to alerts API: {e}")
        return []

# Get data
metrics = fetch_metrics()
alerts = fetch_alerts()

# System Status Overview
st.markdown("### 📊 System Status")

if metrics:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_servers = int(metrics.get('total_servers', 0))
        st.metric("Total Servers", total_servers)

    with col2:
        servers_online = int(metrics.get('servers_online', 0))
        st.metric("Servers Online", servers_online)

    with col3:
        servers_offline = int(metrics.get('servers_offline', 0))
        st.metric("Servers Offline", servers_offline, delta=None, delta_color="inverse")

    with col4:
        if total_servers > 0:
            uptime_pct = round((servers_online / total_servers) * 100, 1)
            st.metric("Uptime", f"{uptime_pct}%")
        else:
            st.metric("Uptime", "N/A")

    # Alert summary
    alert_count = len(alerts)
    if alert_count > 0:
        st.warning(f"⚠️ {alert_count} unresolved alert(s) require attention")
    else:
        st.success("✓ No active alerts - system operating normally")

    # Log activity summary
    log_col1, log_col2, log_col3 = st.columns(3)

    with log_col1:
        total_logs = metrics.get('total_logs_last_hour', 0)
        st.metric("Logs (Last Hour)", total_logs)

    with log_col2:
        error_logs = metrics.get('error_logs_last_hour', 0)
        st.metric("Error Logs", error_logs)

    with log_col3:
        error_rate = metrics.get('error_rate_last_hour')
        if error_rate is not None:
            error_rate_pct = round(error_rate * 100, 2)
            st.metric("Error Rate", f"{error_rate_pct}%")
        else:
            st.metric("Error Rate", "N/A")

else:
    st.warning("Unable to load system metrics. API may be unavailable.")

st.divider()

# Quick Actions
st.markdown("### ⚡ Quick Actions")

action_col1, action_col2, action_col3, action_col4 = st.columns(4)

with action_col1:
    if st.button('🎯 Demo & Pitch', type='primary', use_container_width=True):
        st.switch_page('pages/26_Admin_Demo.py')
    st.markdown("**Presentation-ready demo** of all admin features")

with action_col2:
    if st.button('📊 View System Metrics', type='primary', use_container_width=True):
        st.switch_page('pages/22_System_Metrics.py')
    st.markdown("Monitor real-time server health and performance")

with action_col3:
    if st.button('🚨 Manage Alerts', type='primary', use_container_width=True):
        st.switch_page('pages/24_Alert_Management.py')
    alert_count = len(alerts)
    if alert_count > 0:
        st.markdown(f"⚠️ **{alert_count} unresolved alerts**")
    else:
        st.markdown("✓ No unresolved alerts")

with action_col4:
    if st.button('📋 View Audit Logs', type='primary', use_container_width=True):
        st.switch_page('pages/23_Audit_Logs.py')
    st.markdown("Review system activity and authentication logs")

st.divider()

# Recent Alerts Preview
if alerts and len(alerts) > 0:
    st.markdown("### 🚨 Recent Alerts")
    st.markdown(f"Showing {min(3, len(alerts))} of {len(alerts)} unresolved alerts")

    for i, alert in enumerate(alerts[:3]):  # Show top 3 alerts
        with st.container(border=True):
            alert_type = alert.get('alertType', 'Unknown')
            alert_id = alert.get('alertID', 'N/A')
            description = alert.get('description', 'No description')

            col_a, col_b = st.columns([3, 1])

            with col_a:
                st.markdown(f"**{alert_type}** (ID: {alert_id})")
                st.markdown(f"{description}")

            with col_b:
                if st.button("View →", key=f"view_alert_{alert_id}", use_container_width=True):
                    st.switch_page('pages/24_Alert_Management.py')

    if len(alerts) > 3:
        st.markdown(f"*...and {len(alerts) - 3} more alerts*")

st.divider()

# System Health Indicator
if metrics:
    servers_offline = int(metrics.get('servers_offline', 0))
    error_rate = metrics.get('error_rate_last_hour', 0)

    # Determine overall health
    if servers_offline == 0 and (error_rate is None or error_rate < 0.05):
        st.success("✓ System Health: EXCELLENT - All systems operational")
    elif servers_offline > 0 or (error_rate and error_rate > 0.10):
        st.error("⚠️ System Health: NEEDS ATTENTION - Issues detected")
    else:
        st.warning("⚠️ System Health: FAIR - Minor issues detected")

# Footer
st.divider()
st.markdown("*Dashboard updates every 60 seconds. Refresh page for latest data.*")
