r"""
GCDC HSE Real-Time Excel Watcher Daemon
Automatically watches the Excel folder for any changes or saves (Ctrl + S).
Immediately updates CSV, index.html, and pushes to live GitHub Pages.
"""

import os
import sys
import time
import datetime
from sync_engine import find_latest_excel, execute_sync, get_last_status

POLL_INTERVAL_SECONDS = 3

def start_watching():
    print("=" * 60)
    print("  GCDC HSE DASHBOARD - REAL-TIME EXCEL WATCHER ACTIVE")
    print("=" * 60)
    
    last_file = find_latest_excel()
    last_mtime = os.path.getmtime(last_file) if (last_file and os.path.exists(last_file)) else 0
    
    print(f"[*] Initial Active File: {last_file}")
    if last_file:
        mtime_str = datetime.datetime.fromtimestamp(last_mtime).strftime("%d-%b-%Y %I:%M:%S %p")
        print(f"[*] Last Modified: {mtime_str}")
    print(f"[*] Monitoring for changes every {POLL_INTERVAL_SECONDS} seconds...")
    print("=" * 60)

    while True:
        try:
            current_file = find_latest_excel()
            if not current_file:
                time.sleep(POLL_INTERVAL_SECONDS)
                continue
                
            current_mtime = os.path.getmtime(current_file)
            
            # Check if file changed or file was modified
            if current_file != last_file or current_mtime > last_mtime:
                filename = os.path.basename(current_file)
                print(f"\n[+] [{datetime.datetime.now().strftime('%H:%M:%S')}] Change detected in: {filename}")
                print("    Waiting 2 seconds for Excel write lock to release...")
                time.sleep(2)
                
                print("    Executing automated sync & GitHub deployment...")
                result = execute_sync(push=True)
                
                if result.get("success"):
                    print(f"    [SUCCESS] Synced {result.get('filename')}!")
                    if result.get("pushed"):
                        print(f"    [SUCCESS] Pushed to GitHub Pages live link!")
                    else:
                        print(f"    [NOTE] Git message: {result.get('push_msg')}")
                else:
                    print(f"    [ERROR] Sync failed: {result.get('error')}")
                    
                last_file = current_file
                last_mtime = os.path.getmtime(current_file)
                
            time.sleep(POLL_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("\n[*] Watcher stopped by user.")
            break
        except Exception as e:
            print(f"[!] Watcher error: {e}")
            time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    start_watching()
