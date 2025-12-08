import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Alert Management - ClubHub",
    page_icon="🚨",
    layout="wide")

# API Base URL
API_BASE_URL = "http://web-api:4000"

# Sidebar navigation
st.sidebar.title("🖥️ David's Pages")
st.sidebar.markdown("**Current:** Alert Management")
st.sidebar.page_link("pages/20_Admin_Home.py", label="Admin Home")
st.sidebar.page_link("pages/22_System_Metrics.py", label="System Metrics")
st.sidebar.page_link("pages/23_Audit_Logs.py", label="Audit Logs")
st.sidebar.page_link("pages/25_Server_Management.py", label="Server Management")
st.sidebar.divider()
st.sidebar.page_link("Home.py", label="← Back to Home")

# Main page title
st.title("🚨 Alert Management")
st.markdown("View and resolve system alerts")
st.divider()

# Fetch alerts from API
@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_alerts():
    try:
        response = requests.get(f"{API_BASE_URL}/admin/alerts", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"Could not connect to API: {e}")
        return []

# Function to resolve an alert
def resolve_alert(alert_id):
    try:
        response = requests.put(f"{API_BASE_URL}/admin/alerts/{alert_id}", timeout=5)
        if response.status_code == 200:
            return True, "Alert resolved successfully!"
        elif response.status_code == 404:
            return False, "Alert not found"
        else:
            return False, f"Error: Status {response.status_code}"
    except Exception as e:
        return False, f"Could not connect to API: {e}"

# Get alerts
alerts = fetch_alerts()

if alerts:
    # Summary metrics
    st.markdown("### 📊 Alert Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_alerts = len(alerts)
        st.metric("Total Unresolved Alerts", total_alerts)

    with col2:
        # Count by alert type
        if total_alerts > 0:
            df = pd.DataFrame(alerts)
            alert_types = df['alertType'].nunique() if 'alertType' in df.columns else 0
            st.metric("Alert Types", alert_types)
        else:
            st.metric("Alert Types", 0)

    with col3:
        # Count alerts with eventID
        event_alerts = len([a for a in alerts if a.get('eventID')]) if alerts else 0
        st.metric("Event-Related", event_alerts)

    with col4:
        # Count alerts with studentID
        student_alerts = len([a for a in alerts if a.get('studentID')]) if alerts else 0
        st.metric("Student-Related", student_alerts)

    st.divider()

    # Visualization
    if total_alerts > 0:
        col_viz1, col_viz2 = st.columns(2)

        with col_viz1:
            st.markdown("### Alert Type Distribution")
            df = pd.DataFrame(alerts)
            if 'alertType' in df.columns:
                type_counts = df['alertType'].value_counts().reset_index()
                type_counts.columns = ['Alert Type', 'Count']

                fig = px.bar(
                    type_counts,
                    x='Alert Type',
                    y='Count',
                    title='Alerts by Type',
                    color='Count',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No alert type data available")

        with col_viz2:
            st.markdown("### Alert Category Breakdown")
            if 'alertType' in df.columns:
                fig = px.pie(
                    type_counts,
                    values='Count',
                    names='Alert Type',
                    title='Alert Categories'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No alert type data available")

        st.divider()

    # Alerts list
    st.markdown("### 🚨 Unresolved Alerts")

    if total_alerts > 0:
        # Display alerts
        for alert in alerts:
            with st.container(border=True):
                # Header
                col_header1, col_header2, col_header3 = st.columns([2, 2, 1])

                with col_header1:
                    alert_type = alert.get('alertType', 'Unknown Type')
                    alert_id = alert.get('alertID', 'N/A')

                    # Color code based on alert type
                    if 'error' in alert_type.lower() or 'critical' in alert_type.lower():
                        icon = "🔴"
                    elif 'warning' in alert_type.lower():
                        icon = "🟡"
                    else:
                        icon = "🟠"

                    st.markdown(f"**{icon} {alert_type}**")

                with col_header2:
                    st.markdown(f"*Alert ID: {alert_id}*")

                with col_header3:
                    # Resolve button
                    if st.button("✓ Resolve", key=f"resolve_{alert_id}", use_container_width=True):
                        success, message = resolve_alert(alert_id)
                        if success:
                            st.success(message)
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(message)

                # Description
                description = alert.get('description', 'No description available')
                st.markdown(f"📄 **Description:** {description}")

                # Related entities
                entity_col1, entity_col2 = st.columns(2)

                with entity_col1:
                    event_id = alert.get('eventID')
                    if event_id:
                        st.markdown(f"🎯 **Related Event:** {event_id}")

                with entity_col2:
                    student_id = alert.get('studentID')
                    if student_id:
                        st.markdown(f"👤 **Related Student:** {student_id}")

    else:
        st.success("✓ No unresolved alerts! All systems are functioning normally.")

    st.divider()

    # Refresh button
    if st.button("🔄 Refresh Alerts", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

else:
    # Check if it's because there are no alerts or API error
    st.success("✓ No unresolved alerts found. System is healthy!")
    st.info("If you expect to see alerts, please check if the API is running.")
    if st.button("Retry"):
        st.cache_data.clear()
        st.rerun()

# Footer
st.divider()
st.markdown("*Alerts are cached for 60 seconds. Resolved alerts are automatically removed from this view.*")
