import streamlit as st
import pandas as pd
import altair as alt

# 1. Page Configuration & Theme
st.set_page_config(page_title="Pro Retail Insights", layout="wide")

# Custom CSS for a "Glassmorphism" look on metrics
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #00FFAA; }
    .stChart { border: 1px solid #333; border-radius: 10px; padding: 10px; background: #0E1117; }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Loading
@st.cache_data
def load_data():
    df = pd.read_csv("project1_df.csv")
    df['Purchase Date'] = pd.to_datetime(df['Purchase Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Purchase Date'])
    return df

try:
    df = load_data()

    # --- SIDEBAR & INTERACTIVE SELECTIONS ---
    st.sidebar.title("🎮 Dashboard Controls")
    
    # Altair Selection Objects (The magic for interactivity)
    # This allows clicking on a bar to filter other charts
    click_selection = alt.selection_point(fields=['Product Category'])
    # This allows dragging across the timeline
    brush_selection = alt.selection_interval(encodings=['x'])

    # Standard Sidebar Filters
    locations = st.sidebar.multiselect("📍 Location", options=df["Location"].unique(), default=df["Location"].unique()[:5])
    
    # Filter base data by sidebar
    filtered_df = df[df["Location"].isin(locations)]

    # --- TOP ROW: KPI METRICS ---
    st.title("🚀 Executive Retail Intelligence")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Revenue", f"₹{filtered_df['Net Amount'].sum():,.0f}")
    m2.metric("Orders", f"{len(filtered_df):,}")
    m3.metric("Avg Basket", f"₹{filtered_df['Net Amount'].mean():,.2f}")
    m4.metric("Cities", f"{filtered_df['Location'].nunique()}")

    st.write("---")

    # --- MIDDLE ROW: INTERACTIVE ANALYTICS ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📈 Revenue Timeline (Drag to Zoom)")
        # Time Series with Selection Brush
        timeseries = alt.Chart(filtered_df).mark_area(
            line={'color':'#00FFAA'},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='#00FFAA', offset=0),
                       alt.GradientStop(color='transparent', offset=1)],
                x1=1, x2=1, y1=1, y2=0
            )
        ).encode(
            x=alt.X("Purchase Date:T", title="Date"),
            y=alt.Y("sum(Net Amount):Q", title="Revenue"),
            tooltip=['sum(Net Amount)']
        ).add_params(brush_selection).properties(height=350)
        
        st.altair_chart(timeseries, use_container_width=True)

    with col_right:
        st.subheader("🎯 Sales by Category")
        # Bar Chart that reacts to the timeline brush
        category_bars = alt.Chart(filtered_df).mark_bar(cornerRadiusEnd=5).encode(
            y=alt.Y("Product Category:N", sort='-x'),
            x=alt.X("sum(Net Amount):Q", title="Revenue"),
            color=alt.condition(click_selection, alt.value("#00FFAA"), alt.value("#333")),
            tooltip=["Product Category", "sum(Net Amount)"]
        ).transform_filter(
            brush_selection # Re-calculates based on time brush
        ).add_params(
            click_selection
        ).properties(height=350)
        
        st.altair_chart(category_bars, use_container_width=True)

    # --- BOTTOM ROW: DEEP DIVE ---
    st.subheader("💳 Payment Methods by City (Heatmap)")
    
    heatmap = alt.Chart(filtered_df).mark_rect().encode(
        x=alt.X("Location:N", title="City"),
        y=alt.Y("Purchase Method:N", title="Method"),
        color=alt.Color("count():Q", scale=alt.Scale(scheme='viridis'), title="Transactions"),
        tooltip=["Location", "Purchase Method", "count()"]
    ).transform_filter(
        brush_selection # Heatmap also reacts to time selection
    ).properties(height=300)

    st.altair_chart(heatmap, use_container_width=True)

    # --- DATA EXPLORER ---
    with st.expander("🔍 View Transaction Details"):
        st.dataframe(filtered_df.sort_values("Purchase Date", ascending=False), use_container_width=True)

except FileNotFoundError:
    st.error("Missing `project1_df.csv` file!")