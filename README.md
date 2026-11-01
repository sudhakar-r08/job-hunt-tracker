# Career Pipeline & Job Hunt Tracker

An automated job discovery pipeline, intelligence aggregator, and local tracking dashboard designed for **Sudhakar Raju** (Lead Mobile Architect at Guardian, ex-Ayla Networks, ex-Vectone Mobile).

Targeting roles:
- **Mobile Application Architect**
- **Staff Software Engineer (Mobile)**
- **Senior Software Engineer**
- **SDE 3**

Target locations: **Bangalore**, **Chennai**, **Hyderabad**, and **Dubai (UAE)**.

---

## Features

- ⚡ **Local Command Center**: High-performance dark-mode dashboard running on Python standard library (no heavy npm/pip dependencies required).
- 🔒 **Secure Authentication**: Built-in login screen and credential protection.
- 🎯 **Target Compensation Benchmarking**: Automatically analyzes market rates and positions candidate offers at +30% hike (₹36.4+ LPA or AED 28,000–36,000/mo tax-free in the UAE).
- 📑 **Seamless Markdown Reader**: Integrated Markdown rendering inside the web app for viewing `data/core_profile.md` and tailored company resumes.
- 🏢 **Multi-Dimension Intelligence**: Logs company line of business, strategic hiring need, Glassdoor/culture reviews, and tailored application strategies.
- 🔗 **Exact Matching Job Links**: Direct, exact boolean quoted search URLs to active job listings on LinkedIn and corporate career portals.
- ⏰ **Scheduled Automation Sidecar**: Automated daily background cron runner at 9:00 AM Asia/Kolkata (`CRON_TZ=Asia/Kolkata 0 9 * * *`).

---

## Quick Start

### 1. Run the Web Application
```bash
python3 app.py serve --port 5050
```
Open **http://localhost:5050** in your browser.

### 2. Login Credentials
- **Username**: `sudhakar` (or `sudhakar.r08@gmail.com`)
- **Password**: `JobHunt2026!`

---

## Project Structure

```
├── app.py                     # Python HTTP server & SQLite REST API with auth
├── static/
│   └── index.html             # Sleek dashboard UI with embedded Markdown reader & login
├── data/
│   ├── jobs.db                # SQLite database storing tracked jobs and statuses
│   ├── core_profile.md        # Master single-source-of-truth profile
│   ├── core_profile.json      # Structured profile metadata
│   └── candidate_profile.json # Quick candidate preferences
├── resumes/                   # Role-tailored Markdown resumes generated per company
│   ├── youtrip-staff-mobile-engineer.md
│   ├── nagarro-mobile-architect.md
│   ├── deloitte-mobile-lead-architect.md
│   ├── emirates-mobile-architect-dubai.md
│   ├── phonepe-staff-mobile-architect.md
│   └── careem-staff-mobile-architect.md
└── update_jobs.py             # Database seed & URL migration script
```

---

## Scheduled Automation Sidecar

The automated sidecar configuration is located at:
`~/.gemini/config/sidecars/daily-job-hunt-assistant/sidecar.json`

Schedule: Daily at 9:00 AM (Asia/Kolkata)  
Command: `agentapi new-conversation -- <prompt>`
