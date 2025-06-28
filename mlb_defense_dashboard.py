
# Filename: mlb_defense_dashboard.py

import streamlit as st
import pandas as pd
from pybaseball import statcast_fielding
from datetime import datetime

st.set_page_config(layout="wide", page_title="MLB Defensive Analytics")

st.title("⚾ MLB Defensive Metrics Dashboard (Live via PyBaseball)")

# User inputs
year = st.selectbox("Select Season Year", options=list(range(2018, datetime.now().year + 1))[::-1])
min_games = st.slider("Minimum Innings Played", 100, 1000, 500)

st.info("This app pulls live defensive data using PyBaseball and allows you to compare MLB players by position or team.")

# Load data
@st.cache_data(show_spinner=True)
def load_defense_data(year):
    start_date = f"{year}-03-01"
    end_date = f"{year}-10-31"
    df = statcast_fielding(start_date, end_date)
    return df

data = load_defense_data(year)

# Filter
positions = data['position'].dropna().unique()
position_filter = st.multiselect("Filter by Position(s)", options=sorted(positions), default=['SS', 'CF'])
team_filter = st.multiselect("Filter by Team(s)", options=sorted(data['team'].dropna().unique()), default=[])

filtered = data.copy()

if position_filter:
    filtered = filtered[filtered['position'].isin(position_filter)]
if team_filter:
    filtered = filtered[filtered['team'].isin(team_filter)]

filtered = filtered[filtered['innings'] >= min_games]

st.subheader("Defensive Leaderboard")

# Show table
cols_to_display = [
    'player_name', 'team', 'position', 'innings',
    'outs_above_average', 'arm_strength', 'release_spin_rate'
]

st.dataframe(filtered[cols_to_display].sort_values(by='outs_above_average', ascending=False).reset_index(drop=True), use_container_width=True)

# Visualization
st.subheader("📊 Compare Players")

metric = st.selectbox("Select Metric to Compare", ['outs_above_average', 'arm_strength', 'release_spin_rate'])

top_players = filtered.sort_values(by=metric, ascending=False).head(10)

st.bar_chart(top_players.set_index('player_name')[metric])
