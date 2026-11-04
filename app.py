import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import os
import csv
import json
from datetime import datetime

# Page Configuration - Left Side Panel Open
st.set_page_config(
    page_title="GCDC HSE Performance Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enterprise Modern CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 22px 28px;
        border-radius: 14px;
        margin-bottom: 22px;
        color: white;
        border: 1px solid #334155;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }
    
    .main-header h1 {
        font-size: 24px;
        font-weight: 700;
        margin: 0 0 4px 0;
        color: #f8fafc;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .main-header p {
        margin: 0;
        color: #94a3b8;
        font-size: 13px;
    }

    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .kpi-title {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 6px;
    }
    
    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 4px;
    }
    
    .kpi-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
        width: fit-content;
    }
    
    .badge-success { background: #dcfce7; color: #15803d; }
    .badge-info { background: #e0f2fe; color: #0369a1; }
    .badge-warning { background: #fef3c7; color: #b45309; }
    .badge-danger { background: #fee2e2; color: #b91c1c; }
    
    .metric-sub {
        font-size: 11px;
        color: #64748b;
        margin-top: 4px;
    }
    
    .section-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 22px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    
    .section-title {
        font-size: 16px;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Executive Compliance Card matching Excel B28 (=DATA!D16) */
    .compliance-box {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #0f172a;
        box-shadow: 0 4px 14px rgba(0,0,0,0.12);
        max-width: 380px;
        margin: 0 auto 16px auto;
    }
    
    .compliance-header {
        background: #8fa0b5;
        color: #0f2438;
        font-size: 18px;
        font-weight: 700;
        text-align: center;
        padding: 10px 14px;
        letter-spacing: 0.02em;
    }
    
    .compliance-value-block {
        background: #0d1e30;
        color: #ffffff;
        font-size: 52px;
        font-weight: 800;
        text-align: center;
        padding: 16px 12px 6px 12px;
        line-height: 1;
    }
    
    .compliance-subtext {
        background: #0d1e30;
        color: #94a3b8;
        font-size: 12px;
        text-align: center;
        padding-bottom: 14px;
        font-weight: 500;
    }

    .yellow-note-box {
        background: #fef08a;
        color: #713f12;
        border: 1px solid #fde047;
        border-radius: 10px;
        padding: 14px 16px;
        font-size: 13px;
        line-height: 1.5;
        font-weight: 600;
        margin-top: 20px;
    }

    /* Excel Styled Table Box */
    .excel-table-box {
        border: 1px solid #0f2438;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }

    .excel-table-header {
        background: #0d233a;
        color: white;
        text-align: center;
        font-weight: 800;
        font-size: 15px;
        padding: 10px 14px;
        letter-spacing: 0.02em;
    }

    .excel-table-row {
        display: flex;
        border-bottom: 1px solid #cbd5e1;
    }

    .excel-table-row:last-child {
        border-bottom: none;
    }

    .excel-col-label {
        flex: 1.1;
        background: #94a3b8;
        color: #0f2438;
        font-weight: 700;
        font-size: 13px;
        padding: 8px 14px;
        display: flex;
        align-items: center;
        border-right: 1px solid #cbd5e1;
    }

    .excel-col-value {
        flex: 1;
        background: #ffffff;
        color: #0f172a;
        font-weight: 700;
        font-size: 15px;
        padding: 8px 14px;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .excel-total-label {
        background: #94a3b8;
        color: #0f2438;
        font-weight: 800;
        font-size: 14px;
    }

    .excel-total-value {
        background: #f8fafc;
        color: #0f172a;
        font-weight: 800;
        font-size: 16px;
    }

    /* Sidebar Navigation Button Styles */
    .stSidebar [data-testid="stButton"] button {
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
        padding: 10px 14px;
        text-align: left;
        justify-content: flex-start;
        transition: all 0.2s ease;
        border: 1px solid #e2e8f0;
    }
    .stSidebar [data-testid="stButton"] button:hover {
        border-color: #38bdf8;
        color: #0284c7;
        background: #f0f9ff;
    }
</style>
""", unsafe_allow_html=True)

# Data Loader
CSV_PATH = os.path.join(os.path.dirname(__file__), "single_sheet_data.csv")
if not os.path.exists(CSV_PATH):
    CSV_PATH = "single_sheet_data.csv"


def load_data():
    if not os.path.exists(CSV_PATH):
        st.error(f"Data file not found at: {CSV_PATH}")
        st.stop()
        
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    def get_c(r: int, c: int, default: str = "") -> str:
        try:
            val = rows[r][c].strip()
            return val if val != "" else default
        except IndexError:
            return default

    def get_f(r: int, c: int, default: float = 0.0) -> float:
        v = get_c(r, c, "")
        try:
            return float(v)
        except ValueError:
            return default

    def get_i(r: int, c: int, default: int = 0) -> int:
        return int(round(get_f(r, c, default)))

    OFFSET = 33

    # Row 28 Top KPIs
    closure_rate = get_f(27, 1)
    total_incidents = get_i(27, 5)
    safe_man_hours = get_f(27, 9)
    training_rate = get_f(27, 13)
    ltifr = get_f(27, 17)
    trir = get_f(27, 21)
    ltifr_rating = get_c(32, 17, "Excellent")
    trir_rating = get_c(32, 21, "Good")

    # Incidents
    incidents = {
        "NM": get_i(5 + OFFSET, 6),
        "MTC": get_i(6 + OFFSET, 6),
        "MVA": get_i(7 + OFFSET, 6),
        "FAC": get_i(8 + OFFSET, 6),
        "PD": get_i(9 + OFFSET, 6),
        "FAT": get_i(10 + OFFSET, 6),
        "RWC": get_i(11 + OFFSET, 6),
        "LTI": get_i(12 + OFFSET, 6),
        "Total": total_incidents if total_incidents > 0 else 102
    }

    # Man-hours & Manpower
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_hours = {}
    for i, m in enumerate(months):
        r = 5 + i + OFFSET
        val = get_c(r, 10)
        if val != "":
            monthly_hours[m] = float(val)

    monthly_manpower = {}
    for i, m in enumerate(months):
        r = 22 + i + OFFSET
        val = get_c(r, 10)
        if val != "":
            monthly_manpower[m] = float(val)

    # Compliance
    obs_open = get_i(6 + OFFSET, 2)
    obs_close = get_i(7 + OFFSET, 2)
    obs_total = get_i(8 + OFFSET, 2)
    obs_rate = get_f(6 + OFFSET, 3)

    ncr_open = get_i(9 + OFFSET, 2)
    ncr_close = get_i(10 + OFFSET, 2)
    ncr_total = get_i(11 + OFFSET, 2)
    ncr_rate = get_f(9 + OFFSET, 3)

    audit_open = get_i(12 + OFFSET, 2)
    audit_close = get_i(13 + OFFSET, 2)
    audit_total = get_i(14 + OFFSET, 2)
    audit_rate = get_f(12 + OFFSET, 3)

    grand_open = get_i(15 + OFFSET, 2)
    grand_close = get_i(16 + OFFSET, 2)
    grand_total = get_i(17 + OFFSET, 2)
    grand_rate = closure_rate if closure_rate > 0 else 0.9923

    # Activities & Staffing
    act = {
        "tbt": get_i(15 + OFFSET, 19, 114),
        "inspections": get_i(16 + OFFSET, 19, 6),
        "campaigns": get_i(17 + OFFSET, 19, 1),
        "total": get_i(18 + OFFSET, 19, 121)
    }

    staffing = {
        "actual": get_f(21 + OFFSET, 19, 22.0),
        "required": get_f(22 + OFFSET, 19, 24.89),
        "gap": get_f(23 + OFFSET, 19, 2.89),
        "compliance_rate": get_f(24 + OFFSET, 19, 0.8839)
    }

    # Monthly KPI Scores
    month_names_full = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October"]
    kpi_monthly = []
    for i, mname in enumerate(month_names_full):
        r = 23 + i + OFFSET
        s = get_c(r, 1)
        b = get_f(r, 2, 0.90)
        if s != "":
            try:
                kpi_monthly.append({"month": mname, "short": months[i], "score": float(s), "baseline": b})
            except ValueError:
                pass
    kpi_avg = get_f(33 + OFFSET, 1, 0.83)

    # Monthly PSI/PCI
    psi_monthly = []
    for i, mname in enumerate(month_names_full):
        r = 39 + i + OFFSET
        s = get_c(r, 1)
        b = get_f(r, 2, 0.90)
        if s != "":
            try:
                psi_monthly.append({"month": mname, "short": months[i], "score": float(s), "baseline": b})
            except ValueError:
                pass
    psi_avg = get_f(39 + OFFSET, 14, 0.761)

    # Weekly Welfare
    welfare_weeks = []
    for r in range(2 + OFFSET, 53 + OFFSET):
        wk = get_c(r, 21)
        score = get_c(r, 22)
        target = get_f(r, 23, 0.90)
        if wk != "" and score != "":
            try:
                welfare_weeks.append({"week": wk, "score": float(score), "target": target})
            except ValueError:
                pass
    welfare_avg = get_f(54 + OFFSET, 21, 0.66)

    return {
        "incidents": incidents,
        "safe_man_hours": {
            "prior": get_f(19 + OFFSET, 8, 2916176.0),
            "monthly": monthly_hours,
            "total": safe_man_hours
        },
        "manpower": {
            "monthly": monthly_manpower,
            "average": get_f(34 + OFFSET, 10, 1244.4)
        },
        "rates": {
            "ltifr": ltifr,
            "trir": trir,
            "ltifr_rating": ltifr_rating,
            "trir_rating": trir_rating
        },
        "compliance": {
            "obs": {"open": obs_open, "closed": obs_close, "total": obs_total, "rate": obs_rate},
            "ncr": {"open": ncr_open, "closed": ncr_close, "total": ncr_total, "rate": ncr_rate},
            "audits": {"open": audit_open, "closed": audit_close, "total": audit_total, "rate": audit_rate},
            "grand": {"open": grand_open, "closed": grand_close, "total": grand_total, "rate": grand_rate}
        },
        "staffing": staffing,
        "activities": act,
        "training": {
            "rate": training_rate,
            "trainings": get_i(17 + OFFSET, 14, 5),
            "attendees": get_i(17 + OFFSET, 15, 62),
            "target": get_i(17 + OFFSET, 16, 17)
        },
        "kpi_monthly": kpi_monthly,
        "kpi_avg": kpi_avg,
        "psi_monthly": psi_monthly,
        "psi_avg": psi_avg,
        "welfare": {
            "weekly": welfare_weeks,
            "average": welfare_avg
        }
    }

data = load_data()

# Helper gauge function
def create_gauge(value: float, title: str, max_val: float, thresholds: list, target_text: str = ""):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': f"<b>{title}</b><br><span style='font-size:12px;color:#64748b'>{target_text}</span>", 'font': {'size': 15, 'color': '#0f172a'}},
        number={'font': {'size': 30, 'family': 'Inter, sans-serif', 'color': '#0f172a'}, 'valueformat': '.3f' if value < 1 else '.2f'},
        gauge={
            'axis': {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': '#94a3b8'},
            'bar': {'color': '#0284c7', 'thickness': 0.28},
            'bgcolor': 'white',
            'borderwidth': 1,
            'bordercolor': '#cbd5e1',
            'steps': thresholds
        }
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=15, r=15, t=45, b=15),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig

def make_speedometer(title, slice_vals, slice_colors, needle_frac):
    """Create a semicircular speedometer gauge with needle matching Excel Image 2."""
    total_top = sum(slice_vals)
    pie_vals = list(slice_vals) + [total_top]
    pie_colors = list(slice_colors) + ['rgba(0,0,0,0)']
    
    theta = np.pi * (1.0 - needle_frac)
    
    # Needle line from center (0.5, 0.5) to arc inner edge
    x_head = 0.5 + 0.38 * np.cos(theta)
    y_head = 0.5 + 0.38 * np.sin(theta)
    
    # Outer black band marker on arc (matching Excel needle style)
    x_band_in = 0.5 + 0.32 * np.cos(theta)
    y_band_in = 0.5 + 0.32 * np.sin(theta)
    x_band_out = 0.5 + 0.47 * np.cos(theta)
    y_band_out = 0.5 + 0.47 * np.sin(theta)
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        values=pie_vals,
        rotation=-90,
        direction='clockwise',
        sort=False,
        hole=0.68,
        marker=dict(colors=pie_colors, line=dict(color='white', width=2)),
        textinfo='none',
        hoverinfo='none',
        showlegend=False
    ))
    
    # Needle line
    fig.add_shape(type='line', x0=0.5, y0=0.5, x1=x_head, y1=y_head, line=dict(color='#000000', width=2.5))
    # Black band marker on arc
    fig.add_shape(type='line', x0=x_band_in, y0=y_band_in, x1=x_band_out, y1=y_band_out, line=dict(color='#000000', width=7))
    
    fig.update_layout(
        title=dict(text=f'<b>{title}</b>', font=dict(size=24, color='#0d2640', family='Segoe UI, Inter, sans-serif'), x=0.5, xanchor='center'),
        height=260,
        margin=dict(l=15, r=15, t=55, b=10),
        xaxis=dict(range=[0, 1], visible=False),
        yaxis=dict(range=[0.38, 1.08], visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def render_html(html_str: str):
    """Strip all leading/trailing whitespace per line to prevent markdown code block triggers."""
    clean = "".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(clean, unsafe_allow_html=True)

# Initialize Active Page in Session State
if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

def set_page(page_name):
    st.session_state.active_page = page_name

# =========================================================================
# 🧭 LEFT SIDE PANEL: NAVIGATION BUTTONS
# =========================================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=52)
    st.markdown("### GCDC HSE Hub")
    st.caption("Kharafi National / SBARC")
    st.markdown("---")
    st.markdown("<p style='font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase;'>📌 Navigation Pages</p>", unsafe_allow_html=True)

    # Clean Navigation Buttons on Left Panel
    pages = [
        ("🏠 Main Home (Summary)", "Home"),
        ("📋 Compliance Rate %", "Compliance"),
        ("🔍 Site Observations", "Observations"),
        ("📑 NCRs Performance", "NCRs"),
        ("🛠️ HSE Activities", "Activities"),
        ("⚠️ Total Incidents Analysis", "Incidents"),
        ("⏱️ Safe Man-Hours & Workforce", "Workforce"),
        ("📈 Monthly KPI & Scores", "KPIs"),
        ("🎓 HSE Training Rate", "Training"),
        ("🎯 Safety Rates (LTIFR / TRIR)", "Rates"),
        ("🤝 Welfare & Proactive Safety", "Welfare")
    ]

    for label, key in pages:
        is_active = (st.session_state.active_page == key)
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
            set_page(key)
            st.rerun()

    st.markdown("---")
    st.markdown(f"**Current Page:** `{st.session_state.active_page}`")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

    # Dedicated Site Observations Section in Left Side Panel (Matching User's New Excel Images)
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #002060; color: #ffffff; padding: 7px 10px; border-radius: 4px; font-weight: 800; font-size: 13.5px; text-align: center; margin-bottom: 12px; letter-spacing: 0.5px; border: 1.5px solid #001030;">
        🔍 SITE OBSERVATION (EXCEL)
    </div>
    """, unsafe_allow_html=True)

    # Table 1: Status Counts (Exact Image 2)
    obs_tbl_1 = """
    <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; font-size: 12.5px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
        <thead>
            <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #000000;">
                <th colspan="2" style="padding: 6px; text-align: center; font-size: 13.5px; font-weight: 800; letter-spacing: 0.5px;">Site Observation</th>
            </tr>
        </thead>
        <tbody>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000; width: 62%;">Open</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center; width: 38%;">8</td>
            </tr>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Closed</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">1242</td>
            </tr>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Overdue</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">8</td>
            </tr>
            <tr>
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 1.5px solid #000000;">Total</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">1250</td>
            </tr>
        </tbody>
    </table>
    """
    render_html(obs_tbl_1)

    # Table 2: Rates & Performance (Exact Image 1)
    obs_tbl_2 = """
    <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; font-size: 12.5px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
        <thead>
            <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #000000;">
                <th colspan="2" style="padding: 6px; text-align: center; font-size: 13.5px; font-weight: 800; letter-spacing: 0.5px;">Site Observation</th>
            </tr>
        </thead>
        <tbody>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000; width: 62%;">Closure Rate</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center; width: 38%;">99%</td>
            </tr>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">OD Rate</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">1.4%</td>
            </tr>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">OTC Rate</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">2%</td>
            </tr>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 1.5px solid #000000;">Total OD</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">17</td>
            </tr>
            <tr>
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Closed On-time</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">25</td>
            </tr>
        </tbody>
    </table>
    """
    render_html(obs_tbl_2)

    # Bar Chart (Exact Image 3)
    fig_obs_sb = go.Figure()
    fig_obs_sb.add_trace(go.Bar(
        x=['Open', 'Closed', 'Overdue'],
        y=[8, 1242, 8],
        text=['8', '1242', '8'],
        textposition='outside',
        textfont=dict(size=12, color='#0d2640', weight='bold'),
        marker=dict(
            color='#0e5374',
            line=dict(color='#09384f', width=1.5)
        ),
        width=0.45
    ))
    fig_obs_sb.update_layout(
        title=dict(text='<b>Site Observations</b>', font=dict(size=18, color='#0d2640', family='Segoe UI, Inter, sans-serif'), x=0.5, xanchor='center'),
        yaxis=dict(
            range=[0, 1500],
            tickvals=[0, 200, 400, 600, 800, 1000, 1200, 1400],
            gridcolor='#e2e8f0',
            zerolinecolor='#cbd5e1'
        ),
        xaxis=dict(
            tickfont=dict(size=11, color='#0d2640', weight='bold')
        ),
        height=240,
        margin=dict(l=35, r=15, t=35, b=25),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_obs_sb, use_container_width=True)

    # Dedicated NCRs Section in Left Side Panel (Matching User's Excel Images)
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #002060; color: #ffffff; padding: 7px 10px; border-radius: 4px; font-weight: 800; font-size: 13.5px; text-align: center; margin-bottom: 12px; letter-spacing: 0.5px; border: 1.5px solid #001030;">
        📑 NCRs SECTION (EXCEL)
    </div>
    """, unsafe_allow_html=True)

    # Table 1: Status Counts (Exact Image 1)
    ncr_tbl_1 = """
    <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; font-size: 12.5px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
        <thead>
            <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #000000;">
                <th colspan="2" style="padding: 6px; text-align: center; font-size: 13.5px; font-weight: 800; letter-spacing: 0.5px;">NCRs</th>
            </tr>
        </thead>
        <tbody>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000; width: 62%;">Open</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center; width: 38%;">2</td>
            </tr>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Closed</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">52</td>
            </tr>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Overdue</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">2</td>
            </tr>
            <tr>
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 1.5px solid #000000;">Total</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">54</td>
            </tr>
        </tbody>
    </table>
    """
    render_html(ncr_tbl_1)

    # Table 2: Rates & Performance (Exact Image 2)
    ncr_tbl_2 = """
    <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; font-size: 12.5px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
        <thead>
            <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #000000;">
                <th colspan="2" style="padding: 6px; text-align: center; font-size: 13.5px; font-weight: 800; letter-spacing: 0.5px;">NCRs</th>
            </tr>
        </thead>
        <tbody>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000; width: 62%;">Closure Rate</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center; width: 38%;">96%</td>
            </tr>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">OD Rate</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">4%</td>
            </tr>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">OTC Rate</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">0%</td>
            </tr>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 1.5px solid #000000;">Total OD</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">2</td>
            </tr>
            <tr>
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Closed On-time</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">0</td>
            </tr>
        </tbody>
    </table>
    """
    render_html(ncr_tbl_2)

    # Bar Chart (Exact Image 3)
    fig_ncr_sb = go.Figure()
    fig_ncr_sb.add_trace(go.Bar(
        x=['Open', 'Closed', 'Overdue'],
        y=[2, 52, 2],
        text=['2', '52', '2'],
        textposition='outside',
        textfont=dict(size=12, color='#0d2640', weight='bold'),
        marker=dict(
            color='#0e5374',
            line=dict(color='#09384f', width=1.5)
        ),
        width=0.45
    ))
    fig_ncr_sb.update_layout(
        title=dict(text='<b>NCRs</b>', font=dict(size=18, color='#0d2640', family='Segoe UI, Inter, sans-serif'), x=0.5, xanchor='center'),
        yaxis=dict(
            title=dict(text='Num. of NCRs', font=dict(size=11, color='#0d2640')),
            range=[0, 65],
            tickvals=[0, 10, 20, 30, 40, 50, 60],
            gridcolor='#e2e8f0',
            zerolinecolor='#cbd5e1'
        ),
        xaxis=dict(
            tickfont=dict(size=11, color='#0d2640', weight='bold')
        ),
        height=240,
        margin=dict(l=35, r=15, t=35, b=25),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_ncr_sb, use_container_width=True)

    # Dedicated HSE Activities Section in Left Side Panel (Matching User's New Excel Images)
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #002060; color: #ffffff; padding: 7px 10px; border-radius: 4px; font-weight: 800; font-size: 13.5px; text-align: center; margin-bottom: 12px; letter-spacing: 0.5px; border: 1.5px solid #001030;">
        🛠️ HSE ACTIVITIES (EXCEL)
    </div>
    """, unsafe_allow_html=True)

    # Table: HSE Activities (Exact Image 1)
    act_tbl_html = """
    <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; font-size: 12.5px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
        <thead>
            <tr style="background-color: #002060; color: #ffffff; border-bottom: 1px solid #ffffff;">
                <th colspan="2" style="padding: 6px; text-align: center; font-size: 13.5px; font-weight: 800; letter-spacing: 0.5px;">HSE Activities</th>
            </tr>
            <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #000000;">
                <th style="padding: 5px 8px; text-align: center; font-size: 12px; font-weight: 700; border-right: 1.5px solid #ffffff; width: 60%;">Activity</th>
                <th style="padding: 5px 8px; text-align: center; font-size: 12px; font-weight: 700; width: 40%;">Quantity</th>
            </tr>
        </thead>
        <tbody>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">TBT</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">114</td>
            </tr>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">inspections</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">6</td>
            </tr>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Campaigns</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">1</td>
            </tr>
            <tr>
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 1.5px solid #000000;">Total</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">121</td>
            </tr>
        </tbody>
    </table>
    """
    render_html(act_tbl_html)

    # Bar Chart: HSE Activities (Exact Image 2)
    fig_act_sb = go.Figure()
    fig_act_sb.add_trace(go.Bar(
        x=['TBT', 'inspections', 'Campaigns'],
        y=[114, 6, 1],
        text=['114', '6', '1'],
        textposition='outside',
        textfont=dict(size=12, color='#0d2640', weight='bold'),
        marker=dict(
            color='#0e5374',
            line=dict(color='#09384f', width=1.5)
        ),
        width=0.45
    ))
    fig_act_sb.update_layout(
        title=dict(text='<b>HSE Activities</b>', font=dict(size=18, color='#0d2640', family='Segoe UI, Inter, sans-serif'), x=0.5, xanchor='center'),
        yaxis=dict(
            range=[0, 130],
            tickvals=[0, 20, 40, 60, 80, 100, 120],
            gridcolor='#e2e8f0',
            zerolinecolor='#cbd5e1'
        ),
        xaxis=dict(
            tickfont=dict(size=11, color='#0d2640', weight='bold')
        ),
        height=240,
        margin=dict(l=35, r=15, t=35, b=25),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_act_sb, use_container_width=True)

    # Dedicated HSE Staffing Compliance Section in Left Side Panel (Matching User's Excel Image)
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #002060; color: #ffffff; padding: 7px 10px; border-radius: 4px; font-weight: 800; font-size: 13px; text-align: center; margin-bottom: 12px; letter-spacing: 0.5px; border: 1.5px solid #001030;">
        👥 HSE STAFFING COMPLIANCE
    </div>
    """, unsafe_allow_html=True)

    staff_sidebar_tbl = """
    <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; font-size: 12.5px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
        <thead>
            <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #000000;">
                <th colspan="2" style="padding: 6px; text-align: center; font-size: 13px; font-weight: 800; letter-spacing: 0.5px;">HSE Staffing Compliance</th>
            </tr>
        </thead>
        <tbody>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000; width: 62%;">Actual</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center; width: 38%;">22</td>
            </tr>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Required</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">25</td>
            </tr>
            <tr style="border-bottom: 1px solid #000000;">
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Gap</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #dc2626; font-weight: 800; text-align: center;">3</td>
            </tr>
            <tr>
                <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 1.5px solid #000000;">Compliance</td>
                <td style="padding: 5px 8px; background-color: #ffffff; color: #15803d; font-weight: 800; text-align: center;">88%</td>
            </tr>
        </tbody>
    </table>
    """
    render_html(staff_sidebar_tbl)

# Top Executive Banner (Always present)
st.markdown("""
<div class="main-header">
    <div>
        <h1>🛡️ GCDC HSE Performance Executive Dashboard</h1>
        <p>Comprehensive Safety, Health & Environmental Metrics • Single Consolidated Sheet View</p>
    </div>
    <div style="text-align: right;">
        <span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 600; border: 1px solid rgba(56, 189, 248, 0.3);">
            Live Sheet Active
        </span>
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================================
# ⚠️ PAGE: DEDICATED TOTAL INCIDENTS (MATCHING USER'S NEW IMAGES)
# =========================================================================
if st.session_state.active_page == "Incidents":
    st.markdown("## ⚠️ Total Incidents Breakdown & Severity Analysis")
    st.caption("Complete breakdown matching the project incident registry and classification register")

    # Top KPI summary row for incidents
    ik1, ik2, ik3, ik4, ik5 = st.columns(5)
    with ik1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Incidents</div>
            <div class="kpi-value">{data['incidents']['Total']}</div>
            <span class="kpi-badge badge-info">YTD 2026 Log</span>
            <div class="metric-sub">All Classifications</div>
        </div>
        """, unsafe_allow_html=True)
    with ik2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Near Misses (NM)</div>
            <div class="kpi-value">{data['incidents']['NM']}</div>
            <span class="kpi-badge badge-success">81.4% of Total</span>
            <div class="metric-sub">Proactive Reporting</div>
        </div>
        """, unsafe_allow_html=True)
    with ik3:
        mtc_mva = data['incidents']['MTC'] + data['incidents']['MVA']
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">MTC + MVA Cases</div>
            <div class="kpi-value">{mtc_mva}</div>
            <span class="kpi-badge badge-warning">8 MTC • 5 MVA</span>
            <div class="metric-sub">Managed & Investigated</div>
        </div>
        """, unsafe_allow_html=True)
    with ik4:
        fac_pd = data['incidents']['FAC'] + data['incidents']['PD']
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">FAC + PD Cases</div>
            <div class="kpi-value">{fac_pd}</div>
            <span class="kpi-badge badge-info">2 FAC • 4 PD</span>
            <div class="metric-sub">Treated & Rectified</div>
        </div>
        """, unsafe_allow_html=True)
    with ik5:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">LTI / FAT / RWC</div>
            <div class="kpi-value" style="color:#15803d;">0</div>
            <span class="kpi-badge badge-success">Zero Incidents</span>
            <div class="metric-sub">World-Class Milestone</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # MAIN ROW: EXACT TABLE (IMAGE 1) & EXACT BAR CHART (IMAGE 2)
    col_t, col_c = st.columns([1, 1.6])

    with col_t:
        st.markdown('<div class="section-title">📋 Total Incidents Registry (Excel Format)</div>', unsafe_allow_html=True)

        inc = data['incidents']
        
        # HTML Rendering of the Exact Excel Table (Image 1)
        inc_table_html = f"""
        <div class="excel-table-box">
            <div class="excel-table-header">Total Incidents</div>
            <div class="excel-table-row">
                <div class="excel-col-label">NM</div>
                <div class="excel-col-value">{inc['NM']}</div>
            </div>
            <div class="excel-table-row">
                <div class="excel-col-label">MTC</div>
                <div class="excel-col-value">{inc['MTC']}</div>
            </div>
            <div class="excel-table-row">
                <div class="excel-col-label">MVA</div>
                <div class="excel-col-value">{inc['MVA']}</div>
            </div>
            <div class="excel-table-row">
                <div class="excel-col-label">FAC</div>
                <div class="excel-col-value">{inc['FAC']}</div>
            </div>
            <div class="excel-table-row">
                <div class="excel-col-label">PD</div>
                <div class="excel-col-value">{inc['PD']}</div>
            </div>
            <div class="excel-table-row">
                <div class="excel-col-label">FAT</div>
                <div class="excel-col-value" style="color:#16a34a;">{inc['FAT']}</div>
            </div>
            <div class="excel-table-row">
                <div class="excel-col-label">RWC</div>
                <div class="excel-col-value" style="color:#16a34a;">{inc['RWC']}</div>
            </div>
            <div class="excel-table-row">
                <div class="excel-col-label">LTI</div>
                <div class="excel-col-value" style="color:#16a34a;">{inc['LTI']}</div>
            </div>
            <div class="excel-table-row">
                <div class="excel-col-label excel-total-label">Total</div>
                <div class="excel-col-value excel-total-value">{inc['Total']}</div>
            </div>
        </div>
        """
        render_html(inc_table_html)

        st.caption("Data source: GCDC Project Incident Logbook & Register")

    with col_c:
        st.markdown('<div class="section-title">📊 Incidents Chart (Matching Image 2)</div>', unsafe_allow_html=True)

        # Plotly Bar Chart exactly matching Excel Image 2
        categories = ["NM", "MTC", "MVA", "FAC", "PD", "FAT", "RWC", "LTI"]
        counts = [inc["NM"], inc["MTC"], inc["MVA"], inc["FAC"], inc["PD"], inc["FAT"], inc["RWC"], inc["LTI"]]
        
        # Colors: Deep Teal/Navy for active, muted for zeros
        bar_colors = ["#005a87" if c > 0 else "#94a3b8" for c in counts]

        fig_inc_bar = go.Figure()
        fig_inc_bar.add_trace(go.Bar(
            x=categories,
            y=counts,
            text=counts,
            textposition='outside',
            textfont=dict(size=14, color='#0f2438', family='Inter, sans-serif'),
            marker=dict(
                color=bar_colors,
                line=dict(color='#003853', width=1.5)
            ),
            width=0.45
        ))

        fig_inc_bar.update_layout(
            title=dict(
                text="<b>Incidents</b>",
                font=dict(size=20, color='#0d233a', family='Inter, sans-serif'),
                x=0.5,
                xanchor='center'
            ),
            height=370,
            margin=dict(l=30, r=20, t=50, b=30),
            yaxis=dict(
                range=[0, 105],
                tickvals=[0, 20, 40, 60, 80, 100],
                gridcolor='#e2e8f0',
                tickfont=dict(size=12, color='#64748b')
            ),
            xaxis=dict(
                tickfont=dict(size=13, color='#0f172a', family='Inter, sans-serif')
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_inc_bar, use_container_width=True)

    # Secondary Row: Safety Pyramid & Proactive Interpretation
    r2_col1, r2_col2 = st.columns([1.1, 0.9])
    with r2_col1:
        st.markdown('<div class="section-card"><div class="section-title">📐 Heinrich\'s Safety Pyramid (Visual Funnel Model)</div>', unsafe_allow_html=True)
        
        # Native Plotly Funnel Pyramid - 100% Readable, No Clipping, Outside Labels
        pyr_levels = ["Fatalities", "Lost Time (LTI)", "Medical (MTC)", "Minor (FAC+MVA+PD)", "Near Misses (NM)"]
        pyr_counts = [inc['FAT'], inc['LTI'], inc['MTC'], inc['FAC'] + inc['MVA'] + inc['PD'], inc['NM']]
        pyr_labels = [
            f"<b>{inc['FAT']} Cases</b> (Zero / Safe)",
            f"<b>{inc['LTI']} Cases</b> (Zero / Safe)",
            f"<b>{inc['MTC']} Cases</b> (Managed)",
            f"<b>{inc['FAC'] + inc['MVA'] + inc['PD']} Cases</b> (Minor)",
            f"<b>{inc['NM']} Cases</b> (81.4% Proactive Base)"
        ]
        pyr_colors = ["#0f172a", "#dc2626", "#ea580c", "#ca8a04", "#0284c7"]

        fig_pyr = go.Figure(go.Funnel(
            y=pyr_levels,
            x=pyr_counts,
            text=pyr_labels,
            textposition="outside",
            textinfo="text",
            marker=dict(
                color=pyr_colors,
                line=dict(color="#ffffff", width=1.5)
            ),
            connector=dict(line=dict(color="#cbd5e1", width=1, dash="dot")),
            opacity=0.95
        ))

        fig_pyr.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=15, b=15),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(
                tickfont=dict(size=12, color='#0f172a', family='Inter, sans-serif')
            )
        )
        st.plotly_chart(fig_pyr, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r2_col2:
        st.markdown('<div class="section-card"><div class="section-title">💡 Safety Culture & Analysis Insights</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <span style="font-weight:600; color:#334155;">Proactive Reporting (Near Misses):</span>
                <span style="font-weight:700; color:#0284c7;">83 cases (81.4%)</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <span style="font-weight:600; color:#334155;">Recordable Cases (MTC):</span>
                <span style="font-weight:700; color:#f59e0b;">8 cases (7.8%)</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <span style="font-weight:600; color:#334155;">Asset & Vehicle Events (MVA + PD):</span>
                <span style="font-weight:700; color:#8b5cf6;">9 cases (8.8%)</span>
            </div>
            <div style="display:flex; justify-content:space-between; padding-top:8px; border-top:1px solid #e2e8f0;">
                <span style="font-weight:700; color:#15803d;">Severe Events (FAT / LTI / RWC):</span>
                <span style="font-weight:800; color:#15803d;">ZERO (0.0%)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.success("✅ **Benchmark:** Zero LTIs and a high ratio of Near Miss reporting indicates an active safety climate where hazards are caught before causing harm.")
        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================================
# 📋 PAGE: DEDICATED COMPLIANCE RATE %
# =========================================================================
elif st.session_state.active_page == "Compliance":
    st.markdown("## 📋 Compliance Rate % & Action Closure Analysis")
    st.caption("Detailed breakdown matching Excel Inspection and Action Closure Register")

    # Top Hero Section: Executive Card (Image 2) & Radial Gauge
    col_c1, col_c2 = st.columns([1, 1.2])

    with col_c1:
        st.markdown('<div class="section-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown('<div class="section-title" style="justify-content:center;">Executive KPI Card</div>', unsafe_allow_html=True)
        
        # Excel Image 2 Styled Box
        g_rate_pct = data['compliance']['grand']['rate'] * 100
        st.markdown(f"""
        <div class="compliance-box">
            <div class="compliance-header">Compliance Rate</div>
            <div class="compliance-value-block">{g_rate_pct:.0f}%</div>
            <div class="compliance-subtext">{data['compliance']['grand']['closed']:,} of {data['compliance']['grand']['total']:,} Closed</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Grand Compliance Progress Meter</div>', unsafe_allow_html=True)
        fig_comp_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=g_rate_pct,
            number={'suffix': "%", 'font': {'size': 32, 'color': '#0f2438'}},
            gauge={
                'axis': {'range': [0, 100], 'tickvals': [0, 50, 80, 95, 100], 'ticktext': ['0%', '50%', '80%', '95%', '100%']},
                'bar': {'color': '#16a34a', 'thickness': 0.35},
                'steps': [
                    {'range': [0, 80], 'color': '#fee2e2'},
                    {'range': [80, 95], 'color': '#fef3c7'},
                    {'range': [95, 100], 'color': '#dcfce7'}
                ],
                'threshold': {'line': {'color': "#15803d", 'width': 3}, 'thickness': 0.75, 'value': 95}
            }
        ))
        fig_comp_gauge.update_layout(height=180, margin=dict(l=20, r=20, t=20, b=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_comp_gauge, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Categorical Inspection Breakdown
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Category-wise Action & Inspection Status</div>', unsafe_allow_html=True)

    obs = data['compliance']['obs']
    ncr = data['compliance']['ncr']
    aud = data['compliance']['audits']
    grand = data['compliance']['grand']

    c_b1, c_b2, c_b3 = st.columns(3)

    with c_b1:
        st.markdown(f"""
        <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-weight:700; color:#166534; font-size:14px;">Observations</span>
                <span style="background:#15803d; color:white; font-weight:700; font-size:12px; padding:2px 8px; border-radius:4px;">{obs['rate']*100:.0f}%</span>
            </div>
            <div style="font-size:12px; color:#374151; margin-bottom:10px;">
                <b>{obs['closed']:,}</b> Closed &nbsp;|&nbsp; <b>{obs['open']}</b> Open &nbsp;|&nbsp; <b>{obs['total']:,}</b> Total
            </div>
            <div style="background:#dcfce7; border-radius:6px; height:8px; overflow:hidden;">
                <div style="background:#15803d; width:{obs['rate']*100:.1f}%; height:100%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_b2:
        st.markdown(f"""
        <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-weight:700; color:#166534; font-size:14px;">NCR (Non-Conformance)</span>
                <span style="background:#15803d; color:white; font-weight:700; font-size:12px; padding:2px 8px; border-radius:4px;">{ncr['rate']*100:.0f}%</span>
            </div>
            <div style="font-size:12px; color:#374151; margin-bottom:10px;">
                <b>{ncr['closed']}</b> Closed &nbsp;|&nbsp; <b>{ncr['open']}</b> Open &nbsp;|&nbsp; <b>{ncr['total']}</b> Total
            </div>
            <div style="background:#dcfce7; border-radius:6px; height:8px; overflow:hidden;">
                <div style="background:#15803d; width:{ncr['rate']*100:.1f}%; height:100%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_b3:
        st.markdown(f"""
        <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:10px; padding:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-weight:700; color:#991b1b; font-size:14px;">Audits & Other Inspections</span>
                <span style="background:#dc2626; color:white; font-weight:700; font-size:12px; padding:2px 8px; border-radius:4px;">{aud['rate']*100:.0f}%</span>
            </div>
            <div style="font-size:12px; color:#991b1b; margin-bottom:10px;">
                <b>{aud['closed']}</b> Closed &nbsp;|&nbsp; <b style="color:#b91c1c;">{aud['open']}</b> Open &nbsp;|&nbsp; <b>{aud['total']}</b> Total
            </div>
            <div style="background:#fee2e2; border-radius:6px; height:8px; overflow:hidden;">
                <div style="background:#dc2626; width:{aud['rate']*100:.1f}%; height:100%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Detailed Table
    st.markdown("<br>", unsafe_allow_html=True)
    table_data = pd.DataFrame([
        {"Inspections": "Observations", "Open": obs['open'], "Close": f"{obs['closed']:,}", "Total": f"{obs['total']:,}", "Closure Rate": f"{obs['rate']*100:.0f}%"},
        {"Inspections": "NCR", "Open": ncr['open'], "Close": str(ncr['closed']), "Total": str(ncr['total']), "Closure Rate": f"{ncr['rate']*100:.0f}%"},
        {"Inspections": "Other Inspections including Audits", "Open": aud['open'], "Close": str(aud['closed']), "Total": str(aud['total']), "Closure Rate": f"{aud['rate']*100:.0f}% (Action Required)"},
        {"Inspections": "Grand total", "Open": grand['open'], "Close": f"{grand['closed']:,}", "Total": f"{grand['total']:,}", "Closure Rate": f"{grand['rate']*100:.0f}%"}
    ])
    st.dataframe(table_data, use_container_width=True, hide_index=True)

    # Yellow Note Box
    st.markdown("""
    <div class="yellow-note-box">
        ⚠️ <b>Important Note:</b> The HSE completed activities in <b>T22</b> are included in the grand total closed performance rate.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================================
# 🔍 PAGE: DEDICATED SITE OBSERVATIONS (MATCHING USER'S NEW EXCEL IMAGES)
# =========================================================================
elif st.session_state.active_page == "Observations":
    st.markdown("## 🔍 Site Observations Performance & Field Rectification Tracking")
    st.caption("Complete breakdown matching the official Excel Site Observation register, closure analytics, and overdue rates")

    # 1. TOP EXECUTIVE KPI CARDS
    ok1, ok2, ok3, ok4, ok5 = st.columns(5)
    with ok1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Total Site Observations</div>
            <div class="kpi-value">1,250</div>
            <span class="kpi-badge badge-info">YTD Field Logs</span>
            <div class="metric-sub">Cumulative Action Items</div>
        </div>
        """, unsafe_allow_html=True)
    with ok2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Closed Observations</div>
            <div class="kpi-value" style="color:#15803d;">1,242</div>
            <span class="kpi-badge badge-success">99% Closure Rate</span>
            <div class="metric-sub">World-Class Resolution Rate</div>
        </div>
        """, unsafe_allow_html=True)
    with ok3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Active Open Observations</div>
            <div class="kpi-value" style="color:#0284c7;">8</div>
            <span class="kpi-badge badge-info">Under Rectification</span>
            <div class="metric-sub">Immediate Field Actions</div>
        </div>
        """, unsafe_allow_html=True)
    with ok4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Overdue (OD) Observations</div>
            <div class="kpi-value" style="color:#dc2626;">8</div>
            <span class="kpi-badge badge-danger">1.4% OD Rate</span>
            <div class="metric-sub">Target &le; 5% Achieved</div>
        </div>
        """, unsafe_allow_html=True)
    with ok5:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Closed On-Time (OTC)</div>
            <div class="kpi-value">25</div>
            <span class="kpi-badge badge-success">2% OTC Rate</span>
            <div class="metric-sub">On-Time Closed Logs</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. MAIN CONTENT: EXACT EXCEL TABLES (IMAGE 1 & 2) + EXCEL BAR CHART (IMAGE 3)
    col_obs_t, col_obs_c = st.columns([1, 1.45])

    with col_obs_t:
        st.markdown('<div class="section-title">📋 Excel Site Observation Registry Tables</div>', unsafe_allow_html=True)
        
        ot1, ot2 = st.columns(2)
        with ot1:
            st.markdown('<div style="font-size:12px; font-weight:700; color:#64748b; margin-bottom:4px; text-transform:uppercase;">Status Counts (Image 2)</div>', unsafe_allow_html=True)
            tbl_obs1_html = """
            <table style="width: 100%; border-collapse: collapse; border: 2px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; font-size: 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
                <thead>
                    <tr style="background-color: #002060; color: #ffffff; border-bottom: 2px solid #000000;">
                        <th colspan="2" style="padding: 8px; text-align: center; font-size: 16px; font-weight: 800; letter-spacing: 0.5px;">Site Observation</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1.5px solid #000000;">
                        <td style="padding: 8px 12px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Open</td>
                        <td style="padding: 8px 12px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">8</td>
                    </tr>
                    <tr style="border-bottom: 1.5px solid #000000;">
                        <td style="padding: 8px 12px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Closed</td>
                        <td style="padding: 8px 12px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">1242</td>
                    </tr>
                    <tr style="border-bottom: 1.5px solid #000000;">
                        <td style="padding: 8px 12px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Overdue</td>
                        <td style="padding: 8px 12px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">8</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 12px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 2px solid #000000;">Total</td>
                        <td style="padding: 8px 12px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">1250</td>
                    </tr>
                </tbody>
            </table>
            """
            render_html(tbl_obs1_html)

        with ot2:
            st.markdown('<div style="font-size:12px; font-weight:700; color:#64748b; margin-bottom:4px; text-transform:uppercase;">Performance Rates (Image 1)</div>', unsafe_allow_html=True)
            tbl_obs2_html = """
            <table style="width: 100%; border-collapse: collapse; border: 2px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; font-size: 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
                <thead>
                    <tr style="background-color: #002060; color: #ffffff; border-bottom: 2px solid #000000;">
                        <th colspan="2" style="padding: 8px; text-align: center; font-size: 16px; font-weight: 800; letter-spacing: 0.5px;">Site Observation</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1.5px solid #000000;">
                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Closure Rate</td>
                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">99%</td>
                    </tr>
                    <tr style="border-bottom: 1.5px solid #000000;">
                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">OD Rate</td>
                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">1.4%</td>
                    </tr>
                    <tr style="border-bottom: 1.5px solid #000000;">
                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">OTC Rate</td>
                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">2%</td>
                    </tr>
                    <tr style="border-bottom: 1.5px solid #000000;">
                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 2px solid #000000;">Total OD</td>
                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">17</td>
                    </tr>
                    <tr>
                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Closed On-time</td>
                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">25</td>
                    </tr>
                </tbody>
            </table>
            """
            render_html(tbl_obs2_html)

        st.markdown("""
        <div style="margin-top: 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px;">
            <div style="font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase;">Mathematical Formulation</div>
            <div style="font-size: 12.5px; color: #1e293b; margin-top: 4px; line-height: 1.5;">
                • <b>Closure Rate:</b> (1,242 Closed &divide; 1,250 Total) &times; 100 = <b>99.36% (~99%)</b><br>
                • <b>OD (Overdue) Rate:</b> (17 Total OD &divide; 1,250 Total) &times; 100 = <b>1.36% (~1.4%)</b><br>
                • <b>OTC (On-Time Closure) Rate:</b> (25 &divide; 1,250 Total) &times; 100 = <b>2.0%</b><br>
                • <b>Active Outstanding:</b> 8 Open Items currently in field close-out loop.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_obs_c:
        st.markdown('<div class="section-title">📊 Excel Site Observations Visual Distribution (Image 3)</div>', unsafe_allow_html=True)
        fig_obs_main = go.Figure()
        fig_obs_main.add_trace(go.Bar(
            x=['Open', 'Closed', 'Overdue'],
            y=[8, 1242, 8],
            text=['8', '1242', '8'],
            textposition='outside',
            textfont=dict(size=15, color='#0d2640', weight='bold'),
            marker=dict(
                color='#0e5374',
                line=dict(color='#09384f', width=2)
            ),
            width=0.42
        ))
        fig_obs_main.update_layout(
            title=dict(text='<b>Site Observations</b>', font=dict(size=22, color='#0d2640', family='Segoe UI, Inter, sans-serif'), x=0.5, xanchor='center'),
            yaxis=dict(
                range=[0, 1500],
                tickvals=[0, 200, 400, 600, 800, 1000, 1200, 1400],
                gridcolor='#e2e8f0',
                zerolinecolor='#cbd5e1'
            ),
            xaxis=dict(
                tickfont=dict(size=14, color='#0d2640', weight='bold')
            ),
            height=340,
            margin=dict(l=40, r=20, t=45, b=35),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_obs_main, use_container_width=True)

        st.markdown("""
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px; margin-top: 10px;">
            <span style="color: #166534; font-weight: 700; font-size: 13px;">🏆 Outstanding Proactive Safety:</span>
            <span style="color: #15803d; font-size: 12.5px;"> Exceptional field engagement with 1,242 out of 1,250 proactive observations resolved, achieving a stellar 99% closure velocity.</span>
        </div>
        """, unsafe_allow_html=True)


# =========================================================================
# 📑 PAGE: DEDICATED NCRs PERFORMANCE (MATCHING USER'S NEW EXCEL IMAGES)
# =========================================================================
elif st.session_state.active_page == "NCRs":
    st.markdown("## 📑 Non-Conformance Reports (NCRs) Performance & Action Tracking")
    st.caption("Complete breakdown matching the official Excel NCR register, closure analytics, and overdue rates")

    # 1. TOP EXECUTIVE KPI CARDS
    nk1, nk2, nk3, nk4, nk5 = st.columns(5)
    with nk1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Total NCRs Logged</div>
            <div class="kpi-value">54</div>
            <span class="kpi-badge badge-info">YTD Registry</span>
            <div class="metric-sub">Cumulative Action Items</div>
        </div>
        """, unsafe_allow_html=True)
    with nk2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Closed NCRs</div>
            <div class="kpi-value" style="color:#15803d;">52</div>
            <span class="kpi-badge badge-success">96% Closure Rate</span>
            <div class="metric-sub">Target &ge; 90% Achieved</div>
        </div>
        """, unsafe_allow_html=True)
    with nk3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Active Open NCRs</div>
            <div class="kpi-value" style="color:#0284c7;">2</div>
            <span class="kpi-badge badge-info">Under Rectification</span>
            <div class="metric-sub">Field Actions In Progress</div>
        </div>
        """, unsafe_allow_html=True)
    with nk4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Overdue (OD) NCRs</div>
            <div class="kpi-value" style="color:#dc2626;">2</div>
            <span class="kpi-badge badge-danger">4% OD Rate</span>
            <div class="metric-sub">Requires Expedited Action</div>
        </div>
        """, unsafe_allow_html=True)
    with nk5:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Closed On-Time (OTC)</div>
            <div class="kpi-value">0</div>
            <span class="kpi-badge badge-warning">0% OTC Rate</span>
            <div class="metric-sub">Pending SLA Validation</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. MAIN CONTENT: EXACT EXCEL TABLES (IMAGE 1 & 2) + EXCEL BAR CHART (IMAGE 3)
    col_ncr_t, col_ncr_c = st.columns([1, 1.45])

    with col_ncr_t:
        st.markdown('<div class="section-title">📋 Excel NCRs Registry Tables</div>', unsafe_allow_html=True)
        
        # Sub-columns for side-by-side or stacked display of both tables
        nt1, nt2 = st.columns(2)
        with nt1:
            st.markdown('<div style="font-size:12px; font-weight:700; color:#64748b; margin-bottom:4px; text-transform:uppercase;">Status Counts (Image 1)</div>', unsafe_allow_html=True)
            tbl_1_html = """
            <table style="width: 100%; border-collapse: collapse; border: 2px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; font-size: 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
                <thead>
                    <tr style="background-color: #002060; color: #ffffff; border-bottom: 2px solid #000000;">
                        <th colspan="2" style="padding: 8px; text-align: center; font-size: 16px; font-weight: 800; letter-spacing: 0.5px;">NCRs</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1.5px solid #000000;">
                        <td style="padding: 8px 12px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Open</td>
                        <td style="padding: 8px 12px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">2</td>
                    </tr>
                    <tr style="border-bottom: 1.5px solid #000000;">
                        <td style="padding: 8px 12px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Closed</td>
                        <td style="padding: 8px 12px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">52</td>
                    </tr>
                    <tr style="border-bottom: 1.5px solid #000000;">
                        <td style="padding: 8px 12px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Overdue</td>
                        <td style="padding: 8px 12px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">2</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 12px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 2px solid #000000;">Total</td>
                        <td style="padding: 8px 12px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">54</td>
                    </tr>
                </tbody>
            </table>
            """
            render_html(tbl_1_html)

        with nt2:
            st.markdown('<div style="font-size:12px; font-weight:700; color:#64748b; margin-bottom:4px; text-transform:uppercase;">Performance Rates (Image 2)</div>', unsafe_allow_html=True)
            tbl_2_html = """
            <table style="width: 100%; border-collapse: collapse; border: 2px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; font-size: 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
                <thead>
                    <tr style="background-color: #002060; color: #ffffff; border-bottom: 2px solid #000000;">
                        <th colspan="2" style="padding: 8px; text-align: center; font-size: 16px; font-weight: 800; letter-spacing: 0.5px;">NCRs</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1.5px solid #000000;">
                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Closure Rate</td>
                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">96%</td>
                    </tr>
                    <tr style="border-bottom: 1.5px solid #000000;">
                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">OD Rate</td>
                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">4%</td>
                    </tr>
                    <tr style="border-bottom: 1.5px solid #000000;">
                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">OTC Rate</td>
                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">0%</td>
                    </tr>
                    <tr style="border-bottom: 1.5px solid #000000;">
                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 2px solid #000000;">Total OD</td>
                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">2</td>
                    </tr>
                    <tr>
                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Closed On-time</td>
                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">0</td>
                    </tr>
                </tbody>
            </table>
            """
            render_html(tbl_2_html)

        st.markdown("""
        <div style="margin-top: 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px;">
            <div style="font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase;">Mathematical Formulation</div>
            <div style="font-size: 12.5px; color: #1e293b; margin-top: 4px; line-height: 1.5;">
                • <b>Closure Rate:</b> (52 Closed &divide; 54 Total) &times; 100 = <b>96.3% (~96%)</b><br>
                • <b>OD (Overdue) Rate:</b> (2 Overdue &divide; 54 Total) &times; 100 = <b>3.7% (~4%)</b><br>
                • <b>Total Outstanding:</b> 2 Open Items (currently being expedited)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_ncr_c:
        st.markdown('<div class="section-title">📊 Excel NCRs Visual Distribution (Image 3)</div>', unsafe_allow_html=True)
        fig_ncr_main = go.Figure()
        fig_ncr_main.add_trace(go.Bar(
            x=['Open', 'Closed', 'Overdue'],
            y=[2, 52, 2],
            text=['2', '52', '2'],
            textposition='outside',
            textfont=dict(size=15, color='#0d2640', weight='bold'),
            marker=dict(
                color='#0e5374',
                line=dict(color='#09384f', width=2)
            ),
            width=0.42
        ))
        fig_ncr_main.update_layout(
            title=dict(text='<b>NCRs</b>', font=dict(size=22, color='#0d2640', family='Segoe UI, Inter, sans-serif'), x=0.5, xanchor='center'),
            yaxis=dict(
                title=dict(text='<b>Num. of NCRs</b>', font=dict(size=13, color='#0d2640')),
                range=[0, 65],
                tickvals=[0, 10, 20, 30, 40, 50, 60],
                gridcolor='#e2e8f0',
                zerolinecolor='#cbd5e1'
            ),
            xaxis=dict(
                tickfont=dict(size=14, color='#0d2640', weight='bold')
            ),
            height=340,
            margin=dict(l=40, r=20, t=45, b=35),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_ncr_main, use_container_width=True)

        st.markdown("""
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px; margin-top: 10px;">
            <span style="color: #166534; font-weight: 700; font-size: 13px;">✅ Quality Performance Note:</span>
            <span style="color: #15803d; font-size: 12.5px;"> High compliance standard maintained with 52 out of 54 non-conformances successfully closed (96% resolution efficiency).</span>
        </div>
        """, unsafe_allow_html=True)


# =========================================================================
# 🛠️ PAGE: DEDICATED HSE ACTIVITIES (MATCHING USER'S NEW EXCEL IMAGES)
# =========================================================================
elif st.session_state.active_page == "Activities":
    st.markdown("## 🛠️ HSE Activities Execution & Field Engagement")
    st.caption("Complete breakdown matching the official Excel HSE Activity log, Toolbox Talks (TBT), inspections, and campaigns")

    # 1. TOP EXECUTIVE KPI CARDS
    ak1, ak2, ak3, ak4 = st.columns(4)
    with ak1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Total HSE Activities</div>
            <div class="kpi-value">121</div>
            <span class="kpi-badge badge-info">YTD Execution</span>
            <div class="metric-sub">Cumulative Field Sessions</div>
        </div>
        """, unsafe_allow_html=True)
    with ak2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Toolbox Talks (TBT)</div>
            <div class="kpi-value" style="color:#0284c7;">114</div>
            <span class="kpi-badge badge-success">94.2% of Total</span>
            <div class="metric-sub">Daily Frontline Briefings</div>
        </div>
        """, unsafe_allow_html=True)
    with ak3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Site Inspections</div>
            <div class="kpi-value" style="color:#15803d;">6</div>
            <span class="kpi-badge badge-info">Scheduled Audits</span>
            <div class="metric-sub">Rigorous Field Monitoring</div>
        </div>
        """, unsafe_allow_html=True)
    with ak4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Safety Campaigns</div>
            <div class="kpi-value" style="color:#d97706;">1</div>
            <span class="kpi-badge badge-warning">Targeted Campaign</span>
            <div class="metric-sub">Project-Wide Awareness</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. MAIN CONTENT: EXACT EXCEL TABLE (IMAGE 1) + EXCEL BAR CHART (IMAGE 2)
    col_act_t, col_act_c = st.columns([1, 1.45])

    with col_act_t:
        st.markdown('<div class="section-title">📋 Excel HSE Activities Table</div>', unsafe_allow_html=True)
        act_page_tbl = """
        <table style="width: 100%; border-collapse: collapse; border: 2px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; font-size: 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
            <thead>
                <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #ffffff;">
                    <th colspan="2" style="padding: 8px; text-align: center; font-size: 16px; font-weight: 800; letter-spacing: 0.5px;">HSE Activities</th>
                </tr>
                <tr style="background-color: #002060; color: #ffffff; border-bottom: 2px solid #000000;">
                    <th style="padding: 7px 12px; text-align: center; font-size: 13.5px; font-weight: 700; border-right: 2px solid #ffffff; width: 60%;">Activity</th>
                    <th style="padding: 7px 12px; text-align: center; font-size: 13.5px; font-weight: 700; width: 40%;">Quantity</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1.5px solid #000000;">
                    <td style="padding: 8px 12px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">TBT</td>
                    <td style="padding: 8px 12px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">114</td>
                </tr>
                <tr style="border-bottom: 1.5px solid #000000;">
                    <td style="padding: 8px 12px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">inspections</td>
                    <td style="padding: 8px 12px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">6</td>
                </tr>
                <tr style="border-bottom: 1.5px solid #000000;">
                    <td style="padding: 8px 12px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Campaigns</td>
                    <td style="padding: 8px 12px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">1</td>
                </tr>
                <tr>
                    <td style="padding: 8px 12px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 2px solid #000000;">Total</td>
                    <td style="padding: 8px 12px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">121</td>
                </tr>
            </tbody>
        </table>
        """
        render_html(act_page_tbl)

        st.markdown("""
        <div style="margin-top: 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px;">
            <div style="font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase;">Activity Proportions</div>
            <div style="font-size: 12.5px; color: #1e293b; margin-top: 4px; line-height: 1.5;">
                • <b>Toolbox Talks (TBT):</b> 114 sessions (94.2%)<br>
                • <b>Formal Inspections:</b> 6 scheduled walkthroughs (5.0%)<br>
                • <b>Safety Campaigns:</b> 1 major worker engagement drive (0.8%)<br>
                • <b>Total Field Touchpoints:</b> 121 proactive activities executed.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_act_c:
        st.markdown('<div class="section-title">📊 Excel HSE Activities Visual Distribution (Image 2)</div>', unsafe_allow_html=True)
        fig_act_main = go.Figure()
        fig_act_main.add_trace(go.Bar(
            x=['TBT', 'inspections', 'Campaigns'],
            y=[114, 6, 1],
            text=['114', '6', '1'],
            textposition='outside',
            textfont=dict(size=15, color='#0d2640', weight='bold'),
            marker=dict(
                color='#0e5374',
                line=dict(color='#09384f', width=2)
            ),
            width=0.42
        ))
        fig_act_main.update_layout(
            title=dict(text='<b>HSE Activities</b>', font=dict(size=22, color='#0d2640', family='Segoe UI, Inter, sans-serif'), x=0.5, xanchor='center'),
            yaxis=dict(
                range=[0, 130],
                tickvals=[0, 20, 40, 60, 80, 100, 120],
                gridcolor='#e2e8f0',
                zerolinecolor='#cbd5e1'
            ),
            xaxis=dict(
                tickfont=dict(size=14, color='#0d2640', weight='bold')
            ),
            height=340,
            margin=dict(l=40, r=20, t=45, b=35),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_act_main, use_container_width=True)

        st.markdown("""
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px; margin-top: 10px;">
            <span style="color: #166534; font-weight: 700; font-size: 13px;">🛡️ Proactive Communication:</span>
            <span style="color: #15803d; font-size: 12.5px;"> High-intensity daily hazard briefings through 114 TBTs ensure consistent frontline risk mitigation and safety protocol adherence.</span>
        </div>
        """, unsafe_allow_html=True)


# =========================================================================
# 🏠 PAGE: MAIN HOME (SUMMARIZED VISUALIZATION)
# =========================================================================
elif st.session_state.active_page == "Home":
    st.markdown("## 🏠 Executive Overview & KPI Summary")
    st.caption("Consolidated project safety dashboard across all functional HSE domains")

    # 1. TOP 6 EXECUTIVE KPI CARDS
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        g_rate = data['compliance']['grand']['rate'] * 100
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Compliance Rate</div>
            <div class="kpi-value">{g_rate:.1f}%</div>
            <span class="kpi-badge badge-success">Target &ge; 95%</span>
            <div class="metric-sub">1,416 / 1,427 Closed</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Incidents</div>
            <div class="kpi-value">{data['incidents']['Total']}</div>
            <span class="kpi-badge badge-info">81% Near Misses</span>
            <div class="metric-sub">Zero Fatalities / Zero LTI</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Safe Man-Hours</div>
            <div class="kpi-value">{data['safe_man_hours']['total']:,.0f}</div>
            <span class="kpi-badge badge-success">Cumulative</span>
            <div class="metric-sub">Prior: {data['safe_man_hours']['prior']:,.0f} hrs</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        tr_rate = data['training']['rate'] * 100
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Training Execution</div>
            <div class="kpi-value">{tr_rate:.1f}%</div>
            <span class="kpi-badge badge-warning">5 of 17 Sessions</span>
            <div class="metric-sub">62 Attendees Logged</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        ltifr_val = data['rates']['ltifr']
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">LTIFR</div>
            <div class="kpi-value">{ltifr_val:.2f}</div>
            <span class="kpi-badge badge-success">{data['rates']['ltifr_rating']}</span>
            <div class="metric-sub">Target: 0.00</div>
        </div>
        """, unsafe_allow_html=True)

    with c6:
        trir_val = data['rates']['trir']
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">TRIR</div>
            <div class="kpi-value">{trir_val:.3f}</div>
            <span class="kpi-badge badge-info">{data['rates']['trir_rating']} (&le;0.50)</span>
            <div class="metric-sub">Industry Benchmark</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. GAUGES & INCIDENT COMPOSITION
    row1_left, row1_right = st.columns([1, 1])

    with row1_left:
        st.markdown('<div class="section-card"><div class="section-title">🎯 Safety Frequency Rates (Gauges)</div>', unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            fig_ltifr = create_gauge(
                value=data['rates']['ltifr'],
                title="LTIFR",
                max_val=1.0,
                thresholds=[
                    {'range': [0, 0.01], 'color': '#86efac'},
                    {'range': [0.01, 0.2], 'color': '#fde047'},
                    {'range': [0.2, 1.0], 'color': '#fca5a5'}
                ],
                target_text="Lost Time Injury Rate (Zero Target)"
            )
            st.plotly_chart(fig_ltifr, use_container_width=True)
        with g2:
            fig_trir = create_gauge(
                value=data['rates']['trir'],
                title="TRIR",
                max_val=1.5,
                thresholds=[
                    {'range': [0, 0.2], 'color': '#86efac'},
                    {'range': [0.2, 0.5], 'color': '#93c5fd'},
                    {'range': [0.5, 0.75], 'color': '#fde047'},
                    {'range': [0.75, 1.5], 'color': '#fca5a5'}
                ],
                target_text="Total Recordable Rate (&le;0.50 Good)"
            )
            st.plotly_chart(fig_trir, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with row1_right:
        st.markdown('<div class="section-card"><div class="section-title">🚨 Incident Severity Distribution (102 Recorded Cases)</div>', unsafe_allow_html=True)
        inc_data = [
            {"Category": "Near Miss (NM)", "Count": data['incidents']['NM'], "Color": "#005a87"},
            {"Category": "Medical Treatment (MTC)", "Count": data['incidents']['MTC'], "Color": "#f59e0b"},
            {"Category": "Motor Vehicle (MVA)", "Count": data['incidents']['MVA'], "Color": "#ec4899"},
            {"Category": "Property Damage (PD)", "Count": data['incidents']['PD'], "Color": "#8b5cf6"},
            {"Category": "First Aid Case (FAC)", "Count": data['incidents']['FAC'], "Color": "#10b981"},
            {"Category": "Lost Time Injury (LTI)", "Count": data['incidents']['LTI'], "Color": "#ef4444"},
            {"Category": "Fatality (FAT)", "Count": data['incidents']['FAT'], "Color": "#000000"}
        ]
        df_inc = pd.DataFrame(inc_data)
        df_inc = df_inc[df_inc['Count'] > 0]
        
        fig_donut = px.pie(
            df_inc,
            names="Category",
            values="Count",
            hole=0.55,
            color="Category",
            color_discrete_map={row["Category"]: row["Color"] for row in inc_data}
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#ffffff', width=2)))
        fig_donut.update_layout(
            height=220,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. SAFE MAN-HOURS & DAILY MANPOWER
    st.markdown('<div class="section-card"><div class="section-title">⏱️ Monthly Safe Man-Hours & Daily Workforce Dynamics (Jan – Sep 2026)</div>', unsafe_allow_html=True)
    m_hours = data['safe_man_hours']['monthly']
    m_power = data['manpower']['monthly']
    chart_months = list(m_hours.keys())
    chart_hours = list(m_hours.values())
    chart_power = [m_power.get(m, 0) for m in chart_months]

    fig_dual = go.Figure()
    fig_dual.add_trace(go.Bar(
        x=chart_months,
        y=chart_hours,
        name="Monthly Safe Man-Hours",
        marker_color="#38bdf8",
        opacity=0.85,
        yaxis="y1"
    ))
    fig_dual.add_trace(go.Scatter(
        x=chart_months,
        y=chart_power,
        name="Average Daily Manpower",
        mode="lines+markers",
        line=dict(color="#f97316", width=3),
        marker=dict(size=8, color="#ea580c"),
        yaxis="y2"
    ))
    fig_dual.update_layout(
        height=280,
        margin=dict(l=40, r=40, t=20, b=25),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Safe Man-Hours", side="left", gridcolor="#f1f5f9"),
        yaxis2=dict(title="Daily Manpower", side="right", overlaying="y", showgrid=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified"
    )
    st.plotly_chart(fig_dual, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. HSE Staffing Compliance & Proactive Engagements (Exact Excel Visuals)
    st.markdown('<div class="section-card"><div class="section-title">👥 HSE Staffing Compliance & Capacity Analytics (Excel Format)</div>', unsafe_allow_html=True)

    col_st_t, col_st_g, col_st_b = st.columns([1, 1, 1.25])

    with col_st_t:
        st.markdown('<div style="font-size:12px; font-weight:700; color:#64748b; margin-bottom:6px; text-transform:uppercase;">Excel Registry Table</div>', unsafe_allow_html=True)
        staff_home_tbl = """
        <table style="width: 100%; border-collapse: collapse; border: 2px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; font-size: 13.5px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
            <thead>
                <tr style="background-color: #002060; color: #ffffff; border-bottom: 2px solid #000000;">
                    <th colspan="2" style="padding: 8px; text-align: center; font-size: 15px; font-weight: 800; letter-spacing: 0.5px;">HSE Staffing Compliance</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1.5px solid #000000;">
                    <td style="padding: 7px 12px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000; width: 62%;">Actual</td>
                    <td style="padding: 7px 12px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center; width: 38%; font-size: 15px;">22</td>
                </tr>
                <tr style="border-bottom: 1.5px solid #000000;">
                    <td style="padding: 7px 12px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Required</td>
                    <td style="padding: 7px 12px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center; font-size: 15px;">25</td>
                </tr>
                <tr style="border-bottom: 1.5px solid #000000;">
                    <td style="padding: 7px 12px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Gap</td>
                    <td style="padding: 7px 12px; background-color: #ffffff; color: #dc2626; font-weight: 800; text-align: center; font-size: 15px;">3</td>
                </tr>
                <tr>
                    <td style="padding: 7px 12px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 2px solid #000000;">Compliance</td>
                    <td style="padding: 7px 12px; background-color: #ffffff; color: #15803d; font-weight: 800; text-align: center; font-size: 16px;">88%</td>
                </tr>
            </tbody>
        </table>
        """
        render_html(staff_home_tbl)

        st.markdown("""
        <div style="margin-top: 10px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; font-size: 11.5px; color: #475569; line-height: 1.4;">
            • <b>Formula:</b> (22 &divide; 25) &times; 100 = <b>88.0%</b><br>
            • <b>Current Gap:</b> 3 Safety Positions in mobilization
        </div>
        """, unsafe_allow_html=True)

    with col_st_g:
        st.markdown('<div style="font-size:12px; font-weight:700; color:#64748b; margin-bottom:6px; text-transform:uppercase;">Compliance Progress Meter</div>', unsafe_allow_html=True)
        fig_staff_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=88,
            number={'suffix': "%", 'font': {'size': 32, 'color': '#0d2640', 'family': 'Inter, sans-serif'}},
            title={'text': "<b>Staffing Compliance</b><br><span style='font-size:12px;color:#64748b'>22 of 25 Staff On-Site</span>", 'font': {'size': 14, 'color': '#0d2640'}},
            gauge={
                'axis': {'range': [0, 100], 'tickvals': [0, 50, 80, 88, 100], 'ticktext': ['0%', '50%', '80%', '88%', '100%']},
                'bar': {'color': '#0284c7', 'thickness': 0.32},
                'steps': [
                    {'range': [0, 80], 'color': '#fee2e2'},
                    {'range': [80, 95], 'color': '#fef3c7'},
                    {'range': [95, 100], 'color': '#dcfce7'}
                ],
                'threshold': {'line': {'color': "#15803d", 'width': 3.5}, 'thickness': 0.8, 'value': 100}
            }
        ))
        fig_staff_gauge.update_layout(height=230, margin=dict(l=20, r=20, t=35, b=15), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_staff_gauge, use_container_width=True)

    with col_st_b:
        st.markdown('<div style="font-size:12px; font-weight:700; color:#64748b; margin-bottom:6px; text-transform:uppercase;">Headcount Distribution</div>', unsafe_allow_html=True)
        fig_staff_bar = go.Figure()
        fig_staff_bar.add_trace(go.Bar(
            x=['Actual', 'Required', 'Gap'],
            y=[22, 25, 3],
            text=['22', '25', '3'],
            textposition='outside',
            textfont=dict(size=14, color='#0d2640', weight='bold'),
            marker=dict(
                color=['#0e5374', '#15803d', '#dc2626'],
                line=dict(color=['#09384f', '#166534', '#991b1b'], width=1.5)
            ),
            width=0.45
        ))
        fig_staff_bar.update_layout(
            title=dict(text='<b>Staffing Headcount</b>', font=dict(size=16, color='#0d2640', family='Segoe UI, Inter, sans-serif'), x=0.5, xanchor='center'),
            yaxis=dict(
                title=dict(text='Personnel', font=dict(size=11, color='#0d2640')),
                range=[0, 30],
                tickvals=[0, 5, 10, 15, 20, 25],
                gridcolor='#e2e8f0'
            ),
            xaxis=dict(tickfont=dict(size=12, color='#0d2640', weight='bold')),
            height=230,
            margin=dict(l=35, r=15, t=40, b=25),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_staff_bar, use_container_width=True)

    # 4 Quick Metric Pills for Proactive Overview
    st.markdown("<hr style='margin: 15px 0 10px 0; border: none; border-top: 1px dashed #e2e8f0;'>", unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.metric("Toolbox Talks (TBT)", "114 Sessions", "Frontline Briefings")
    with p2:
        st.metric("Formal Inspections", "6 Audits", "Quality & Compliance")
    with p3:
        st.metric("Safety Campaigns", "1 Drive", "Targeted Worker Awareness")
    with p4:
        st.metric("Staffing Compliance", "88.0%", "22 / 25 Mobilized (Gap: 3)")
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================================
# ⏱️ PAGE: MAN-HOURS & WORKFORCE
# =========================================================================
elif st.session_state.active_page == "Workforce":
    st.markdown("## ⏱️ Safe Man-Hours & Workforce Analysis")
    st.caption("Month-by-month safe man-hours, prior historical hours, and workforce staffing")

    # Top KPI Metrics Cards
    current_2026_total = sum(data['safe_man_hours']['monthly'].values())
    w1, w2, w3, w4 = st.columns(4)
    with w1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Safe Man-Hours</div>
            <div class="kpi-value">{data['safe_man_hours']['total']:,.0f}</div>
            <span class="kpi-badge badge-success">Cumulative Total</span>
            <div class="metric-sub">Zero LTI Milestone</div>
        </div>
        """, unsafe_allow_html=True)
    with w2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">YTD 2026 Safe Hours</div>
            <div class="kpi-value">{current_2026_total:,.0f}</div>
            <span class="kpi-badge badge-info">Jan – Sep 2026</span>
            <div class="metric-sub">Avg: {current_2026_total/9:,.0f} hrs/mo</div>
        </div>
        """, unsafe_allow_html=True)
    with w3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Hours Prior to 2026</div>
            <div class="kpi-value">{data['safe_man_hours']['prior']:,.0f}</div>
            <span class="kpi-badge badge-warning">Up to Dec 2025</span>
            <div class="metric-sub">Baseline Carryover</div>
        </div>
        """, unsafe_allow_html=True)
    with w4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Daily Manpower</div>
            <div class="kpi-value">{data['manpower']['average']:,.0f}</div>
            <span class="kpi-badge badge-success">Personnel On-Site</span>
            <div class="metric-sub">Peak: 1,400 (Feb)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # MAIN ROW: EXACT TABLE (IMAGE 1) & EXACT BAR CHART (IMAGE 2)
    col_t_hours, col_c_hours = st.columns([1, 1.6])

    with col_t_hours:
        st.markdown('<div class="section-title">📋 Safe Man-Hours Table (Excel Format)</div>', unsafe_allow_html=True)

        all_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        m_dict = data['safe_man_hours']['monthly']
        
        # Build clean single-line rows
        month_rows_html = "".join([
            f'<div class="excel-table-row"><div class="excel-col-label">{m}</div><div class="excel-col-value">{f"{m_dict[m]:,.0f}" if m in m_dict else ""}</div></div>'
            for m in all_months
        ])

        table_html = f"""
        <div class="excel-table-box">
            <div class="excel-table-header">Total Safe Man-hours</div>
            {month_rows_html}
            <div class="excel-table-row">
                <div class="excel-col-label excel-total-label">Total</div>
                <div class="excel-col-value excel-total-value">{data['safe_man_hours']['total']:,.0f}</div>
            </div>
        </div>
        <div style="margin-top:10px; border:1px solid #cbd5e1; border-radius:8px; overflow:hidden; display:flex; box-shadow:0 2px 4px rgba(0,0,0,0.04);">
            <div style="background:#94a3b8; color:#0f2438; padding:9px 14px; font-weight:700; font-size:12px; border-right:1px solid #cbd5e1; flex:1.5; display:flex; align-items:center;">
                Man-hours upto december 2025
            </div>
            <div style="background:#ffffff; color:#0f172a; padding:9px 14px; font-weight:800; font-size:15px; flex:1; text-align:center; display:flex; align-items:center; justify-content:center;">
                {data['safe_man_hours']['prior']:,.0f}
            </div>
        </div>
        """
        render_html(table_html)

    with col_c_hours:
        st.markdown('<div class="section-title">📊 Safe Man-Hours Executive Performance & Trajectory</div>', unsafe_allow_html=True)

        # Active Data Calculation
        active_m = [m for m in all_months if m in m_dict]
        active_v = [m_dict[m] for m in active_m]
        max_h = max(active_v) if active_v else 0
        peak_month = active_m[active_v.index(max_h)] if active_v else "N/A"
        avg_v = sum(active_v) / len(active_v) if active_v else 0

        # Sleek Metric Badges above chart
        st.markdown(f"""
        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:12px;">
            <div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:6px; padding:6px 12px; font-size:12px; font-weight:700; color:#0369a1;">
                🏆 Peak Month: {peak_month} ({max_h:,.0f} hrs)
            </div>
            <div style="background:#fefce8; border:1px solid #fef08a; border-radius:6px; padding:6px 12px; font-size:12px; font-weight:700; color:#854d0e;">
                📈 Monthly Average: {avg_v:,.0f} hrs/mo
            </div>
            <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:6px; padding:6px 12px; font-size:12px; font-weight:700; color:#15803d;">
                🛡️ Milestone: {data['safe_man_hours']['total']:,.0f} hrs (Zero LTI)
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Tab views: Monthly Bar vs Cumulative S-Curve
        tab_chart_bar, tab_chart_cumul = st.tabs(["📊 Monthly Hours & Benchmark", "📈 Cumulative 6.2M Trajectory"])

        with tab_chart_bar:
            # Color coding: Peak gets glowing electric cyan, others get rich royal blue
            bar_palette = []
            for v in active_v:
                if v == max_h:
                    bar_palette.append("#0ea5e9") # Vibrant Cyan Peak
                elif v < avg_v:
                    bar_palette.append("#475569") # Subdued Slate for lower months
                else:
                    bar_palette.append("#0284c7") # Modern Deep Sky Blue

            fig_hours_bar = go.Figure()

            # Main Bars
            fig_hours_bar.add_trace(go.Bar(
                x=active_m,
                y=active_v,
                text=[f"<b>{v:,.0f}</b>" for v in active_v],
                textposition='outside',
                textfont=dict(size=12, color='#0f172a', family='Inter, sans-serif'),
                marker=dict(
                    color=bar_palette,
                    line=dict(color='#0f172a', width=1.5)
                ),
                width=0.62,
                name="Monthly Safe Hours",
                hovertemplate="<b>%{x}</b><br>Safe Hours: <b>%{y:,.0f} hrs</b><br>Status: Zero LTI Recorded<extra></extra>"
            ))

            # Benchmark Average Line
            fig_hours_bar.add_trace(go.Scatter(
                x=active_m,
                y=[avg_v] * len(active_m),
                mode='lines',
                name=f"Monthly Average ({avg_v/1000:.0f}k hrs)",
                line=dict(color='#f59e0b', width=2.5, dash='dash'),
                hovertemplate="Monthly Benchmark Average: <b>%{y:,.0f} hrs</b><extra></extra>"
            ))

            # Peak Month Annotation Callout
            fig_hours_bar.add_annotation(
                x=peak_month,
                y=max_h,
                text="<b>🏆 Peak Record</b>",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1.5,
                arrowcolor="#0ea5e9",
                ax=0,
                ay=-35,
                bgcolor="#ffffff",
                bordercolor="#0ea5e9",
                borderwidth=1.5,
                borderpad=4,
                font=dict(size=11, color="#0369a1", family='Inter, sans-serif')
            )

            fig_hours_bar.update_layout(
                title=dict(
                    text="<b>Safe Man-Hours Performance (2026)</b>",
                    font=dict(size=18, color='#0d233a', family='Inter, sans-serif'),
                    x=0.5,
                    xanchor='center'
                ),
                height=400,
                margin=dict(l=40, r=20, t=60, b=30),
                yaxis=dict(
                    range=[0, 500000],
                    tickvals=[0, 100000, 200000, 300000, 400000, 500000],
                    gridcolor='#e2e8f0',
                    tickfont=dict(size=12, color='#64748b'),
                    tickformat=",d"
                ),
                xaxis=dict(
                    tickfont=dict(size=13, color='#0f172a', family='Inter, sans-serif', weight='bold')
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=11)
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_hours_bar, use_container_width=True)

        with tab_chart_cumul:
            # Cumulative safe hours progression
            prior = data['safe_man_hours']['prior']
            cumul_hours = []
            curr_sum = prior
            for v in active_v:
                curr_sum += v
                cumul_hours.append(curr_sum)

            # Smart text positioning to prevent clipping at edges:
            # Jan (first) -> 'top right', Sep (last) -> 'top left', Others -> 'top center'
            cumul_text_positions = [
                'top right' if i == 0 else ('top left' if i == len(active_m) - 1 else 'top center')
                for i in range(len(active_m))
            ]

            fig_cumul = go.Figure()
            fig_cumul.add_trace(go.Scatter(
                x=active_m,
                y=cumul_hours,
                mode='lines+markers+text',
                text=[f"<b>{c/1000000:.2f}M</b>" for c in cumul_hours],
                textposition=cumul_text_positions,
                textfont=dict(size=12, color='#0f172a', family='Inter, sans-serif'),
                cliponaxis=False,
                line=dict(color='#0284c7', width=3.5),
                marker=dict(size=9, color='#0369a1', line=dict(color='#ffffff', width=2)),
                fill='tozeroy',
                fillcolor='rgba(2, 132, 199, 0.1)',
                name="Cumulative Total",
                hovertemplate="Month: <b>%{x}</b><br>Cumulative Safe Hours: <b>%{y:,.0f} hrs</b><extra></extra>"
            ))

            fig_cumul.update_layout(
                title=dict(
                    text="<b>Cumulative Safe Man-Hours Trajectory (Zero LTI)</b>",
                    font=dict(size=18, color='#0d233a', family='Inter, sans-serif'),
                    x=0.5,
                    xanchor='center'
                ),
                height=400,
                margin=dict(l=65, r=65, t=55, b=35),
                yaxis=dict(
                    range=[2600000, 6950000],
                    tickformat=",.0f",
                    gridcolor='#e2e8f0',
                    tickfont=dict(size=12, color='#64748b')
                ),
                xaxis=dict(
                    tickfont=dict(size=13, color='#0f172a', family='Inter, sans-serif', weight='bold')
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_cumul, use_container_width=True)

    # Secondary Row: Safe Man-hours vs Daily Manpower Dynamics
    st.markdown('<div class="section-card"><div class="section-title">⏱️ Safe Man-Hours vs Average Daily Workforce Trend</div>', unsafe_allow_html=True)
    m_power = data['manpower']['monthly']
    active_months = [m for m in all_months if m in m_dict]
    active_hours = [m_dict[m] for m in active_months]
    active_power = [m_power.get(m, 0) for m in active_months]

    fig_dual_wf = go.Figure()
    fig_dual_wf.add_trace(go.Bar(
        x=active_months,
        y=active_hours,
        name="Monthly Safe Man-Hours",
        marker_color="#38bdf8",
        opacity=0.85,
        yaxis="y1"
    ))
    fig_dual_wf.add_trace(go.Scatter(
        x=active_months,
        y=active_power,
        name="Average Daily Manpower",
        mode="lines+markers",
        line=dict(color="#f97316", width=3),
        marker=dict(size=8, color="#ea580c"),
        yaxis="y2"
    ))
    fig_dual_wf.update_layout(
        height=320,
        margin=dict(l=40, r=40, t=20, b=25),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Safe Man-Hours", side="left", gridcolor="#f1f5f9"),
        yaxis2=dict(title="Daily Manpower", side="right", overlaying="y", showgrid=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified"
    )
    st.plotly_chart(fig_dual_wf, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================================
# 📈 PAGE: MONTHLY KPI & SCORES (MATCHING USER'S EXACT EXCEL & CHART)
# =========================================================================
elif st.session_state.active_page == "KPIs":
    st.markdown("## 📈 HSE Monthly KPI Performance & Trends")
    st.caption("Month-by-month KPI and performance index analysis against the 90% project baseline")

    # 1. TOP 6 EXECUTIVE METRIC CARDS (COVERING BOTH KPI & PSI/PCI)
    kp1, kp2, kp3, kp4, kp5, kp6 = st.columns(6)
    with kp1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Overall KPI Avg</div>
            <div class="kpi-value">{data['kpi_avg']*100:.0f}%</div>
            <span class="kpi-badge badge-warning">Target: 90%</span>
            <div class="metric-sub">Variance: -7.0%</div>
        </div>
        """, unsafe_allow_html=True)
    with kp2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Overall PSI/PCI Avg</div>
            <div class="kpi-value" style="color:#8b5cf6;">65.4%</div>
            <span class="kpi-badge badge-info">Target: 90%</span>
            <div class="metric-sub">Process Safety</div>
        </div>
        """, unsafe_allow_html=True)
    with kp3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Baseline Benchmark</div>
            <div class="kpi-value" style="color:#0284c7;">90%</div>
            <span class="kpi-badge badge-info">Standard Target</span>
            <div class="metric-sub">Fixed Contract KPI</div>
        </div>
        """, unsafe_allow_html=True)
    with kp4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Peak KPI Month</div>
            <div class="kpi-value" style="color:#15803d;">93%</div>
            <span class="kpi-badge badge-success">May 2026</span>
            <div class="metric-sub">+3.0% Above Target</div>
        </div>
        """, unsafe_allow_html=True)
    with kp5:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Peak PSI/PCI Month</div>
            <div class="kpi-value" style="color:#15803d;">75%</div>
            <span class="kpi-badge badge-success">Sep 2026</span>
            <div class="metric-sub">Record Process High</div>
        </div>
        """, unsafe_allow_html=True)
    with kp6:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">PSI/PCI Trend</div>
            <div class="kpi-value" style="color:#059669;">+15%</div>
            <span class="kpi-badge badge-success">58% &rarr; 75%</span>
            <div class="metric-sub">+1.8% Monthly Gain</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. MAIN SECTION: EXACT EXCEL TABLE (IMAGE 1) & EXACT LINE CHART (IMAGE 2)
    col_kpi_t, col_kpi_c = st.columns([1, 1.45])

    # Left Column: Exact HSE Monthly KPI Table
    with col_kpi_t:
        st.markdown('<div class="section-title">📋 HSE Monthly KPI Registry (Excel Format)</div>', unsafe_allow_html=True)

        kpi_months_data = [
            ("January", "84%", "90%"),
            ("February", "81%", "90%"),
            ("March", "87%", "90%"),
            ("April", "90%", "90%"),
            ("May", "93%", "90%"),
            ("June", "85%", "90%"),
            ("July", "91%", "90%"),
            ("August", "68%", "90%"),
            ("September", "68%", "90%"),
            ("October", "", "90%")
        ]

        table_rows_html = ""
        for month_name, score_val, base_val in kpi_months_data:
            table_rows_html += f"""
            <tr style="border-bottom: 1px solid #8ea9db;">
                <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: left;">
                    {month_name}
                </td>
                <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">
                    {score_val}
                </td>
                <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">
                    {base_val}
                </td>
            </tr>
            """

        kpi_table_html = f"""
        <table style="width:100%; border-collapse:collapse; font-family:'Segoe UI', Inter, -apple-system, sans-serif; border: 2px solid #002060; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);">
            <thead>
                <tr style="background-color: #002060; color: #ffffff;">
                    <th colspan="3" style="padding: 10px 14px; font-size: 16px; font-weight: 700; text-align: center; letter-spacing: 0.5px;">
                        HSE Monthly KPI
                    </th>
                </tr>
                <tr style="background-color: #b4c6e7; color: #000000; border-top: 1px solid #8ea9db; border-bottom: 2px solid #002060;">
                    <th style="padding: 8px 12px; font-size: 14px; font-weight: 600; text-align: center; border-right: 1px solid #8ea9db; width: 44%;">Month</th>
                    <th style="padding: 8px 12px; font-size: 14px; font-weight: 600; text-align: center; border-right: 1px solid #8ea9db; width: 28%;">Score</th>
                    <th style="padding: 8px 12px; font-size: 14px; font-weight: 600; text-align: center; width: 28%;">baseline</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_html}
            </tbody>
            <tfoot>
                <tr style="background-color: #002060; color: #ffffff; border-top: 2px solid #002060;">
                    <td style="padding: 10px 12px; text-align: center; border-right: 1px solid #203764; font-weight: 700; font-size: 14px; line-height: 1.2;">
                        Overall Average<br>Score
                    </td>
                    <td style="padding: 10px 12px; text-align: center; border-right: 1px solid #203764; font-size: 16px; font-weight: 800; color: #ffffff;">
                        83%
                    </td>
                    <td style="padding: 10px 12px; text-align: center; font-size: 16px; font-weight: 800; color: #ffffff;">
                        90%
                    </td>
                </tr>
            </tfoot>
        </table>
        """
        render_html(kpi_table_html)

        # Micro summary pills
        st.markdown("""
        <div style="display:flex; justify-content:space-between; margin-top:14px; gap:8px;">
            <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:6px; padding:8px; text-align:center; flex:1;">
                <div style="font-size:10px; font-weight:600; color:#166534; text-transform:uppercase;">Above Target</div>
                <div style="font-size:15px; font-weight:800; color:#15803d;">3 Months</div>
            </div>
            <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:6px; padding:8px; text-align:center; flex:1;">
                <div style="font-size:10px; font-weight:600; color:#92400e; text-transform:uppercase;">Near Target</div>
                <div style="font-size:15px; font-weight:800; color:#b45309;">4 Months</div>
            </div>
            <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:6px; padding:8px; text-align:center; flex:1;">
                <div style="font-size:10px; font-weight:600; color:#991b1b; text-transform:uppercase;">Under Target</div>
                <div style="font-size:15px; font-weight:800; color:#dc2626;">2 Months</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Right Column: Exact Line Chart with Dotted Trendline (Image 2)
    with col_kpi_c:
        st.markdown('<div class="section-title">📈 KPI Performance Line Chart & Linear Trendline</div>', unsafe_allow_html=True)

        kpi_all_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October']
        kpi_scores = [84, 81, 87, 90, 93, 85, 91, 68, 68, None]
        kpi_baseline = [90] * 10

        # Linear trendline projection matching Excel
        val_x = [i for i, v in enumerate(kpi_scores) if v is not None]
        val_y = [v for v in kpi_scores if v is not None]
        slope, intercept = np.polyfit(val_x, val_y, 1)
        kpi_trend = [round(slope * i + intercept, 1) for i in range(len(kpi_all_months))]

        fig_kpi_chart = go.Figure()

        # 1. Target Baseline (90%)
        fig_kpi_chart.add_trace(go.Scatter(
            x=kpi_all_months,
            y=kpi_baseline,
            mode='lines',
            name='Baseline (90%)',
            line=dict(color='#10b981', width=2, dash='dash'),
            hovertemplate='Baseline Benchmark: <b>90%</b><extra></extra>'
        ))

        # 2. Red Dotted Linear Trendline (Exact from Excel Image 2)
        fig_kpi_chart.add_trace(go.Scatter(
            x=kpi_all_months,
            y=kpi_trend,
            mode='lines',
            name='Linear Trendline',
            line=dict(color='#ef4444', width=2.5, dash='dot'),
            hovertemplate='Trendline: <b>%{y:.1f}%</b><extra></extra>'
        ))

        # 3. Monthly KPI Score (Navy / Teal Line with Circles & Percentage Labels)
        fig_kpi_chart.add_trace(go.Scatter(
            x=kpi_all_months,
            y=kpi_scores,
            mode='lines+markers+text',
            name='Monthly KPI Score',
            line=dict(color='#005b82', width=3.8),
            marker=dict(size=9, color='#005b82', line=dict(color='#ffffff', width=2)),
            text=[f"<b>{s:.0f}%</b>" if s is not None else "" for s in kpi_scores],
            textposition='top center',
            textfont=dict(size=12, color='#0f172a', family='Inter, sans-serif'),
            cliponaxis=False,
            hovertemplate='<b>%{x}</b><br>KPI Score: <b>%{y}%</b><extra></extra>'
        ))

        fig_kpi_chart.update_layout(
            title=dict(
                text="<b>KPI</b>",
                font=dict(size=22, color='#0d233a', family='Inter, sans-serif'),
                x=0.5,
                xanchor='center'
            ),
            height=435,
            margin=dict(l=55, r=45, t=55, b=65),
            yaxis=dict(
                range=[0, 105],
                tickvals=[0, 20, 40, 60, 80, 100],
                ticktext=['0%', '20%', '40%', '60%', '80%', '100%'],
                gridcolor='#e2e8f0',
                tickfont=dict(size=12, color='#64748b'),
                zeroline=True,
                zerolinecolor='#94a3b8'
            ),
            xaxis=dict(
                tickangle=-45,
                tickfont=dict(size=12, color='#0f172a', family='Inter, sans-serif')
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=11)
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_kpi_chart, use_container_width=True)

    # =========================================================================
    # 🎯 SECTION 2: HSE MONTHLY PSI/PCI (MATCHING USER'S NEW IMAGES)
    # =========================================================================
    st.markdown("<div style='margin: 40px 0 28px 0; border-top: 2px dashed #cbd5e1;'></div>", unsafe_allow_html=True)
    st.markdown("### 🎯 2. HSE Monthly Process Safety Index (PSI / PCI)")
    st.caption("Month-by-month Process Safety Index performance and positive upward trajectory vs 90% target")

    col_psi_t, col_psi_c = st.columns([1, 1.45])

    # Left Column: Exact HSE Monthly PSI/PCI Table (Image 1)
    with col_psi_t:
        st.markdown('<div class="section-title">📋 HSE Monthly PSI/PCI Registry (Excel Format)</div>', unsafe_allow_html=True)

        psi_months_data = [
            ("January", "60%", "90%"),
            ("February", "58%", "90%"),
            ("March", "59%", "90%"),
            ("April", "67%", "90%"),
            ("May", "66%", "90%"),
            ("June", "67%", "90%"),
            ("July", "69%", "90%"),
            ("August", "68%", "90%"),
            ("September", "75%", "90%"),
            ("October", "", "90%")
        ]

        psi_table_rows_html = ""
        for month_name, score_val, base_val in psi_months_data:
            psi_table_rows_html += f"""
            <tr style="border-bottom: 1px solid #8ea9db;">
                <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: left;">
                    {month_name}
                </td>
                <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">
                    {score_val}
                </td>
                <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">
                    {base_val}
                </td>
            </tr>
            """

        psi_table_html = f"""
        <table style="width:100%; border-collapse:collapse; font-family:'Segoe UI', Inter, -apple-system, sans-serif; border: 2px solid #002060; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);">
            <thead>
                <tr style="background-color: #002060; color: #ffffff;">
                    <th colspan="3" style="padding: 10px 14px; font-size: 16px; font-weight: 700; text-align: center; letter-spacing: 0.5px;">
                        HSE Monthly PSI/PCI
                    </th>
                </tr>
                <tr style="background-color: #b4c6e7; color: #000000; border-top: 1px solid #8ea9db; border-bottom: 2px solid #002060;">
                    <th style="padding: 8px 12px; font-size: 14px; font-weight: 600; text-align: center; border-right: 1px solid #8ea9db; width: 44%;">Month</th>
                    <th style="padding: 8px 12px; font-size: 14px; font-weight: 600; text-align: center; border-right: 1px solid #8ea9db; width: 28%;">Score</th>
                    <th style="padding: 8px 12px; font-size: 14px; font-weight: 600; text-align: center; width: 28%;">baseline</th>
                </tr>
            </thead>
            <tbody>
                {psi_table_rows_html}
            </tbody>
            <tfoot>
                <tr style="background-color: #002060; color: #ffffff; border-top: 2px solid #002060;">
                    <td style="padding: 10px 12px; text-align: center; border-right: 1px solid #203764; font-weight: 700; font-size: 14px; line-height: 1.2;">
                        Overall Average<br>Score
                    </td>
                    <td style="padding: 10px 12px; text-align: center; border-right: 1px solid #203764; font-size: 16px; font-weight: 800; color: #ffffff;">
                        65%
                    </td>
                    <td style="padding: 10px 12px; text-align: center; font-size: 16px; font-weight: 800; color: #ffffff;">
                        90%
                    </td>
                </tr>
            </tfoot>
        </table>
        """
        render_html(psi_table_html)

        # Micro summary pills
        st.markdown("""
        <div style="display:flex; justify-content:space-between; margin-top:14px; gap:8px;">
            <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:6px; padding:8px; text-align:center; flex:1;">
                <div style="font-size:10px; font-weight:600; color:#166534; text-transform:uppercase;">Peak Month</div>
                <div style="font-size:15px; font-weight:800; color:#15803d;">75% (Sep)</div>
            </div>
            <div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:6px; padding:8px; text-align:center; flex:1;">
                <div style="font-size:10px; font-weight:600; color:#0369a1; text-transform:uppercase;">Average Score</div>
                <div style="font-size:15px; font-weight:800; color:#0284c7;">65.4%</div>
            </div>
            <div style="background:#ecfdf5; border:1px solid #a7f3d0; border-radius:6px; padding:8px; text-align:center; flex:1;">
                <div style="font-size:10px; font-weight:600; color:#047857; text-transform:uppercase;">Positive Trend</div>
                <div style="font-size:15px; font-weight:800; color:#059669;">+15% Growth</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Right Column: Exact PSI/PCI Line Chart with Upward Trendline (Image 2)
    with col_psi_c:
        st.markdown('<div class="section-title">📈 PSI/PCI Performance Line Chart & Linear Trendline</div>', unsafe_allow_html=True)

        psi_all_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October']
        psi_scores = [60, 58, 59, 67, 66, 67, 69, 68, 75, None]
        psi_baseline = [90] * 10

        # Linear trendline projection matching Excel
        p_val_x = [i for i, v in enumerate(psi_scores) if v is not None]
        p_val_y = [v for v in psi_scores if v is not None]
        p_slope, p_intercept = np.polyfit(p_val_x, p_val_y, 1)
        psi_trend = [round(p_slope * i + p_intercept, 1) for i in range(len(psi_all_months))]

        fig_psi_chart = go.Figure()

        # 1. Target Baseline (90%)
        fig_psi_chart.add_trace(go.Scatter(
            x=psi_all_months,
            y=psi_baseline,
            mode='lines',
            name='Baseline (90%)',
            line=dict(color='#10b981', width=2, dash='dash'),
            hovertemplate='Baseline Benchmark: <b>90%</b><extra></extra>'
        ))

        # 2. Red Dotted Linear Trendline (Upward slope from Excel Image 2)
        fig_psi_chart.add_trace(go.Scatter(
            x=psi_all_months,
            y=psi_trend,
            mode='lines',
            name='Linear Trendline',
            line=dict(color='#ef4444', width=2.5, dash='dot'),
            hovertemplate='Trendline: <b>%{y:.1f}%</b><extra></extra>'
        ))

        # 3. Monthly PSI/PCI Score (Navy / Teal Line with Circles & Percentage Labels)
        fig_psi_chart.add_trace(go.Scatter(
            x=psi_all_months,
            y=psi_scores,
            mode='lines+markers+text',
            name='PSI/PCI Score',
            line=dict(color='#005b82', width=3.8),
            marker=dict(size=9, color='#005b82', line=dict(color='#ffffff', width=2)),
            text=[f"<b>{s:.0f}%</b>" if s is not None else "" for s in psi_scores],
            textposition='top center',
            textfont=dict(size=12, color='#0f172a', family='Inter, sans-serif'),
            cliponaxis=False,
            hovertemplate='<b>%{x}</b><br>PSI/PCI Score: <b>%{y}%</b><extra></extra>'
        ))

        fig_psi_chart.update_layout(
            title=dict(
                text="<b>PSI/PCI</b>",
                font=dict(size=22, color='#0d233a', family='Inter, sans-serif'),
                x=0.5,
                xanchor='center'
            ),
            height=435,
            margin=dict(l=55, r=45, t=55, b=65),
            yaxis=dict(
                range=[0, 95],
                tickvals=[0, 20, 40, 60, 80],
                ticktext=['0%', '20%', '40%', '60%', '80%'],
                gridcolor='#e2e8f0',
                tickfont=dict(size=12, color='#64748b'),
                zeroline=True,
                zerolinecolor='#94a3b8'
            ),
            xaxis=dict(
                tickangle=-45,
                tickfont=dict(size=12, color='#0f172a', family='Inter, sans-serif')
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=11)
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_psi_chart, use_container_width=True)

    # =========================================================================
    # ⚖️ SECTION 3: COMPARATIVE ANALYTICS & INSIGHTS
    # =========================================================================
    st.markdown("<div style='margin: 40px 0 28px 0; border-top: 2px dashed #cbd5e1;'></div>", unsafe_allow_html=True)
    st.markdown("### ⚖️ 3. Comparative Index Analytics & Performance Drivers")

    tab_compare, tab_var, tab_insights = st.tabs([
        "📊 Dual Comparison: KPI vs PSI/PCI",
        "🎯 Monthly Target Variance (Delta ±%)",
        "📋 Executive Observations & Action Plan"
    ])

    with tab_compare:
        st.markdown('<div class="section-title">Monthly KPI vs PSI/PCI Index Comparison</div>', unsafe_allow_html=True)

        fig_dual_comp = go.Figure()
        fig_dual_comp.add_trace(go.Bar(
            x=kpi_all_months[:9],
            y=[s for s in kpi_scores if s is not None],
            name="Monthly KPI Score",
            marker_color="#005b82",
            text=[f"{s}%" for s in kpi_scores if s is not None],
            textposition="outside"
        ))
        fig_dual_comp.add_trace(go.Bar(
            x=psi_all_months[:9],
            y=[s for s in psi_scores if s is not None],
            name="PSI / PCI Score",
            marker_color="#8b5cf6",
            text=[f"{s}%" for s in psi_scores if s is not None],
            textposition="outside"
        ))
        fig_dual_comp.add_trace(go.Scatter(
            x=kpi_all_months[:9],
            y=[90] * 9,
            name="Baseline Target (90%)",
            mode="lines",
            line=dict(color="#ef4444", width=2, dash="dash")
        ))
        fig_dual_comp.update_layout(
            barmode="group",
            height=320,
            yaxis=dict(range=[0, 110], title="Score (%)", gridcolor="#e2e8f0"),
            xaxis=dict(tickfont=dict(size=12, color="#0f172a")),
            margin=dict(l=40, r=40, t=30, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_dual_comp, use_container_width=True)

    with tab_var:
        st.markdown('<div class="section-title">Monthly KPI Delta vs 90% Target Benchmark</div>', unsafe_allow_html=True)

        kpi_active = [s for s in kpi_scores if s is not None]
        kpi_m_active = kpi_all_months[:len(kpi_active)]
        variances = [s - 90 for s in kpi_active]
        var_colors = ['#15803d' if v >= 0 else ('#f59e0b' if v >= -10 else '#dc2626') for v in variances]

        fig_var = go.Figure()
        fig_var.add_trace(go.Bar(
            x=kpi_m_active,
            y=variances,
            text=[f"{v:+.0f}%" for v in variances],
            textposition='outside',
            textfont=dict(size=12, family='Inter, sans-serif', weight='bold'),
            marker=dict(color=var_colors, line=dict(color='#0f172a', width=1)),
            width=0.55,
            name="KPI Variance vs 90%",
            customdata=kpi_active,
            hovertemplate='<b>%{x}</b><br>KPI Score: <b>%{customdata}%</b><br>Target: <b>90%</b><br>Variance: <b>%{y:+.0f}%</b><extra></extra>'
        ))
        fig_var.update_layout(
            height=280,
            margin=dict(l=40, r=40, t=20, b=30),
            yaxis=dict(
                title="Variance (±%)",
                range=[-28, 10],
                zeroline=True,
                zerolinecolor='#0f172a',
                zerolinewidth=2,
                gridcolor='#e2e8f0'
            ),
            xaxis=dict(tickfont=dict(size=12, color='#0f172a')),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_var, use_container_width=True)

        # Second Diverging Variance Chart: PSI/PCI Delta vs 90% Target
        st.markdown("<div style='margin: 28px 0 16px 0; border-top: 1px dashed #cbd5e1;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Monthly PSI/PCI Delta vs 90% Target Benchmark</div>', unsafe_allow_html=True)

        psi_active = [s for s in psi_scores if s is not None]
        psi_m_active = psi_all_months[:len(psi_active)]
        psi_variances = [s - 90 for s in psi_active]
        psi_var_colors = ['#15803d' if v >= 0 else ('#f59e0b' if v >= -20 else '#dc2626') for v in psi_variances]

        fig_psi_var = go.Figure()
        fig_psi_var.add_trace(go.Bar(
            x=psi_m_active,
            y=psi_variances,
            text=[f"{v:+.0f}%" for v in psi_variances],
            textposition='outside',
            textfont=dict(size=12, family='Inter, sans-serif', weight='bold'),
            marker=dict(color=psi_var_colors, line=dict(color='#0f172a', width=1)),
            width=0.55,
            name="PSI/PCI Variance vs 90%",
            customdata=psi_active,
            hovertemplate='<b>%{x}</b><br>PSI/PCI Score: <b>%{customdata}%</b><br>Target: <b>90%</b><br>Variance: <b>%{y:+.0f}%</b><extra></extra>'
        ))
        fig_psi_var.update_layout(
            height=280,
            margin=dict(l=40, r=40, t=20, b=30),
            yaxis=dict(
                title="Variance (±%)",
                range=[-38, 5],
                zeroline=True,
                zerolinecolor='#0f172a',
                zerolinewidth=2,
                gridcolor='#e2e8f0'
            ),
            xaxis=dict(tickfont=dict(size=12, color='#0f172a')),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_psi_var, use_container_width=True)

    with tab_insights:
        st.markdown('<div class="section-title">Executive HSE Observations & Corrective Actions</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:16px;">
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:16px;">
                <h4 style="margin:0 0 8px 0; color:#0f172a; font-size:14px;">📈 Upward Process Safety Trend (PSI / PCI)</h4>
                <p style="margin:0; font-size:12.5px; color:#475569; line-height:1.5;">
                    Process Safety Index showed sustained month-on-month improvement, climbing from <b>58% in February</b> to a peak of <b>75% in September (+15% gain)</b>, indicating strengthening process safety controls and barrier health.
                </p>
            </div>
            <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:16px;">
                <h4 style="margin:0 0 8px 0; color:#92400e; font-size:14px;">☀️ Summer Protocol Realignment</h4>
                <p style="margin:0; font-size:12.5px; color:#475569; line-height:1.5;">
                    While general HSE KPI dipped during August & September due to heat stress stand-downs, PSI/PCI surged to its highest mark (75%), demonstrating that high-risk process controls remained robust.
                </p>
            </div>
            <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:16px;">
                <h4 style="margin:0 0 8px 0; color:#166534; font-size:14px;">🎯 Q4 Target Alignment</h4>
                <p style="margin:0; font-size:12.5px; color:#475569; line-height:1.5;">
                    Current momentum aims to bring both indices above the <b>90% baseline</b> in Q4 through accelerated inspection closures and continued subcontractor safety leadership.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)


# =========================================================================
# 🎓 PAGE: DEDICATED TRAINING RATE & PERFORMANCE (EXACT USER IMAGES)
# =========================================================================
elif st.session_state.active_page == "Training":
    st.markdown("## 🎓 HSE Training Execution & Attendees Analysis")
    st.caption("Month-by-month HSE training sessions, workforce attendance, and target completion rate")

    # 1. TOP 5 EXECUTIVE METRIC CARDS
    tr1, tr2, tr3, tr4, tr5 = st.columns(5)
    with tr1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Execution Rate</div>
            <div class="kpi-value" style="color:#dc2626;">29%</div>
            <span class="kpi-badge badge-danger">5 of 17 Done</span>
            <div class="metric-sub">Critical Target Deficit</div>
        </div>
        """, unsafe_allow_html=True)
    with tr2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Conducted Sessions</div>
            <div class="kpi-value" style="color:#0284c7;">5</div>
            <span class="kpi-badge badge-info">Jan, Jul, Sep</span>
            <div class="metric-sub">Formal HSE Courses</div>
        </div>
        """, unsafe_allow_html=True)
    with tr3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Target Sessions</div>
            <div class="kpi-value">17</div>
            <span class="kpi-badge badge-info">Annual Plan</span>
            <div class="metric-sub">12 Sessions Remaining</div>
        </div>
        """, unsafe_allow_html=True)
    with tr4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Total Attendees</div>
            <div class="kpi-value" style="color:#15803d;">62</div>
            <span class="kpi-badge badge-success">Workers Certified</span>
            <div class="metric-sub">Peak: 30 in July</div>
        </div>
        """, unsafe_allow_html=True)
    with tr5:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Average Attendance</div>
            <div class="kpi-value">12.4</div>
            <span class="kpi-badge badge-info">Attendees / Session</span>
            <div class="metric-sub">Site Engagement</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. MAIN SECTION: EXACT EXCEL TABLE (IMAGE 1) & EXACT BAR CHART (IMAGE 2)
    col_tr_t, col_tr_c = st.columns([1, 1.45])

    # Left Column: Exact Training Rate Table (Image 1)
    with col_tr_t:
        st.markdown('<div class="section-title">📋 Training Rate Registry (Excel Format)</div>', unsafe_allow_html=True)

        training_rows_data = [
            ("Jan", "2", "15", "2"),
            ("Feb", "", "", "1"),
            ("Mar", "", "", "1"),
            ("Apr", "", "", "1"),
            ("May", "", "", "1"),
            ("Jun", "", "", "1"),
            ("Jul", "2", "30", "2"),
            ("Aug", "", "", "2"),
            ("Sep", "1", "17", "2"),
            ("Oct", "", "", "2"),
            ("Nov", "", "", "2")
        ]

        t_rows_html = ""
        for m_name, t_num, att_num, tgt_num in training_rows_data:
            t_rows_html += f"""
            <tr style="border-bottom: 1px solid #002060;">
                <td style="padding: 6px 12px; background-color: #002060; color: #ffffff; font-weight: 700; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">
                    {m_name}
                </td>
                <td style="padding: 6px 12px; background-color: #9bbcdb; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #002060; text-align: center;">
                    {t_num}
                </td>
                <td style="padding: 6px 12px; background-color: #9bbcdb; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #002060; text-align: center;">
                    {att_num}
                </td>
                <td style="padding: 6px 12px; background-color: #9bbcdb; color: #0d233a; font-weight: 600; font-size: 13.5px; text-align: center;">
                    {tgt_num}
                </td>
            </tr>
            """

        training_table_html = f"""
        <table style="width:100%; border-collapse:collapse; font-family:'Segoe UI', Inter, -apple-system, sans-serif; border: 2px solid #002060; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);">
            <thead>
                <tr style="background-color: #002060; color: #ffffff;">
                    <th colspan="4" style="padding: 10px 14px; font-size: 16px; font-weight: 700; text-align: center; letter-spacing: 0.5px;">
                        Training Rate
                    </th>
                </tr>
                <tr style="background-color: #9bbcdb; color: #000000; border-top: 1px solid #002060; border-bottom: 2px solid #002060;">
                    <th style="padding: 8px 10px; font-size: 13.5px; font-weight: 700; text-align: center; border-right: 1px solid #002060; width: 22%; background-color: #002060; color: #ffffff;">Month</th>
                    <th style="padding: 8px 10px; font-size: 13.5px; font-weight: 700; text-align: center; border-right: 1px solid #002060; width: 26%;"># Tainings</th>
                    <th style="padding: 8px 10px; font-size: 13.5px; font-weight: 700; text-align: center; border-right: 1px solid #002060; width: 26%;"># Attendees</th>
                    <th style="padding: 8px 10px; font-size: 13.5px; font-weight: 700; text-align: center; width: 26%;">Target (training)</th>
                </tr>
            </thead>
            <tbody>
                {t_rows_html}
                <tr style="background-color: #002060; border-top: 2px solid #002060; border-bottom: 2px solid #002060;">
                    <td style="padding: 8px 12px; text-align: center; border-right: 1px solid #8ea9db; font-weight: 700; font-size: 14px; color: #ffffff;">
                        Total
                    </td>
                    <td style="padding: 8px 12px; text-align: center; border-right: 1px solid #002060; font-size: 15px; font-weight: 800; background-color: #9bbcdb; color: #0d233a;">
                        5
                    </td>
                    <td style="padding: 8px 12px; text-align: center; border-right: 1px solid #002060; font-size: 15px; font-weight: 800; background-color: #9bbcdb; color: #0d233a;">
                        62
                    </td>
                    <td style="padding: 8px 12px; text-align: center; font-size: 15px; font-weight: 800; background-color: #9bbcdb; color: #0d233a;">
                        17
                    </td>
                </tr>
            </tbody>
            <tfoot>
                <tr style="border-top: 2px solid #002060;">
                    <td style="padding: 10px 12px; text-align: center; border-right: 1px solid #002060; font-weight: 800; font-size: 15px; background-color: #c59b6d; color: #002060;">
                        Rate
                    </td>
                    <td colspan="3" style="padding: 10px 12px; text-align: center; font-size: 18px; font-weight: 800; background-color: #ff0000; color: #000000;">
                        29%
                    </td>
                </tr>
            </tfoot>
        </table>
        """
        render_html(training_table_html)

        # Micro summary pills
        st.markdown("""
        <div style="display:flex; justify-content:space-between; margin-top:14px; gap:8px;">
            <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:6px; padding:8px; text-align:center; flex:1;">
                <div style="font-size:10px; font-weight:600; color:#991b1b; text-transform:uppercase;">Training Deficit</div>
                <div style="font-size:15px; font-weight:800; color:#dc2626;">-12 Sessions</div>
            </div>
            <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:6px; padding:8px; text-align:center; flex:1;">
                <div style="font-size:10px; font-weight:600; color:#166534; text-transform:uppercase;">Peak Attendance</div>
                <div style="font-size:15px; font-weight:800; color:#15803d;">30 in July</div>
            </div>
            <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:6px; padding:8px; text-align:center; flex:1;">
                <div style="font-size:10px; font-weight:600; color:#92400e; text-transform:uppercase;">Target Plan</div>
                <div style="font-size:15px; font-weight:800; color:#b45309;">17 Sessions</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Right Column: Exact Training Bar Chart (Image 2)
    with col_tr_c:
        st.markdown('<div class="section-title">📊 Training Execution Bar Chart (Image Format)</div>', unsafe_allow_html=True)

        t_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
        t_values = [2, 0, 0, 0, 0, 0, 2, 0, 1, 0, 0]
        t_targets = [2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2]

        fig_train_bar = go.Figure()

        # Main Bars matching Image 2
        fig_train_bar.add_trace(go.Bar(
            x=t_months,
            y=t_values,
            text=[str(v) if v > 0 else "" for v in t_values],
            textposition='outside',
            textfont=dict(size=14, color='#0d233a', family='Inter, sans-serif', weight='bold'),
            marker=dict(
                color='#005a87',
                line=dict(color='#003853', width=1.5)
            ),
            width=0.38,
            name="Conducted Sessions",
            hovertemplate="<b>%{x}</b><br>Trainings Conducted: <b>%{y}</b><extra></extra>"
        ))

        # Target Reference Line
        fig_train_bar.add_trace(go.Scatter(
            x=t_months,
            y=t_targets,
            mode='lines',
            name="Monthly Target",
            line=dict(color='#ef4444', width=2, dash='dash'),
            hovertemplate="Monthly Target: <b>%{y} sessions</b><extra></extra>"
        ))

        fig_train_bar.update_layout(
            title=dict(
                text="<b>Training</b>",
                font=dict(size=22, color='#0d233a', family='Inter, sans-serif'),
                x=0.5,
                xanchor='center'
            ),
            height=435,
            margin=dict(l=45, r=35, t=55, b=55),
            yaxis=dict(
                range=[0, 2.3],
                tickvals=[0, 0.5, 1, 1.5, 2],
                ticktext=['0', '0.5', '1', '1.5', '2'],
                gridcolor='#e2e8f0',
                tickfont=dict(size=12, color='#64748b'),
                zeroline=True,
                zerolinecolor='#94a3b8'
            ),
            xaxis=dict(
                tickfont=dict(size=13, color='#0f172a', family='Inter, sans-serif')
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=11)
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_train_bar, use_container_width=True)

    # 3. SECONDARY ANALYTICS: ATTENDEES & GAP RECOVERY
    st.markdown("<br>", unsafe_allow_html=True)
    tab_att, tab_gap, tab_plan = st.tabs([
        "👥 Workforce Attendance Breakdown (62 Attendees)",
        "⚠️ Training Gap & Deficit Analysis",
        "🚀 Q4 Accelerated Training Schedule"
    ])

    with tab_att:
        st.markdown('<div class="section-title">Attendees Breakdown by Session</div>', unsafe_allow_html=True)
        active_t_m = ["Jan", "Jul", "Sep"]
        active_t_att = [15, 30, 17]
        active_t_ses = [2, 2, 1]

        fig_att = go.Figure()
        fig_att.add_trace(go.Bar(
            x=active_t_m,
            y=active_t_att,
            text=[f"<b>{a} workers</b><br>({s} sessions)" for a, s in zip(active_t_att, active_t_ses)],
            textposition='outside',
            textfont=dict(size=12, family='Inter, sans-serif'),
            marker_color="#0284c7",
            width=0.45,
            name="Attendees"
        ))
        fig_att.update_layout(
            height=280,
            yaxis=dict(range=[0, 38], title="Workers Attended", gridcolor="#e2e8f0"),
            xaxis=dict(tickfont=dict(size=13, color="#0f172a")),
            margin=dict(l=40, r=40, t=25, b=25),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_att, use_container_width=True)

    with tab_gap:
        st.markdown('<div class="section-title">Cumulative Target vs Actual Sessions</div>', unsafe_allow_html=True)
        cum_targets = []
        cum_actuals = []
        tot_tgt = 0
        tot_act = 0
        for m, t, a in zip(t_months, t_targets, t_values):
            tot_tgt += t
            tot_act += a
            cum_targets.append(tot_tgt)
            cum_actuals.append(tot_act)

        fig_gap = go.Figure()
        fig_gap.add_trace(go.Scatter(
            x=t_months,
            y=cum_targets,
            mode='lines+markers',
            name="Target Cumulative (17)",
            line=dict(color="#ef4444", width=3, dash="dash")
        ))
        fig_gap.add_trace(go.Scatter(
            x=t_months,
            y=cum_actuals,
            mode='lines+markers',
            name="Actual Cumulative (5)",
            line=dict(color="#10b981", width=3)
        ))
        fig_gap.update_layout(
            height=280,
            yaxis=dict(title="Sessions", gridcolor="#e2e8f0"),
            xaxis=dict(tickfont=dict(size=12, color="#0f172a")),
            margin=dict(l=40, r=40, t=25, b=25),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_gap, use_container_width=True)

    with tab_plan:
        st.markdown('<div class="section-title">HSE Training Recovery Roadmap (Target: 100% Compliance)</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:16px;">
            <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:16px;">
                <h4 style="margin:0 0 8px 0; color:#991b1b; font-size:14px;">⚠️ Current Execution Status (29%)</h4>
                <p style="margin:0; font-size:12.5px; color:#475569; line-height:1.5;">
                    Only <b>5 out of 17 planned training sessions</b> have been executed YTD, leaving a backlog of <b>12 sessions</b> across working at heights, confined space, and electrical safety.
                </p>
            </div>
            <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:16px;">
                <h4 style="margin:0 0 8px 0; color:#92400e; font-size:14px;">📅 Q4 Acceleration Schedule</h4>
                <p style="margin:0; font-size:12.5px; color:#475569; line-height:1.5;">
                    Scheduled 6 intensive weekend & batch training modules in October and November to cover high-risk operational competencies before project commissioning phases.
                </p>
            </div>
            <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:16px;">
                <h4 style="margin:0 0 8px 0; color:#166534; font-size:14px;">🎯 Subcontractor Mandate</h4>
                <p style="margin:0; font-size:12.5px; color:#475569; line-height:1.5;">
                    All subcontractor foremen and frontline supervisors must produce valid training passports and attendance slips before PTW authorization.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)


# =========================================================================
# 🎯 PAGE: DEDICATED SAFETY FREQUENCY RATES (LTIFR & TRIR - EXACT USER IMAGES)
# =========================================================================
elif st.session_state.active_page == "Rates":
    st.markdown("## 🎯 Safety Frequency Rates (LTIFR & TRIR)")
    st.caption("Lost Time Injury Frequency Rate & Total Recordable Incident Rate performance indices against international benchmarks")

    # 1. TOP SECTION: EXACT STATUS & RATING CARDS (IMAGE 3)
    c_rating_left, c_rating_right = st.columns(2)
    with c_rating_left:
        ltifr_card_html = """
        <div style="border: 2.5px solid #000000; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.06); margin-bottom: 20px;">
            <div style="background-color: #8fa0b5; color: #002060; font-weight: 800; font-size: 22px; text-align: center; padding: 12px; border-bottom: 2px solid #000000; letter-spacing: 0.5px;">
                LTIFR
            </div>
            <div style="background-color: #002060; color: #ffffff; font-weight: 800; font-size: 46px; text-align: center; padding: 18px; border-bottom: 2px solid #000000; font-family: 'Segoe UI', Inter, sans-serif;">
                0.00
            </div>
            <div style="background-color: #ffffff; color: #000000; font-weight: 700; font-size: 28px; text-align: center; padding: 14px; font-family: 'Times New Roman', Georgia, serif;">
                Excellent
            </div>
        </div>
        """
        render_html(ltifr_card_html)

    with c_rating_right:
        trir_card_html = """
        <div style="border: 2.5px solid #000000; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.06); margin-bottom: 20px;">
            <div style="background-color: #8fa0b5; color: #002060; font-weight: 800; font-size: 22px; text-align: center; padding: 12px; border-bottom: 2px solid #000000; letter-spacing: 0.5px;">
                TRIR
            </div>
            <div style="background-color: #002060; color: #ffffff; font-weight: 800; font-size: 46px; text-align: center; padding: 18px; border-bottom: 2px solid #000000; font-family: 'Segoe UI', Inter, sans-serif;">
                0.26
            </div>
            <div style="background-color: #ffffff; color: #000000; font-weight: 700; font-size: 28px; text-align: center; padding: 14px; font-family: 'Times New Roman', Georgia, serif;">
                Good
            </div>
        </div>
        """
        render_html(trir_card_html)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. MAIN ROW: EXACT TABLE (IMAGE 1) & EXACT SPEEDOMETER GAUGES (IMAGE 2)
    col_rate_t, col_rate_g = st.columns([1, 1.45])

    # Left Column: Exact Table (Image 1)
    with col_rate_t:
        st.markdown('<div class="section-title">📋 Safety Frequency Rates Registry (Excel Format)</div>', unsafe_allow_html=True)

        rate_table_html = """
        <table style="width: 100%; border-collapse: collapse; border: 2.5px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08); border-radius: 4px; overflow: hidden;">
            <tbody>
                <tr style="border-bottom: 2px solid #000000;">
                    <td style="padding: 14px 18px; background-color: #002060; color: #ffffff; font-weight: 800; font-size: 20px; border-right: 2px solid #000000; width: 50%;">
                        LTIFR
                    </td>
                    <td style="padding: 14px 18px; background-color: #196b24; color: #ffffff; font-weight: 800; font-size: 22px; text-align: center; width: 50%;">
                        0.00
                    </td>
                </tr>
                <tr>
                    <td style="padding: 14px 18px; background-color: #002060; color: #ffffff; font-weight: 800; font-size: 20px; border-right: 2px solid #000000;">
                        TRIR
                    </td>
                    <td style="padding: 14px 18px; background-color: #4ea72e; color: #ffffff; font-weight: 800; font-size: 22px; text-align: center;">
                        0.26
                    </td>
                </tr>
            </tbody>
        </table>
        """
        render_html(rate_table_html)

        # Mathematical Formula Explanations
        st.markdown("""
        <div style="margin-top: 18px; display: flex; flex-direction: column; gap: 12px;">
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 14px;">
                <div style="font-size: 11px; font-weight: 700; color: #166534; text-transform: uppercase;">LTIFR Mathematical Formula</div>
                <div style="font-size: 13px; color: #0f172a; margin-top: 4px; font-family: 'Consolas', monospace; font-weight: 600;">
                    (0 LTI Cases &times; 200,000) &divide; 6,201,138 hrs = <b>0.000</b>
                </div>
                <div style="font-size: 11.5px; color: #15803d; margin-top: 4px;">
                    🏆 Zero lost time injuries recorded across 6.2 Million cumulative man-hours.
                </div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px;">
                <div style="font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase;">TRIR Mathematical Formula</div>
                <div style="font-size: 13px; color: #0f172a; margin-top: 4px; font-family: 'Consolas', monospace; font-weight: 600;">
                    (8 Recordable Cases &times; 200,000) &divide; 6,201,138 hrs = <b>0.258 (~0.26)</b>
                </div>
                <div style="font-size: 11.5px; color: #475569; margin-top: 4px;">
                    ✅ Safely below international benchmark target threshold (&le; 0.50).
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Right Column: Exact Semicircular Speedometer Gauges (Image 2)
    with col_rate_g:
        st.markdown('<div class="section-title">📊 Safety Rate Speedometer Gauges (Image Format)</div>', unsafe_allow_html=True)

        sg1, sg2 = st.columns(2)
        with sg1:
            fig_speedo_lti = make_speedometer(
                title="LTIFR",
                slice_vals=[0.05, 0.45, 0.50, 1.00],
                slice_colors=['#196b24', '#4ea72e', '#ffc000', '#ff0000'],
                needle_frac=0.01
            )
            st.plotly_chart(fig_speedo_lti, use_container_width=True)
            st.markdown("""
            <div style="text-align: center; margin-top: -15px;">
                <span style="background: #dcfce7; color: #166534; font-weight: 700; font-size: 12px; padding: 4px 12px; border-radius: 9999px; border: 1px solid #bbf7d0;">
                    Target: 0.00 (Zero LTI)
                </span>
            </div>
            """, unsafe_allow_html=True)

        with sg2:
            fig_speedo_tri = make_speedometer(
                title="TRIR",
                slice_vals=[0.06, 0.16, 0.18, 0.40, 0.40],
                slice_colors=['#196b24', '#4ea72e', '#ffff00', '#e97132', '#ff0000'],
                needle_frac=0.18
            )
            st.plotly_chart(fig_speedo_tri, use_container_width=True)
            st.markdown("""
            <div style="text-align: center; margin-top: -15px;">
                <span style="background: #e0f2fe; color: #0369a1; font-weight: 700; font-size: 12px; padding: 4px 12px; border-radius: 9999px; border: 1px solid #bae6fd;">
                    Benchmark: &le; 0.50 (Good)
                </span>
            </div>
            """, unsafe_allow_html=True)

    # 3. SECONDARY BENCHMARK & SEVERITY TABS
    st.markdown("<br><br>", unsafe_allow_html=True)
    tab_bench, tab_safemh, tab_rec = st.tabs([
        "⚖️ International Industry Benchmarking",
        "⏱️ Zero-LTI Man-Hours Progression (6.2M hrs)",
        "📋 Recordable Cases Case Analysis (8 MTC)"
    ])

    with tab_bench:
        st.markdown('<div class="section-title">GCDC Project vs Global Construction Safety Standards</div>', unsafe_allow_html=True)
        b_labels = ["GCDC Actual (TRIR)", "World-Class Threshold", "Industry Average", "High Risk Threshold"]
        b_values = [0.26, 0.50, 1.40, 2.50]
        b_colors = ["#15803d", "#0284c7", "#f59e0b", "#dc2626"]

        fig_bench = go.Figure()
        fig_bench.add_trace(go.Bar(
            x=b_labels,
            y=b_values,
            text=[f"<b>{v:.2f}</b>" for v in b_values],
            textposition='outside',
            textfont=dict(size=13, family='Inter, sans-serif', weight='bold'),
            marker=dict(color=b_colors, line=dict(color='#0f172a', width=1.2)),
            width=0.45
        ))
        fig_bench.update_layout(
            height=280,
            yaxis=dict(range=[0, 3.0], title="Recordable Rate (per 200,000 hrs)", gridcolor="#e2e8f0"),
            xaxis=dict(tickfont=dict(size=12, color="#0f172a")),
            margin=dict(l=40, r=40, t=25, b=25),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_bench, use_container_width=True)

    with tab_safemh:
        st.markdown('<div class="section-title">Safe Man-Hours Milestone Trajectory</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:16px;">
            <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:16px;">
                <div style="font-size:11px; font-weight:700; color:#166534; text-transform:uppercase;">Historical Safe Hours (Prior)</div>
                <div style="font-size:26px; font-weight:800; color:#15803d; margin:6px 0;">2,916,176 hrs</div>
                <div style="font-size:12px; color:#475569;">Recorded up to December 2025</div>
            </div>
            <div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:8px; padding:16px;">
                <div style="font-size:11px; font-weight:700; color:#0369a1; text-transform:uppercase;">YTD 2026 Safe Hours</div>
                <div style="font-size:26px; font-weight:800; color:#0284c7; margin:6px 0;">3,284,962 hrs</div>
                <div style="font-size:12px; color:#475569;">Jan to Sep 2026 Total</div>
            </div>
            <div style="background:#f8fafc; border:2px solid #002060; border-radius:8px; padding:16px;">
                <div style="font-size:11px; font-weight:700; color:#002060; text-transform:uppercase;">Grand Cumulative Total</div>
                <div style="font-size:26px; font-weight:800; color:#002060; margin:6px 0;">6,201,138 hrs</div>
                <div style="font-size:12px; color:#15803d; font-weight:600;">Zero Lost Time Injuries (0 LTI)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab_rec:
        st.markdown('<div class="section-title">Recordable Case Details (8 MTC Incidents)</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:16px; margin-bottom:12px;">
            <div style="font-size:13px; color:#334155; line-height:1.6;">
                The <b>TRIR of 0.26</b> is driven by <b>8 Medical Treatment Cases (MTC)</b> recorded out of 102 total project incidents. 
                All 8 cases involved minor lacerations or sprains treated by the site medical clinic with immediate return to normal duties, resulting in <b>Zero Lost Days</b> and <b>Zero Restricted Work Cases (RWC)</b>.
            </div>
        </div>
        """, unsafe_allow_html=True)


# =========================================================================
# 🤝 PAGE: WELFARE & PROACTIVE SAFETY
# =========================================================================
elif st.session_state.active_page == "Welfare":
    st.markdown("## 🤝 Workforce Welfare & Safety Engagement")
    st.caption("Weekly audit scores of worker welfare facilities and proactive HSE campaign performance")

    w_left, w_right = st.columns([1.2, 0.8])
    with w_left:
        st.markdown(f'<div class="section-card"><div class="section-title">Weekly Worker Welfare Audit Scores (Avg: {data["welfare"]["average"]*100:.1f}%)</div>', unsafe_allow_html=True)
        df_w = pd.DataFrame(data['welfare']['weekly'])
        if not df_w.empty:
            fig_w = go.Figure()
            fig_w.add_trace(go.Scatter(
                x=df_w['week'],
                y=df_w['score'] * 100,
                name="Welfare Score",
                mode="lines+markers",
                line=dict(color="#06b6d4", width=3),
                marker=dict(size=8, color="#0891b2"),
                text=[f"{s*100:.1f}%" for s in df_w['score']],
                textposition='top center'
            ))
            fig_w.add_trace(go.Scatter(
                x=df_w['week'],
                y=df_w['target'] * 100,
                name="Target (90%)",
                mode="lines",
                line=dict(color="#ef4444", width=2, dash="dot")
            ))
            fig_w.update_layout(height=300, yaxis=dict(range=[40, 105], title="Score (%)"), margin=dict(l=20, r=20, t=15, b=20), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_w, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with w_right:
        st.markdown('<div class="section-card"><div class="section-title">Proactive Field Engagement</div>', unsafe_allow_html=True)
        act = data['activities']
        tr = data['training']
        st.markdown(f"""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px; margin-bottom:12px;">
            <div style="font-size:11px; font-weight:600; color:#64748b; text-transform:uppercase;">Toolbox Talks (TBT)</div>
            <div style="font-size:24px; font-weight:700; color:#0284c7;">{act['tbt']} Sessions</div>
        </div>
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px; margin-bottom:12px;">
            <div style="font-size:11px; font-weight:600; color:#64748b; text-transform:uppercase;">Formal HSE Inspections</div>
            <div style="font-size:24px; font-weight:700; color:#16a34a;">{act['inspections']} Completed</div>
        </div>
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px;">
            <div style="font-size:11px; font-weight:600; color:#64748b; text-transform:uppercase;">HSE Trainings Execution</div>
            <div style="font-size:22px; font-weight:700; color:#ea580c;">{tr['trainings']} / {tr['target']} Sessions ({tr['rate']*100:.1f}%)</div>
            <div style="font-size:12px; color:#64748b; margin-top:4px;">{tr['attendees']} workers attended</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 12px; padding: 20px 0 24px 0;">
    GCDC HSE Performance Executive Dashboard • Kharafi National / SBARC • Develop by Abdul Latif HSE Analyst <a href="tel:+966530572691" style="color: #64748b; text-decoration: none; font-weight: 600;">+966530572691</a>
</div>
""", unsafe_allow_html=True)
