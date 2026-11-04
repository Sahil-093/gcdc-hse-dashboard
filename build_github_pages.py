"""
Generates the exact Streamlit-equivalent single-page application for GitHub Pages.
Includes the authentic Streamlit Sidebar (navigation buttons + exact Excel sections),
Top Header Banner, dynamic tab/page routing in pure JS, and all 11 interactive page views.
"""

import os
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime

from hse_parser import parse_single_sheet_csv, CSV_PATH

def generate():
    data = parse_single_sheet_csv(CSV_PATH)
    
    # Helper to convert plotly figure to pure json/html embed
    def to_chart_html(fig, div_id):
        fig_json = fig.to_json()
        return f"""
        <div id="{div_id}" style="width: 100%; height: {fig.layout.height or 280}px;"></div>
        <script>
            (function() {{
                var spec = {fig_json};
                Plotly.newPlot('{div_id}', spec.data, spec.layout, {{responsive: true, displayModeBar: false}});
            }})();
        </script>
        """

    # Helper: Semicircular Speedometer
    def make_speedometer(title, slice_vals, slice_colors, needle_frac, div_id):
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
            height=240,
            margin=dict(l=10, r=10, t=45, b=10),
            xaxis=dict(range=[0, 1], visible=False),
            yaxis=dict(range=[0.38, 1.08], visible=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return to_chart_html(fig, div_id)

    # 1. Sidebar Charts
    fig_obs_sb = go.Figure(go.Bar(
        x=['Open', 'Closed', 'Overdue'], y=[8, 1242, 8],
        text=['8', '1242', '8'], textposition='outside',
        textfont=dict(size=12, color='#0d2640', weight='bold'),
        marker=dict(color='#0e5374', line=dict(color='#09384f', width=1.5)), width=0.45
    ))
    fig_obs_sb.update_layout(
        title=dict(text='<b>Site Observations</b>', font=dict(size=16, color='#0d2640'), x=0.5, xanchor='center'),
        yaxis=dict(range=[0, 1500], tickvals=[0, 300, 600, 900, 1200, 1500], gridcolor='#e2e8f0'),
        xaxis=dict(tickfont=dict(size=11, color='#0d2640', weight='bold')),
        height=220, margin=dict(l=35, r=15, t=35, b=25), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    obs_sb_chart_html = to_chart_html(fig_obs_sb, "chart_obs_sb")

    fig_ncr_sb = go.Figure(go.Bar(
        x=['Open', 'Closed', 'Overdue'], y=[2, 52, 2],
        text=['2', '52', '2'], textposition='outside',
        textfont=dict(size=12, color='#0d2640', weight='bold'),
        marker=dict(color='#0e5374', line=dict(color='#09384f', width=1.5)), width=0.45
    ))
    fig_ncr_sb.update_layout(
        title=dict(text='<b>NCRs</b>', font=dict(size=16, color='#0d2640'), x=0.5, xanchor='center'),
        yaxis=dict(range=[0, 65], tickvals=[0, 15, 30, 45, 60], gridcolor='#e2e8f0'),
        xaxis=dict(tickfont=dict(size=11, color='#0d2640', weight='bold')),
        height=220, margin=dict(l=35, r=15, t=35, b=25), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    ncr_sb_chart_html = to_chart_html(fig_ncr_sb, "chart_ncr_sb")

    fig_act_sb = go.Figure(go.Bar(
        x=['TBT', 'inspections', 'Campaigns'], y=[114, 6, 1],
        text=['114', '6', '1'], textposition='outside',
        textfont=dict(size=12, color='#0d2640', weight='bold'),
        marker=dict(color='#0e5374', line=dict(color='#09384f', width=1.5)), width=0.45
    ))
    fig_act_sb.update_layout(
        title=dict(text='<b>HSE Activities</b>', font=dict(size=16, color='#0d2640'), x=0.5, xanchor='center'),
        yaxis=dict(range=[0, 130], tickvals=[0, 30, 60, 90, 120], gridcolor='#e2e8f0'),
        xaxis=dict(tickfont=dict(size=11, color='#0d2640', weight='bold')),
        height=220, margin=dict(l=35, r=15, t=35, b=25), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    act_sb_chart_html = to_chart_html(fig_act_sb, "chart_act_sb")

    # 2. Home Page Charts
    fig_home_ltifr = go.Figure(go.Indicator(
        mode="gauge+number", value=0.00,
        title={'text': "<b>LTIFR</b><br><span style='font-size:11px;color:#64748b'>Lost Time Injury Rate (Zero Target)</span>", 'font': {'size': 14, 'color': '#0f172a'}},
        number={'font': {'size': 26, 'color': '#0f172a'}, 'valueformat': '.2f'},
        gauge={
            'axis': {'range': [0, 1.0], 'tickwidth': 1, 'tickcolor': '#94a3b8'},
            'bar': {'color': '#0284c7', 'thickness': 0.28},
            'steps': [{'range': [0, 0.01], 'color': '#86efac'}, {'range': [0.01, 0.2], 'color': '#fde047'}, {'range': [0.2, 1.0], 'color': '#fca5a5'}]
        }
    ))
    fig_home_ltifr.update_layout(height=210, margin=dict(l=15, r=15, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)')
    home_ltifr_html = to_chart_html(fig_home_ltifr, "chart_home_ltifr")

    fig_home_trir = go.Figure(go.Indicator(
        mode="gauge+number", value=0.258,
        title={'text': "<b>TRIR</b><br><span style='font-size:11px;color:#64748b'>Total Recordable Rate (&le;0.50 Good)</span>", 'font': {'size': 14, 'color': '#0f172a'}},
        number={'font': {'size': 26, 'color': '#0f172a'}, 'valueformat': '.3f'},
        gauge={
            'axis': {'range': [0, 1.5], 'tickwidth': 1, 'tickcolor': '#94a3b8'},
            'bar': {'color': '#0284c7', 'thickness': 0.28},
            'steps': [{'range': [0, 0.2], 'color': '#86efac'}, {'range': [0.2, 0.5], 'color': '#93c5fd'}, {'range': [0.5, 0.75], 'color': '#fde047'}, {'range': [0.75, 1.5], 'color': '#fca5a5'}]
        }
    ))
    fig_home_trir.update_layout(height=210, margin=dict(l=15, r=15, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)')
    home_trir_html = to_chart_html(fig_home_trir, "chart_home_trir")

    # Incident Donut
    inc_items = [
        {"Category": "Near Miss (NM)", "Count": 83, "Color": "#005a87"},
        {"Category": "Medical Treatment (MTC)", "Count": 8, "Color": "#f59e0b"},
        {"Category": "Motor Vehicle (MVA)", "Count": 5, "Color": "#ec4899"},
        {"Category": "Property Damage (PD)", "Count": 4, "Color": "#8b5cf6"},
        {"Category": "First Aid Case (FAC)", "Count": 2, "Color": "#10b981"},
        {"Category": "Lost Time Injury (LTI)", "Count": 0, "Color": "#ef4444"},
        {"Category": "Fatality (FAT)", "Count": 0, "Color": "#000000"}
    ]
    df_donut = pd.DataFrame([i for i in inc_items if i['Count'] > 0])
    fig_donut = px.pie(
        df_donut, names="Category", values="Count", hole=0.55,
        color="Category", color_discrete_map={row["Category"]: row["Color"] for row in inc_items}
    )
    fig_donut.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#ffffff', width=2)))
    fig_donut.update_layout(height=210, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
    home_donut_html = to_chart_html(fig_donut, "chart_home_donut")

    # Safe Man-Hours & Workforce Dynamics
    m_hours = data['safe_man_hours']['monthly']
    m_power = data['manpower']['monthly']
    chart_months = list(m_hours.keys())
    chart_hours = list(m_hours.values())
    chart_power = [m_power.get(m, 0) for m in chart_months]

    fig_dual = go.Figure()
    fig_dual.add_trace(go.Bar(
        x=chart_months, y=chart_hours, name="Monthly Safe Man-Hours",
        marker_color="#38bdf8", opacity=0.85, yaxis="y1"
    ))
    fig_dual.add_trace(go.Scatter(
        x=chart_months, y=chart_power, name="Average Daily Manpower",
        mode="lines+markers", line=dict(color="#f97316", width=3), marker=dict(size=8, color="#ea580c"), yaxis="y2"
    ))
    fig_dual.update_layout(
        height=280, margin=dict(l=40, r=40, t=20, b=25),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Safe Man-Hours", side="left", gridcolor="#f1f5f9"),
        yaxis2=dict(title="Daily Manpower", side="right", overlaying="y", showgrid=False),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified"
    )
    home_dual_html = to_chart_html(fig_dual, "chart_home_dual")

    # Staffing Gauge & Bar
    fig_staff_g = go.Figure(go.Indicator(
        mode="gauge+number", value=88,
        number={'suffix': "%", 'font': {'size': 32, 'color': '#0d2640', 'family': 'Inter, sans-serif'}},
        title={'text': "<b>Staffing Compliance</b><br><span style='font-size:12px;color:#64748b'>22 of 25 Staff On-Site</span>", 'font': {'size': 13, 'color': '#0d2640'}},
        gauge={
            'axis': {'range': [0, 100], 'tickvals': [0, 50, 80, 88, 100], 'ticktext': ['0%', '50%', '80%', '88%', '100%']},
            'bar': {'color': '#0284c7', 'thickness': 0.32},
            'steps': [{'range': [0, 80], 'color': '#fee2e2'}, {'range': [80, 95], 'color': '#fef3c7'}, {'range': [95, 100], 'color': '#dcfce7'}],
            'threshold': {'line': {'color': "#15803d", 'width': 3.5}, 'thickness': 0.8, 'value': 100}
        }
    ))
    fig_staff_g.update_layout(height=230, margin=dict(l=20, r=20, t=35, b=15), paper_bgcolor='rgba(0,0,0,0)')
    home_staff_g_html = to_chart_html(fig_staff_g, "chart_home_staff_g")

    fig_staff_b = go.Figure(go.Bar(
        x=['Actual', 'Required', 'Gap'], y=[22, 25, 3],
        text=['22', '25', '3'], textposition='outside',
        textfont=dict(size=14, color='#0d2640', weight='bold'),
        marker=dict(color=['#0e5374', '#15803d', '#dc2626'], line=dict(color=['#09384f', '#166534', '#991b1b'], width=1.5)),
        width=0.45
    ))
    fig_staff_b.update_layout(
        title=dict(text='<b>Staffing Headcount</b>', font=dict(size=15, color='#0d2640'), x=0.5, xanchor='center'),
        yaxis=dict(title=dict(text='Personnel', font=dict(size=11, color='#0d2640')), range=[0, 30], tickvals=[0, 5, 10, 15, 20, 25], gridcolor='#e2e8f0'),
        xaxis=dict(tickfont=dict(size=12, color='#0d2640', weight='bold')),
        height=230, margin=dict(l=35, r=15, t=40, b=25), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    home_staff_b_html = to_chart_html(fig_staff_b, "chart_home_staff_b")

    # 3. Rates Page Speedometers
    rates_lti_speedo_html = make_speedometer(
        title="LTIFR",
        slice_vals=[0.05, 0.45, 0.50, 1.00],
        slice_colors=['#196b24', '#4ea72e', '#ffc000', '#ff0000'],
        needle_frac=0.01,
        div_id="chart_rates_speedo_lti"
    )
    rates_tri_speedo_html = make_speedometer(
        title="TRIR",
        slice_vals=[0.06, 0.16, 0.18, 0.40, 0.40],
        slice_colors=['#196b24', '#4ea72e', '#ffff00', '#e97132', '#ff0000'],
        needle_frac=0.18,
        div_id="chart_rates_speedo_tri"
    )

    # Benchmark bar chart
    fig_bench = go.Figure(go.Bar(
        x=["GCDC Actual (TRIR)", "World-Class Threshold", "Industry Average", "High Risk Threshold"],
        y=[0.26, 0.50, 1.40, 2.50],
        text=["<b>0.26</b>", "<b>0.50</b>", "<b>1.40</b>", "<b>2.50</b>"],
        textposition='outside', textfont=dict(size=13, weight='bold'),
        marker=dict(color=["#15803d", "#0284c7", "#f59e0b", "#dc2626"], line=dict(color='#0f172a', width=1.2)), width=0.45
    ))
    fig_bench.update_layout(
        height=260, yaxis=dict(range=[0, 3.0], title="Recordable Rate (per 200k hrs)", gridcolor="#e2e8f0"),
        xaxis=dict(tickfont=dict(size=11, color="#0f172a")), margin=dict(l=35, r=25, t=25, b=25),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    rates_bench_html = to_chart_html(fig_bench, "chart_rates_bench")

    # 4. Incidents Bar & Funnel Pyramid
    fig_inc_bar = go.Figure(go.Bar(
        x=["NM", "MTC", "MVA", "FAC", "PD", "FAT", "RWC", "LTI"],
        y=[83, 8, 5, 2, 4, 0, 0, 0],
        text=[83, 8, 5, 2, 4, 0, 0, 0],
        textposition='outside', textfont=dict(size=13, color='#0f172a', weight='bold'),
        marker=dict(color=["#005a87", "#005a87", "#005a87", "#005a87", "#005a87", "#94a3b8", "#94a3b8", "#94a3b8"], line=dict(color='#003853', width=1.5)), width=0.45
    ))
    fig_inc_bar.update_layout(
        title=dict(text="<b>Incidents</b>", font=dict(size=18, color='#0d233a'), x=0.5, xanchor='center'),
        height=320, margin=dict(l=30, r=20, t=45, b=25),
        yaxis=dict(range=[0, 105], tickvals=[0, 20, 40, 60, 80, 100], gridcolor='#e2e8f0'),
        xaxis=dict(tickfont=dict(size=12, color='#0f172a', weight='bold')),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    inc_bar_html = to_chart_html(fig_inc_bar, "chart_inc_bar")

    pyr_levels = ["Fatalities", "Lost Time (LTI)", "Medical (MTC)", "Minor (FAC+MVA+PD)", "Near Misses (NM)"]
    pyr_counts = [0, 0, 8, 11, 83]
    pyr_labels = ["<b>0 Cases</b> (Zero / Safe)", "<b>0 Cases</b> (Zero / Safe)", "<b>8 Cases</b> (Managed)", "<b>11 Cases</b> (Minor)", "<b>83 Cases</b> (81.4% Base)"]
    fig_pyr = go.Figure(go.Funnel(
        y=pyr_levels, x=pyr_counts, text=pyr_labels, textposition="outside",
        textfont=dict(size=12, color="#0f172a", family="Inter, sans-serif"),
        marker=dict(color=["#0f172a", "#dc2626", "#ea580c", "#0284c7", "#10b981"], line=dict(color="#ffffff", width=2)),
        opacity=0.92, connector=dict(line=dict(color="#cbd5e1", width=1.5))
    ))
    fig_pyr.update_layout(height=320, margin=dict(l=150, r=180, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    inc_pyr_html = to_chart_html(fig_pyr, "chart_inc_pyr")

    # 5. Compliance Rate Page Gauge
    fig_comp_g = go.Figure(go.Indicator(
        mode="gauge+number", value=99.2,
        number={'suffix': "%", 'font': {'size': 32, 'color': '#0f2438'}},
        gauge={
            'axis': {'range': [0, 100], 'tickvals': [0, 50, 80, 95, 100], 'ticktext': ['0%', '50%', '80%', '95%', '100%']},
            'bar': {'color': '#16a34a', 'thickness': 0.35},
            'steps': [{'range': [0, 80], 'color': '#fee2e2'}, {'range': [80, 95], 'color': '#fef3c7'}, {'range': [95, 100], 'color': '#dcfce7'}],
            'threshold': {'line': {'color': "#15803d", 'width': 3}, 'thickness': 0.75, 'value': 95}
        }
    ))
    fig_comp_g.update_layout(height=180, margin=dict(l=20, r=20, t=20, b=10), paper_bgcolor='rgba(0,0,0,0)')
    comp_gauge_html = to_chart_html(fig_comp_g, "chart_comp_gauge")

    # 6. Monthly KPI & PSI Charts
    kpi_all_m = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October"]
    kpi_scores_val = [72, 70, 71, 88, 87, 88, 90, 89, 93, None]
    kpi_base_val = [90] * 10
    val_x = [i for i, v in enumerate(kpi_scores_val) if v is not None]
    val_y = [v for v in kpi_scores_val if v is not None]
    slope_k, intercept_k = np.polyfit(val_x, val_y, 1)
    kpi_trend_val = [round(slope_k * i + intercept_k, 1) for i in range(len(kpi_all_m))]

    fig_kpi = go.Figure()
    fig_kpi.add_trace(go.Scatter(x=kpi_all_m, y=kpi_base_val, mode='lines', name="Baseline (90%)", line=dict(color="#10b981", width=2, dash="dash")))
    fig_kpi.add_trace(go.Scatter(x=kpi_all_m, y=kpi_trend_val, mode='lines', name="Linear Trendline", line=dict(color="#ef4444", width=2.5, dash="dot")))
    fig_kpi.add_trace(go.Scatter(
        x=kpi_all_m, y=kpi_scores_val, mode='lines+markers+text', name="KPI Score",
        line=dict(color="#005b82", width=3.8), marker=dict(size=8, color="#005b82", line=dict(color="#ffffff", width=2)),
        text=[f"<b>{s:.0f}%</b>" if s is not None else "" for s in kpi_scores_val], textposition="top center", textfont=dict(size=11, color="#0f172a")
    ))
    fig_kpi.update_layout(
        title=dict(text="<b>KPI</b>", font=dict(size=20, color="#0d233a"), x=0.5, xanchor="center"),
        height=300, yaxis=dict(range=[0, 105], tickvals=[0, 20, 40, 60, 80, 100], ticktext=['0%', '20%', '40%', '60%', '80%', '100%'], gridcolor="#f1f5f9"),
        xaxis=dict(tickangle=-45, tickfont=dict(size=11, color="#0f172a")), margin=dict(l=45, r=35, t=45, b=55),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    kpis_chart_html = to_chart_html(fig_kpi, "chart_kpis_score")

    psi_scores_val = [60, 58, 59, 67, 66, 67, 69, 68, 75, None]
    val_px = [i for i, v in enumerate(psi_scores_val) if v is not None]
    val_py = [v for v in psi_scores_val if v is not None]
    slope_p, intercept_p = np.polyfit(val_px, val_py, 1)
    psi_trend_val = [round(slope_p * i + intercept_p, 1) for i in range(len(kpi_all_m))]

    fig_psi = go.Figure()
    fig_psi.add_trace(go.Scatter(x=kpi_all_m, y=kpi_base_val, mode='lines', name="Baseline (90%)", line=dict(color="#10b981", width=2, dash="dash")))
    fig_psi.add_trace(go.Scatter(x=kpi_all_m, y=psi_trend_val, mode='lines', name="Linear Trendline", line=dict(color="#ef4444", width=2.5, dash="dot")))
    fig_psi.add_trace(go.Scatter(
        x=kpi_all_m, y=psi_scores_val, mode='lines+markers+text', name="PSI/PCI Score",
        line=dict(color="#005b82", width=3.8), marker=dict(size=8, color="#005b82", line=dict(color="#ffffff", width=2)),
        text=[f"<b>{s:.0f}%</b>" if s is not None else "" for s in psi_scores_val], textposition="top center", textfont=dict(size=11, color="#0f172a")
    ))
    fig_psi.update_layout(
        title=dict(text="<b>PSI/PCI</b>", font=dict(size=20, color="#0d233a"), x=0.5, xanchor="center"),
        height=300, yaxis=dict(range=[0, 95], tickvals=[0, 20, 40, 60, 80], ticktext=['0%', '20%', '40%', '60%', '80%'], gridcolor="#f1f5f9"),
        xaxis=dict(tickangle=-45, tickfont=dict(size=11, color="#0f172a")), margin=dict(l=45, r=35, t=45, b=55),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    kpis_psi_html = to_chart_html(fig_psi, "chart_kpis_psi")

    # 7. Training & Welfare Charts
    t_m = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
    t_v = [2, 0, 0, 0, 0, 0, 2, 0, 1, 0, 0]
    t_tgt = [2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2]
    fig_train = go.Figure()
    fig_train.add_trace(go.Bar(
        x=t_m, y=t_v, text=[str(v) if v > 0 else "" for v in t_v], textposition='outside',
        textfont=dict(size=12, color="#0d233a", weight="bold"),
        marker=dict(color="#005a87", line=dict(color="#003853", width=1.5)), width=0.4, name="Conducted"
    ))
    fig_train.add_trace(go.Scatter(x=t_m, y=t_tgt, mode='lines', name="Target", line=dict(color="#ef4444", width=2, dash="dash")))
    fig_train.update_layout(
        title=dict(text="<b>Training Sessions</b>", font=dict(size=18, color="#0d233a"), x=0.5, xanchor="center"),
        height=280, yaxis=dict(range=[0, 2.5], tickvals=[0, 1, 2], gridcolor="#f1f5f9"),
        xaxis=dict(tickfont=dict(size=11, color="#0f172a")), margin=dict(l=35, r=25, t=45, b=45),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    train_chart_html = to_chart_html(fig_train, "chart_train_sessions")

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
        title=dict(text="<b>Weekly Welfare Score Evolution</b>", font=dict(size=18, color="#0d233a"), x=0.5, xanchor="center"),
        height=280, yaxis=dict(range=[40, 105], title="Score (%)", gridcolor="#f1f5f9"),
        margin=dict(l=40, r=30, t=45, b=25), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    welfare_chart_html = to_chart_html(fig_w, "chart_welfare_weekly")

    # Safe Man-Hours Monthly Chart
    all_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    active_m = [m for m in all_months if m in m_hours]
    active_v = [m_hours[m] for m in active_m]
    fig_hours_bar = go.Figure(go.Bar(
        x=active_m, y=active_v, text=[f"<b>{v:,.0f}</b>" for v in active_v], textposition='outside',
        textfont=dict(size=11, color='#0f172a'), marker=dict(color='#0284c7', line=dict(color='#0f172a', width=1.5)), width=0.55
    ))
    fig_hours_bar.update_layout(
        title=dict(text='<b>Monthly Safe Man-Hours</b>', font=dict(size=18, color='#0d2640'), x=0.5, xanchor='center'),
        yaxis=dict(range=[0, 600000], tickvals=[0, 100000, 200000, 300000, 400000, 500000], gridcolor='#e2e8f0'),
        xaxis=dict(tickfont=dict(size=12, color='#0f172a')), height=300, margin=dict(l=40, r=20, t=45, b=30),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    workforce_bar_html = to_chart_html(fig_hours_bar, "chart_workforce_bar")

    # Build the full HTML Document
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GCDC HSE Performance Executive Dashboard • Abdul Latif</title>
    <link rel="icon" type="image/png" href="https://img.icons8.com/fluency/96/shield.png">
    <!-- Plotly CDN -->
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Segoe+UI:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f8fafc;
            color: #0f172a;
            display: flex;
            min-height: 100vh;
        }}
        
        /* STREAMLIT AUTHENTIC SIDEBAR */
        #sidebar {{
            width: 340px;
            min-width: 340px;
            background-color: #f1f5f9;
            border-right: 1px solid #e2e8f0;
            height: 100vh;
            position: sticky;
            top: 0;
            overflow-y: auto;
            padding: 20px 18px 40px 18px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            z-index: 100;
        }}
        
        /* Mobile Hamburger */
        #mobile-toggle {{
            display: none;
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #0284c7;
            color: white;
            border: none;
            border-radius: 50%;
            width: 54px;
            height: 54px;
            font-size: 24px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.25);
            cursor: pointer;
            z-index: 200;
            align-items: center;
            justify-content: center;
        }}

        /* Sidebar Brand */
        .sidebar-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid #cbd5e1;
        }}
        .sidebar-brand img {{
            width: 44px;
            height: 44px;
        }}
        .sidebar-brand h3 {{
            font-size: 17px;
            font-weight: 800;
            color: #0f2438;
            line-height: 1.2;
        }}
        .sidebar-brand p {{
            font-size: 11.5px;
            color: #64748b;
            font-weight: 500;
        }}

        .nav-section-title {{
            font-size: 11px;
            font-weight: 800;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 4px;
        }}

        /* Streamlit Button Styling */
        .nav-btn {{
            width: 100%;
            text-align: left;
            padding: 9px 12px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.18s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            background: #ffffff;
            color: #0f172a;
            border: 1px solid #cbd5e1;
            margin-bottom: 4px;
        }}
        .nav-btn:hover {{
            background: #f0f9ff;
            border-color: #38bdf8;
            color: #0284c7;
        }}
        .nav-btn.active {{
            background: #0284c7;
            color: #ffffff;
            border-color: #0284c7;
            font-weight: 700;
            box-shadow: 0 2px 6px rgba(2, 132, 199, 0.25);
        }}

        /* Sidebar Sub Info */
        .sub-info-badge {{
            background: #e2e8f0;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            color: #334155;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        /* MAIN CONTENT AREA */
        #main-area {{
            flex: 1;
            padding: 24px 32px 50px 32px;
            max-width: calc(100vw - 340px);
            overflow-y: auto;
        }}

        /* Top Executive Header */
        .main-header {{
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
        }}
        .main-header h1 {{
            font-size: 22px;
            font-weight: 800;
            margin: 0 0 4px 0;
            color: #f8fafc;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .main-header p {{
            margin: 0;
            color: #94a3b8;
            font-size: 12.5px;
        }}
        .live-badge {{
            background: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
            padding: 5px 14px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 700;
            border: 1px solid rgba(56, 189, 248, 0.3);
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        /* KPI Cards Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
            margin-bottom: 22px;
        }}
        .kpi-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 16px 18px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 120px;
        }}
        .kpi-title {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            margin-bottom: 4px;
        }}
        .kpi-value {{
            font-size: 25px;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 4px;
        }}
        .kpi-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 700;
            width: fit-content;
        }}
        .badge-success {{ background: #dcfce7; color: #15803d; }}
        .badge-info {{ background: #e0f2fe; color: #0369a1; }}
        .badge-warning {{ background: #fef3c7; color: #b45309; }}
        .badge-danger {{ background: #fee2e2; color: #b91c1c; }}
        .metric-sub {{
            font-size: 11px;
            color: #64748b;
            margin-top: 4px;
            font-weight: 500;
        }}

        /* Section Cards */
        .section-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 22px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            margin-bottom: 22px;
        }}
        .section-title {{
            font-size: 16px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* Excel Styled Box / Card */
        .compliance-box {{
            border-radius: 8px;
            overflow: hidden;
            border: 1.5px solid #000000;
            box-shadow: 0 3px 8px rgba(0,0,0,0.08);
            max-width: 360px;
            margin: 0 auto 16px auto;
        }}
        .compliance-header {{
            background: #8fa0b5;
            color: #002060;
            font-size: 17px;
            font-weight: 800;
            text-align: center;
            padding: 10px 14px;
            border-bottom: 1.5px solid #000000;
        }}
        .compliance-value-block {{
            background: #002060;
            color: #ffffff;
            font-size: 48px;
            font-weight: 800;
            text-align: center;
            padding: 14px 10px 4px 10px;
            line-height: 1;
        }}
        .compliance-subtext {{
            background: #002060;
            color: #94a3b8;
            font-size: 12px;
            text-align: center;
            padding-bottom: 14px;
            font-weight: 600;
        }}

        .yellow-note-box {{
            background: #fef08a;
            color: #713f12;
            border: 1px solid #fde047;
            border-radius: 8px;
            padding: 14px 16px;
            font-size: 13px;
            line-height: 1.5;
            font-weight: 600;
            margin-top: 18px;
        }}

        .excel-table-box {{
            border: 1.5px solid #000000;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        }}
        .excel-table-header {{
            background: #002060;
            color: white;
            text-align: center;
            font-weight: 800;
            font-size: 14.5px;
            padding: 8px 12px;
            border-bottom: 1.5px solid #000000;
        }}
        .excel-table-row {{
            display: flex;
            border-bottom: 1px solid #000000;
        }}
        .excel-table-row:last-child {{
            border-bottom: none;
        }}
        .excel-col-label {{
            flex: 1.1;
            background: #8fa0b5;
            color: #002060;
            font-weight: 700;
            font-size: 13px;
            padding: 7px 12px;
            display: flex;
            align-items: center;
            border-right: 1.5px solid #000000;
        }}
        .excel-col-value {{
            flex: 1;
            background: #ffffff;
            color: #000000;
            font-weight: 700;
            font-size: 14px;
            padding: 7px 12px;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .excel-total-label {{
            font-weight: 800;
            font-size: 13.5px;
        }}
        .excel-total-value {{
            font-weight: 800;
            font-size: 15px;
        }}

        /* PAGE VIEWS */
        .page-view {{
            display: none;
            animation: fadeIn 0.2s ease-in-out;
        }}
        .page-view.active {{
            display: block;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(4px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Responsive grid utilities */
        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
            gap: 20px;
        }}
        .grid-3 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
        }}

        /* Tabs inside pages */
        .tab-btn-row {{
            display: flex;
            gap: 8px;
            border-bottom: 2px solid #e2e8f0;
            margin-bottom: 18px;
        }}
        .tab-btn {{
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 600;
            background: transparent;
            border: none;
            cursor: pointer;
            color: #64748b;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
        }}
        .tab-btn.active {{
            color: #0284c7;
            border-bottom-color: #0284c7;
            font-weight: 700;
        }}

        /* Footer */
        .app-footer {{
            margin-top: 40px;
            padding-top: 18px;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            font-size: 12px;
            color: #64748b;
            font-weight: 500;
        }}

        /* Responsive Mobile Styles */
        @media (max-width: 992px) {{
            #sidebar {{
                position: fixed;
                left: -350px;
                transition: left 0.3s ease;
                box-shadow: 4px 0 16px rgba(0,0,0,0.15);
            }}
            #sidebar.open {{
                left: 0;
            }}
            #mobile-toggle {{
                display: flex;
            }}
            #main-area {{
                max-width: 100vw;
                padding: 16px;
            }}
            .grid-2 {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>

    <!-- MOBILE HAMBURGER TOGGLE -->
    <button id="mobile-toggle" onclick="toggleSidebar()">☰</button>

    <!-- ========================================================================= -->
    <!-- 🧭 STREAMLIT LEFT SIDEBAR                                                 -->
    <!-- ========================================================================= -->
    <aside id="sidebar">
        <!-- Shield Brand -->
        <div class="sidebar-brand">
            <img src="https://img.icons8.com/fluency/96/shield.png" alt="Shield Logo">
            <div>
                <h3>GCDC HSE Hub</h3>
                <p>Kharafi National / SBARC</p>
            </div>
        </div>

        <!-- Navigation Buttons Header -->
        <div class="nav-section-title">📌 Navigation Pages</div>

        <!-- 11 Clean Navigation Buttons -->
        <nav id="nav-list">
            <button class="nav-btn active" onclick="switchPage('Home')">🏠 Main Home (Summary)</button>
            <button class="nav-btn" onclick="switchPage('Compliance')">📋 Compliance Rate %</button>
            <button class="nav-btn" onclick="switchPage('Observations')">🔍 Site Observations</button>
            <button class="nav-btn" onclick="switchPage('NCRs')">📑 NCRs Performance</button>
            <button class="nav-btn" onclick="switchPage('Activities')">🛠️ HSE Activities</button>
            <button class="nav-btn" onclick="switchPage('Incidents')">⚠️ Total Incidents Analysis</button>
            <button class="nav-btn" onclick="switchPage('Workforce')">⏱️ Safe Man-Hours & Workforce</button>
            <button class="nav-btn" onclick="switchPage('KPIs')">📈 Monthly KPI & Scores</button>
            <button class="nav-btn" onclick="switchPage('Training')">🎓 HSE Training Rate</button>
            <button class="nav-btn" onclick="switchPage('Rates')">🎯 Safety Rates (LTIFR / TRIR)</button>
            <button class="nav-btn" onclick="switchPage('Welfare')">🤝 Welfare & Proactive Safety</button>
        </nav>

        <!-- Current Page & Refresh -->
        <div class="sub-info-badge">
            <span>Current: <strong id="lbl-active-page">Home</strong></span>
            <button onclick="location.reload()" style="background:#0284c7; color:white; border:none; padding:4px 8px; border-radius:4px; font-size:11px; font-weight:700; cursor:pointer;">🔄 Refresh</button>
        </div>

        <hr style="border:none; border-top:1px solid #cbd5e1; margin:4px 0;">

        <!-- 1. Dedicated Site Observations Section in Left Side Panel -->
        <div style="background-color: #002060; color: #ffffff; padding: 7px 10px; border-radius: 4px; font-weight: 800; font-size: 13px; text-align: center; letter-spacing: 0.5px; border: 1.5px solid #001030;">
            🔍 SITE OBSERVATION (EXCEL)
        </div>

        <!-- Table 1: Status Counts -->
        <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000000; font-size: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
            <thead>
                <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #000000;">
                    <th colspan="2" style="padding: 5px; text-align: center; font-size: 13px; font-weight: 800;">Site Observation</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid #000000;">
                    <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000; width: 62%;">Open</td>
                    <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">8</td>
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

        <!-- Table 2: Rates & Performance -->
        <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000000; font-size: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
            <thead>
                <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #000000;">
                    <th colspan="2" style="padding: 5px; text-align: center; font-size: 13px; font-weight: 800;">Site Observation</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid #000000;">
                    <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000; width: 62%;">Closure Rate</td>
                    <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">99%</td>
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

        <!-- Sidebar Obs Bar Chart -->
        {obs_sb_chart_html}

        <hr style="border:none; border-top:1px solid #cbd5e1; margin:4px 0;">

        <!-- 2. Dedicated NCRs Section in Left Side Panel -->
        <div style="background-color: #002060; color: #ffffff; padding: 7px 10px; border-radius: 4px; font-weight: 800; font-size: 13px; text-align: center; letter-spacing: 0.5px; border: 1.5px solid #001030;">
            📑 NCRs SECTION (EXCEL)
        </div>

        <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000000; font-size: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
            <thead>
                <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #000000;">
                    <th colspan="2" style="padding: 5px; text-align: center; font-size: 13px; font-weight: 800;">NCRs</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid #000000;">
                    <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000; width: 62%;">Open</td>
                    <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">2</td>
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

        <!-- Sidebar NCR Bar Chart -->
        {ncr_sb_chart_html}

        <hr style="border:none; border-top:1px solid #cbd5e1; margin:4px 0;">

        <!-- 3. Dedicated HSE Activities Section in Left Side Panel -->
        <div style="background-color: #002060; color: #ffffff; padding: 7px 10px; border-radius: 4px; font-weight: 800; font-size: 13px; text-align: center; letter-spacing: 0.5px; border: 1.5px solid #001030;">
            🛠️ HSE ACTIVITIES (EXCEL)
        </div>

        <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000000; font-size: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
            <thead>
                <tr style="background-color: #002060; color: #ffffff; border-bottom: 1px solid #ffffff;">
                    <th colspan="2" style="padding: 5px; text-align: center; font-size: 13px; font-weight: 800;">HSE Activities</th>
                </tr>
                <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #000000;">
                    <th style="padding: 4px 8px; text-align: center; font-size: 11px; font-weight: 700; border-right: 1.5px solid #ffffff; width: 60%;">Activity</th>
                    <th style="padding: 4px 8px; text-align: center; font-size: 11px; font-weight: 700; width: 40%;">Quantity</th>
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

        <!-- Sidebar HSE Activities Bar Chart -->
        {act_sb_chart_html}

        <hr style="border:none; border-top:1px solid #cbd5e1; margin:4px 0;">

        <!-- 4. Dedicated HSE Staffing Compliance Section in Left Side Panel -->
        <div style="background-color: #002060; color: #ffffff; padding: 7px 10px; border-radius: 4px; font-weight: 800; font-size: 13px; text-align: center; letter-spacing: 0.5px; border: 1.5px solid #001030;">
            👥 HSE STAFFING COMPLIANCE
        </div>

        <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #000000; font-size: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
            <thead>
                <tr style="background-color: #002060; color: #ffffff; border-bottom: 1.5px solid #000000;">
                    <th colspan="2" style="padding: 5px; text-align: center; font-size: 13px; font-weight: 800;">HSE Staffing Compliance</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid #000000;">
                    <td style="padding: 5px 8px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 1.5px solid #000000; width: 62%;">Actual</td>
                    <td style="padding: 5px 8px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">22</td>
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
    </aside>

    <!-- ========================================================================= -->
    <!-- 📊 MAIN CONTENT CONTAINER                                                 -->
    <!-- ========================================================================= -->
    <main id="main-area">

        <!-- Top Executive Header Banner -->
        <header class="main-header">
            <div>
                <h1>🛡️ GCDC HSE Performance Executive Dashboard</h1>
                <p>Comprehensive Safety, Health & Environmental Metrics • Single Consolidated Sheet View</p>
            </div>
            <div>
                <span class="live-badge">🟢 Live Sheet Active</span>
            </div>
        </header>

        <!-- ===================================================================== -->
        <!-- 🏠 PAGE 1: MAIN HOME (SUMMARY)                                        -->
        <!-- ===================================================================== -->
        <section id="page-Home" class="page-view active">
            <h2 style="font-size:20px; font-weight:800; color:#0f172a; margin-bottom:4px;">🏠 Executive Overview & KPI Summary</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Consolidated project safety dashboard across all functional HSE domains</p>

            <!-- 6 KPI CARDS -->
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Compliance Rate</div>
                    <div class="kpi-value" style="color:#15803d;">99.2%</div>
                    <span class="kpi-badge badge-success">Target &ge; 95%</span>
                    <div class="metric-sub">1,416 / 1,427 Closed</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Total Incidents</div>
                    <div class="kpi-value" style="color:#0284c7;">102</div>
                    <span class="kpi-badge badge-info">81% Near Misses</span>
                    <div class="metric-sub">Zero Fatalities / Zero LTI</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Safe Man-Hours</div>
                    <div class="kpi-value">6,201,138</div>
                    <span class="kpi-badge badge-success">Cumulative</span>
                    <div class="metric-sub">Prior: 2,916,176 hrs</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Training Execution</div>
                    <div class="kpi-value" style="color:#b45309;">97.4%</div>
                    <span class="kpi-badge badge-warning">5 of 17 Sessions</span>
                    <div class="metric-sub">62 Attendees Logged</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">LTIFR</div>
                    <div class="kpi-value" style="color:#15803d;">0.00</div>
                    <span class="kpi-badge badge-success">Excellent</span>
                    <div class="metric-sub">Target: 0.00</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">TRIR</div>
                    <div class="kpi-value" style="color:#0284c7;">0.26</div>
                    <span class="kpi-badge badge-info">Good (&le;0.50)</span>
                    <div class="metric-sub">Industry Benchmark</div>
                </div>
            </div>

            <!-- GAUGES & INCIDENT DISTRIBUTION -->
            <div class="grid-2">
                <div class="section-card">
                    <div class="section-title">🎯 Safety Frequency Rates (Gauges)</div>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                        <div>{home_ltifr_html}</div>
                        <div>{home_trir_html}</div>
                    </div>
                </div>
                <div class="section-card">
                    <div class="section-title">🚨 Incident Severity Distribution (102 Recorded Cases)</div>
                    <div>{home_donut_html}</div>
                </div>
            </div>

            <!-- SAFE MAN-HOURS & DAILY WORKFORCE -->
            <div class="section-card">
                <div class="section-title">⏱️ Monthly Safe Man-Hours & Daily Workforce Dynamics (Jan – Sep 2026)</div>
                <div>{home_dual_html}</div>
            </div>

            <!-- HSE STAFFING COMPLIANCE & CAPACITY ANALYTICS -->
            <div class="section-card">
                <div class="section-title">👥 HSE Staffing Compliance & Capacity Analytics (Excel Format)</div>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:18px; align-items:start;">
                    <div>
                        <div style="font-size:11px; font-weight:700; color:#64748b; margin-bottom:6px; text-transform:uppercase;">Excel Registry Table</div>
                        <table style="width: 100%; border-collapse: collapse; border: 2px solid #000000; font-size: 13.5px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
                            <thead>
                                <tr style="background-color: #002060; color: #ffffff; border-bottom: 2px solid #000000;">
                                    <th colspan="2" style="padding: 8px; text-align: center; font-size: 15px; font-weight: 800;">HSE Staffing Compliance</th>
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
                                    <td style="padding: 7px 12px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Gap</td>
                                    <td style="padding: 7px 12px; background-color: #ffffff; color: #dc2626; font-weight: 800; text-align: center; font-size: 15px;">3</td>
                                </tr>
                                <tr>
                                    <td style="padding: 7px 12px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 2px solid #000000;">Compliance</td>
                                    <td style="padding: 7px 12px; background-color: #ffffff; color: #15803d; font-weight: 800; text-align: center; font-size: 16px;">88%</td>
                                </tr>
                            </tbody>
                        </table>
                        <div style="margin-top: 10px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; font-size: 11.5px; color: #475569; line-height: 1.4;">
                            • <b>Formula:</b> (22 &divide; 25) &times; 100 = <b>88.0%</b><br>
                            • <b>Current Gap:</b> 3 Safety Positions in mobilization
                        </div>
                    </div>
                    <div>
                        <div style="font-size:11px; font-weight:700; color:#64748b; margin-bottom:6px; text-transform:uppercase;">Compliance Progress Meter</div>
                        {home_staff_g_html}
                    </div>
                    <div>
                        <div style="font-size:11px; font-weight:700; color:#64748b; margin-bottom:6px; text-transform:uppercase;">Headcount Distribution</div>
                        {home_staff_b_html}
                    </div>
                </div>

                <hr style="margin: 18px 0 14px 0; border: none; border-top: 1px dashed #e2e8f0;">

                <div class="grid-3">
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px;">
                        <div style="font-size:11px; color:#64748b; font-weight:700; text-transform:uppercase;">Toolbox Talks (TBT)</div>
                        <div style="font-size:20px; font-weight:800; color:#0f172a; margin:3px 0;">114 Sessions</div>
                        <div style="font-size:11px; color:#0284c7; font-weight:600;">Frontline Briefings</div>
                    </div>
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px;">
                        <div style="font-size:11px; color:#64748b; font-weight:700; text-transform:uppercase;">Formal Inspections</div>
                        <div style="font-size:20px; font-weight:800; color:#0f172a; margin:3px 0;">6 Audits</div>
                        <div style="font-size:11px; color:#15803d; font-weight:600;">Quality & Compliance</div>
                    </div>
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px;">
                        <div style="font-size:11px; color:#64748b; font-weight:700; text-transform:uppercase;">Safety Campaigns</div>
                        <div style="font-size:20px; font-weight:800; color:#0f172a; margin:3px 0;">1 Drive</div>
                        <div style="font-size:11px; color:#ea580c; font-weight:600;">Targeted Worker Awareness</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- ===================================================================== -->
        <!-- 📋 PAGE 2: COMPLIANCE RATE %                                          -->
        <!-- ===================================================================== -->
        <section id="page-Compliance" class="page-view">
            <h2 style="font-size:20px; font-weight:800; color:#0f172a; margin-bottom:4px;">📋 Compliance Rate % & Action Closure Analysis</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Detailed breakdown matching Excel Inspection and Action Closure Register</p>

            <div class="grid-2">
                <div class="section-card" style="text-align:center;">
                    <div class="section-title" style="justify-content:center;">Executive KPI Card</div>
                    <div class="compliance-box">
                        <div class="compliance-header">Compliance Rate</div>
                        <div class="compliance-value-block">99%</div>
                        <div class="compliance-subtext">1,416 of 1,427 Closed</div>
                    </div>
                </div>
                <div class="section-card">
                    <div class="section-title">Grand Compliance Progress Meter</div>
                    {comp_gauge_html}
                </div>
            </div>

            <div class="section-card">
                <div class="section-title">📊 Category-wise Action & Inspection Status</div>
                <div class="grid-3">
                    <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:16px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-weight:700; color:#166534; font-size:14px;">Observations</span>
                            <span style="background:#15803d; color:white; font-weight:700; font-size:12px; padding:2px 8px; border-radius:4px;">99%</span>
                        </div>
                        <div style="font-size:12px; color:#374151; margin-bottom:10px;">
                            <b>1,242</b> Closed &nbsp;|&nbsp; <b>8</b> Open &nbsp;|&nbsp; <b>1,250</b> Total
                        </div>
                        <div style="background:#dcfce7; border-radius:6px; height:8px; overflow:hidden;">
                            <div style="background:#15803d; width:99.4%; height:100%;"></div>
                        </div>
                    </div>
                    <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:16px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-weight:700; color:#166534; font-size:14px;">NCR (Non-Conformance)</span>
                            <span style="background:#15803d; color:white; font-weight:700; font-size:12px; padding:2px 8px; border-radius:4px;">96%</span>
                        </div>
                        <div style="font-size:12px; color:#374151; margin-bottom:10px;">
                            <b>52</b> Closed &nbsp;|&nbsp; <b>2</b> Open &nbsp;|&nbsp; <b>54</b> Total
                        </div>
                        <div style="background:#dcfce7; border-radius:6px; height:8px; overflow:hidden;">
                            <div style="background:#15803d; width:96.3%; height:100%;"></div>
                        </div>
                    </div>
                    <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:10px; padding:16px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-weight:700; color:#991b1b; font-size:14px;">Other Inspections / Audits</span>
                            <span style="background:#dc2626; color:white; font-weight:700; font-size:12px; padding:2px 8px; border-radius:4px;">50%</span>
                        </div>
                        <div style="font-size:12px; color:#991b1b; margin-bottom:10px;">
                            <b>1</b> Closed &nbsp;|&nbsp; <b style="color:#b91c1c;">1</b> Open &nbsp;|&nbsp; <b>2</b> Total
                        </div>
                        <div style="background:#fee2e2; border-radius:6px; height:8px; overflow:hidden;">
                            <div style="background:#dc2626; width:50%; height:100%;"></div>
                        </div>
                    </div>
                </div>

                <div class="yellow-note-box">
                    ⚠️ <b>Important Note:</b> The HSE completed activities in <b>T22</b> are included in the grand total closed performance rate.
                </div>
            </div>
        </section>

        <!-- ===================================================================== -->
        <!-- 🔍 PAGE 3: SITE OBSERVATIONS                                          -->
        <!-- ===================================================================== -->
        <section id="page-Observations" class="page-view">
            <h2 style="font-size:20px; font-weight:800; color:#0f172a; margin-bottom:4px;">🔍 Site Observations Performance & Field Rectification Tracking</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Complete breakdown matching the official Excel Site Observation register, closure analytics, and overdue rates</p>

            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Total Site Observations</div>
                    <div class="kpi-value">1,250</div>
                    <span class="kpi-badge badge-info">YTD Field Logs</span>
                    <div class="metric-sub">Cumulative Action Items</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Closed Observations</div>
                    <div class="kpi-value" style="color:#15803d;">1,242</div>
                    <span class="kpi-badge badge-success">99% Closure Rate</span>
                    <div class="metric-sub">World-Class Resolution Rate</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Active Open Observations</div>
                    <div class="kpi-value" style="color:#0284c7;">8</div>
                    <span class="kpi-badge badge-info">Under Rectification</span>
                    <div class="metric-sub">Immediate Field Actions</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Overdue (OD) Observations</div>
                    <div class="kpi-value" style="color:#dc2626;">8</div>
                    <span class="kpi-badge badge-danger">1.4% OD Rate</span>
                    <div class="metric-sub">Target &le; 5% Achieved</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Closed On-Time (OTC)</div>
                    <div class="kpi-value">25</div>
                    <span class="kpi-badge badge-success">2% OTC Rate</span>
                    <div class="metric-sub">On-Time Closed Logs</div>
                </div>
            </div>

            <div class="section-card">
                <div class="section-title">📊 Observations Visual Distribution & Status Analysis</div>
                {obs_sb_chart_html}
            </div>
        </section>

        <!-- ===================================================================== -->
        <!-- 📑 PAGE 4: NCRS PERFORMANCE                                           -->
        <!-- ===================================================================== -->
        <section id="page-NCRs" class="page-view">
            <h2 style="font-size:20px; font-weight:800; color:#0f172a; margin-bottom:4px;">📑 Non-Conformance Reports (NCRs) Performance</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Engineering, quality, and environmental non-conformance closure compliance</p>

            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Total NCRs Issued</div>
                    <div class="kpi-value">54</div>
                    <span class="kpi-badge badge-info">YTD Log</span>
                    <div class="metric-sub">Quality & Safety NCRs</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Closed NCRs</div>
                    <div class="kpi-value" style="color:#15803d;">52</div>
                    <span class="kpi-badge badge-success">96% Closure Rate</span>
                    <div class="metric-sub">Target &ge; 90%</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Active Open NCRs</div>
                    <div class="kpi-value" style="color:#0284c7;">2</div>
                    <span class="kpi-badge badge-warning">Under Review</span>
                    <div class="metric-sub">Corrective Action Pending</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Overdue NCRs</div>
                    <div class="kpi-value" style="color:#dc2626;">2</div>
                    <span class="kpi-badge badge-danger">4.0% OD Rate</span>
                    <div class="metric-sub">Low Risk Level</div>
                </div>
            </div>

            <div class="section-card">
                <div class="section-title">📊 NCRs Visual Resolution Trajectory</div>
                {ncr_sb_chart_html}
            </div>
        </section>

        <!-- ===================================================================== -->
        <!-- 🛠️ PAGE 5: HSE ACTIVITIES                                             -->
        <!-- ===================================================================== -->
        <section id="page-Activities" class="page-view">
            <h2 style="font-size:20px; font-weight:800; color:#0f172a; margin-bottom:4px;">🛠️ HSE Completed Activities Register</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Field execution tracking across Toolbox Talks, formal inspections, and safety campaigns</p>

            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Total HSE Engagements</div>
                    <div class="kpi-value">121</div>
                    <span class="kpi-badge badge-success">High Engagement</span>
                    <div class="metric-sub">All Site Activities</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Toolbox Talks (TBT)</div>
                    <div class="kpi-value" style="color:#0284c7;">114</div>
                    <span class="kpi-badge badge-info">94.2% of Total</span>
                    <div class="metric-sub">Daily Shift Briefings</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Formal Inspections</div>
                    <div class="kpi-value" style="color:#15803d;">6</div>
                    <span class="kpi-badge badge-success">Audits Logged</span>
                    <div class="metric-sub">Comprehensive Checks</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Safety Campaigns</div>
                    <div class="kpi-value" style="color:#ea580c;">1</div>
                    <span class="kpi-badge badge-warning">Drive Complete</span>
                    <div class="metric-sub">Site Heat Stress Campaign</div>
                </div>
            </div>

            <div class="section-card">
                <div class="section-title">📊 Activities Volume Distribution</div>
                {act_sb_chart_html}
            </div>
        </section>

        <!-- ===================================================================== -->
        <!-- ⚠️ PAGE 6: TOTAL INCIDENTS ANALYSIS                                   -->
        <!-- ===================================================================== -->
        <section id="page-Incidents" class="page-view">
            <h2 style="font-size:20px; font-weight:800; color:#0f172a; margin-bottom:4px;">⚠️ Total Incidents Breakdown & Severity Analysis</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Complete breakdown matching the project incident registry and classification register</p>

            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Total Incidents</div>
                    <div class="kpi-value">102</div>
                    <span class="kpi-badge badge-info">YTD 2026 Log</span>
                    <div class="metric-sub">All Classifications</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Near Misses (NM)</div>
                    <div class="kpi-value" style="color:#15803d;">83</div>
                    <span class="kpi-badge badge-success">81.4% of Total</span>
                    <div class="metric-sub">Proactive Reporting</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">MTC + MVA Cases</div>
                    <div class="kpi-value" style="color:#b45309;">13</div>
                    <span class="kpi-badge badge-warning">8 MTC • 5 MVA</span>
                    <div class="metric-sub">Managed & Investigated</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">FAC + PD Cases</div>
                    <div class="kpi-value" style="color:#0284c7;">6</div>
                    <span class="kpi-badge badge-info">2 FAC • 4 PD</span>
                    <div class="metric-sub">Treated & Rectified</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">LTI / FAT / RWC</div>
                    <div class="kpi-value" style="color:#15803d;">0</div>
                    <span class="kpi-badge badge-success">Zero Incidents</span>
                    <div class="metric-sub">World-Class Milestone</div>
                </div>
            </div>

            <div class="grid-2">
                <div class="section-card">
                    <div class="section-title">📋 Total Incidents Registry (Excel Format)</div>
                    <div class="excel-table-box">
                        <div class="excel-table-header">Total Incidents</div>
                        <div class="excel-table-row"><div class="excel-col-label">NM</div><div class="excel-col-value">83</div></div>
                        <div class="excel-table-row"><div class="excel-col-label">MTC</div><div class="excel-col-value">8</div></div>
                        <div class="excel-table-row"><div class="excel-col-label">MVA</div><div class="excel-col-value">5</div></div>
                        <div class="excel-table-row"><div class="excel-col-label">FAC</div><div class="excel-col-value">2</div></div>
                        <div class="excel-table-row"><div class="excel-col-label">PD</div><div class="excel-col-value">4</div></div>
                        <div class="excel-table-row"><div class="excel-col-label">FAT</div><div class="excel-col-value" style="color:#16a34a;">0</div></div>
                        <div class="excel-table-row"><div class="excel-col-label">RWC</div><div class="excel-col-value" style="color:#16a34a;">0</div></div>
                        <div class="excel-table-row"><div class="excel-col-label">LTI</div><div class="excel-col-value" style="color:#16a34a;">0</div></div>
                        <div class="excel-table-row"><div class="excel-col-label excel-total-label">Total</div><div class="excel-col-value excel-total-value">102</div></div>
                    </div>
                </div>
                <div class="section-card">
                    <div class="section-title">📊 Incidents Chart</div>
                    {inc_bar_html}
                </div>
            </div>

            <div class="section-card">
                <div class="section-title">📐 Heinrich's Safety Pyramid (Visual Funnel Model)</div>
                {inc_pyr_html}
            </div>
        </section>

        <!-- ===================================================================== -->
        <!-- ⏱️ PAGE 7: SAFE MAN-HOURS & WORKFORCE                                 -->
        <!-- ===================================================================== -->
        <section id="page-Workforce" class="page-view">
            <h2 style="font-size:20px; font-weight:800; color:#0f172a; margin-bottom:4px;">⏱️ Safe Man-Hours & Workforce Analysis</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Month-by-month safe man-hours, prior historical hours, and workforce staffing</p>

            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Total Safe Man-Hours</div>
                    <div class="kpi-value">6,201,138</div>
                    <span class="kpi-badge badge-success">Cumulative Total</span>
                    <div class="metric-sub">Zero LTI Milestone</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">YTD 2026 Safe Hours</div>
                    <div class="kpi-value">3,284,962</div>
                    <span class="kpi-badge badge-info">Jan – Sep 2026</span>
                    <div class="metric-sub">Avg: 364,996 hrs/mo</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Hours Prior to 2026</div>
                    <div class="kpi-value">2,916,176</div>
                    <span class="kpi-badge badge-warning">Up to Dec 2025</span>
                    <div class="metric-sub">Baseline Carryover</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Average Daily Manpower</div>
                    <div class="kpi-value">1,244</div>
                    <span class="kpi-badge badge-success">Personnel On-Site</span>
                    <div class="metric-sub">Peak: 1,400 (Feb)</div>
                </div>
            </div>

            <div class="section-card">
                <div class="section-title">📊 Safe Man-Hours Executive Performance</div>
                {workforce_bar_html}
            </div>
        </section>

        <!-- ===================================================================== -->
        <!-- 📈 PAGE 8: MONTHLY KPI & SCORES                                       -->
        <!-- ===================================================================== -->
        <section id="page-KPIs" class="page-view">
            <h2 style="font-size:20px; font-weight:800; color:#0f172a; margin-bottom:4px;">📈 Monthly KPI & PSI Score Trends</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Proactive safety performance index and project safety implementation trends</p>

            <div class="grid-2">
                <div class="section-card">
                    <div class="section-title">📈 Monthly KPI Performance vs 90% Target</div>
                    {kpis_chart_html}
                </div>
                <div class="section-card">
                    <div class="section-title">📈 Monthly PSI/PCI Safety Index</div>
                    {kpis_psi_html}
                </div>
            </div>
        </section>

        <!-- ===================================================================== -->
        <!-- 🎓 PAGE 9: HSE TRAINING RATE                                          -->
        <!-- ===================================================================== -->
        <section id="page-Training" class="page-view">
            <h2 style="font-size:20px; font-weight:800; color:#0f172a; margin-bottom:4px;">🎓 HSE Training Execution & Competency Building</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Targeted safety training modules, certified attendees, and curriculum execution</p>

            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Overall Training Rate</div>
                    <div class="kpi-value" style="color:#b45309;">97.4%</div>
                    <span class="kpi-badge badge-warning">Target: 100%</span>
                    <div class="metric-sub">Curriculum Delivery</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Sessions Conducted</div>
                    <div class="kpi-value">5</div>
                    <span class="kpi-badge badge-info">Target: 17</span>
                    <div class="metric-sub">Classroom & Practical</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Trained Workers</div>
                    <div class="kpi-value" style="color:#15803d;">62</div>
                    <span class="kpi-badge badge-success">Certified Log</span>
                    <div class="metric-sub">Site Personnel Trained</div>
                </div>
            </div>

            <div class="section-card">
                <div class="section-title">📊 Monthly Training Sessions vs Target</div>
                {train_chart_html}
            </div>
        </section>

        <!-- ===================================================================== -->
        <!-- 🎯 PAGE 10: SAFETY RATES (LTIFR / TRIR)                               -->
        <!-- ===================================================================== -->
        <section id="page-Rates" class="page-view">
            <h2 style="font-size:20px; font-weight:800; color:#0f172a; margin-bottom:4px;">🎯 Safety Frequency Rates (LTIFR & TRIR)</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Lost Time Injury Frequency Rate & Total Recordable Incident Rate performance indices against international benchmarks</p>

            <!-- Status Rating Cards -->
            <div class="grid-2" style="margin-bottom:18px;">
                <div style="border: 2.5px solid #000000; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.06);">
                    <div style="background-color: #8fa0b5; color: #002060; font-weight: 800; font-size: 20px; text-align: center; padding: 10px; border-bottom: 2px solid #000000;">
                        LTIFR
                    </div>
                    <div style="background-color: #002060; color: #ffffff; font-weight: 800; font-size: 42px; text-align: center; padding: 14px; border-bottom: 2px solid #000000;">
                        0.00
                    </div>
                    <div style="background-color: #ffffff; color: #000000; font-weight: 700; font-size: 24px; text-align: center; padding: 12px; font-family: 'Times New Roman', Georgia, serif;">
                        Excellent
                    </div>
                </div>

                <div style="border: 2.5px solid #000000; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.06);">
                    <div style="background-color: #8fa0b5; color: #002060; font-weight: 800; font-size: 20px; text-align: center; padding: 10px; border-bottom: 2px solid #000000;">
                        TRIR
                    </div>
                    <div style="background-color: #002060; color: #ffffff; font-weight: 800; font-size: 42px; text-align: center; padding: 14px; border-bottom: 2px solid #000000;">
                        0.26
                    </div>
                    <div style="background-color: #ffffff; color: #000000; font-weight: 700; font-size: 24px; text-align: center; padding: 12px; font-family: 'Times New Roman', Georgia, serif;">
                        Good
                    </div>
                </div>
            </div>

            <!-- Registry & Speedometers (Left to Right: Green -> Yellow -> Red) -->
            <div class="grid-2">
                <div class="section-card">
                    <div class="section-title">📋 Safety Frequency Rates Registry (Excel Format)</div>
                    <table style="width: 100%; border-collapse: collapse; border: 2.5px solid #000000; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08); border-radius: 4px; overflow: hidden;">
                        <tbody>
                            <tr style="border-bottom: 2px solid #000000;">
                                <td style="padding: 14px 18px; background-color: #002060; color: #ffffff; font-weight: 800; font-size: 20px; border-right: 2px solid #000000; width: 50%;">LTIFR</td>
                                <td style="padding: 14px 18px; background-color: #196b24; color: #ffffff; font-weight: 800; font-size: 22px; text-align: center; width: 50%;">0.00</td>
                            </tr>
                            <tr>
                                <td style="padding: 14px 18px; background-color: #002060; color: #ffffff; font-weight: 800; font-size: 20px; border-right: 2px solid #000000;">TRIR</td>
                                <td style="padding: 14px 18px; background-color: #4ea72e; color: #ffffff; font-weight: 800; font-size: 22px; text-align: center;">0.26</td>
                            </tr>
                        </tbody>
                    </table>

                    <div style="margin-top: 18px; display: flex; flex-direction: column; gap: 12px;">
                        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 14px;">
                            <div style="font-size: 11px; font-weight: 700; color: #166534; text-transform: uppercase;">LTIFR Mathematical Formula</div>
                            <div style="font-size: 13px; color: #0f172a; margin-top: 4px; font-family: monospace; font-weight: 600;">
                                (0 LTI Cases &times; 200,000) &divide; 6,201,138 hrs = <b>0.000</b>
                            </div>
                            <div style="font-size: 11.5px; color: #15803d; margin-top: 4px;">
                                🏆 Zero lost time injuries recorded across 6.2 Million cumulative man-hours.
                            </div>
                        </div>
                        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px;">
                            <div style="font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase;">TRIR Mathematical Formula</div>
                            <div style="font-size: 13px; color: #0f172a; margin-top: 4px; font-family: monospace; font-weight: 600;">
                                (8 Recordable Cases &times; 200,000) &divide; 6,201,138 hrs = <b>0.258 (~0.26)</b>
                            </div>
                            <div style="font-size: 11.5px; color: #475569; margin-top: 4px;">
                                ✅ Safely below international benchmark target threshold (&le; 0.50).
                            </div>
                        </div>
                    </div>
                </div>

                <div class="section-card">
                    <div class="section-title">📊 Safety Rate Speedometer Gauges (Left ➔ Right: Green ➔ Red)</div>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
                        <div>
                            {rates_lti_speedo_html}
                            <div style="text-align: center; margin-top: -10px;">
                                <span style="background: #dcfce7; color: #166534; font-weight: 700; font-size: 11.5px; padding: 3px 10px; border-radius: 9999px; border: 1px solid #bbf7d0;">
                                    Target: 0.00 (Zero LTI)
                                </span>
                            </div>
                        </div>
                        <div>
                            {rates_tri_speedo_html}
                            <div style="text-align: center; margin-top: -10px;">
                                <span style="background: #e0f2fe; color: #0369a1; font-weight: 700; font-size: 11.5px; padding: 3px 10px; border-radius: 9999px; border: 1px solid #bae6fd;">
                                    Benchmark: &le; 0.50 (Good)
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- International Benchmarking -->
            <div class="section-card">
                <div class="section-title">⚖️ International Industry Benchmarking</div>
                {rates_bench_html}
            </div>
        </section>

        <!-- ===================================================================== -->
        <!-- 🤝 PAGE 11: WELFARE & PROACTIVE SAFETY                                -->
        <!-- ===================================================================== -->
        <section id="page-Welfare" class="page-view">
            <h2 style="font-size:20px; font-weight:800; color:#0f172a; margin-bottom:4px;">🤝 Welfare & Proactive Safety Initiatives</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Labor camp standards, site heat stress monitoring, and worker wellbeing index</p>

            <div class="section-card">
                <div class="section-title">📈 Weekly Welfare Score Monitoring (Benchmark &ge; 90%)</div>
                {welfare_chart_html}
            </div>
        </section>

        <!-- FOOTER -->
        <footer class="app-footer">
            <p><strong>GCDC HSE Performance Executive System</strong> • Data Source: Consolidated Sheet • Kharafi National / SBARC</p>
            <p style="margin-top: 4px; color: #0284c7; font-weight: 600;">Develop by Abdul Latif HSE Analyst +966530572691</p>
        </footer>

    </main>

    <!-- ===================================================================== -->
    <!-- INTERACTIVE PAGE ROUTING SCRIPT                                       -->
    <!-- ===================================================================== -->
    <script>
        function switchPage(pageKey) {{
            // Hide all pages
            var pages = document.querySelectorAll('.page-view');
            pages.forEach(function(p) {{
                p.classList.remove('active');
            }});

            // Show targeted page
            var target = document.getElementById('page-' + pageKey);
            if (target) {{
                target.classList.add('active');
            }}

            // Update nav buttons
            var btns = document.querySelectorAll('.nav-btn');
            btns.forEach(function(btn) {{
                if (btn.getAttribute('onclick') && btn.getAttribute('onclick').indexOf(pageKey) !== -1) {{
                    btn.classList.add('active');
                }} else {{
                    btn.classList.remove('active');
                }}
            }});

            // Update label
            var lbl = document.getElementById('lbl-active-page');
            if (lbl) {{
                lbl.innerText = pageKey;
            }}

            // Update URL hash without full reload
            if (history.pushState) {{
                history.pushState(null, null, '#' + pageKey.toLowerCase());
            }}

            // Trigger Plotly relayout to guarantee perfect sizing
            window.dispatchEvent(new Event('resize'));

            // On mobile close sidebar
            if (window.innerWidth <= 992) {{
                document.getElementById('sidebar').classList.remove('open');
            }}

            // Scroll main area to top
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        function toggleSidebar() {{
            var sb = document.getElementById('sidebar');
            sb.classList.toggle('open');
        }}

        // Handle direct deep-links like #rates or #incidents
        window.addEventListener('DOMContentLoaded', function() {{
            var hash = window.location.hash.replace('#', '').toLowerCase();
            var map = {{
                'home': 'Home',
                'compliance': 'Compliance',
                'observations': 'Observations',
                'ncrs': 'NCRs',
                'activities': 'Activities',
                'incidents': 'Incidents',
                'workforce': 'Workforce',
                'kpis': 'KPIs',
                'training': 'Training',
                'rates': 'Rates',
                'welfare': 'Welfare'
            }};
            if (hash && map[hash]) {{
                switchPage(map[hash]);
            }}
        }});
    </script>
</body>
</html>
"""
    output_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Successfully generated full Streamlit-equivalent SPA at {output_path} ({len(html):,} bytes)")

if __name__ == "__main__":
    generate()
