import streamlit as st
import requests
import pandas as pd
import altair as alt

# Page config
st.set_page_config(
    page_title="Club Rankings - ClubHub",
    page_icon="🏆",
    layout="wide")

# API Base URL
API_BASE_URL = "http://web-api:4000"

# Sidebar navigation
st.sidebar.title("🎒 Ruth's Pages")
st.sidebar.page_link("pages/1_Ruth_Event_Discovery.py", label="Event Discovery")
st.sidebar.page_link("pages/2_Ruth_Club_Comparison.py", label="Club Comparison")
st.sidebar.page_link("pages/3_Ruth_My_Schedule.py", label="My Schedule")
st.sidebar.page_link("pages/4_Ruth_Friends_Invites.py", label="Friends & Invites")
st.sidebar.markdown("**Current:** Club Rankings")
st.sidebar.divider()
st.sidebar.page_link("Home.py", label="← Back to Home")

# Main page title
st.title("🏆 Club Rankings")
st.markdown("Discover top clubs by budget, members, events, and competitiveness")
st.divider()

# Ranking controls
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### 📊 Rank By:")
    rank_by = st.radio(
        "Select ranking metric:",
        options=["Budget", "Members", "Events", "Competitiveness"],
        horizontal=True,
        label_visibility="collapsed"
    )

with col2:
    st.markdown("### 📅 Current Period: 2025")
#    period = st.selectbox(
#        "Select period:",
#        options=["2024-Q4", "2024-Q3", "2024-Q2", "2024-Q1", "2025-Q1"],
#        label_visibility="collapsed")

st.divider()

# Insert line breaks into long club names so x-axis labels
def wrap_label(text, width=12):
    if not isinstance(text, str):
        return text
    text = text.strip()
    return "\n".join(text[i:i+width] for i in range(0, len(text), width))

# Fetch clubs data
@st.cache_data(ttl=60)
def fetch_clubs_for_ranking():
    try:
        # ✅ use the new API that already includes member_count & event_count
        clubs_response = requests.get(
            f"{API_BASE_URL}/clubs/clubs/with-metrics",
            timeout=5
        )
        if clubs_response.status_code != 200:
            return []

        clubs = clubs_response.json()

        # (optional but nice) make sure numeric fields are numeric
        for club in clubs:
            if "budget" in club and isinstance(club["budget"], str):
                try:
                    club["budget"] = float(club["budget"])
                except ValueError:
                    pass

        return clubs

    except Exception as e:
        st.error(f"Could not fetch clubs: {e}")
        return []

# Get clubs data
clubs_data = fetch_clubs_for_ranking()

if not clubs_data:
    st.warning("No clubs available. Check your database connection.")
