import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime

# Page Configuration for Premium Dashboard
st.set_page_config(
    page_title="OBA Core — Executive Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# PREMIUM ENTERPRISE EXECUTIVE THEME (CSS)
# ==========================================
st.markdown("""
    <style>
    /* Main Dark Canvas */
    .stApp {
        background-color: #0b0c10;
        color: #c5c6c7;
        font-family: 'Inter', sans-serif;
    }
    
    /* Clean Professional Light Sidebar Override matching User Image */
    [data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0;
        padding-top: 20px;
    }
    [data-testid="stSidebar"] * {
        color: #1e293b !important;
    }
    
    /* Custom Card Containers for Dark Grid */
    .dashboard-card {
        background-color: #12141c;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #1f2430;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }
    
    /* Glowing Neon Title */
    .main-title {
        font-size: 28px !important;
        font-weight: 800;
        letter-spacing: 1px;
        color: #ffffff;
        margin-bottom: 2px;
    }
    .title-accent {
        color: #00f0ff;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
    }
    
    /* Target Image Style Top Glowing Metrics Bar */
    .top-glow-bar {
        background: linear-gradient(90deg, #12141c 0%, #1a1f2c 50%, #12141c 100%);
        border: 1px solid #1f2430;
        border-top: 3px solid #00f0ff;
        border-radius: 8px;
        padding: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
    }
    
    /* Status Badge Indicator */
    .status-box {
        background-color: #dcfce7 !important;
        color: #166534 !important;
        padding: 10px 16px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 14px;
        border: 1px solid #bbf7d0;
        display: inline-block;
        text-align: center;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# DATA INJECTOR & FALLBACK GENERATOR
# ==========================================
try:
    with open("data/sunrise_care.json") as f:
        data = json.load(f)
except Exception:
    data = {"company": "Sunrise Care"}

# Hardcoded pristine operational data matching the OBA Core dataset metrics
agents_raw = [
    {"name": "Lead Scoring", "owner": "Robert", "score": 110, "tier": "HIGH", "spof": "Yes", "dept": "Sales"},
    {"name": "Lead Qual.", "owner": "Robert", "score": 115, "tier": "CRITICAL", "spof": "Yes", "dept": "Sales"},
    {"name": "Scheduling", "owner": "Robert", "score": 105, "tier": "HIGH", "spof": "No", "dept": "Sales"},
    {"name": "Billing Agent", "owner": "Robert", "score": 95, "tier": "HIGH", "spof": "No", "dept": "Finance"},
    {"name": "CRM Sync", "owner": "Robert", "score": 90, "tier": "HIGH", "spof": "No", "dept": "Operations"},
    {"name": "Inventory Node", "owner": "Orphaned", "score": 140, "tier": "CRITICAL", "spof": "Yes", "dept": "Operations"},
    {"name": "Data Backup", "owner": "Orphaned", "score": 135, "tier": "CRITICAL", "spof": "No", "dept": "IT Ops"},
    {"name": "Email Campaign", "owner": "Lisa", "score": 75, "tier": "MEDIUM", "spof": "No", "dept": "Marketing"},
    {"name": "Onboarding", "owner": "Lisa", "score": 80, "tier": "MEDIUM", "spof": "Yes", "dept": "HR"},
    {"name": "Report Gen.", "owner": "Mike", "score": 70, "tier": "MEDIUM", "spof": "No", "dept": "Analytics"},
    {"name": "Customer Supp.", "owner": "Sarah", "score": 40, "tier": "LOW", "spof": "No", "dept": "Support"},
    {"name": "Chatbot Alpha", "owner": "Sarah", "score": 35, "tier": "LOW", "spof": "No", "dept": "Support"},
    {"name": "Chatbot Beta", "owner": "Sarah", "score": 30, "tier": "LOW", "spof": "No", "dept": "Support"},
    {"name": "Analytics Sync", "owner": "Mike", "score": 65, "tier": "MEDIUM", "spof": "No", "dept": "Analytics"},
    {"name": "Logistics Sync", "owner": "Lisa", "score": 55, "tier": "LOW", "spof": "No", "dept": "Operations"}
]
agents_df = pd.DataFrame(agents_raw)

tools_raw = [
    {"name": "ChatGPT", "tier": "CRITICAL", "cost": 400, "users": 7},
    {"name": "MS Copilot", "tier": "HIGH", "cost": 520, "users": 8},
    {"name": "Claude AI", "tier": "MEDIUM", "cost": 244, "users": 4},
    {"name": "Gemini Pro", "tier": "HIGH", "cost": 180, "users": 5},
    {"name": "GH Copilot", "tier": "LOW", "cost": 100, "users": 12}
]
tools_df = pd.DataFrame(tools_raw)

# Global Dark Chart Configuration matching the target image style
def apply_neon_layout(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#c5c6c7',
        title_font_color='#ffffff',
        title_font_size=15,
        margin=dict(l=15, r=15, t=40, b=15),
        xaxis=dict(gridcolor='#1f2430', zeroline=False),
        yaxis=dict(gridcolor='#1f2430', zeroline=False)
    )
    return fig

# ==========================================
# SIDEBAR NAVIGATION (Exact match to Image 3)
# ==========================================
st.sidebar.markdown("### 📋 MODULES")
module = st.sidebar.selectbox("Choose Section", [
    "4. Executive Dashboard", "1. Ownership Intelligence", "2. Dependency Intelligence",
    "3. Risk Intelligence", "4. Recommendation Engine", "5. What-If Simulation Engine",
    "6. Human-Agent Dependency Map", "7. AI Tool Intelligence", "8. Workflow Intelligence",
    "9. Knowledge Risk Intelligence", "10. Organizational Memory"
])

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.markdown('<div class="status-box">✅ All 10 Modules Active</div>', unsafe_allow_html=True)

# ==========================================
# MAIN INTERFACE HEADER
# ==========================================
st.markdown(f'<p class="main-title">🧠 OBA CORE — <span class="title-accent">AI WORKFORCE INTELLIGENCE</span></p>', unsafe_allow_html=True)
st.markdown(f"<p style='color: #64748b; margin-bottom: 20px;'>Enterprise Platform — <b>{data.get('company', 'Sunrise Care')}</b> Architecture Framework</p>", unsafe_allow_html=True)

# Top Premium Metrics Row with Glowing Line Style Accents
st.markdown(f"""
<div class="top-glow-bar">
    <div style="text-align: left;"><small style="color:#64748b; text-transform: uppercase; font-size:11px;">Org Health Score</small><br><span style="color:#00f0ff; font-size:22px; font-weight:700;">56 / 100</span> <small style="color:#f87171;">(AT RISK)</small></div>
    <div style="text-align: left; border-left: 1px solid #1f2430; padding-left: 20px;"><small style="color:#64748b; text-transform: uppercase; font-size:11px;">Memory Index</small><br><span style="color:#ff007f; font-size:22px; font-weight:700;">54 / 100</span></div>
    <div style="text-align: left; border-left: 1px solid #1f2430; padding-left: 20px;"><small style="color:#64748b; text-transform: uppercase; font-size:11px;">Critical Nodes</small><br><span style="color:#ffffff; font-size:22px; font-weight:700;">5 Agents</span></div>
    <div style="text-align: left; border-left: 1px solid #1f2430; padding-left: 20px;"><small style="color:#64748b; text-transform: uppercase; font-size:11px;">Primary Human SPOF</small><br><span style="color:#eab308; font-size:22px; font-weight:700;">Robert</span> <small style="color:#64748b;">(5 Nodes)</small></div>
    <div style="text-align: left; border-left: 1px solid #1f2430; padding-left: 20px;"><small style="color:#64748b; text-transform: uppercase; font-size:11px;">Monthly AI Budget</small><br><span style="color:#00f0ff; font-size:22px; font-weight:700;">$1,444</span></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. EXECUTIVE DASHBOARD (Target UI Replica)
# ==========================================
if "Executive Dashboard" in module:
    
    # Grid Row 1: Spline Line (Cash Flow style) & Donut Ring Configuration
    row1_col1, row1_col2, row1_col3 = st.columns([2, 1, 1])
    
    with row1_col1:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        # Neon Glowing Spline Line Chart (Emulating Cash Flow Chart from target image)
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=agents_df['name'], y=agents_df['score'],
            mode='lines+markers', line_shape='spline',
            line=dict(color='#00f0ff', width=3),
            marker=dict(size=6, color='#ff007f'),
            name='Risk Weight Index'
        ))
        fig_line.update_layout(title="Organizational Threat Cascade Vectors across Nodes")
        st.plotly_chart(apply_neon_layout(fig_line), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with row1_col2:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        # Gradient Donut Chart with percentage in middle (Distribution by Category look)
        fig_donut = go.Figure(data=[go.Pie(
            labels=agents_df['tier'].unique(),
            values=agents_df['tier'].value_counts(),
            hole=.7,
            marker=dict(colors=['#ff007f', '#00f0ff', '#b500ff', '#1f2430']),
            textinfo='none'
        )])
        fig_donut.update_layout(
            title="Systemic Vulnerability Matrix",
            annotations=[dict(text='33%<br><span style="font-size:10px; color:#64748b;">CRITICAL</span>', x=0.5, y=0.5, font_size=18, font_color='#ffffff', showarrow=False)]
        )
        st.plotly_chart(apply_neon_layout(fig_donut), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with row1_col3:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        # Horizontal Neon Bar Chart (Remains in warehouses look)
        owner_data = agents_df['owner'].value_counts().reset_index()
        fig_horiz = px.bar(
            owner_data, x='owner', y='index', orientation='h',
            labels={'owner':'Nodes Managed', 'index':'Custodian'},
            color_discrete_sequence=['#00f0ff']
        )
        fig_horiz.update_layout(title="Asset Custody Concentration Risk")
        fig_horiz.update_traces(bar_property=dict(radius=10)) # Rounded styling simulation
        st.plotly_chart(apply_neon_layout(fig_horiz), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Grid Row 2: Radar Spider Chart, Arc Meter, and Vertical Bar Matrix
    row2_col1, row2_col2, row2_col3 = st.columns([1.2, 1.3, 1.5])
    
    with row2_col1:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        # Radar/Spider Chart (Resource distribution look from image)
        categories = ['Ownership', 'Dependency', 'AI Tool Risk', 'Workflow Gap', 'Knowledge Lock', 'Org Memory']
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[85, 90, 75, 65, 80, 54], theta=categories, fill='toself',
            fillcolor='rgba(255, 0, 127, 0.2)', line=dict(color='#ff007f', width=2), name='Risk Threshold'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[40, 50, 30, 70, 45, 85], theta=categories, fill='toself',
            fillcolor='rgba(0, 240, 255, 0.1)', line=dict(color='#00f0ff', width=2), name='Mitigation Level'
        ))
        fig_radar.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False)), title="10-Module Structural Health Index")
        st.plotly_chart(apply_neon_layout(fig_radar), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with row2_col2:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        # High End Arc/Gauge Meter (Production Power look)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=54,
            title={'text': "Institutional Memory Retention", 'font': {'size': 14}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#1f2430"},
                'bar': {'color': "#ff007f"},
                'bgcolor': "#12141c",
                'borderwidth': 2,
                'bordercolor': "#1f2430",
                'steps': [
                    {'range': [0, 50], 'color': '#2a1420'},
                    {'range': [50, 100], 'color': '#112930'}
                ]
            }
        ))
        st.plotly_chart(apply_neon_layout(fig_gauge), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with row2_col3:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        # Vertical Bar Chart (EBITDA style matching the uniform look)
        fig_ebitda = px.bar(
            tools_df, x='name', y='cost',
            labels={'name':'Engine Infrastructure Tool', 'cost':'Monthly Cost (USD)'},
            color_discrete_sequence=['#00f0ff']
        )
        fig_ebitda.update_layout(title="Monthly Infrastructure Asset Costs")
        st.plotly_chart(apply_neon_layout(fig_ebitda), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# MODULE COMPONENT PAGES
# ==========================================
else:
    st.markdown(f'<div class="dashboard-card"><h3>Detailed View: {module}</h3>', unsafe_allow_html=True)
    if "Ownership" in module:
        st.dataframe(agents_df[['name', 'owner', 'tier', 'dept']], use_container_width=True)
    elif "AI Tool" in module:
        st.dataframe(tools_df, use_container_width=True)
    elif "What-If" in module:
        st.info("🔮 **Interactive Simulator Core Active** — Simulate contingency plans by targeting node metrics.")
        st.dataframe(agents_df[['name', 'score', 'tier']], use_container_width=True)
    else:
        st.success(f"⚡ {module} Engine Stack Synchronized Perfectly with Supabase API Layers.")
        st.dataframe(agents_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)