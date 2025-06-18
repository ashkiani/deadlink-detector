#!/usr/bin/env python3
"""
Link Checker Script
Author: Siavash Ashkiani
Purpose: Crawl a website and report broken internal links with real-time status.
Only internal (same-domain) links are checked.
External domains and fragments (#) are ignored.
"""

import sys
import csv
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict

visited = set()
broken_links = defaultdict(list)
page_counter = 0
link_counter = 0
ok_counter = 0
broken_counter = 0

from urllib.parse import urlparse

def get_log_filename(base_url):
    parsed = urlparse(base_url)
    domain = parsed.netloc.replace(":", "_")  # replace : in case of port
    return f"broken_links_{domain}.csv"

log_filename = ""  # will be set in __main__

def is_http_url(url):
    return url.startswith("http://") or url.startswith("https://")

def write_broken_link_to_log(source_page, bad_link, error):
    with open(log_filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([source_page, bad_link, error])

def check_link(base_url, link_url):
    global link_counter, ok_counter, broken_counter
    full_url = urljoin(base_url, link_url)
    link_counter += 1
    try:
        response = requests.head(full_url, allow_redirects=True, timeout=5)
        if response.status_code >= 400:
            broken_counter += 1
            return full_url, response.status_code
        else:
            ok_counter += 1
    except Exception as e:
        broken_counter += 1
        return full_url, str(e)
    return None, None

def crawl_page(url, root_url, depth=0, max_depth=5):
    global page_counter
    normalized_url = url.split('#')[0]
    if normalized_url in visited or depth > max_depth:
        return
    visited.add(normalized_url)
    page_counter += 1

    try:
        res = requests.get(normalized_url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        broken_links[normalized_url].append((normalized_url, f"PAGE LOAD ERROR: {e}"))
        write_broken_link_to_log(normalized_url, normalized_url, f"PAGE LOAD ERROR: {e}")
        return

    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.find_all("a", href=True)

    for tag in links:
        href = tag["href"]
        full_link = urljoin(normalized_url, href)
        parsed_full = urlparse(full_link)
        full_link_clean = full_link.split('#')[0]

        if not full_link_clean.startswith(root_url):
            continue

        # Update single-line status bar
        status_line = f"Checked: {link_counter+1} | OK: {GREEN}{ok_counter}{RESET} | Broken: {RED}{broken_counter}{RESET} | Current: {full_link_clean[:80]}"
        print("\r" + status_line.ljust(120), end="", flush=True)

        link_url, error = check_link(normalized_url, href)
        if error:
            broken_links[normalized_url].append((link_url, error))
            write_broken_link_to_log(normalized_url, link_url, error)

        crawl_page(full_link_clean, root_url, depth + 1, max_depth)

    time.sleep(0.05)

def print_final_report():
    print("\n\n✅ Crawl complete.")
    print(f"Pages crawled: {page_counter}")
    print(f"Links checked: {link_counter}")
    print(f"Working links: {ok_counter}")
    print(f"Broken links: {broken_counter}")
    print(f"📄 Broken link details saved to: {log_filename}")


GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
TEAL = "\033[36m"  # or for bright teal: "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nLink Checker by Siavash Ashkiani")
        print("Usage: python deadlink-detector.py <starting_url> [output_csv_file]")
        print("Example: python deadlink-detector.py https://www.arc-it.net")
        print("         python deadlink-detector.py https://example.com report.csv")
        sys.exit(1)

    start_url = sys.argv[1]
    if not is_http_url(start_url):
        print("Only http(s) URLs are supported.")
        sys.exit(1)

    # Use custom file name if given, else fallback to domain-based name
    log_filename = sys.argv[2] if len(sys.argv) > 2 else get_log_filename(start_url)

    # Prepare log file
    with open(log_filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Source Page", "Broken Link", "Error/Status"])
    
    print(f"{GREEN}Link Checker Script{RESET}")
    print("Author: Siavash Ashkiani")
    print("Purpose: Crawl a website and report broken internal links with real-time status.")
    print("⚠️ Only internal (same-domain) links are checked. External domains and fragments (#) are ignored.")

    print(f"🌐 Starting crawl from: {start_url}\n")
    crawl_page(start_url, start_url)
    print_final_report()