else:
    # Create DataFrame for easier manipulation
    df = pd.DataFrame(clubs_data)
    
    # Map ranking type to column
    ranking_map = {
        "Budget": "budget",
        "Members": "member_count",
        "Events": "event_count",
        "Competitiveness": "competitiveness_level"}
    
    sort_column = ranking_map[rank_by]
    
    # Check if column exists, if not, show warning
    if sort_column not in df.columns:
        st.error(f"⚠️ {rank_by} data not available yet. Database schema may need updating.")
        st.info(f"Expected column '{sort_column}' in clubs data. Available columns: {list(df.columns)}")
    else:
        # Sort by selected metric (descending)
        df_sorted = df.sort_values(by=sort_column, ascending=False).reset_index(drop=True)
        df_sorted['rank'] = range(1, len(df_sorted) + 1)

        # 🥇🥈🥉 add medal indicator for top 3
        df_sorted['medal'] = df_sorted['rank'].map({1: "🥇", 2: "🥈", 3: "🥉"}).fillna("")

        # --- Bar chart with medals ---
        st.markdown(f"### 📊 Top 10 Clubs by {rank_by}")

        # Take top 10 and preserve descending order
        top10 = df_sorted.head(10).copy()

        # ✅ wrap long club names so labels show horizontally on multiple lines
        top10["club_name_wrapped"] = top10["club_name"].apply(wrap_label)
        x_order = list(top10["club_name_wrapped"])  # explicit x order: already sorted desc

        # Base bar chart
        base = alt.Chart(top10).encode(
            x=alt.X("club_name_wrapped:N", sort=x_order, title="Club"),
            y=alt.Y(f"{sort_column}:Q", title=rank_by),
            tooltip=[
                alt.Tooltip("club_name:N", title="Club"),
                alt.Tooltip(f"{sort_column}:Q", title=rank_by),
                alt.Tooltip("rank:Q", title="Rank")])

        bars = base.mark_bar()

        # Medal labels for top 3 only
        top3 = top10[top10["rank"] <= 3]

        medals = alt.Chart(top3).mark_text(
            dy=-10,      # move text above bar
            size=18
        ).encode(
            x=alt.X("club_name_wrapped:N", sort=x_order),
            y=alt.Y(f"{sort_column}:Q"),
            text="medal:N")

        st.altair_chart(bars + medals, use_container_width=True)
        
        st.divider()
        
        # Display detailed table
        st.markdown("### 📋 Detailed Rankings")
        
        # Select columns to display
        display_columns = ['rank', 'club_name', 'budget', 'member_count', 'event_count']
        
        # Add competitiveness if it exists
        if 'competitiveness_level' in df_sorted.columns:
            display_columns.append('competitiveness_level')
        
        # Filter to existing columns
        available_columns = [col for col in display_columns if col in df_sorted.columns]
        
        # Rename for display
        column_names = {
            'rank': 'Rank',
            'club_name': 'Club Name',
            'budget': 'Budget ($)',
            'member_count': 'Members',
            'event_count': 'Events',
            'competitiveness_level': 'Competitiveness (1-10)'}
        
        display_df = df_sorted[available_columns].rename(columns=column_names)
        
        # Display with highlighting
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank": st.column_config.NumberColumn(format="%d"),
                "Budget ($)": st.column_config.NumberColumn(format="$%.2f"),
                "Members": st.column_config.NumberColumn(format="%d"),
                "Events": st.column_config.NumberColumn(format="%d"),
                "Competitiveness (1-10)": st.column_config.NumberColumn(format="%d")})
        
        # Show top 3 highlights
        st.divider()
        st.markdown("### 🌟 Highlights")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            top_club = df_sorted.iloc[0]
            st.success(f"🥇 **#1: {top_club['club_name']}**")
            if sort_column in top_club:
                value = top_club[sort_column]
                if rank_by == "Budget":
                    st.markdown(f"Budget: **${value:,.2f}**")
                elif rank_by == "Competitiveness":
                    st.markdown(f"Competitiveness: **{int(value)}/10**")
                else:
                    st.markdown(f"{rank_by}: **{int(value)}**")
        
        with col_b:
            if len(df_sorted) > 1:
                second_club = df_sorted.iloc[1]
                st.info(f"🥈 **#2: {second_club['club_name']}**")
                if sort_column in second_club:
                    value = second_club[sort_column]
                    if rank_by == "Budget":
                        st.markdown(f"Budget: **${value:,.2f}**")
                    elif rank_by == "Competitiveness":
                        st.markdown(f"Competitiveness: **{int(value)}/10**")
                    else:
                        st.markdown(f"{rank_by}: **{int(value)}**")
        
        with col_c:
            if len(df_sorted) > 2:
                third_club = df_sorted.iloc[2]
                st.warning(f"🥉 **#3: {third_club['club_name']}**")
                if sort_column in third_club:
                    value = third_club[sort_column]
                    if rank_by == "Budget":
                        st.markdown(f"Budget: **${value:,.2f}**")
                    elif rank_by == "Competitiveness":
                        st.markdown(f"Competitiveness: **{int(value)}/10**")
                    else:
                        st.markdown(f"{rank_by}: **{int(value)}**")

# Footer
st.divider()
st.markdown("*Rankings update every quarter based on club activity and metrics*")