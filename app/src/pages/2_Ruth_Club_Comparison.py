import streamlit as st
import requests
import pandas as pd

# Page config
st.set_page_config(
    page_title="Club Comparison - ClubHub",
    page_icon="⚖️",
    layout="wide"
)

# API Base URL
API_BASE_URL = "http://web-api:4000"

# Sidebar navigation
st.sidebar.title("🎒 Ruth's Pages")
st.sidebar.page_link("pages/1_Ruth_Event_Discovery.py", label="Event Discovery")
st.sidebar.markdown("**Current:** Club Comparison")
st.sidebar.page_link("pages/3_Ruth_My_Schedule.py", label="My Schedule")
st.sidebar.page_link("pages/4_Ruth_Friends_Invites.py", label="Friends & Invites")
st.sidebar.page_link("pages/5_Ruth_Club_Rankings.py", label="Club Rankings")
st.sidebar.divider()
st.sidebar.page_link("Home.py", label="← Back to Home")

# Main page title
st.title("⚖️ Club Comparison")
st.markdown("Try comparing your clubs side-by-side to find the best fit 🧐")
st.divider()

# Fetch all clubs
@st.cache_data(ttl=60)
def fetch_all_clubs():
    try:
        response = requests.get(f"{API_BASE_URL}/clubs", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"Could not connect to API: {e}")
        return []

# Fetch comparison data
def fetch_club_comparison(club_ids):
    try:
        ids_str = ','.join(map(str, club_ids))
        response = requests.get(
            f"{API_BASE_URL}/clubs/compare?ids={ids_str}", 
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"Could not fetch comparison: {e}")
        return []

# Get all clubs
all_clubs = fetch_all_clubs()

if not all_clubs:
    st.warning("No clubs available. Check your database connection.")
else:
    # Create club selection
    st.markdown("### Select Clubs to Compare (2-4 clubs)")
    
    # Create a mapping of club names to IDs
    club_options = {club['club_name']: club['club_id'] for club in all_clubs}
    
    # Multi-select for clubs
    selected_club_names = st.multiselect(
        "Choose clubs:",
        options=list(club_options.keys()),
        max_selections=4,
        help="Select 2-4 clubs to compare"
    )
    
    # Compare button
    if len(selected_club_names) < 2:
        st.info("👆 Select at least 2 clubs to compare")
    else:
        if st.button("Compare Selected Clubs", type="primary", use_container_width=True):
            # Get club IDs for selected clubs
            selected_club_ids = [club_options[name] for name in selected_club_names]
            
            # Fetch comparison data
            comparison_data = fetch_club_comparison(selected_club_ids)
            
            if comparison_data:
                st.divider()
                st.markdown("### 📊 Comparison Results")
                
                # Create comparison table
                comparison_df = pd.DataFrame(comparison_data)
                
                # Rename columns for display
                column_names = {
                    'club_name': 'Club Name',
                    'curriculum': 'Description',
                    'budget': 'Budget ($)',
                    'number_of_members': 'Members',
                    'benefits': 'Benefits',
                    'competitiveness_level': 'Competitiveness'
                }
                
                comparison_df = comparison_df.rename(columns=column_names)
                
                # Display as table
                st.dataframe(
                    comparison_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Visual comparison charts
                st.divider()
                st.markdown("### 📈 Visual Comparison")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Budget Comparison**")
                    budget_chart = comparison_df[['Club Name', 'Budget ($)']].set_index('Club Name')
                    st.bar_chart(budget_chart)
                
                with col2:
                    st.markdown("**Member Count Comparison**")
                    members_chart = comparison_df[['Club Name', 'Members']].set_index('Club Name')
                    st.bar_chart(members_chart)
                
                # Highlight best/worst
                st.divider()
                st.markdown("### 💡 Quick Insights")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    # Largest club
                    max_members = comparison_df.loc[comparison_df['Members'].idxmax()]
                    st.success(f"🏆 **Largest:** {max_members['Club Name']} ({max_members['Members']} members)")
                
                with col_b:
                    # Highest budget
                    max_budget = comparison_df.loc[comparison_df['Budget ($)'].idxmax()]
                    st.info(f"💰 **Highest Budget:** {max_budget['Club Name']} (${max_budget['Budget ($)']})")
            else:
                st.error("Could not load comparison data. Please try again.")

# Footer
st.divider()
st.markdown("*Use this comparison to make an informed decision about which clubs to join!*")