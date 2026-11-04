"""
Generates a standalone, fully-interactive self-contained single-sheet HTML dashboard report.
Features a dedicated Left Side Panel for the Compliance Rate % Section matching the user's Excel specifications.
"""
import os
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime

from hse_parser import parse_single_sheet_csv, CSV_PATH

def generate_html_report(output_path: str = "GCDC_HSE_Executive_Report.html"):
    data = parse_single_sheet_csv(CSV_PATH)
    
    # 1. Exact Excel Semicircular Speedometers (Image 2)
    def make_speedo_fig(title, slice_vals, slice_colors, needle_frac):
        total_top = sum(slice_vals)
        pie_vals = list(slice_vals) + [total_top]
        pie_colors = list(slice_colors) + ['rgba(0,0,0,0)']
        theta = np.pi * (1.0 - needle_frac)
        
        x_head = 0.5 + 0.38 * np.cos(theta)
        y_head = 0.5 + 0.38 * np.sin(theta)
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
        fig.add_shape(type='line', x0=0.5, y0=0.5, x1=x_head, y1=y_head, line=dict(color='#000000', width=2.5))
        fig.add_shape(type='line', x0=x_band_in, y0=y_band_in, x1=x_band_out, y1=y_band_out, line=dict(color='#000000', width=7))
        fig.update_layout(
            title=dict(text=f'<b>{title}</b>', font=dict(size=22, color='#0d2640', family='Segoe UI, Inter, sans-serif'), x=0.5, xanchor='center'),
            height=230,
            margin=dict(l=10, r=10, t=45, b=10),
            xaxis=dict(range=[0, 1], visible=False),
            yaxis=dict(range=[0.38, 1.08], visible=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    fig_ltifr_html = make_speedo_fig(
        title="LTIFR",
        slice_vals=[0.05, 0.45, 0.50, 1.00],
        slice_colors=['#196b24', '#4ea72e', '#ffc000', '#ff0000'],
        needle_frac=0.01
    )
    
    fig_trir_html = make_speedo_fig(
        title="TRIR",
        slice_vals=[0.06, 0.16, 0.18, 0.40, 0.40],
        slice_colors=['#196b24', '#4ea72e', '#ffff00', '#e97132', '#ff0000'],
        needle_frac=0.18
    )

    # Sidebar Mini Gauge for Compliance Rate
    g_rate_pct = data['compliance']['grand_total']['rate'] * 100
    fig_comp_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=g_rate_pct,
        number={'suffix': "%", 'font': {'size': 20, 'color': '#0f2438'}},
        gauge={
            'axis': {'range': [0, 100], 'tickvals': [0, 50, 95, 100], 'ticktext': ['0%', '50%', '95%', '100%'], 'tickfont': {'size': 10}},
            'bar': {'color': '#16a34a', 'thickness': 0.35},
            'steps': [
                {'range': [0, 80], 'color': '#fecaca'},
                {'range': [80, 95], 'color': '#fef08a'},
                {'range': [95, 100], 'color': '#bbf7d0'}
            ],
            'threshold': {'line': {'color': "#15803d", 'width': 3}, 'thickness': 0.75, 'value': 95}
        }
    ))
    fig_comp_gauge.update_layout(height=140, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig_comp_gauge_html = fig_comp_gauge.to_html(full_html=False, include_plotlyjs=False)

    # 2. Incident Donut
    inc_data = [
        {"Category": "Near Miss (NM)", "Count": data['incidents']['NM'], "Color": "#3b82f6"},
        {"Category": "Medical Treatment (MTC)", "Count": data['incidents']['MTC'], "Color": "#f59e0b"},
        {"Category": "Motor Vehicle (MVA)", "Count": data['incidents']['MVA'], "Color": "#ec4899"},
        {"Category": "Property Damage (PD)", "Count": data['incidents']['PD'], "Color": "#8b5cf6"},
        {"Category": "First Aid (FAC)", "Count": data['incidents']['FAC'], "Color": "#10b981"},
        {"Category": "Lost Time (LTI)", "Count": data['incidents']['LTI'], "Color": "#ef4444"},
        {"Category": "Fatality (FAT)", "Count": data['incidents']['FAT'], "Color": "#000000"}
    ]
    df_inc = pd.DataFrame(inc_data)
    df_inc = df_inc[df_inc['Count'] > 0]
    fig_donut = px.pie(
        df_inc, names="Category", values="Count", hole=0.55,
        color="Category", color_discrete_map={row["Category"]: row["Color"] for row in inc_data}
    )
    fig_donut.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#ffffff', width=2)))
    fig_donut.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
    fig_donut_html = fig_donut.to_html(full_html=False, include_plotlyjs=False)

    # 3. Manhours & Manpower Chart
    m_hours = data['safe_man_hours']['monthly']
    m_power = data['manpower']['monthly']
    chart_months = list(m_hours.keys())
    chart_hours = list(m_hours.values())
    chart_power = [m_power.get(m, 0) for m in chart_months]
    
    fig_dual = go.Figure()
    fig_dual.add_trace(go.Bar(x=chart_months, y=chart_hours, name="Monthly Safe Man-Hours", marker_color="#38bdf8", opacity=0.85, yaxis="y1"))
    fig_dual.add_trace(go.Scatter(x=chart_months, y=chart_power, name="Daily Manpower", mode="lines+markers", line=dict(color="#f97316", width=3), marker=dict(size=8, color="#ea580c"), yaxis="y2"))
    fig_dual.update_layout(
        height=280, margin=dict(l=40, r=40, t=20, b=25),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Safe Man-Hours", side="left", gridcolor="#f1f5f9"),
        yaxis2=dict(title="Daily Manpower", side="right", overlaying="y", showgrid=False),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    fig_dual_html = fig_dual.to_html(full_html=False, include_plotlyjs=False)

    # 4. Monthly KPI Score Chart & Trendline (Exact from Excel Image 2)
    kpi_all_m = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October']
    kpi_scores_val = [84, 81, 87, 90, 93, 85, 91, 68, 68, None]
    kpi_base_val = [90] * 10

    # Linear trendline projection
    val_x = [i for i, v in enumerate(kpi_scores_val) if v is not None]
    val_y = [v for v in kpi_scores_val if v is not None]
    slope_k, intercept_k = np.polyfit(val_x, val_y, 1)
    kpi_trend_val = [round(slope_k * i + intercept_k, 1) for i in range(len(kpi_all_m))]

    fig_kpi = go.Figure()
    fig_kpi.add_trace(go.Scatter(
        x=kpi_all_m, y=kpi_base_val, mode='lines', name="Baseline (90%)",
        line=dict(color="#10b981", width=2, dash="dash"),
        hovertemplate="Baseline Target: <b>90%</b><extra></extra>"
    ))
    fig_kpi.add_trace(go.Scatter(
        x=kpi_all_m, y=kpi_trend_val, mode='lines', name="Linear Trendline",
        line=dict(color="#ef4444", width=2.5, dash="dot"),
        hovertemplate="Trendline: <b>%{y:.1f}%</b><extra></extra>"
    ))
    fig_kpi.add_trace(go.Scatter(
        x=kpi_all_m, y=kpi_scores_val, mode='lines+markers+text', name="Monthly KPI Score",
        line=dict(color="#005b82", width=3.8),
        marker=dict(size=8, color="#005b82", line=dict(color="#ffffff", width=2)),
        text=[f"<b>{s:.0f}%</b>" if s is not None else "" for s in kpi_scores_val],
        textposition="top center", textfont=dict(size=11, color="#0f172a"),
        cliponaxis=False, hovertemplate="<b>%{x}</b><br>Score: <b>%{y}%</b><extra></extra>"
    ))
    fig_kpi.update_layout(
        title=dict(text="<b>KPI</b>", font=dict(size=20, color="#0d233a"), x=0.5, xanchor="center"),
        height=320,
        yaxis=dict(range=[0, 105], tickvals=[0, 20, 40, 60, 80, 100], ticktext=['0%', '20%', '40%', '60%', '80%', '100%'], gridcolor="#f1f5f9"),
        xaxis=dict(tickangle=-45, tickfont=dict(size=11, color="#0f172a")),
        margin=dict(l=45, r=35, t=45, b=55),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    fig_kpi_html = fig_kpi.to_html(full_html=False, include_plotlyjs=False)

    # 4b. Monthly PSI/PCI Score Chart & Upward Trendline (Exact from Excel Image 2)
    psi_scores_val = [60, 58, 59, 67, 66, 67, 69, 68, 75, None]
    val_px = [i for i, v in enumerate(psi_scores_val) if v is not None]
    val_py = [v for v in psi_scores_val if v is not None]
    slope_p, intercept_p = np.polyfit(val_px, val_py, 1)
    psi_trend_val = [round(slope_p * i + intercept_p, 1) for i in range(len(kpi_all_m))]

    fig_psi = go.Figure()
    fig_psi.add_trace(go.Scatter(
        x=kpi_all_m, y=kpi_base_val, mode='lines', name="Baseline (90%)",
        line=dict(color="#10b981", width=2, dash="dash"),
        hovertemplate="Baseline Target: <b>90%</b><extra></extra>"
    ))
    fig_psi.add_trace(go.Scatter(
        x=kpi_all_m, y=psi_trend_val, mode='lines', name="Linear Trendline",
        line=dict(color="#ef4444", width=2.5, dash="dot"),
        hovertemplate="Trendline: <b>%{y:.1f}%</b><extra></extra>"
    ))
    fig_psi.add_trace(go.Scatter(
        x=kpi_all_m, y=psi_scores_val, mode='lines+markers+text', name="PSI/PCI Score",
        line=dict(color="#005b82", width=3.8),
        marker=dict(size=8, color="#005b82", line=dict(color="#ffffff", width=2)),
        text=[f"<b>{s:.0f}%</b>" if s is not None else "" for s in psi_scores_val],
        textposition="top center", textfont=dict(size=11, color="#0f172a"),
        cliponaxis=False, hovertemplate="<b>%{x}</b><br>PSI/PCI: <b>%{y}%</b><extra></extra>"
    ))
    fig_psi.update_layout(
        title=dict(text="<b>PSI/PCI</b>", font=dict(size=20, color="#0d233a"), x=0.5, xanchor="center"),
        height=320,
        yaxis=dict(range=[0, 95], tickvals=[0, 20, 40, 60, 80], ticktext=['0%', '20%', '40%', '60%', '80%'], gridcolor="#f1f5f9"),
        xaxis=dict(tickangle=-45, tickfont=dict(size=11, color="#0f172a")),
        margin=dict(l=45, r=35, t=45, b=55),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    fig_psi_html = fig_psi.to_html(full_html=False, include_plotlyjs=False)

    # 5. Weekly Welfare Score Chart
    df_w = pd.DataFrame(data['welfare']['weekly'])
    fig_w = go.Figure()
    fig_w.add_trace(go.Scatter(
        x=df_w['week'], y=df_w['score'] * 100, name="Welfare Score",
        mode="lines+markers", line=dict(color="#06b6d4", width=3), marker=dict(size=8, color="#0891b2"),
        text=[f"{s*100:.1f}%" for s in df_w['score']], textposition='top center'
    ))
    fig_w.add_trace(go.Scatter(
        x=df_w['week'], y=df_w['target'] * 100, name="Target Benchmark (90%)",
        mode="lines", line=dict(color="#ef4444", width=2, dash="dot")
    ))
    fig_w.update_layout(
        height=260, yaxis=dict(range=[40, 105], title="Score (%)", gridcolor="#f1f5f9"),
        margin=dict(l=30, r=30, t=15, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    fig_w_html = fig_w.to_html(full_html=False, include_plotlyjs=False)

    # 6. Training Bar Chart (Exact Image 2)
    t_m = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
    t_v = [2, 0, 0, 0, 0, 0, 2, 0, 1, 0, 0]
    t_tgt = [2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2]
    fig_train = go.Figure()
    fig_train.add_trace(go.Bar(
        x=t_m, y=t_v, text=[str(v) if v > 0 else "" for v in t_v], textposition='outside',
        textfont=dict(size=12, color="#0d233a", weight="bold"),
        marker=dict(color="#005a87", line=dict(color="#003853", width=1.5)), width=0.4, name="Conducted"
    ))
    fig_train.add_trace(go.Scatter(
        x=t_m, y=t_tgt, mode='lines', name="Target",
        line=dict(color="#ef4444", width=2, dash="dash")
    ))
    fig_train.update_layout(
        title=dict(text="<b>Training</b>", font=dict(size=20, color="#0d233a"), x=0.5, xanchor="center"),
        height=320, yaxis=dict(range=[0, 2.3], tickvals=[0, 0.5, 1, 1.5, 2], gridcolor="#f1f5f9"),
        xaxis=dict(tickfont=dict(size=11, color="#0f172a")), margin=dict(l=35, r=25, t=45, b=45),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    fig_train_html = fig_train.to_html(full_html=False, include_plotlyjs=False)

    # 7. NCRs Bar Chart (Exact Image 3)
    fig_ncr = go.Figure()
    fig_ncr.add_trace(go.Bar(
        x=['Open', 'Closed', 'Overdue'],
        y=[2, 52, 2],
        text=['2', '52', '2'],
        textposition='outside',
        textfont=dict(size=12, color="#0d2640", weight="bold"),
        marker=dict(color="#0e5374", line=dict(color="#09384f", width=1.5)),
        width=0.45
    ))
    fig_ncr.update_layout(
        title=dict(text="<b>NCRs</b>", font=dict(size=18, color="#0d2640"), x=0.5, xanchor="center"),
        height=220,
        yaxis=dict(title=dict(text="Num. of NCRs", font=dict(size=10, color="#0d2640")), range=[0, 65], tickvals=[0, 10, 20, 30, 40, 50, 60], gridcolor="#f1f5f9"),
        xaxis=dict(tickfont=dict(size=11, color="#0d2640", weight="bold")),
        margin=dict(l=35, r=15, t=35, b=25),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    fig_ncr_html = fig_ncr.to_html(full_html=False, include_plotlyjs=False)

    # 8. Site Observations Bar Chart (Exact Image 3)
    fig_obs = go.Figure()
    fig_obs.add_trace(go.Bar(
        x=['Open', 'Closed', 'Overdue'],
        y=[8, 1242, 8],
        text=['8', '1242', '8'],
        textposition='outside',
        textfont=dict(size=12, color="#0d2640", weight="bold"),
        marker=dict(color="#0e5374", line=dict(color="#09384f", width=1.5)),
        width=0.45
    ))
    fig_obs.update_layout(
        title=dict(text="<b>Site Observations</b>", font=dict(size=18, color="#0d2640"), x=0.5, xanchor="center"),
        height=220,
        yaxis=dict(range=[0, 1500], tickvals=[0, 200, 400, 600, 800, 1000, 1200, 1400], gridcolor="#f1f5f9"),
        xaxis=dict(tickfont=dict(size=11, color="#0d2640", weight="bold")),
        margin=dict(l=35, r=15, t=35, b=25),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    fig_obs_html = fig_obs.to_html(full_html=False, include_plotlyjs=False)

    # 9. HSE Activities Bar Chart (Exact Image 2)
    fig_act = go.Figure()
    fig_act.add_trace(go.Bar(
        x=['TBT', 'inspections', 'Campaigns'],
        y=[114, 6, 1],
        text=['114', '6', '1'],
        textposition='outside',
        textfont=dict(size=12, color="#0d2640", weight="bold"),
        marker=dict(color="#0e5374", line=dict(color="#09384f", width=1.5)),
        width=0.45
    ))
    fig_act.update_layout(
        title=dict(text="<b>HSE Activities</b>", font=dict(size=18, color="#0d2640"), x=0.5, xanchor="center"),
        height=220,
        yaxis=dict(range=[0, 130], tickvals=[0, 20, 40, 60, 80, 100, 120], gridcolor="#f1f5f9"),
        xaxis=dict(tickfont=dict(size=11, color="#0d2640", weight="bold")),
        margin=dict(l=35, r=15, t=35, b=25),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    fig_act_html = fig_act.to_html(full_html=False, include_plotlyjs=False)

    # 10. Staffing Compliance Gauge & Bar (Excel Image)
    fig_staff_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=88,
        number={'suffix': "%", 'font': {'size': 28, 'color': '#0d2640'}},
        title={'text': "<b>Staffing Compliance</b><br><span style='font-size:11px;color:#64748b'>22 of 25 Staff</span>", 'font': {'size': 13, 'color': '#0d2640'}},
        gauge={
            'axis': {'range': [0, 100], 'tickvals': [0, 50, 80, 88, 100], 'ticktext': ['0%', '50%', '80%', '88%', '100%']},
            'bar': {'color': '#0284c7', 'thickness': 0.32},
            'steps': [
                {'range': [0, 80], 'color': '#fee2e2'},
                {'range': [80, 95], 'color': '#fef3c7'},
                {'range': [95, 100], 'color': '#dcfce7'}
            ],
            'threshold': {'line': {'color': "#15803d", 'width': 3}, 'thickness': 0.8, 'value': 100}
        }
    ))
    fig_staff_gauge.update_layout(height=200, margin=dict(l=15, r=15, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)')
    fig_staff_gauge_html = fig_staff_gauge.to_html(full_html=False, include_plotlyjs=False)

    fig_staff_bar = go.Figure()
    fig_staff_bar.add_trace(go.Bar(
        x=['Actual', 'Required', 'Gap'],
        y=[22, 25, 3],
        text=['22', '25', '3'],
        textposition='outside',
        textfont=dict(size=12, color='#0d2640', weight='bold'),
        marker=dict(color=['#0e5374', '#15803d', '#dc2626'], line=dict(color=['#09384f', '#166534', '#991b1b'], width=1.5)),
        width=0.45
    ))
    fig_staff_bar.update_layout(
        title=dict(text='<b>Staffing Deployment</b>', font=dict(size=15, color='#0d2640'), x=0.5, xanchor='center'),
        yaxis=dict(range=[0, 30], tickvals=[0, 5, 10, 15, 20, 25], gridcolor='#f1f5f9'),
        xaxis=dict(tickfont=dict(size=11, color='#0d2640', weight='bold')),
        height=200, margin=dict(l=30, r=15, t=35, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    fig_staff_bar_html = fig_staff_bar.to_html(full_html=False, include_plotlyjs=False)

    obs = data['compliance']['observations']
    ncr = data['compliance']['ncr']
    aud = data['compliance']['audits']
    grand = data['compliance']['grand_total']

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GCDC HSE Executive Dashboard - Compliance Special</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f1f5f9; color: #0f172a; }}
        .glass-card {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.03); }}
        
        .compliance-box {{
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #0f172a;
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        }}
        .compliance-header {{
            background: #8fa0b5;
            color: #0f2438;
            font-size: 15px;
            font-weight: 700;
            text-align: center;
            padding: 8px 12px;
        }}
        .compliance-value-block {{
            background: #0d1e30;
            color: #ffffff;
            font-size: 42px;
            font-weight: 800;
            text-align: center;
            padding: 12px 10px 4px 10px;
            line-height: 1;
        }}
        .compliance-subtext {{
            background: #0d1e30;
            color: #94a3b8;
            font-size: 11px;
            text-align: center;
            padding-bottom: 12px;
            font-weight: 500;
        }}
    </style>
</head>
<body class="p-4 md:p-6 max-w-[1600px] mx-auto">
    <!-- Top Executive Header -->
    <div class="bg-slate-900 text-white rounded-2xl p-6 mb-6 shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center border border-slate-800">
        <div>
            <div class="flex items-center gap-3 mb-1">
                <span class="text-3xl">🛡️</span>
                <h1 class="text-2xl md:text-3xl font-bold tracking-tight">GCDC HSE Performance Executive Dashboard</h1>
            </div>
            <p class="text-slate-400 text-sm">Kharafi National / SBARC • Integrated Left Side Panel Compliance Visualization</p>
        </div>
        <div class="mt-4 md:mt-0 text-left md:text-right text-xs text-slate-400">
            <div>View: <span class="text-sky-400 font-mono font-medium">Compliance-Focused Executive View</span></div>
            <div>Updated: <span class="text-slate-200">{datetime.now().strftime('%Y-%m-%d %H:%M')}</span></div>
        </div>
    </div>

    <!-- MAIN TWO-COLUMN LAYOUT (LEFT SIDE PANEL + MAIN DASHBOARD) -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
        
        <!-- LEFT SIDE PANEL: COMPLIANCE RATE SECTION -->
        <div class="lg:col-span-1 space-y-4">
            <div class="glass-card p-5 border-sky-200 shadow-md">
                <div class="flex items-center justify-between mb-3 border-b pb-2">
                    <h2 class="text-base font-bold text-slate-900 flex items-center gap-2">
                        📋 Compliance Rate %
                    </h2>
                    <span class="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">Target &ge; 95%</span>
                </div>

                <!-- Card Matching Excel Image 2 -->
                <div class="compliance-box mb-4">
                    <div class="compliance-header">Compliance Rate</div>
                    <div class="compliance-value-block">{g_rate_pct:.0f}%</div>
                    <div class="compliance-subtext">{grand['closed']:,} of {grand['total']:,} Closed</div>
                </div>

                <!-- Mini Gauge -->
                <div class="mb-4">
                    {fig_comp_gauge_html}
                </div>

                <!-- Breakdown Cards Matching Image 1 -->
                <div class="space-y-3">
                    <!-- Site Observations -->
                    <div class="bg-slate-50 border border-slate-200 rounded-lg p-3">
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-xs font-semibold text-slate-800">Observations</span>
                            <span class="bg-emerald-700 text-white text-xs font-bold px-2 py-0.5 rounded">{obs['rate']*100:.0f}%</span>
                        </div>
                        <div class="text-xs text-slate-500 mb-1"><b>{obs['closed']:,}</b> Closed • <b>{obs['open']}</b> Open (Total: {obs['total']:,})</div>
                        <div class="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                            <div class="bg-emerald-600 h-1.5" style="width: {obs['rate']*100:.1f}%"></div>
                        </div>
                    </div>

                    <!-- NCR -->
                    <div class="bg-slate-50 border border-slate-200 rounded-lg p-3">
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-xs font-semibold text-slate-800">NCR</span>
                            <span class="bg-emerald-700 text-white text-xs font-bold px-2 py-0.5 rounded">{ncr['rate']*100:.0f}%</span>
                        </div>
                        <div class="text-xs text-slate-500 mb-1"><b>{ncr['closed']}</b> Closed • <b>{ncr['open']}</b> Open (Total: {ncr['total']})</div>
                        <div class="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                            <div class="bg-emerald-600 h-1.5" style="width: {ncr['rate']*100:.1f}%"></div>
                        </div>
                    </div>

                    <!-- Audits & Other Inspections (RED 50%) -->
                    <div class="bg-red-50 border border-red-200 rounded-lg p-3">
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-xs font-bold text-red-900">Other Inspections / Audits</span>
                            <span class="bg-red-600 text-white text-xs font-bold px-2 py-0.5 rounded">{aud['rate']*100:.0f}%</span>
                        </div>
                        <div class="text-xs text-red-700 mb-1"><b>{aud['closed']}</b> Closed • <b class="text-red-800">{aud['open']}</b> Open (Total: {aud['total']})</div>
                        <div class="w-full bg-red-200 rounded-full h-1.5 overflow-hidden">
                            <div class="bg-red-600 h-1.5" style="width: {aud['rate']*100:.1f}%"></div>
                        </div>
                    </div>

                    <!-- Grand Total -->
                    <div class="bg-slate-100 border border-slate-300 rounded-lg p-3">
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-xs font-bold text-slate-900">Grand Total Actions</span>
                            <span class="bg-slate-900 text-white text-xs font-bold px-2 py-0.5 rounded">{grand['rate']*100:.0f}%</span>
                        </div>
                        <div class="text-xs text-slate-600 mb-1"><b>{grand['closed']:,}</b> Closed • <b>{grand['open']}</b> Open (Total: {grand['total']:,})</div>
                        <div class="w-full bg-slate-300 rounded-full h-2 overflow-hidden">
                            <div class="bg-slate-900 h-2" style="width: {grand['rate']*100:.1f}%"></div>
                        </div>
                    </div>
                </div>

                <!-- Yellow Important Note Callout -->
                <div class="mt-4 bg-amber-100 border border-amber-300 rounded-lg p-3 text-xs text-amber-900 leading-snug font-medium">
                    ⚠️ <b>Important Note:</b><br>
                    The HSE completed activities in <b>T22</b> are included in the grand total closed performance rate.
                </div>

                <!-- Dedicated Site Observations Section (Excel Format) -->
                <div class="mt-4 pt-4 border-t border-slate-200">
                    <div class="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                        🔍 Site Observations (Excel)
                    </div>

                    <!-- Table 1: Status Counts -->
                    <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000000; font-size: 11.5px; margin-bottom: 8px;">
                        <thead>
                            <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #000000;">
                                <th colspan="2" style="padding: 4px; text-align: center; font-size: 12px; font-weight: 800;">Site Observation</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000; width: 60%;">Open</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">8</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Closed</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">1242</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Overdue</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">8</td>
                            </tr>
                            <tr>
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 1.5px solid #000000;">Total</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">1250</td>
                            </tr>
                        </tbody>
                    </table>

                    <!-- Table 2: Rates & Performance -->
                    <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000000; font-size: 11.5px; margin-bottom: 8px;">
                        <thead>
                            <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #000000;">
                                <th colspan="2" style="padding: 4px; text-align: center; font-size: 12px; font-weight: 800;">Site Observation</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000; width: 62%;">Closure Rate</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">99%</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">OD Rate</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">1.4%</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">OTC Rate</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">2%</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 1.5px solid #000000;">Total OD</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">17</td>
                            </tr>
                            <tr>
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Closed On-time</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">25</td>
                            </tr>
                        </tbody>
                    </table>

                    <!-- Bar Chart -->
                    <div>
                        {fig_obs_html}
                    </div>
                </div>

                <!-- Dedicated NCRs Section (Excel Format) -->
                <div class="mt-4 pt-4 border-t border-slate-200">
                    <div class="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                        📑 NCRs Performance (Excel)
                    </div>

                    <!-- Table 1: Status Counts -->
                    <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000000; font-size: 11.5px; margin-bottom: 8px;">
                        <thead>
                            <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #000000;">
                                <th colspan="2" style="padding: 4px; text-align: center; font-size: 12px; font-weight: 800;">NCRs</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000; width: 60%;">Open</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">2</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Closed</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">52</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Overdue</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">2</td>
                            </tr>
                            <tr>
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 1.5px solid #000000;">Total</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">54</td>
                            </tr>
                        </tbody>
                    </table>

                    <!-- Table 2: Rates & Performance -->
                    <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000000; font-size: 11.5px; margin-bottom: 8px;">
                        <thead>
                            <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #000000;">
                                <th colspan="2" style="padding: 4px; text-align: center; font-size: 12px; font-weight: 800;">NCRs</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000; width: 62%;">Closure Rate</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">96%</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">OD Rate</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">4%</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">OTC Rate</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">0%</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 1.5px solid #000000;">Total OD</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">2</td>
                            </tr>
                            <tr>
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Closed On-time</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">0</td>
                            </tr>
                        </tbody>
                    </table>

                    <!-- Bar Chart -->
                    <div>
                        {fig_ncr_html}
                    </div>
                </div>

                <!-- Dedicated HSE Activities Section (Excel Format) -->
                <div class="mt-4 pt-4 border-t border-slate-200">
                    <div class="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                        🛠️ HSE Activities (Excel)
                    </div>

                    <!-- Table: HSE Activities -->
                    <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000000; font-size: 11.5px; margin-bottom: 8px;">
                        <thead>
                            <tr style="background-color: #002060; color: #ffffff; border-bottom: 1px solid #ffffff;">
                                <th colspan="2" style="padding: 4px; text-align: center; font-size: 12px; font-weight: 800;">HSE Activities</th>
                            </tr>
                            <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #000000;">
                                <th style="padding: 4px 6px; text-align: center; font-size: 11.5px; font-weight: 700; border-right: 1.5px solid #ffffff; width: 60%;">Activity</th>
                                <th style="padding: 4px 6px; text-align: center; font-size: 11.5px; font-weight: 700; width: 40%;">Quantity</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">TBT</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">114</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">inspections</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">6</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #000000;">
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000;">Campaigns</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">1</td>
                            </tr>
                            <tr>
                                <td style="padding: 4px 6px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 1.5px solid #000000;">Total</td>
                                <td style="padding: 4px 6px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">121</td>
                            </tr>
                        </tbody>
                    </table>

                    <!-- Bar Chart -->
                    <div>
                        {fig_act_html}
                    </div>
                </div>
            </div>
        </div>

        <!-- RIGHT SIDE: MAIN EXECUTIVE DASHBOARD (3 COLUMNS) -->
        <div class="lg:col-span-3 space-y-6">
            
            <!-- Top 5 Executive KPI Cards -->
            <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
                <div class="glass-card p-4">
                    <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Total Incidents</div>
                    <div class="text-2xl font-bold text-slate-900">{data['incidents']['Total']}</div>
                    <span class="inline-block mt-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-sky-100 text-sky-800">81% Near Miss</span>
                </div>
                <div class="glass-card p-4">
                    <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Safe Man-Hours</div>
                    <div class="text-2xl font-bold text-slate-900">{data['safe_man_hours']['total_safe_hours']:,.0f}</div>
                    <span class="inline-block mt-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800">Cumulative</span>
                </div>
                <div class="glass-card p-4">
                    <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Training Rate</div>
                    <div class="text-2xl font-bold text-slate-900">{data['training']['completion_rate']*100:.1f}%</div>
                    <span class="inline-block mt-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-amber-100 text-amber-800">5 of 17 Done</span>
                </div>
                <div class="glass-card p-4">
                    <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">LTIFR</div>
                    <div class="text-2xl font-bold text-slate-900">{data['rates']['ltifr']:.2f}</div>
                    <span class="inline-block mt-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800">{data['rates']['ltifr_rating']}</span>
                </div>
                <div class="glass-card p-4">
                    <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">TRIR</div>
                    <div class="text-2xl font-bold text-slate-900">{data['rates']['trir']:.3f}</div>
                    <span class="inline-block mt-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-sky-100 text-sky-800">{data['rates']['trir_rating']} (&le;0.50)</span>
                </div>
            </div>

            <!-- Gauges & Incident Donut -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="glass-card p-5">
                    <h2 class="text-base font-semibold text-slate-800 mb-2">🎯 Safety Frequency Rates (Gauges)</h2>
                    <div class="grid grid-cols-2 gap-2">
                        <div>{fig_ltifr_html}</div>
                        <div>{fig_trir_html}</div>
                    </div>
                </div>
                <div class="glass-card p-5">
                    <h2 class="text-base font-semibold text-slate-800 mb-2">🚨 Incident Severity Distribution (102 Cases)</h2>
                    <div>{fig_donut_html}</div>
                </div>
            </div>

            <!-- Safe Man-hours & Manpower Chart -->
            <div class="glass-card p-5">
                <h2 class="text-base font-semibold text-slate-800 mb-2">⏱️ Monthly Safe Man-Hours & Daily Workforce Dynamics</h2>
                <div>{fig_dual_html}</div>
            </div>

            <!-- Monthly KPI, PSI/PCI & Weekly Welfare -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="glass-card p-5">
                    <h2 class="text-base font-semibold text-slate-800 mb-2">📈 HSE Monthly KPI Scores & Trendline vs 90% Target</h2>
                    <div>{fig_kpi_html}</div>
                </div>
                <div class="glass-card p-5">
                    <h2 class="text-base font-semibold text-slate-800 mb-2">🎯 HSE Monthly PSI/PCI Scores & Upward Trendline</h2>
                    <div>{fig_psi_html}</div>
                </div>
            </div>

            <!-- HSE Staffing Compliance & Department Capacity (Excel Format) -->
            <div class="glass-card p-5">
                <h2 class="text-base font-semibold text-slate-800 mb-3">👥 HSE Staffing Compliance & Department Capacity (Excel Format)</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
                    <div>
                        <!-- Exact Table (Excel Image) -->
                        <table style="width: 100%; border-collapse: collapse; border: 2px solid #000000; font-size: 13px;">
                            <thead>
                                <tr style="background-color: #002060; color: #ffffff; border-bottom: 2px solid #000000;">
                                    <th colspan="2" style="padding: 6px; text-align: center; font-size: 14px; font-weight: 800;">HSE Staffing Compliance</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="border-bottom: 1.5px solid #000000;">
                                    <td style="padding: 6px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000; width: 62%;">Actual</td>
                                    <td style="padding: 6px 10px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center; width: 38%;">22</td>
                                </tr>
                                <tr style="border-bottom: 1.5px solid #000000;">
                                    <td style="padding: 6px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Required</td>
                                    <td style="padding: 6px 10px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">25</td>
                                </tr>
                                <tr style="border-bottom: 1.5px solid #000000;">
                                    <td style="padding: 6px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Gap</td>
                                    <td style="padding: 6px 10px; background-color: #ffffff; color: #dc2626; font-weight: 800; text-align: center;">3</td>
                                </tr>
                                <tr>
                                    <td style="padding: 6px 10px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 2px solid #000000;">Compliance</td>
                                    <td style="padding: 6px 10px; background-color: #ffffff; color: #15803d; font-weight: 800; text-align: center;">88%</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div>
                        {fig_staff_gauge_html}
                    </div>
                    <div>
                        {fig_staff_bar_html}
                    </div>
                </div>
            </div>

            <!-- Weekly Welfare & Training Sessions -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="glass-card p-5">
                    <h2 class="text-base font-semibold text-slate-800 mb-2">🎓 HSE Training Execution (29% Rate • 62 Attendees)</h2>
                    <div>{fig_train_html}</div>
                </div>
                <div class="glass-card p-5">
                    <h2 class="text-base font-semibold text-slate-800 mb-2">🤝 Weekly Worker Welfare Scores vs 90% Target</h2>
                    <div>{fig_w_html}</div>
                </div>
            </div>

        </div>
    </div>

    <!-- Footer -->
    <div class="text-center text-xs text-slate-400 py-4 border-t border-slate-200">
        GCDC HSE Performance Executive Dashboard • Kharafi National / SBARC • Develop by Abdul Latif HSE Analyst <a href="tel:+966530572691" class="text-slate-500 font-semibold no-underline">+966530572691</a>
    </div>
</body>
</html>"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated standalone HTML report: {output_path}")

if __name__ == "__main__":
    generate_html_report()
