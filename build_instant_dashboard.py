"""
Builds the 100% instant-load (0.5 second) pre-rendered single-page dashboard.
Contains every single chart, table, KPI card, and tab from all 11 pages of app.py.
Zero loading bars, zero WebAssembly overhead, opens instantly on all devices.
"""

import os
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from hse_parser import parse_single_sheet_csv, CSV_PATH

def generate():
    data = parse_single_sheet_csv(CSV_PATH)

    def to_chart_html(fig, div_id):
        fig_json = fig.to_json()
        h = fig.layout.height or 280
        return f"""
        <div id="{div_id}" class="chart-container" style="width: 100%; min-height: {h}px;"></div>
        <script>
            (function() {{
                var spec = {fig_json};
                var config = {{
                    responsive: true,
                    displayModeBar: 'hover',
                    displaylogo: false,
                    modeBarButtonsToRemove: ['lasso2d', 'select2d']
                }};
                Plotly.newPlot('{div_id}', spec.data, spec.layout, config);
            }})();
        </script>
        """

    def make_svg_speedometer(title, slice_vals, slice_colors, needle_frac, badge_text, badge_color, badge_bg, badge_border):
        total_top = sum(slice_vals)
        cx, cy = 160, 142
        r_out = 100
        r_in = 68
        
        curr_angle = 180.0
        paths_svg = []
        for val, color in zip(slice_vals, slice_colors):
            span = 180.0 * (val / total_top)
            next_angle = max(0.0, curr_angle - span)
            
            a_rad = np.radians(curr_angle)
            b_rad = np.radians(next_angle)
            
            x1 = cx + r_out * np.cos(a_rad)
            y1 = cy - r_out * np.sin(a_rad)
            x2 = cx + r_out * np.cos(b_rad)
            y2 = cy - r_out * np.sin(b_rad)
            
            x3 = cx + r_in * np.cos(b_rad)
            y3 = cy - r_in * np.sin(b_rad)
            x4 = cx + r_in * np.cos(a_rad)
            y4 = cy - r_in * np.sin(a_rad)
            
            d = f"M {x1:.2f} {y1:.2f} A {r_out} {r_out} 0 0 1 {x2:.2f} {y2:.2f} L {x3:.2f} {y3:.2f} A {r_in} {r_in} 0 0 0 {x4:.2f} {y4:.2f} Z"
            paths_svg.append(f'<path d="{d}" fill="{color}" stroke="#ffffff" stroke-width="2"/>')
            curr_angle = next_angle
            
        paths_str = "".join(paths_svg)
        
        needle_deg = 180.0 - (180.0 * needle_frac)
        n_rad = np.radians(needle_deg)
        
        nx_tip = cx + (r_in - 2) * np.cos(n_rad)
        ny_tip = cy - (r_in - 2) * np.sin(n_rad)
        
        bx_in = cx + (r_in - 4) * np.cos(n_rad)
        by_in = cy - (r_in - 4) * np.sin(n_rad)
        bx_out = cx + (r_out + 5) * np.cos(n_rad)
        by_out = cy - (r_out + 5) * np.sin(n_rad)
        
        svg = f"""
        <div style="display:flex; flex-direction:column; align-items:center; width:100%; max-width:320px; margin:0 auto 10px auto;">
            <svg viewBox="0 0 320 165" width="100%" height="auto" style="overflow:visible; display:block;">
                <text x="160" y="24" text-anchor="middle" font-family="'Segoe UI', Inter, sans-serif" font-size="22" font-weight="800" fill="#0d2640">{title}</text>
                <g>{paths_str}</g>
                <line x1="{cx}" y1="{cy}" x2="{nx_tip:.2f}" y2="{ny_tip:.2f}" stroke="#000000" stroke-width="3" stroke-linecap="round"/>
                <line x1="{bx_in:.2f}" y1="{by_in:.2f}" x2="{bx_out:.2f}" y2="{by_out:.2f}" stroke="#000000" stroke-width="8" stroke-linecap="square"/>
                <circle cx="{cx}" cy="{cy}" r="5" fill="#000000"/>
            </svg>
            <div style="margin-top: 6px; text-align: center;">
                <span style="display:inline-block; background:{badge_bg}; color:{badge_color}; font-size:12px; font-weight:700; padding:4px 14px; border-radius:9999px; border:1px solid {badge_border}; font-family:'Segoe UI', Inter, sans-serif;">
                    {badge_text}
                </span>
            </div>
        </div>
        """
        return svg

    # --- SIDEBAR CHARTS ---
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
        yaxis=dict(title=dict(text='Num. of NCRs', font=dict(size=10, color='#0d2640')), range=[0, 65], tickvals=[0, 15, 30, 45, 60], gridcolor='#e2e8f0'),
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

    # --- DEDICATED MAIN PAGE CHARTS (Unique IDs & High Resolution) ---
    fig_obs_page = go.Figure(go.Bar(
        x=['Open', 'Closed', 'Overdue'], y=[8, 1242, 8],
        text=['8', '1242', '8'], textposition='outside',
        textfont=dict(size=15, color='#0d2640', weight='bold'),
        marker=dict(color='#0e5374', line=dict(color='#09384f', width=2)),
        width=0.42
    ))
    fig_obs_page.update_layout(
        title=dict(text='<b>Site Observations</b>', font=dict(size=22, color='#0d2640', family='Segoe UI, Inter, sans-serif'), x=0.5, xanchor='center'),
        yaxis=dict(range=[0, 1500], tickvals=[0, 200, 400, 600, 800, 1000, 1200, 1400], gridcolor='#e2e8f0', zerolinecolor='#cbd5e1'),
        xaxis=dict(tickfont=dict(size=14, color='#0d2640', weight='bold')),
        height=340, margin=dict(l=40, r=20, t=45, b=35), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    obs_page_chart_html = to_chart_html(fig_obs_page, "chart_obs_page")

    fig_ncr_page = go.Figure(go.Bar(
        x=['Open', 'Closed', 'Overdue'], y=[2, 52, 2],
        text=['2', '52', '2'], textposition='outside',
        textfont=dict(size=15, color='#0d2640', weight='bold'),
        marker=dict(color='#0e5374', line=dict(color='#09384f', width=2)),
        width=0.42
    ))
    fig_ncr_page.update_layout(
        title=dict(text='<b>NCRs</b>', font=dict(size=22, color='#0d2640', family='Segoe UI, Inter, sans-serif'), x=0.5, xanchor='center'),
        yaxis=dict(title=dict(text='Num. of NCRs', font=dict(size=12, color='#0d2640')), range=[0, 65], tickvals=[0, 15, 30, 45, 60], gridcolor='#e2e8f0'),
        xaxis=dict(tickfont=dict(size=14, color='#0d2640', weight='bold')),
        height=340, margin=dict(l=40, r=20, t=45, b=35), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    ncr_page_chart_html = to_chart_html(fig_ncr_page, "chart_ncr_page")

    fig_act_page = go.Figure(go.Bar(
        x=['TBT', 'inspections', 'Campaigns'], y=[114, 6, 1],
        text=['114', '6', '1'], textposition='outside',
        textfont=dict(size=15, color='#0d2640', weight='bold'),
        marker=dict(color='#0e5374', line=dict(color='#09384f', width=2)),
        width=0.42
    ))
    fig_act_page.update_layout(
        title=dict(text='<b>HSE Activities</b>', font=dict(size=22, color='#0d2640', family='Segoe UI, Inter, sans-serif'), x=0.5, xanchor='center'),
        yaxis=dict(range=[0, 130], tickvals=[0, 30, 60, 90, 120], gridcolor='#e2e8f0'),
        xaxis=dict(tickfont=dict(size=14, color='#0d2640', weight='bold')),
        height=340, margin=dict(l=40, r=20, t=45, b=35), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    act_page_chart_html = to_chart_html(fig_act_page, "chart_act_page")

    # --- HOME PAGE CHARTS ---
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

    # --- RATES PAGE SPEEDOMETERS (PRECISION SVG) ---
    rates_lti_speedo_html = make_svg_speedometer(
        title="LTIFR",
        slice_vals=[0.05, 0.45, 0.50, 1.00],
        slice_colors=['#196b24', '#4ea72e', '#ffc000', '#ff0000'],
        needle_frac=0.01,
        badge_text="Target: 0.00 (Zero LTI)",
        badge_color="#166534",
        badge_bg="#dcfce7",
        badge_border="#bbf7d0"
    )
    rates_tri_speedo_html = make_svg_speedometer(
        title="TRIR",
        slice_vals=[0.06, 0.16, 0.18, 0.40, 0.40],
        slice_colors=['#196b24', '#4ea72e', '#ffff00', '#e97132', '#ff0000'],
        needle_frac=0.18,
        badge_text="Benchmark: ≤ 0.50 (Good)",
        badge_color="#0369a1",
        badge_bg="#e0f2fe",
        badge_border="#bae6fd"
    )

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

    # --- INCIDENTS BAR & FUNNEL PYRAMID ---
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

    # --- COMPLIANCE GAUGE ---
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

    # --- MONTHLY KPIS & PSI CHARTS ---
    kpi_all_m = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October"]
    kpi_scores_val = [84, 81, 87, 90, 93, 85, 91, 68, 68, None]
    kpi_base_val = [90] * 10
    val_x = [i for i, v in enumerate(kpi_scores_val) if v is not None]
    val_y = [v for v in kpi_scores_val if v is not None]
    slope_k, intercept_k = np.polyfit(val_x, val_y, 1)
    kpi_trend_val = [round(slope_k * i + intercept_k, 1) for i in range(len(kpi_all_m))]

    fig_kpi = go.Figure()
    fig_kpi.add_trace(go.Scatter(x=kpi_all_m, y=kpi_base_val, mode='lines', name="Baseline (90%)", line=dict(color="#10b981", width=2, dash="dash"), hovertemplate='Baseline: <b>90%</b><extra></extra>'))
    fig_kpi.add_trace(go.Scatter(x=kpi_all_m, y=kpi_trend_val, mode='lines', name="Linear Trendline", line=dict(color="#ef4444", width=2.5, dash="dot"), hovertemplate='Trendline: <b>%{y:.1f}%</b><extra></extra>'))
    fig_kpi.add_trace(go.Scatter(
        x=kpi_all_m, y=kpi_scores_val, mode='lines+markers+text', name="Monthly KPI Score",
        line=dict(color="#005b82", width=3.8), marker=dict(size=9, color="#005b82", line=dict(color="#ffffff", width=2)),
        text=[f"<b>{s:.0f}%</b>" if s is not None else "" for s in kpi_scores_val], textposition="top center", textfont=dict(size=12, color="#0f172a"),
        cliponaxis=False, hovertemplate='<b>%{x}</b><br>KPI Score: <b>%{y}%</b><extra></extra>'
    ))
    fig_kpi.update_layout(
        title=dict(text="<b>KPI</b>", font=dict(size=22, color="#0d233a", family="Segoe UI, Inter, sans-serif"), x=0.5, xanchor="center"),
        height=435, yaxis=dict(range=[0, 105], tickvals=[0, 20, 40, 60, 80, 100], ticktext=['0%', '20%', '40%', '60%', '80%', '100%'], gridcolor="#e2e8f0"),
        xaxis=dict(tickangle=-45, tickfont=dict(size=12, color="#0f172a")), margin=dict(l=45, r=35, t=55, b=65),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    kpis_chart_html = to_chart_html(fig_kpi, "chart_kpis_score")

    psi_scores_val = [60, 58, 59, 67, 66, 67, 69, 68, 75, None]
    val_px = [i for i, v in enumerate(psi_scores_val) if v is not None]
    val_py = [v for v in psi_scores_val if v is not None]
    slope_p, intercept_p = np.polyfit(val_px, val_py, 1)
    psi_trend_val = [round(slope_p * i + intercept_p, 1) for i in range(len(kpi_all_m))]

    fig_psi = go.Figure()
    fig_psi.add_trace(go.Scatter(x=kpi_all_m, y=kpi_base_val, mode='lines', name="Baseline (90%)", line=dict(color="#10b981", width=2, dash="dash"), hovertemplate='Baseline: <b>90%</b><extra></extra>'))
    fig_psi.add_trace(go.Scatter(x=kpi_all_m, y=psi_trend_val, mode='lines', name="Linear Trendline", line=dict(color="#ef4444", width=2.5, dash="dot"), hovertemplate='Trendline: <b>%{y:.1f}%</b><extra></extra>'))
    fig_psi.add_trace(go.Scatter(
        x=kpi_all_m, y=psi_scores_val, mode='lines+markers+text', name="PSI/PCI Score",
        line=dict(color="#005b82", width=3.8), marker=dict(size=9, color="#005b82", line=dict(color="#ffffff", width=2)),
        text=[f"<b>{s:.0f}%</b>" if s is not None else "" for s in psi_scores_val], textposition="top center", textfont=dict(size=12, color="#0f172a"),
        cliponaxis=False, hovertemplate='<b>%{x}</b><br>PSI/PCI Score: <b>%{y}%</b><extra></extra>'
    ))
    fig_psi.update_layout(
        title=dict(text="<b>PSI/PCI</b>", font=dict(size=22, color="#0d233a", family="Segoe UI, Inter, sans-serif"), x=0.5, xanchor="center"),
        height=435, yaxis=dict(range=[0, 95], tickvals=[0, 20, 40, 60, 80], ticktext=['0%', '20%', '40%', '60%', '80%'], gridcolor="#e2e8f0"),
        xaxis=dict(tickangle=-45, tickfont=dict(size=12, color="#0f172a")), margin=dict(l=45, r=35, t=55, b=65),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    kpis_psi_html = to_chart_html(fig_psi, "chart_kpis_psi")

    # --- TRAINING & WELFARE ---
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

    # Complete Self-Contained HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GCDC HSE Performance Executive Dashboard • Abdul Latif</title>
    <link rel="icon" type="image/png" href="https://img.icons8.com/fluency/96/shield.png">
    
    <!-- Instant Plotly Library from CDN -->
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    
    <!-- Typography -->
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
        
        /* STREAMLIT SIDEBAR */
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
        
        #mobile-toggle {{
            display: none;
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #ff4b4b;
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
            background: #fff5f5;
            border-color: #fca5a5;
            color: #ef4444;
        }}
        .nav-btn.active {{
            background: #ff4b4b !important;
            color: #ffffff !important;
            border-color: #ff4b4b !important;
            font-weight: 700;
            box-shadow: 0 3px 10px rgba(255, 75, 75, 0.38) !important;
        }}

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

        /* MAIN CONTENT */
        #main-area {{
            flex: 1;
            padding: 24px 32px 50px 32px;
            max-width: calc(100vw - 340px);
            overflow-y: auto;
        }}

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

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
            gap: 12px;
            margin-bottom: 22px;
        }}
        .kpi-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 14px 16px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 115px;
            min-width: 140px;
            box-sizing: border-box;
        }}
        .kpi-title {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            margin-bottom: 4px;
            white-space: normal !important;
            word-break: normal !important;
            line-height: 1.25;
        }}
        .kpi-value {{
            font-size: 24px;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 4px;
            white-space: nowrap !important;
            word-break: keep-all !important;
            font-variant-numeric: tabular-nums;
        }}
        .kpi-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 700;
            width: fit-content;
            white-space: nowrap !important;
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

        .page-view {{
            display: none;
            animation: fadeIn 0.15s ease-in-out;
        }}
        .page-view.active {{
            display: block;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}

        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 18px;
        }}
        .grid-3 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
        }}

        .app-footer {{
            margin-top: 40px;
            padding-top: 18px;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            font-size: 12px;
            color: #64748b;
            font-weight: 500;
        }}

        /* MOBILE & TABLET STICKY TOPBAR */
        #mobile-topbar {{
            display: none;
            position: sticky;
            top: 0;
            left: 0;
            right: 0;
            background: #0f172a;
            color: white;
            padding: 10px 14px;
            z-index: 500;
            border-bottom: 1px solid #334155;
            box-shadow: 0 2px 10px rgba(0,0,0,0.15);
            align-items: center;
            justify-content: space-between;
            gap: 8px;
        }}
        .mobile-brand {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            font-weight: 700;
            color: #f8fafc;
            text-decoration: none;
            white-space: nowrap;
        }}
        .mobile-brand img {{
            width: 26px;
            height: 26px;
        }}
        .mobile-nav-select {{
            background: #1e293b;
            color: #f8fafc;
            border: 1px solid #475569;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            outline: none;
            cursor: pointer;
            flex: 1;
            max-width: 200px;
        }}
        .mobile-btn {{
            background: #ff4b4b;
            color: white;
            border: none;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: background 0.15s;
        }}
        .mobile-btn:active {{
            background: #dc2626;
        }}

        /* SIDEBAR OVERLAY */
        #sidebar-overlay {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.65);
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
            z-index: 998;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        #sidebar-overlay.active {{
            display: block;
            opacity: 1;
        }}

        /* SIDEBAR CLOSE BUTTON */
        .sidebar-close-btn {{
            display: none;
            background: #e2e8f0;
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            font-size: 15px;
            font-weight: 700;
            color: #334155;
            cursor: pointer;
            align-items: center;
            justify-content: center;
            margin-left: auto;
        }}

        /* RESPONSIVE TABLE WRAPPER */
        .table-responsive {{
            width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin-bottom: 14px;
            border-radius: 8px;
        }}
        .table-responsive::-webkit-scrollbar {{
            height: 6px;
        }}
        .table-responsive::-webkit-scrollbar-thumb {{
            background: #cbd5e1;
            border-radius: 4px;
        }}

        /* GAUGE DUO GRID */
        .gauge-duo {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            align-items: center;
            justify-content: center;
        }}

        /* INTERACTIVE KPI CARDS */
        .interactive-card {{
            cursor: pointer;
            position: relative;
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s, border-color 0.2s;
        }}
        .interactive-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 10px 20px -3px rgba(2, 132, 199, 0.15), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            border-color: #38bdf8;
        }}
        .interactive-card:active {{
            transform: scale(0.98);
        }}
        .kpi-tap-hint {{
            font-size: 10px;
            color: #0284c7;
            font-weight: 600;
            margin-top: 6px;
            display: flex;
            align-items: center;
            gap: 3px;
        }}

        /* INTERACTIVE TABLE SEARCH & CHIPS */
        .filter-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 12px;
            align-items: center;
        }}
        .search-input {{
            padding: 8px 12px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            font-size: 12.5px;
            outline: none;
            flex: 1;
            min-width: 180px;
            transition: border-color 0.15s;
        }}
        .search-input:focus {{
            border-color: #ff4b4b;
            box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.15);
        }}
        .filter-chip {{
            background: #f1f5f9;
            color: #334155;
            border: 1px solid #cbd5e1;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 11.5px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
            user-select: none;
        }}
        .filter-chip:hover, .filter-chip.active {{
            background: #ff4b4b;
            color: white;
            border-color: #ff4b4b;
        }}

        /* HEADER ACTION BUTTONS */
        .header-actions {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .action-btn {{
            background: rgba(255, 255, 255, 0.1);
            color: #f8fafc;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            transition: background 0.15s;
        }}
        .action-btn:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        /* MEDIA QUERIES FOR TABLET & MOBILE */
        @media (max-width: 1024px) {{
            #mobile-topbar {{
                display: flex;
            }}
            #sidebar {{
                position: fixed;
                left: -350px;
                top: 0;
                bottom: 0;
                width: 320px;
                height: 100vh;
                z-index: 1000;
                transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 6px 0 24px rgba(0,0,0,0.2);
            }}
            #sidebar.open {{
                left: 0;
            }}
            .sidebar-close-btn {{
                display: flex;
            }}
            #mobile-toggle {{
                display: none;
            }}
            #main-area {{
                max-width: 100vw;
                width: 100vw;
                padding: 16px 16px 60px 16px;
            }}
            .grid-2 {{
                grid-template-columns: 1fr;
                gap: 16px;
            }}
            .kpi-grid {{
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
            }}
        }}

        @media (max-width: 768px) {{
            #main-area {{
                padding: 12px 12px 60px 12px;
            }}
            .main-header {{
                padding: 16px;
                border-radius: 10px;
            }}
            .main-header h1 {{
                font-size: 18px;
            }}
            .kpi-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 8px;
            }}
            .kpi-card {{
                padding: 12px 14px;
                min-height: 105px;
            }}
            .kpi-value {{
                font-size: 20px;
            }}
            .section-card {{
                padding: 14px;
                border-radius: 10px;
                margin-bottom: 14px;
            }}
            .section-title {{
                font-size: 14.5px;
            }}
            .grid-3 {{
                grid-template-columns: 1fr;
                gap: 10px;
            }}
        }}

        @media (max-width: 480px) {{
            .mobile-brand span {{
                display: none;
            }}
            .kpi-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .kpi-card {{
                padding: 10px 12px;
            }}
            .kpi-value {{
                font-size: 18px;
            }}
            .kpi-title {{
                font-size: 10px;
            }}
        }}

        @media print {{
            #sidebar, #mobile-topbar, .header-actions, .filter-bar, .sub-info-badge {{
                display: none !important;
            }}
            #main-area {{
                max-width: 100% !important;
                padding: 0 !important;
            }}
            .page-view {{
                display: block !important;
            }}
        }}
    </style>
