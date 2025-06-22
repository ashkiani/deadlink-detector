#!/usr/bin/env python3
"""
Link Checker Script
Author: Siavash Ashkiani
Purpose: Crawl a website and report broken links with real-time status.
Features:
  - Internal link crawling up to a configurable depth
  - Optional external link checking and crawling up to a separate depth
  - Adjustable delay between requests
  - Adjustable HTTP timeout
  - Linux-style CLI flags: -h/--help, -v/--version, etc.
"""

import argparse
import csv
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict

# ─── Globals ─────────────────────────────────────────────────────────────────
visited = set()
broken_links = defaultdict(list)
page_counter = 0
link_counter = 0
ok_counter = 0
broken_counter = 0

# to be set from CLI args
start_url        = ""
log_filename     = ""
use_external     = False
max_internal     = 5
max_external     = 0
delay            = 0.05
req_timeout      = 5.0

# ANSI color codes
GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"

# ─── Helpers ─────────────────────────────────────────────────────────────────

def get_log_filename(base_url):
    parsed = urlparse(base_url)
    domain = parsed.netloc.replace(":", "_")
    return f"broken_links_{domain}.csv"

def is_http_url(url):
    return url.startswith("http://") or url.startswith("https://")

def write_broken_link_to_log(source_page, bad_link, error):
    with open(log_filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([source_page, bad_link, error])

def check_link(base_url, link_url):
    """HEAD request; returns (full_url, error) if broken, else (None, None)."""
    global link_counter, ok_counter, broken_counter
    full_url = urljoin(base_url, link_url)
    link_counter += 1
    try:
        resp = requests.head(full_url, allow_redirects=True, timeout=req_timeout)
        if resp.status_code >= 400:
            broken_counter += 1
            return full_url, resp.status_code
        ok_counter += 1
    except Exception as e:
        broken_counter += 1
        return full_url, str(e)
    return None, None

def crawl_page(url, depth):
    """Recursively crawl pages starting from 'url' at given 'depth'."""
    global page_counter

    normalized = url.split('#')[0]
    if normalized in visited:
        return

    # Determine if this URL is internal or external
    internal = normalized.startswith(start_url)

    # Depth checks
    if internal:
        if depth > max_internal:
            return
    else:
        if (not use_external) or depth > max_external:
            return

    visited.add(normalized)
    page_counter += 1

    # Fetch page
    try:
        res = requests.get(normalized, timeout=req_timeout)
        res.raise_for_status()
    except Exception as e:
        err = f"PAGE LOAD ERROR: {e}"
        broken_links[normalized].append((normalized, err))
        write_broken_link_to_log(normalized, normalized, err)
        return

    soup = BeautifulSoup(res.text, "html.parser")
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        full = urljoin(normalized, href).split('#')[0]

        # Skip external if not wanted
        if not full.startswith(start_url) and not use_external:
            continue

        # Print status line
        status = (
            f"Checked: {link_counter+1} | "
            f"OK: {GREEN}{ok_counter}{RESET} | "
            f"Broken: {RED}{broken_counter}{RESET} | "
            f"Current: {full[:80]}"
        )
        print("\r" + status.ljust(120), end="", flush=True)

        # Check the link
        bad, err = check_link(normalized, href)
        if err:
            broken_links[normalized].append((bad, err))
            write_broken_link_to_log(normalized, bad, err)

        # Recurse
        next_depth = depth + 1
        if full.startswith(start_url):
            if next_depth <= max_internal:
                crawl_page(full, next_depth)
        else:
            if use_external and next_depth <= max_external:
                crawl_page(full, next_depth)

    time.sleep(delay)

def print_final_report():
    print("\n\n✅ Crawl complete.")
    print(f"Pages crawled: {page_counter}")
    print(f"Links checked: {link_counter}")
    print(f"Working links: {ok_counter}")
    print(f"Broken links: {broken_counter}")
    print(f"📄 Broken link details saved to: {log_filename}")

# ─── CLI ─────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Crawl a site and report broken links (internal and/or external).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("start_url",
                        help="URL to begin crawling from")
    parser.add_argument("-o", "--output-file",
                        dest="output_file",
                        help="CSV file to write broken-link log into")
    parser.add_argument("-e", "--external", action="store_true",
                        help="also check and crawl external links")
    parser.add_argument("--depth-internal", type=int, default=5,
                        help="max recursion depth for internal links")
    parser.add_argument("--depth-external", type=int, default=0,
                        help="max recursion depth for external links (0 = only status check)")
    parser.add_argument("--delay", type=float, default=0.05,
                        help="seconds to sleep between each request")
    parser.add_argument("--timeout", type=float, default=5.0,
                        help="HTTP request timeout in seconds")
    parser.add_argument("-v", "--version", action="version",
                        version="deadlink-detector 1.1.0")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # Assign globals from args
    start_url     = args.start_url
    log_filename  = args.output_file if args.output_file else get_log_filename(start_url)
    use_external  = args.external
    max_internal  = args.depth_internal
    max_external  = args.depth_external
    delay         = args.delay
    req_timeout   = args.timeout

    # Prepare CSV log
    with open(log_filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Source Page", "Broken Link", "Error/Status"])

    # Header
    print(f"{GREEN}Link Checker Script{RESET}")
    print("Author: Siavash Ashkiani")
    print("Purpose: Crawl a website and report broken links in real time.")
    print("⚠️  Only internal links by default; use --external to include others.")
    print(f"🌐 Starting crawl from: {start_url}\n")

    crawl_page(start_url, depth=0)
    print_final_report()
