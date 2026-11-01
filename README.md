# Career Pipeline & Job Hunt Tracker

An automated job discovery pipeline, application automation engine, Gmail confirmation verifier, interview preparation generator, and Web/Mobile PWA dashboard designed for **Sudhakar Raju** (`sudhakar.r08@gmail.com` | Lead Mobile Architect at Guardian, ex-Ayla Networks, ex-Vectone Mobile, ex-Infitech Reality).

Targeting roles:
- **Mobile Application Architect**
- **Staff Software Engineer (Mobile)**
- **Senior Software Engineer / Lead Android Developer**
- **SDE 3**

Target locations: **Bangalore**, **Chennai**, **Hyderabad**, and **UAE (Dubai / Abu Dhabi)**.

---

## Features

- ⚡ **Local & Cloud Mobile PWA Command Center**: High-performance dark-mode dashboard running locally on Python (`http://localhost:5050`) and hosted on GitHub Pages (`https://sudhakar-r08.github.io/job-hunt-tracker/`) with Android Share Sheet integration (`manifest.json` + `sw.js`).
- 🟢 **Two-Stage Application Status Button**:
  - **Outlined `◎ Applied` (`status: "Applied"`)**: Automatically set when the automation submits your application.
  - **Filled Solid Green `✓ Applied` (`status: "Confirmed"`)**: Automatically upgraded when a confirmation receipt is verified in `sudhakar.r08@gmail.com` (or clicked manually).
- 🎯 **Tailored Interview Preparation Guides (`prep/*.md`) & Resumes (`resumes/*.md`)**: Integrated 2-tab Markdown reader inside each job's detail modal (`🎯 Interview Preparation Guide (.md)` + `📄 Tailored Resume (.md)`) plus `data/core_profile.md`.
- 🔗 **Job URL Queue & Next-Session Scheduler**: Paste any LinkedIn or company job URL on Desktop or Mobile to queue it (`Queued for Next Session`) for automatic scraping, resume tailoring, prep guide creation, and application in the next scheduled run.
- 💰 **Target Compensation Benchmarking**: Positions candidate offers at `+30% hike` (`₹36.4–42+ LPA` on `28 LPA` baseline, or `AED 30,000–35,000/mo` tax-free in the UAE).
- ⏰ **Daily 9:00 AM IST Automated Pipeline**: Background scheduled automation (`CRON_TZ=Asia/Kolkata 0 9 * * *`).

---

## Quick Start

### 1. Run the Local Web Server
```bash
python3 app.py serve --port 5050
```
Open **http://localhost:5050** in your browser (or **https://sudhakar-r08.github.io/job-hunt-tracker/** on Mobile).

### 2. Login & Portal Credentials
- **Dashboard Login**: `sudhakar` or `sudhakar.r08@gmail.com` / `JobHunt2026!`
- **External Career Portals (Deloitte USI, Emirates Group)**: `sudhakar.r08@gmail.com` / `JobHunt@2026!`

---

## Project Structure

```
├── app.py                     # Python HTTP server, SQLite REST API & JSON/Prep exporter
├── index.html                 # GitHub Pages / Mobile PWA entry point
├── static/
│   └── index.html             # Dashboard UI with Prep Guide & Resume tabs, URL Scheduler & Gmail matcher
├── manifest.json              # PWA Web App Manifest with Android Share Target support
├── sw.js                      # Offline-capable Service Worker
├── data/
│   ├── jobs.db                # SQLite database storing tracked jobs and statuses
│   ├── jobs.json              # Auto-synced JSON payload (includes resumes & prep guides for Mobile/GitHub Pages)
│   ├── core_profile.md        # Master single-source-of-truth candidate profile
│   └── core_profile.json      # Structured profile metadata
├── resumes/                   # Role-tailored Markdown resumes generated per company
│   ├── youtrip-staff-mobile-engineer.md
│   ├── nagarro-mobile-architect.md
│   ├── deloitte-mobile-lead-architect.md
│   ├── emirates-mobile-architect-dubai.md
│   ├── phonepe-staff-mobile-architect.md
│   ├── careem-staff-mobile-architect.md
│   └── valuelabs-lead-android-developer.md
└── prep/                      # Role-tailored Interview Preparation Guides (System Design, Q&A, STAR, Comp)
    ├── youtrip-prep.md
    ├── nagarro-prep.md
    ├── deloitte-prep.md
    ├── emirates-prep.md
    ├── phonepe-prep.md
    ├── careem-prep.md
    └── valuelabs-prep.md
```