</head>
<body>

    <!-- MOBILE & TABLET STICKY TOPBAR -->
    <div id="mobile-topbar">
        <button class="mobile-btn" onclick="toggleSidebar()" aria-label="Toggle Navigation Menu">
            <span>☰</span> <span>Menu</span>
        </button>
        <div class="mobile-brand">
            <img src="https://img.icons8.com/fluency/96/shield.png" alt="Shield Logo">
            <span>GCDC HSE Hub</span>
        </div>
        <select id="mobile-nav-select" class="mobile-nav-select" onchange="switchPage(this.value)">
            <option value="Home">🏠 Main Home</option>
            <option value="Compliance">📋 Compliance Rate</option>
            <option value="Observations">🔍 Site Observations</option>
            <option value="NCRs">📑 NCRs Performance</option>
            <option value="Activities">🛠️ HSE Activities</option>
            <option value="Incidents">⚠️ Total Incidents</option>
            <option value="Workforce">⏱️ Safe Man-Hours</option>
            <option value="KPIs">📈 Monthly KPI</option>
            <option value="Training">🎓 HSE Training</option>
            <option value="Rates">🎯 Safety Rates</option>
            <option value="Welfare">🤝 Welfare Safety</option>
        </select>
        <button class="mobile-btn" onclick="toggleFullScreen()" title="Fullscreen" style="padding:6px 8px;">⛶</button>
    </div>

    <!-- BACKDROP OVERLAY FOR SIDEBAR ON MOBILE/TABLET -->
    <div id="sidebar-overlay" onclick="closeSidebar()"></div>

    <!-- SIDEBAR -->
    <aside id="sidebar">
        <div class="sidebar-brand">
            <img src="https://img.icons8.com/fluency/96/shield.png" alt="Shield Logo">
            <div>
                <h3>GCDC HSE Hub</h3>
                <p>Kharafi National / SBARC</p>
            </div>
            <button class="sidebar-close-btn" onclick="closeSidebar()" aria-label="Close Sidebar">✕</button>
        </div>

        <div class="nav-section-title">📌 Navigation Pages</div>

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

        <div class="sub-info-badge">
            <span>Current: <strong id="lbl-active-page">Home</strong></span>
            <button onclick="location.reload()" style="background:#ffffff; color:#334155; border:1px solid #cbd5e1; padding:4px 8px; border-radius:4px; font-size:11px; font-weight:700; cursor:pointer;">🔄 Refresh</button>
        </div>

                <hr style="border:none; border-top:1px solid #cbd5e1; margin:4px 0;">
    </aside>

    <!-- MAIN AREA -->
    <main id="main-area">

        <header class="main-header">
            <div>
                <h1>🛡️ GCDC HSE Performance Executive Dashboard</h1>
                <p>Comprehensive Safety, Health & Environmental Metrics • Single Consolidated Sheet View</p>
            </div>
            <div class="header-actions">
                <button class="action-btn" onclick="toggleFullScreen()" title="Toggle Fullscreen Mode">⛶ Fullscreen</button>
                <button class="action-btn" onclick="window.print()" title="Print / Save PDF Report">🖨️ Print / PDF</button>
                <span class="live-badge">🟢 Instant Live CDN</span>
            </div>
        </header>

        <!-- PAGE 1: HOME -->
        <section id="page-Home" class="page-view active">
            <h2 style="font-size:20px; font-weight:800; color:#0f172a; margin-bottom:4px;">🏠 Executive Overview & KPI Summary</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Consolidated project safety dashboard across all functional HSE domains</p>

            <div class="kpi-grid">
                <div class="kpi-card interactive-card" onclick="switchPage('Compliance')" title="Click to view detailed Compliance Analysis">
                    <div class="kpi-title">Compliance Rate</div>
                    <div class="kpi-value" style="color:#15803d;">99.2%</div>
                    <span class="kpi-badge badge-success">Target &ge; 95%</span>
                    <div class="metric-sub">1,416 / 1,427 Closed</div>
                    <div class="kpi-tap-hint">Tap to explore ↗</div>
                </div>
                <div class="kpi-card interactive-card" onclick="switchPage('Incidents')" title="Click to view Incidents Breakdown">
                    <div class="kpi-title">Total Incidents</div>
                    <div class="kpi-value" style="color:#0284c7;">102</div>
                    <span class="kpi-badge badge-info">81% Near Misses</span>
                    <div class="metric-sub">Zero Fatalities / Zero LTI</div>
                    <div class="kpi-tap-hint">Tap to explore ↗</div>
                </div>
                <div class="kpi-card interactive-card" onclick="switchPage('Workforce')" title="Click to view Safe Man-Hours & Workforce">
                    <div class="kpi-title">Safe Man-Hours</div>
                    <div class="kpi-value">6,201,138</div>
                    <span class="kpi-badge badge-success">Cumulative</span>
                    <div class="metric-sub">Prior: 2,916,176 hrs</div>
                    <div class="kpi-tap-hint">Tap to explore ↗</div>
                </div>
                <div class="kpi-card interactive-card" onclick="switchPage('Training')" title="Click to view Training Rate & Sessions">
                    <div class="kpi-title">Training Execution</div>
                    <div class="kpi-value" style="color:#b45309;">97.4%</div>
                    <span class="kpi-badge badge-warning">5 of 17 Sessions</span>
                    <div class="metric-sub">62 Attendees Logged</div>
                    <div class="kpi-tap-hint">Tap to explore ↗</div>
                </div>
                <div class="kpi-card interactive-card" onclick="switchPage('Rates')" title="Click to view Safety Frequency Rates (LTIFR / TRIR)">
                    <div class="kpi-title">LTIFR</div>
                    <div class="kpi-value" style="color:#15803d;">0.00</div>
                    <span class="kpi-badge badge-success">Excellent</span>
                    <div class="metric-sub">Target: 0.00</div>
                    <div class="kpi-tap-hint">Tap to explore ↗</div>
                </div>
                <div class="kpi-card interactive-card" onclick="switchPage('Rates')" title="Click to view Safety Frequency Rates (LTIFR / TRIR)">
                    <div class="kpi-title">TRIR</div>
                    <div class="kpi-value" style="color:#0284c7;">0.26</div>
                    <span class="kpi-badge badge-info">Good (&le;0.50)</span>
                    <div class="metric-sub">Industry Benchmark</div>
                    <div class="kpi-tap-hint">Tap to explore ↗</div>
                </div>
            </div>

            <div class="grid-2">
                <div class="section-card">
                    <div class="section-title">🎯 Safety Frequency Rates (Gauges)</div>
                    <div class="gauge-duo">
                        <div>{home_ltifr_html}</div>
                        <div>{home_trir_html}</div>
                    </div>
                </div>
                <div class="section-card">
                    <div class="section-title">🚨 Incident Severity Distribution (102 Recorded Cases)</div>
                    <div>{home_donut_html}</div>
                </div>
            </div>

            <div class="section-card">
                <div class="section-title">⏱️ Monthly Safe Man-Hours & Daily Workforce Dynamics (Jan – Sep 2026)</div>
                <div>{home_dual_html}</div>
            </div>

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

        <!-- PAGE 2: COMPLIANCE -->
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

        <!-- PAGE 3: OBSERVATIONS -->
        <section id="page-Observations" class="page-view">
            <h2 style="font-size:22px; font-weight:800; color:#0f172a; margin-bottom:4px;">🔍 Site Observations Performance & Field Rectification Tracking</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Complete breakdown matching the official Excel Site Observation register, closure analytics, and overdue rates</p>

            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">TOTAL SITE OBSERVATIONS</div>
                    <div class="kpi-value">1,250</div>
                    <span class="kpi-badge badge-info">YTD Field Logs</span>
                    <div class="metric-sub">Cumulative Action Items</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">CLOSED OBSERVATIONS</div>
                    <div class="kpi-value" style="color:#15803d;">1,242</div>
                    <span class="kpi-badge badge-success">99% Closure Rate</span>
                    <div class="metric-sub">World-Class Resolution Rate</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">ACTIVE OPEN OBSERVATIONS</div>
                    <div class="kpi-value" style="color:#0284c7;">8</div>
                    <span class="kpi-badge badge-info">Under Rectification</span>
                    <div class="metric-sub">Immediate Field Actions</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">OVERDUE (OD) OBSERVATIONS</div>
                    <div class="kpi-value" style="color:#dc2626;">8</div>
                    <span class="kpi-badge badge-danger">1.4% OD Rate</span>
                    <div class="metric-sub">Target &le; 5% Achieved</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">CLOSED ON-TIME (OTC)</div>
                    <div class="kpi-value">25</div>
                    <span class="kpi-badge badge-success">2% OTC Rate</span>
                    <div class="metric-sub">On-Time Closed Logs</div>
                </div>
            </div>

            <div class="grid-2">
                <div class="section-card">
                    <div class="section-title">📋 Excel Site Observation Registry Tables</div>
                    
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;" class="table-responsive">
                        <div>
                            <div style="font-size:11.5px; font-weight:700; color:#64748b; margin-bottom:4px; text-transform:uppercase;">STATUS COUNTS (IMAGE 2)</div>
                            <table style="width: 100%; border-collapse: collapse; border: 2px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; font-size: 13.5px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
                                <thead>
                                    <tr style="background-color: #002060; color: #ffffff; border-bottom: 2px solid #000000;">
                                        <th colspan="2" style="padding: 7px; text-align: center; font-size: 15px; font-weight: 800; letter-spacing: 0.5px;">Site Observation</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr style="border-bottom: 1.5px solid #000000;">
                                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000; width: 62%;">Open</td>
                                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center; width: 38%;">8</td>
                                    </tr>
                                    <tr style="border-bottom: 1.5px solid #000000;">
                                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Closed</td>
                                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">1242</td>
                                    </tr>
                                    <tr style="border-bottom: 1.5px solid #000000;">
                                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Overdue</td>
                                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">8</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 2px solid #000000;">Total</td>
                                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">1250</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <div>
                            <div style="font-size:11.5px; font-weight:700; color:#64748b; margin-bottom:4px; text-transform:uppercase;">PERFORMANCE RATES (IMAGE 1)</div>
                            <table style="width: 100%; border-collapse: collapse; border: 2px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; font-size: 13.5px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
                                <thead>
                                    <tr style="background-color: #002060; color: #ffffff; border-bottom: 2px solid #000000;">
                                        <th colspan="2" style="padding: 7px; text-align: center; font-size: 15px; font-weight: 800; letter-spacing: 0.5px;">Site Observation</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr style="border-bottom: 1.5px solid #000000;">
                                        <td style="padding: 6px 9px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000; width: 62%;">Closure Rate</td>
                                        <td style="padding: 6px 9px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center; width: 38%;">99%</td>
                                    </tr>
                                    <tr style="border-bottom: 1.5px solid #000000;">
                                        <td style="padding: 6px 9px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">OD Rate</td>
                                        <td style="padding: 6px 9px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">1.4%</td>
                                    </tr>
                                    <tr style="border-bottom: 1.5px solid #000000;">
                                        <td style="padding: 6px 9px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">OTC Rate</td>
                                        <td style="padding: 6px 9px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">2%</td>
                                    </tr>
                                    <tr style="border-bottom: 1.5px solid #000000;">
                                        <td style="padding: 6px 9px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 2px solid #000000;">Total OD</td>
                                        <td style="padding: 6px 9px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">17</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 6px 9px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Closed On-time</td>
                                        <td style="padding: 6px 9px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">25</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div style="margin-top: 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px;">
                        <div style="font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase;">MATHEMATICAL FORMULATION</div>
                        <div style="font-size: 12.5px; color: #1e293b; margin-top: 4px; line-height: 1.5;">
                            • <b>Closure Rate:</b> (1,242 Closed &divide; 1,250 Total) &times; 100 = <b>99.36% (~99%)</b><br>
                            • <b>OD (Overdue) Rate:</b> (17 Total OD &divide; 1,250 Total) &times; 100 = <b>1.36% (~1.4%)</b><br>
                            • <b>OTC (On-Time Closure) Rate:</b> (25 &divide; 1,250 Total) &times; 100 = <b>2.0%</b><br>
                            • <b>Active Outstanding:</b> 8 Open Items currently in field close-out loop.
                        </div>
                    </div>
                </div>

                <div class="section-card">
                    <div class="section-title">📊 Excel Site Observations Visual Distribution (Image 3)</div>
                    {obs_page_chart_html}
                    
                    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px; margin-top: 14px;">
                        <span style="color: #166534; font-weight: 700; font-size: 13px;">🏆 Outstanding Proactive Safety:</span>
                        <span style="color: #15803d; font-size: 12.5px;"> Exceptional field engagement with 1,242 out of 1,250 proactive observations resolved, achieving a stellar 99% closure velocity.</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- PAGE 4: NCRS -->
        <section id="page-NCRs" class="page-view">
            <h2 style="font-size:22px; font-weight:800; color:#0f172a; margin-bottom:4px;">📑 Non-Conformance Reports (NCRs) Performance</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Engineering, quality, and environmental non-conformance closure compliance</p>

            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">TOTAL NCRS ISSUED</div>
                    <div class="kpi-value">54</div>
                    <span class="kpi-badge badge-info">YTD Log</span>
                    <div class="metric-sub">Quality & Safety NCRs</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">CLOSED NCRS</div>
                    <div class="kpi-value" style="color:#15803d;">52</div>
                    <span class="kpi-badge badge-success">96% Closure Rate</span>
                    <div class="metric-sub">Target &ge; 90%</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">ACTIVE OPEN NCRS</div>
                    <div class="kpi-value" style="color:#0284c7;">2</div>
                    <span class="kpi-badge badge-warning">Under Review</span>
                    <div class="metric-sub">Corrective Action Pending</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">OVERDUE NCRS</div>
                    <div class="kpi-value" style="color:#dc2626;">2</div>
                    <span class="kpi-badge badge-danger">4.0% OD Rate</span>
                    <div class="metric-sub">Low Risk Level</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">CLOSED ON-TIME (OTC)</div>
                    <div class="kpi-value">0</div>
                    <span class="kpi-badge badge-warning">0% OTC Rate</span>
                    <div class="metric-sub">Pending SLA Validation</div>
                </div>
            </div>

            <div class="grid-2">
                <div class="section-card">
                    <div class="section-title">📋 Excel NCRs Registry Tables</div>
                    
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;" class="table-responsive">
                        <div>
                            <div style="font-size:11.5px; font-weight:700; color:#64748b; margin-bottom:4px; text-transform:uppercase;">STATUS COUNTS (IMAGE 1)</div>
                            <table style="width: 100%; border-collapse: collapse; border: 2px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; font-size: 13.5px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
                                <thead>
                                    <tr style="background-color: #002060; color: #ffffff; border-bottom: 2px solid #000000;">
                                        <th colspan="2" style="padding: 7px; text-align: center; font-size: 15px; font-weight: 800; letter-spacing: 0.5px;">NCRs</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr style="border-bottom: 1.5px solid #000000;">
                                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000; width: 62%;">Open</td>
                                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center; width: 38%;">2</td>
                                    </tr>
                                    <tr style="border-bottom: 1.5px solid #000000;">
                                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Closed</td>
                                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">52</td>
                                    </tr>
                                    <tr style="border-bottom: 1.5px solid #000000;">
                                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Overdue</td>
                                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">2</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 7px 10px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 2px solid #000000;">Total</td>
                                        <td style="padding: 7px 10px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">54</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <div>
                            <div style="font-size:11.5px; font-weight:700; color:#64748b; margin-bottom:4px; text-transform:uppercase;">PERFORMANCE RATES (IMAGE 2)</div>
                            <table style="width: 100%; border-collapse: collapse; border: 2px solid #000000; font-family: 'Segoe UI', Inter, sans-serif; font-size: 13.5px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
                                <thead>
                                    <tr style="background-color: #002060; color: #ffffff; border-bottom: 2px solid #000000;">
                                        <th colspan="2" style="padding: 7px; text-align: center; font-size: 15px; font-weight: 800; letter-spacing: 0.5px;">NCRs</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr style="border-bottom: 1.5px solid #000000;">
                                        <td style="padding: 6px 9px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000; width: 62%;">Closure Rate</td>
                                        <td style="padding: 6px 9px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center; width: 38%;">96%</td>
                                    </tr>
                                    <tr style="border-bottom: 1.5px solid #000000;">
                                        <td style="padding: 6px 9px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">OD Rate</td>
                                        <td style="padding: 6px 9px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">4%</td>
                                    </tr>
                                    <tr style="border-bottom: 1.5px solid #000000;">
                                        <td style="padding: 6px 9px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">OTC Rate</td>
                                        <td style="padding: 6px 9px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">0%</td>
                                    </tr>
                                    <tr style="border-bottom: 1.5px solid #000000;">
                                        <td style="padding: 6px 9px; background-color: #8fa0b5; color: #002060; font-weight: 800; border-right: 2px solid #000000;">Total OD</td>
                                        <td style="padding: 6px 9px; background-color: #ffffff; color: #000000; font-weight: 800; text-align: center;">2</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 6px 9px; background-color: #8fa0b5; color: #002060; font-weight: 700; border-right: 2px solid #000000;">Closed On-time</td>
                                        <td style="padding: 6px 9px; background-color: #ffffff; color: #000000; font-weight: 700; text-align: center;">0</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div style="margin-top: 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px;">
                        <div style="font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase;">MATHEMATICAL FORMULATION</div>
                        <div style="font-size: 12.5px; color: #1e293b; margin-top: 4px; line-height: 1.5;">
                            • <b>Closure Rate:</b> (52 Closed &divide; 54 Total) &times; 100 = <b>96.3% (~96%)</b><br>
                            • <b>OD (Overdue) Rate:</b> (2 Overdue &divide; 54 Total) &times; 100 = <b>3.7% (~4%)</b><br>
                            • <b>Active NCRs:</b> 2 open non-conformances under formal corrective action plan.
                        </div>
                    </div>
                </div>

                <div class="section-card">
                    <div class="section-title">📊 Excel NCRs Visual Trajectory</div>
                    {ncr_page_chart_html}
                    
                    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px; margin-top: 14px;">
                        <span style="color: #166534; font-weight: 700; font-size: 13px;">🏆 High Quality Resolution:</span>
                        <span style="color: #15803d; font-size: 12.5px;"> Exceptional closure velocity with 52 out of 54 NCRs formally resolved, demonstrating rigorous compliance.</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- PAGE 5: ACTIVITIES -->
        <section id="page-Activities" class="page-view">
            <h2 style="font-size:22px; font-weight:800; color:#0f172a; margin-bottom:4px;">🛠️ HSE Completed Activities Register</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Field execution tracking across Toolbox Talks, formal inspections, and safety campaigns</p>

            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">TOTAL HSE ACTIVITIES</div>
                    <div class="kpi-value">121</div>
                    <span class="kpi-badge badge-success">High Engagement</span>
                    <div class="metric-sub">Cumulative Field Sessions</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">TOOLBOX TALKS (TBT)</div>
                    <div class="kpi-value" style="color:#0284c7;">114</div>
                    <span class="kpi-badge badge-info">94.2% of Total</span>
                    <div class="metric-sub">Daily Frontline Briefings</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">SITE INSPECTIONS</div>
                    <div class="kpi-value" style="color:#15803d;">6</div>
                    <span class="kpi-badge badge-success">Scheduled Audits</span>
                    <div class="metric-sub">Rigorous Field Monitoring</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">SAFETY CAMPAIGNS</div>
                    <div class="kpi-value" style="color:#d97706;">1</div>
                    <span class="kpi-badge badge-warning">Targeted Campaign</span>
                    <div class="metric-sub">Project-Wide Awareness</div>
                </div>
            </div>

            <div class="grid-2">
                <div class="section-card">
                    <div class="section-title">📋 Excel HSE Activities Table</div>
                    
                    <div class="table-responsive">
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
                    </div>

                    <div style="margin-top: 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px;">
                        <div style="font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase;">ACTIVITY RATIO BREAKDOWN</div>
                        <div style="font-size: 12.5px; color: #1e293b; margin-top: 4px; line-height: 1.5;">
                            • <b>TBT Proportion:</b> (114 &divide; 121) &times; 100 = <b>94.2%</b><br>
                            • <b>Inspection Proportion:</b> (6 &divide; 121) &times; 100 = <b>5.0%</b><br>
                            • <b>Campaign Proportion:</b> (1 &divide; 121) &times; 100 = <b>0.8%</b>
                        </div>
                    </div>
                </div>

                <div class="section-card">
                    <div class="section-title">📊 Excel HSE Activities Visual Distribution</div>
                    {act_page_chart_html}
                    
                    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px; margin-top: 14px;">
                        <span style="color: #166534; font-weight: 700; font-size: 13px;">🏆 Frontline Proactive Presence:</span>
                        <span style="color: #15803d; font-size: 12.5px;"> 114 Toolbox Talks delivered across shifts with 6 formal audits maintaining zero lost-time standards.</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- PAGE 6: INCIDENTS -->
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
                    <div class="section-title">📋 Total Incidents Registry (Interactive & Excel Format)</div>
                    <div class="filter-bar">
                        <input type="text" id="incident-search" class="search-input" placeholder="🔍 Search Incident (e.g. Near Miss, MTC, FAC, LTI)..." onkeyup="filterIncidents()">
                        <span class="filter-chip active" data-val="" onclick="filterIncidents('')">All (102)</span>
                        <span class="filter-chip" data-val="nm" onclick="filterIncidents('nm')">Near Miss (83)</span>
                        <span class="filter-chip" data-val="mtc" onclick="filterIncidents('mtc')">MTC (8)</span>
                        <span class="filter-chip" data-val="mva" onclick="filterIncidents('mva')">MVA (5)</span>
                        <span class="filter-chip" data-val="pd" onclick="filterIncidents('pd')">PD (4)</span>
                        <span class="filter-chip" data-val="fac" onclick="filterIncidents('fac')">FAC (2)</span>
                        <span class="filter-chip" data-val="zero" onclick="filterIncidents('zero')">Zero LTI (0)</span>
                    </div>
                    <div id="incident-filter-count" style="font-size:11.5px; color:#64748b; margin-bottom:8px; font-weight:600;">Showing all 102 incidents</div>
                    <div class="excel-table-box">
                        <div class="excel-table-header">Total Incidents Registry</div>
                        <div class="excel-table-row incident-row" data-cat="nm near miss"><div class="excel-col-label">NM (Near Miss)</div><div class="excel-col-value">83</div></div>
                        <div class="excel-table-row incident-row" data-cat="mtc medical treatment"><div class="excel-col-label">MTC (Medical Treatment)</div><div class="excel-col-value">8</div></div>
                        <div class="excel-table-row incident-row" data-cat="mva motor vehicle accident"><div class="excel-col-label">MVA (Motor Vehicle Accident)</div><div class="excel-col-value">5</div></div>
                        <div class="excel-table-row incident-row" data-cat="fac first aid case"><div class="excel-col-label">FAC (First Aid Case)</div><div class="excel-col-value">2</div></div>
                        <div class="excel-table-row incident-row" data-cat="pd property damage"><div class="excel-col-label">PD (Property Damage)</div><div class="excel-col-value">4</div></div>
                        <div class="excel-table-row incident-row" data-cat="fat fatality zero"><div class="excel-col-label">FAT (Fatality)</div><div class="excel-col-value" style="color:#16a34a;">0</div></div>
                        <div class="excel-table-row incident-row" data-cat="rwc restricted work zero"><div class="excel-col-label">RWC (Restricted Work Case)</div><div class="excel-col-value" style="color:#16a34a;">0</div></div>
                        <div class="excel-table-row incident-row" data-cat="lti lost time injury zero"><div class="excel-col-label">LTI (Lost Time Injury)</div><div class="excel-col-value" style="color:#16a34a;">0</div></div>
                        <div class="excel-table-row"><div class="excel-col-label excel-total-label">Total Recorded</div><div class="excel-col-value excel-total-value">102</div></div>
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

        <!-- PAGE 7: WORKFORCE -->
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

        <!-- PAGE 8: KPIS -->
        <section id="page-KPIs" class="page-view">
            <h2 style="font-size:22px; font-weight:800; color:#0f172a; margin-bottom:4px;">📈 HSE Monthly KPI Performance & Trends</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Month-by-month KPI and performance index analysis against the 90% project baseline</p>

            <!-- 1. TOP 6 EXECUTIVE METRIC CARDS -->
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Overall KPI Avg</div>
                    <div class="kpi-value">83%</div>
                    <span class="kpi-badge badge-warning">Target: 90%</span>
                    <div class="metric-sub">Variance: -7.0%</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Overall PSI/PCI Avg</div>
                    <div class="kpi-value" style="color:#8b5cf6;">65.4%</div>
                    <span class="kpi-badge badge-info">Target: 90%</span>
                    <div class="metric-sub">Process Safety</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Baseline Benchmark</div>
                    <div class="kpi-value" style="color:#0284c7;">90%</div>
                    <span class="kpi-badge badge-info">Standard Target</span>
                    <div class="metric-sub">Fixed Contract KPI</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Peak KPI Month</div>
                    <div class="kpi-value" style="color:#15803d;">93%</div>
                    <span class="kpi-badge badge-success">May 2026</span>
                    <div class="metric-sub">+3.0% Above Target</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Peak PSI/PCI Month</div>
                    <div class="kpi-value" style="color:#15803d;">75%</div>
                    <span class="kpi-badge badge-success">Sep 2026</span>
                    <div class="metric-sub">Record Process High</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">PSI/PCI Trend</div>
                    <div class="kpi-value" style="color:#059669;">+15%</div>
                    <span class="kpi-badge badge-success">58% &rarr; 75%</span>
                    <div class="metric-sub">+1.8% Monthly Gain</div>
                </div>
            </div>

            <!-- SECTION 1: HSE MONTHLY OVERALL KPI -->
            <div class="grid-2">
                <div class="section-card">
                    <div class="section-title">📋 HSE Monthly KPI Registry (Excel Format)</div>
                    
                    <div class="table-responsive">
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
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">January</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">84%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">February</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">81%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">March</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">87%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">April</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">90%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">May</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">93%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">June</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">85%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">July</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">91%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">August</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">68%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">September</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">68%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">October</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;"></td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
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
                    </div>

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
                </div>

                <div class="section-card">
                    <div class="section-title">📈 KPI Performance Line Chart & Linear Trendline</div>
                    {kpis_chart_html}
                </div>
            </div>

            <!-- SECTION 2: HSE MONTHLY PSI/PCI -->
            <div style="margin: 36px 0 24px 0; border-top: 2px dashed #cbd5e1;"></div>
            <h3 style="font-size:18px; font-weight:800; color:#0f172a; margin-bottom:4px;">🎯 2. HSE Monthly Process Safety Index (PSI / PCI)</h3>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Month-by-month Process Safety Index performance and positive upward trajectory vs 90% target</p>

            <div class="grid-2">
                <div class="section-card">
                    <div class="section-title">📋 HSE Monthly PSI/PCI Registry (Excel Format)</div>
                    
                    <div class="table-responsive">
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
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">January</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">60%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">February</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">58%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">March</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">59%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">April</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">67%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">May</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">66%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">June</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">67%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">July</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">69%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">August</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">68%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">September</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;">75%</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #8ea9db;">
                                    <td style="padding: 7px 14px; background-color: #cfdbee; color: #0d233a; font-weight: 500; font-size: 13.5px; border-right: 1px solid #8ea9db;">October</td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 600; font-size: 13.5px; border-right: 1px solid #8ea9db; text-align: center;"></td>
                                    <td style="padding: 7px 14px; background-color: #ffffff; color: #0d233a; font-weight: 500; font-size: 13.5px; text-align: center;">90%</td>
                                </tr>
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
                    </div>

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
                </div>

                <div class="section-card">
                    <div class="section-title">📈 PSI/PCI Performance Line Chart & Linear Trendline</div>
                    {kpis_psi_html}
                </div>
            </div>
        </section>

        <!-- PAGE 9: TRAINING -->
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

        <!-- PAGE 10: RATES -->
        <section id="page-Rates" class="page-view">
            <h2 style="font-size:20px; font-weight:800; color:#0f172a; margin-bottom:4px;">🎯 Safety Frequency Rates (LTIFR & TRIR)</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Lost Time Injury Frequency Rate & Total Recordable Incident Rate performance indices against international benchmarks</p>

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
                    <div class="gauge-duo">
                        <div>{rates_lti_speedo_html}</div>
                        <div>{rates_tri_speedo_html}</div>
                    </div>
                </div>
            </div>

            <div class="section-card">
                <div class="section-title">⚖️ International Industry Benchmarking</div>
                {rates_bench_html}
            </div>
        </section>

        <!-- PAGE 11: WELFARE -->
        <section id="page-Welfare" class="page-view">
            <h2 style="font-size:20px; font-weight:800; color:#0f172a; margin-bottom:4px;">🤝 Welfare & Proactive Safety Initiatives</h2>
            <p style="font-size:13px; color:#64748b; margin-bottom:18px;">Labor camp standards, site heat stress monitoring, and worker wellbeing index</p>

            <div class="section-card">
                <div class="section-title">📈 Weekly Welfare Score Monitoring (Benchmark &ge; 90%)</div>
                {welfare_chart_html}
            </div>
        </section>

        <footer class="app-footer">
            <p><strong>GCDC HSE Performance Executive System</strong> • Data Source: Consolidated Sheet • Kharafi National / SBARC</p>
            <p style="margin-top: 4px; color: #0284c7; font-weight: 600;">Develop by Abdul Latif HSE Analyst +966530572691</p>
        </footer>

    </main>

    <script>
        function switchPage(pageKey) {{
            var pages = document.querySelectorAll('.page-view');
            pages.forEach(function(p) {{
                p.classList.remove('active');
            }});

            var target = document.getElementById('page-' + pageKey);
            if (target) {{
                target.classList.add('active');
            }}

            var btns = document.querySelectorAll('.nav-btn');
            btns.forEach(function(btn) {{
                if (btn.getAttribute('onclick') && btn.getAttribute('onclick').indexOf(pageKey) !== -1) {{
                    btn.classList.add('active');
                }} else {{
                    btn.classList.remove('active');
                }}
            }});

            var lbl = document.getElementById('lbl-active-page');
            if (lbl) {{
                lbl.innerText = pageKey;
            }}

            var mobileSelect = document.getElementById('mobile-nav-select');
            if (mobileSelect) {{
                mobileSelect.value = pageKey;
            }}

            if (history.pushState) {{
                history.pushState(null, null, '#' + pageKey.toLowerCase());
            }}

            closeSidebar();

            window.scrollTo({{ top: 0, behavior: 'smooth' }});

            // Trigger Plotly redraw and relayout on all visible charts
            setTimeout(function() {{
                var target = document.getElementById('page-' + pageKey);
                if (target) {{
                    var plots = target.querySelectorAll('.js-plotly-plot');
                    plots.forEach(function(plot) {{
                        Plotly.relayout(plot, {{ autosize: true }});
                        Plotly.Plots.resize(plot);
                    }});
                }}
                document.querySelectorAll('.js-plotly-plot').forEach(function(el) {{
                    Plotly.Plots.resize(el);
                }});
            }}, 50);
        }}

        function toggleSidebar() {{
            var sb = document.getElementById('sidebar');
            var ov = document.getElementById('sidebar-overlay');
            sb.classList.toggle('open');
            if (sb.classList.contains('open')) {{
                ov.classList.add('active');
                document.body.style.overflow = 'hidden';
            }} else {{
                ov.classList.remove('active');
                document.body.style.overflow = '';
            }}
        }}

        function closeSidebar() {{
            var sb = document.getElementById('sidebar');
            var ov = document.getElementById('sidebar-overlay');
            if (sb) sb.classList.remove('open');
            if (ov) ov.classList.remove('active');
            document.body.style.overflow = '';
        }}

        function toggleFullScreen() {{
            if (!document.fullscreenElement) {{
                if (document.documentElement.requestFullscreen) {{
                    document.documentElement.requestFullscreen();
                }} else if (document.documentElement.webkitRequestFullscreen) {{
                    document.documentElement.webkitRequestFullscreen();
                }}
            }} else {{
                if (document.exitFullscreen) {{
                    document.exitFullscreen();
                }}
            }}
        }}

        // Live search filter for incidents table
        function filterIncidents(term) {{
            var input = document.getElementById('incident-search');
            var filter = (term !== undefined ? term : (input ? input.value : '')).toLowerCase().trim();
            var rows = document.querySelectorAll('.incident-row');
            var visibleCount = 0;
            rows.forEach(function(r) {{
                var text = (r.innerText + ' ' + (r.getAttribute('data-cat') || '')).toLowerCase();
                if (filter === '' || text.indexOf(filter) !== -1) {{
                    r.style.display = '';
                    visibleCount++;
                }} else {{
                    r.style.display = 'none';
                }}
            }});
            var countEl = document.getElementById('incident-filter-count');
            if (countEl) {{
                countEl.innerText = filter === '' ? 'Showing all 102 incidents' : 'Filtered: ' + visibleCount + ' matching categories';
            }}
            // Update chip active states
            var chips = document.querySelectorAll('.filter-chip');
            chips.forEach(function(c) {{
                if (c.getAttribute('data-val') === term) {{
                    c.classList.add('active');
                }} else {{
                    c.classList.remove('active');
                }}
            }});
            if (input && term !== undefined) {{
                input.value = term;
            }}
        }}

        window.addEventListener('resize', function() {{
            document.querySelectorAll('.js-plotly-plot').forEach(function(el) {{
                Plotly.Plots.resize(el);
            }});
        }});

        window.addEventListener('orientationchange', function() {{
            setTimeout(function() {{
                document.querySelectorAll('.js-plotly-plot').forEach(function(el) {{
                    Plotly.Plots.resize(el);
                }});
            }}, 200);
        }});

        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                closeSidebar();
            }}
        }});

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
    print(f"Generated instant-load dashboard to {output_path} ({len(html):,} bytes)")

if __name__ == "__main__":
    generate()
