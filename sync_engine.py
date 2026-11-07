r"""
GCDC HSE Dashboard Sync Engine
Synchronizes Excel workbook (D:\Kharafi\SBARC\...) with:
1. single_sheet_data.csv
2. index.html (build_instant_dashboard.py)
3. Live GitHub Pages repository (origin main)
4. Streamlit local dashboard (localhost:8550)
"""

import os
import sys
import glob
import shutil
import tempfile
import datetime
import json
import csv
import subprocess
import threading
import socket
import select
import http.server
import socketserver
from typing import Dict, Any, Tuple, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_DIR = r"D:\Kharafi\SBARC\DASHBOARDS - REGISTERS & LOGS\GCDC HSE Dashboard"
CSV_PATH = os.path.join(BASE_DIR, "single_sheet_data.csv")
STATUS_FILE = os.path.join(BASE_DIR, "sync_status.json")

class DoHProxyHandler(http.server.BaseHTTPRequestHandler):
    """Local forward proxy for GitHub pushing when system DNS fails."""
    def do_CONNECT(self):
        upstream = None
        try:
            host, port = self.path.split(":")
            port = int(port)
            github_ips = ["140.82.121.3", "140.82.121.4", "20.205.243.166"]
            if host == "github.com":
                for ip in github_ips:
                    try:
                        upstream = socket.create_connection((ip, port), timeout=4)
                        break
                    except Exception:
                        continue
            if not upstream:
                upstream = socket.create_connection((host, port), timeout=4)

            self.send_response(200, "Connection Established")
            self.end_headers()

            conns = [self.connection, upstream]
            while True:
                r, _, _ = select.select(conns, [], [], 10)
                if not r:
                    break
                for s in r:
                    other = upstream if s is self.connection else self.connection
                    data = s.recv(16384)
                    if not data:
                        return
                    other.sendall(data)
        except Exception:
            pass
        finally:
            if upstream:
                upstream.close()

    def log_message(self, format, *args):
        pass  # Quiet logging

def find_latest_excel() -> Optional[str]:
    """Finds the most recent valid .xlsx file from configured directories."""
    candidate_dirs = [
        EXCEL_DIR,
        BASE_DIR,
        os.path.abspath(os.path.join(BASE_DIR, "..")),
        os.path.abspath(os.path.join(BASE_DIR, "../..")),
    ]
    
    all_files = []
    for d in candidate_dirs:
        if os.path.exists(d):
            found = [
                f for f in glob.glob(os.path.join(d, "*.xlsx"))
                if not os.path.basename(f).startswith("~$")
            ]
            all_files.extend(found)
            
    if not all_files:
        return None
        
    return max(all_files, key=os.path.getmtime)

def read_excel_safely(excel_path: str) -> Tuple[bool, Any, str]:
    """Safely copies and reads Excel data even if currently locked by Microsoft Excel."""
    if not os.path.exists(excel_path):
        return False, None, f"File not found: {excel_path}"
        
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name
            
        shutil.copy2(excel_path, tmp_path)
        
        import openpyxl
        wb = openpyxl.load_workbook(tmp_path, data_only=True)
        if "DASHBOARD" not in wb.sheetnames or "DATA" not in wb.sheetnames:
            return False, None, f"Missing 'DASHBOARD' or 'DATA' sheets in {os.path.basename(excel_path)}"
            
        ws_dash = wb["DASHBOARD"]
        ws_data = wb["DATA"]
        
        dash_rows = [[cell.value if cell.value is not None else "" for cell in row] for row in ws_dash.iter_rows(max_row=33, max_col=24)]
        data_rows = [[cell.value if cell.value is not None else "" for cell in row] for row in ws_data.iter_rows(max_col=24)]
        all_rows = dash_rows + data_rows
        
        return True, all_rows, "Success"
    except Exception as e:
        return False, None, str(e)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

def push_to_github(commit_msg: str) -> Tuple[bool, str]:
    """Pushes changes to GitHub repository using local DNS forward proxy."""
    proxy_port = 9982
    server = None
    try:
        server = socketserver.ThreadingTCPServer(("127.0.0.1", proxy_port), DoHProxyHandler)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        
        proxy_url = f"http://127.0.0.1:{proxy_port}"
        
        # Git Add
        subprocess.run(
            ["git", "add", "single_sheet_data.csv", "index.html", "sync_status.json"],
            cwd=BASE_DIR, check=True, capture_output=True
        )
        
        # Git Commit
        commit_res = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=BASE_DIR, capture_output=True, text=True
        )
        
        # If nothing changed to commit, we can still report success
        if "nothing to commit" in commit_res.stdout or "nothing to commit" in commit_res.stderr:
            return True, "No repository changes to push."
            
        # Git Push via proxy
        cmd = [
            "git", "-c", f"http.proxy={proxy_url}", "-c", f"https.proxy={proxy_url}",
            "push", "origin", "main"
        ]
        push_res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, timeout=25)
        
        if push_res.returncode == 0:
            return True, "Successfully pushed to GitHub Pages!"
        else:
            return False, f"Git push failed: {push_res.stderr or push_res.stdout}"
    except Exception as e:
        return False, f"GitHub push exception: {str(e)}"
    finally:
        if server:
            try:
                server.shutdown()
                server.server_close()
            except Exception:
                pass

def execute_sync(push: bool = True) -> Dict[str, Any]:
    """Executes full synchronization from latest Excel file."""
    excel_file = find_latest_excel()
    if not excel_file:
        res = {"success": False, "error": "No Excel file found in configured locations."}
        save_status(res)
        return res
        
    mtime = os.path.getmtime(excel_file)
    mtime_dt = datetime.datetime.fromtimestamp(mtime).strftime("%d-%b-%Y %I:%M:%S %p")
    filename = os.path.basename(excel_file)
    
    # Read Excel safely
    ok, rows, err = read_excel_safely(excel_file)
    if not ok:
        res = {"success": False, "error": f"Failed to read Excel: {err}", "filename": filename}
        save_status(res)
        return res
        
    # Write CSV
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
        
    # Rebuild index.html
    build_script = os.path.join(BASE_DIR, "build_instant_dashboard.py")
    build_res = subprocess.run([sys.executable, build_script], cwd=BASE_DIR, capture_output=True, text=True)
    build_ok = (build_res.returncode == 0)
    
    # Save Status
    now_str = datetime.datetime.now().strftime("%d-%b-%Y %I:%M:%S %p")
    status_info = {
        "success": True,
        "filename": filename,
        "filepath": excel_file,
        "excel_mtime": mtime,
        "excel_mtime_str": mtime_dt,
        "synced_at": now_str,
        "rows_count": len(rows),
        "build_ok": build_ok,
        "pushed": False,
        "push_msg": ""
    }
    
    # Push to GitHub
    if push and build_ok:
        save_status(status_info)
        commit_msg = f"auto-sync: Synced dashboard from {filename} ({now_str})"
        push_ok, push_msg = push_to_github(commit_msg)
        status_info["pushed"] = push_ok
        status_info["push_msg"] = push_msg
        save_status(status_info)
    else:
        save_status(status_info)
        
    return status_info

def save_status(status: Dict[str, Any]):
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2)
    except Exception:
        pass

def get_last_status() -> Dict[str, Any]:
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"success": False, "synced_at": "Never", "filename": "None"}

if __name__ == "__main__":
    push_flag = ("--no-push" not in sys.argv)
    print("Starting GCDC HSE Dashboard Sync...")
    result = execute_sync(push=push_flag)
    print(json.dumps(result, indent=2))
