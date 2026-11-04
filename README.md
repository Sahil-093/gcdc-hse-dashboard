# GCDC HSE Performance Executive Web Dashboard 🛡️

Interactive Executive Dashboard for the **GCDC Project** (Kharafi National / SBARC), parsing directly from your project Excel registers and dashboard workbooks in:
`D:\Kharafi\SBARC\DASHBOARDS - REGISTERS & LOGS\GCDC HSE Dashboard`

---

## 🚀 Quick Start Options

### Option 1: Launch Interactive Web Dashboard (Streamlit)
Double-click `run_dashboard.bat` or run the following command in PowerShell:
```powershell
streamlit run app.py
```
This launches a browser interface at `http://localhost:8501` featuring:
- **Live File Switcher:** Toggle between snapshots (`September 2026`, `12-10-2026`, `02-09-2026`, etc.).
- **Interactive Gauges:** Real-time speedometer dials for **LTIFR** (Zero target) and **TRIR** (Threshold benchmark).
- **Incident Pyramid & Donut:** Visual breakdown of all 102 incidents (Near Misses, MTC, MVA, PD, FAC).
- **Manpower & Man-Hours Dual Chart:** Correlates monthly safe hours against on-site workforce numbers.
- **Compliance Matrix & NCR SLA:** Real-time overdue and on-time action tracking.
- **Welfare & KPI Trends:** Weekly worker welfare tracking against the 90% benchmark.
- **Data Export:** Instant JSON/CSV export of extracted metrics.

---

### Option 2: Open Standalone Interactive HTML Report (No Python Required)
Double-click or open in any web browser:
```
e:\Abdul Latif\Google Antigravity\hse_dashboard\GCDC_HSE_Executive_Report.html
```
To refresh the report after updating any Excel file, simply run:
```powershell
python export_report.py
```

---

## 📁 Project Structure

```
hse_dashboard/
├── app.py                         # Main interactive Streamlit web dashboard
├── hse_parser.py                  # OpenPyXL parser for GCDC HSE workbooks
├── export_report.py               # Generator for standalone portable HTML report
├── run_dashboard.bat              # One-click desktop launcher
├── GCDC_HSE_Executive_Report.html # Generated self-contained HTML executive report
└── README.md                      # Documentation
```
