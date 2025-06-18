# 🕵️‍♂️ deadlink-detector

**Author:** Siavash Ashkiani  
**License:** MIT  
**Version:** 1.0.0

A fast, terminal-based tool for scanning internal links on a website and detecting broken URLs.  
Includes live progress display, CSV logging, and optional output file customization.

---

## 🔧 Features

- ✅ Recursively crawls internal links on a given domain
- ⚡ Displays live progress with counts for checked, working, and broken links
- 📄 Logs broken links in a CSV file (`broken_links_<domain>.csv`)
- 🛠 Optional override to specify a custom output file
- 💬 Simple, no-dependency CLI tool (Python + `requests` + `BeautifulSoup`)

---

## 🚀 Usage

### 🧩 Prerequisites

- Python 3.7+
- Install dependencies:

```bash
pip install requests beautifulsoup4
```

---

### 🖥️ Run the tool

```bash
python deadlink-detector.py <start_url> [optional_output_file.csv]
```

#### Examples

```bash
# Crawl arc-it.net and log to broken_links_arc-it.net.csv
python deadlink-detector.py https://www.arc-it.net

# Crawl a custom site and log to a specific file
python deadlink-detector.py https://example.com myreport.csv
```

---

## 📂 Output

Broken links are saved in a CSV file with the format:

```csv
Source Page,Broken Link,Error/Status
https://example.com/page1.html,https://example.com/missing.html,404
https://example.com/page2.html,https://example.com/timeout.js,ReadTimeout
```

---

## ✅ Sample Terminal Output

```
🌐 Starting crawl from: https://example.com

Checked: 132 | OK: 127 | Broken: 5 | Current: https://example.com/page/about.html
```

> Note: Only **one line** is printed to the screen and updated in place.  
> Broken links are not printed — they are saved directly to the log file.

---

## ✏️ Notes

- This tool checks only **internal links** (same domain).
- External links and media (images, scripts, etc.) are skipped.
- Links with fragments (e.g. `#section`) are normalized before crawling.
- By default, max depth is set to 5.

---

## 📜 License

MIT License © Siavash Ashkiani


---

## 🧱 Using the Pre-Built Executable (No Python Needed)

If you don’t want to install Python or dependencies, you can use the standalone Windows `.exe` version.

### 🔽 Download

You’ll find the executable in the **Releases** section of this repository (look for `deadlink-detector.exe`).

### ▶️ How to Run

Open Command Prompt and run:

```bash
deadlink-detector.exe <start_url> [optional_output_file.csv]
```

#### Example:

```bash
deadlink-detector.exe https://www.arc-it.net
```

It will produce a CSV report of broken links in the current directory.

### 🧩 Notes:

- Works on Windows 10/11
- No installation needed — just run the `.exe`
- Console output and logging behave the same as the Python version
