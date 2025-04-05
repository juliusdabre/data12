
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import matplotlib.pyplot as plt

# --- USER LOGIN ---
USERS = {"admin": "pass123", "propwealth": "invest2025"}

def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
        else:
            st.sidebar.error("Invalid credentials")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if not st.session_state.logged_in:
    login()
    st.stop()

# --- LOAD DATA ---
@st.cache_data
def load_data():
    return pd.read_excel("Book2.xlsx", sheet_name="Sheet1")

st.image("PropWealth logo final-05 (4).png", width=200)
st.title("PropwealthNext: Investment Dashboard")

# --- STYLE ---
st.markdown("""
    <style>
    .main, .css-18e3th9 { background-color: #fff0f5; }
    .stApp { color: black; }
    </style>
""", unsafe_allow_html=True)

# --- DATA ---
df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🎛️ Filter Suburbs")
states = df['State'].dropna().unique()
regions = df['Region\n(SA4)'].dropna().unique()
sa3s = df['Sub Region\n(SA3)'].dropna().unique()
property_types = df['Property\nType'].dropna().unique() if 'Property\nType' in df.columns else []

selected_states = st.sidebar.multiselect("State", states)
selected_regions = st.sidebar.multiselect("Region (SA4)", regions)
selected_sa3s = st.sidebar.multiselect("Sub Region (SA3)", sa3s)
selected_property = st.sidebar.multiselect("Property Type", property_types)

min_yield = st.sidebar.slider("Min Yield (%)", float(df['Yield'].min()), float(df['Yield'].max()), float(df['Yield'].mean()))
min_score = st.sidebar.slider("Min Investor Score", 0, 100, 50)
min_growth = st.sidebar.slider("Min 12m Growth %", int(df['12m Growth (%)'].min()), int(df['12m Growth (%)'].max()), 0)

# --- FILTERING ---
filtered = df.copy()
if selected_states:
    filtered = filtered[filtered['State'].isin(selected_states)]
if selected_regions:
    filtered = filtered[filtered['Region\n(SA4)'].isin(selected_regions)]
if selected_sa3s:
    filtered = filtered[filtered['Sub Region\n(SA3)'].isin(selected_sa3s)]
if selected_property:
    filtered = filtered[filtered['Property\nType'].isin(selected_property)]

filtered = filtered[(filtered['Investor Score (Out Of 100)'] >= min_score) &
                    (filtered['12m Growth (%)'] >= min_growth) &
                    (filtered['Yield'] >= min_yield)]

# --- TABLE ---
st.subheader("📋 Full Suburb Data")
st.dataframe(filtered, use_container_width=True)

# --- MAP ---
selected_suburb = None
if 'Latitude' in filtered.columns and 'Longitude' in filtered.columns:
    st.subheader("🗺️ 12-Month Growth Map")
    filtered = filtered.dropna(subset=['Latitude', 'Longitude'])
    selected_suburb = st.selectbox("Select a Suburb for Trends", filtered['Suburb'].unique())
    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=filtered['Latitude'].mean(),
            longitude=filtered['Longitude'].mean(),
            zoom=6,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=filtered,
                get_position='[Longitude, Latitude]',
                get_color='[255, 20, 147, 160]',
                get_radius=1000,
                pickable=True,
            )
        ],
        tooltip={"text": "{Suburb}\n12m Growth: {12m Growth (%)}%"},
    ))

# --- GRAPHS ---
if selected_suburb:
    st.subheader(f"📈 Trends for {selected_suburb}")
    suburb_data = df[df['Suburb'] == selected_suburb].sort_index()
    def plot_line(data, col, title):
        if col in data.columns:
            st.write(title)
            fig, ax = plt.subplots()
            ax.plot(data.index, data[col], marker='o', color='hotpink')
            ax.set_ylabel(col)
            st.pyplot(fig)

    plot_line(suburb_data, 'Median Price Growth', 'Median Price Growth Trend')
    plot_line(suburb_data, 'Days on Market', 'Days on Market Trend')
    plot_line(suburb_data, 'Rental Growth', 'Rental Growth Trend')
    plot_line(suburb_data, 'Sales Turnover', 'Sales Turnover Trend')

st.markdown("---")
st.markdown("Built with ❤️ by PropwealthNext")
