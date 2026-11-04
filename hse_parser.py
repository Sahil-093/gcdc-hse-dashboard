import os
import csv
from typing import Dict, Any, List

WORKSPACE_DIR = r"e:\Abdul Latif\Google Antigravity\hse_dashboard"
CSV_PATH = os.path.join(WORKSPACE_DIR, "single_sheet_data.csv")

def parse_single_sheet_csv(csv_path: str = CSV_PATH) -> Dict[str, Any]:
    """Parse the consolidated single-sheet HSE dataset."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Single sheet file not found: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as f:
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

    OFFSET = 33 # Row offset where DATA table begins

    # Top Executive KPI row (Row 28 -> index 27)
    closure_rate = get_f(27, 1)
    total_incidents = get_i(27, 5)
    safe_man_hours = get_f(27, 9)
    training_rate = get_f(27, 13)
    ltifr = get_f(27, 17)
    trir = get_f(27, 21)
    ltifr_rating = get_c(32, 17, "Excellent")
    trir_rating = get_c(32, 21, "Good")

    # 1. Total Incidents Breakdown
    incidents = {
        "NM": get_i(5 + OFFSET, 6),
        "MTC": get_i(6 + OFFSET, 6),
        "MVA": get_i(7 + OFFSET, 6),
        "FAC": get_i(8 + OFFSET, 6),
        "PD": get_i(9 + OFFSET, 6),
        "FAT": get_i(10 + OFFSET, 6),
        "RWC": get_i(11 + OFFSET, 6),
        "LTI": get_i(12 + OFFSET, 6),
        "Total": total_incidents if total_incidents > 0 else get_i(13 + OFFSET, 6)
    }

    # 2. Cumulative Safe Man-Hours
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_hours = {}
    for i, m in enumerate(months):
        r = 5 + i + OFFSET
        val = get_c(r, 10)
        if val != "":
            monthly_hours[m] = float(val)
    prior_man_hours = get_f(19 + OFFSET, 8, 2916176.0)

    # 3. Monthly Manpower
    monthly_manpower = {}
    for i, m in enumerate(months):
        r = 22 + i + OFFSET
        val = get_c(r, 10)
        if val != "":
            monthly_manpower[m] = float(val)
    avg_manpower = get_f(34 + OFFSET, 10, 1244.4)

    # 4. Compliance & Inspections
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
    grand_rate = closure_rate if closure_rate > 0 else get_f(15 + OFFSET, 3)

    # 5. Site Observations & NCR SLA Tracking
    site_obs_metrics = {
        "closure_rate": get_f(27 + OFFSET, 19, obs_rate),
        "od_rate": get_f(28 + OFFSET, 19, 0.0136),
        "otc_rate": get_f(29 + OFFSET, 19, 0.02),
        "total_od": get_i(30 + OFFSET, 19, 17),
        "closed_on_time": get_i(31 + OFFSET, 19, 25),
        "open": get_i(41 + OFFSET, 19, obs_open),
        "closed": get_i(42 + OFFSET, 19, obs_close),
        "overdue": get_i(43 + OFFSET, 19, 8),
        "total": get_i(44 + OFFSET, 19, obs_total)
    }

    ncr_metrics = {
        "open": get_i(8 + OFFSET, 19, ncr_open),
        "closed": get_i(9 + OFFSET, 19, ncr_close),
        "overdue": get_i(10 + OFFSET, 19, 2),
        "total": get_i(11 + OFFSET, 19, ncr_total),
        "closure_rate": get_f(34 + OFFSET, 19, ncr_rate),
        "od_rate": get_f(35 + OFFSET, 19, 0.037),
        "otc_rate": get_f(36 + OFFSET, 19, 0.0),
        "total_od": get_i(37 + OFFSET, 19, 2),
        "closed_on_time": get_i(38 + OFFSET, 19, 0)
    }

    # 6. HSE Staffing Compliance
    staffing = {
        "actual": get_f(21 + OFFSET, 19, 22.0),
        "required": get_f(22 + OFFSET, 19, 24.89),
        "gap": get_f(23 + OFFSET, 19, 2.89),
        "compliance_rate": get_f(24 + OFFSET, 19, 0.8839)
    }

    # 7. HSE Proactive Activities
    hse_activities = {
        "tbt": get_i(15 + OFFSET, 19, 114),
        "inspections": get_i(16 + OFFSET, 19, 6),
        "campaigns": get_i(17 + OFFSET, 19, 1),
        "total": get_i(18 + OFFSET, 19, 121)
    }

    # 8. Training
    trainings = {}
    for i, m in enumerate(months):
        r = 6 + i + OFFSET
        t_count = get_c(r, 14)
        att = get_c(r, 15)
        tgt = get_c(r, 16)
        if any([t_count, att, tgt]):
            trainings[m] = {
                "trainings": int(float(t_count)) if t_count else 0,
                "attendees": int(float(att)) if att else 0,
                "target": int(float(tgt)) if tgt else 0
            }
    training_summary = {
        "total_trainings": get_i(17 + OFFSET, 14, 5),
        "total_attendees": get_i(17 + OFFSET, 15, 62),
        "total_target": get_i(17 + OFFSET, 16, 17),
        "completion_rate": training_rate,
        "by_month": trainings
    }

    # 9. HSE Monthly KPI Scores
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

    # 10. HSE Monthly PSI/PCI Scores
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

    # 11. Welfare Score Weekly
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
        "filepath": csv_path,
        "filename": "Single Sheet HSE Dataset",
        "incidents": incidents,
        "safe_man_hours": {
            "prior_to_2026": prior_man_hours,
            "monthly": monthly_hours,
            "total_safe_hours": safe_man_hours
        },
        "manpower": {
            "monthly": monthly_manpower,
            "average": avg_manpower
        },
        "rates": {
            "ltifr": ltifr,
            "trir": trir,
            "ltifr_rating": ltifr_rating,
            "trir_rating": trir_rating
        },
        "compliance": {
            "observations": {"open": obs_open, "closed": obs_close, "total": obs_total, "rate": obs_rate},
            "ncr": {"open": ncr_open, "closed": ncr_close, "total": ncr_total, "rate": ncr_rate},
            "audits": {"open": audit_open, "closed": audit_close, "total": audit_total, "rate": audit_rate},
            "grand_total": {"open": grand_open, "closed": grand_close, "total": grand_total, "rate": grand_rate}
        },
        "site_obs_metrics": site_obs_metrics,
        "ncr_metrics": ncr_metrics,
        "staffing": staffing,
        "hse_activities": hse_activities,
        "training": training_summary,
        "kpi_monthly": kpi_monthly,
        "kpi_avg": kpi_avg,
        "psi_monthly": psi_monthly,
        "psi_avg": psi_avg,
        "welfare": {
            "weekly": welfare_weeks,
            "average": welfare_avg
        }
    }

def parse_hse_workbook(filepath: str = None) -> Dict[str, Any]:
    return parse_single_sheet_csv(CSV_PATH)

def get_available_excel_files() -> List[Dict[str, Any]]:
    return [{
        "filename": "Single Sheet HSE Dataset",
        "filepath": CSV_PATH,
        "mtime": os.path.getmtime(CSV_PATH) if os.path.exists(CSV_PATH) else 0,
        "size_kb": round(os.path.getsize(CSV_PATH) / 1024, 1) if os.path.exists(CSV_PATH) else 0
    }]
