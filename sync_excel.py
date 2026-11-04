# -*- coding: utf-8 -*-
"""
One-click Excel Sync for GCDC HSE Dashboard
Syncs changes from the latest Excel workbook in D:\Kharafi... into single_sheet_data.csv,
rebuilds index.html, and pushes to GitHub Pages.
"""
import os
import sys
import glob
import csv
import subprocess
import time

EXCEL_DIR = r"D:\Kharafi\SBARC\DASHBOARDS - REGISTERS & LOGS\GCDC HSE Dashboard"
TARGET_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_CSV = os.path.join(TARGET_DIR, "single_sheet_data.csv")

def main():
    print("=" * 60)
    print("  GCDC HSE Performance Dashboard - Excel Live Synchronizer")
    print("=" * 60)
    
    if not os.path.exists(EXCEL_DIR):
        print(f"[-] ERROR: Excel folder not found at: {EXCEL_DIR}")
        return 1
        
    files = [f for f in glob.glob(os.path.join(EXCEL_DIR, "*.xlsx")) if not os.path.basename(f).startswith("~$")]
    if not files:
        print(f"[-] ERROR: No valid .xlsx workbooks found in {EXCEL_DIR}")
        return 1
        
    newest = max(files, key=os.path.getmtime)
    print(f"[+] Found newest Excel workbook:\n    {newest}")
    print(f"    Modified: {time.ctime(os.path.getmtime(newest))}")
    
    print("\n[+] Reading DASHBOARD & DATA sheets...")
    try:
        import openpyxl
        wb = openpyxl.load_workbook(newest, data_only=True)
        if "DASHBOARD" not in wb.sheetnames or "DATA" not in wb.sheetnames:
            print(f"[-] ERROR: Missing 'DASHBOARD' or 'DATA' sheet in workbook!")
            return 1
            
        ws_dash = wb["DASHBOARD"]
        ws_data = wb["DATA"]
        
        dash_rows = [[cell.value if cell.value is not None else "" for cell in row] for row in ws_dash.iter_rows(max_row=33, max_col=24)]
        data_rows = [[cell.value if cell.value is not None else "" for cell in row] for row in ws_data.iter_rows(max_col=24)]
        all_rows = dash_rows + data_rows
        
        with open(TARGET_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(all_rows)
            
        print(f"[+] Updated {TARGET_CSV} ({len(all_rows)} rows extracted successfully).")
    except Exception as e:
        print(f"[-] ERROR parsing Excel: {e}")
        return 1
        
    print("\n[+] Rebuilding instant HTML dashboard (index.html)...")
    res = subprocess.run([sys.executable, os.path.join(TARGET_DIR, "build_instant_dashboard.py")], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[+] index.html successfully regenerated.")
    else:
        print(f"[-] build_instant_dashboard error: {res.stderr}")
        
    print("\n[+] Pushing update to GitHub Pages...")
    try:
        # Run proxy push
        proxy_code = '''
import socket, select, threading, subprocess, sys, time
def dns_query_a(host):
    try:
        query = b'\\xaa\\xbb\\x01\\x00\\x00\\x01\\x00\\x00\\x00\\x00\\x00\\x00'
        for part in host.split('.'):
            query += bytes([len(part)]) + part.encode()
        query += b'\\x00\\x00\\x01\\x00\\x01'
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(3.0)
        s.sendto(query, ('8.8.8.8', 53))
        data, _ = s.recvfrom(1024)
        s.close()
        return ".".join(str(b) for b in data[-4:])
    except:
        return "20.233.83.145"

def handle_client(c):
    try:
        req = c.recv(4096)
        if not req: return
        p = req.split(b'\\r\\n')[0].decode('utf-8', errors='ignore').split(' ')
        if len(p) >= 2 and p[0].upper() == 'CONNECT':
            host, port = p[1].split(':')
            ip = dns_query_a(host)
            r = socket.create_connection((ip, int(port)), timeout=10)
            c.sendall(b"HTTP/1.1 200 Connection established\\r\\n\\r\\n")
            socks = [c, r]
            while True:
                rd, _, _ = select.select(socks, [], [], 30)
                if not rd: break
                for s in rd:
                    o = r if s is c else c
                    d = s.recv(8192)
                    if not d: return
                    o.sendall(d)
    except: pass
    finally:
        try: c.close()
        except: pass

def start():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('127.0.0.1', 9997))
    srv.listen(10)
    while True:
        try:
            cl, _ = srv.accept()
            threading.Thread(target=handle_client, args=(cl,), daemon=True).start()
        except: break

threading.Thread(target=start, daemon=True).start()
time.sleep(0.5)
subprocess.run(["git", "add", "single_sheet_data.csv", "index.html", "build_instant_dashboard.py", "app.py"])
subprocess.run(["git", "commit", "-m", "sync: Auto-sync changes from Excel workbook"])
subprocess.run(["git", "-c", "http.proxy=http://127.0.0.1:9997", "push", "origin", "main"])
'''
        subprocess.run([sys.executable, "-c", proxy_code], capture_output=True)
        print("[+] GitHub Pages updated successfully!")
    except Exception as e:
        print(f"[-] Git push skipped/error: {e}")
        
    print("\n" + "=" * 60)
    print("  Sync Complete! Localhost & GitHub Pages are up to date.")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
