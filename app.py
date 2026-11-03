#!/usr/bin/env python3
"""
Job Hunt Tracker - Local Dashboard & Storage with Authentication, URL Queueing,
Two-Stage Applied/Confirmed Workflow & Gmail IMAP Confirmation Verifier
"""
import os
import re
import html
import json
import sqlite3
import subprocess
import argparse
import hashlib
import secrets
import imaplib
import email
from email.header import decode_header
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "jobs.db")
RESUMES_DIR = os.path.join(BASE_DIR, "resumes")
PREP_DIR = os.path.join(BASE_DIR, "prep")
CORE_PROFILE_PATH = os.path.join(BASE_DIR, "data", "core_profile.md")
EMAIL_CONFIG_PATH = os.path.join(BASE_DIR, "data", "email_config.json")
CANDIDATE_EMAIL = "sudhakar.r08@gmail.com"

os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
os.makedirs(RESUMES_DIR, exist_ok=True)
os.makedirs(PREP_DIR, exist_ok=True)

PREP_FILE_MAP = {
    "deloitte": "deloitte-prep.md",
    "phonepe": "phonepe-prep.md",
    "youtrip": "youtrip-prep.md",
    "emirates": "emirates-prep.md",
    "careem": "careem-prep.md",
    "nagarro": "nagarro-prep.md",
    "valuelabs": "valuelabs-prep.md",
    "talabat": "talabat-prep.md",
    "speechify": "speechify-prep.md",
    "bureau": "bureau-prep.md",
    "dazn": "dazn-prep.md",
}

def get_prep_info_for_company(company_name):
    """Returns (prep_rel_path, prep_content) for a given company name, supporting both mapped and dynamic <slug>-prep.md files."""
    c_lower = (company_name or "").lower().strip()
    if not c_lower:
        return ("", "")
    # 1. Check explicit map first
    for token, filename in PREP_FILE_MAP.items():
        if token in c_lower:
            full_path = os.path.join(PREP_DIR, filename)
            rel_path = os.path.join("prep", filename)
            if os.path.exists(full_path):
                try:
                    with open(full_path, "r", encoding="utf-8") as pf:
                        return (rel_path, pf.read())
                except Exception:
                    return (rel_path, "")
    # 2. Dynamic lookup in prep/ directory for any new companies added by daily automation
    primary_slug = re.sub(r"[^a-z0-9]+", "-", c_lower).strip("-")
    first_word = re.split(r"[\s,/()-]+", c_lower)[0]
    candidate_filenames = [f"{primary_slug}-prep.md", f"{first_word}-prep.md"]
    if os.path.exists(PREP_DIR):
        for fname in os.listdir(PREP_DIR):
            if not fname.endswith("-prep.md"):
                continue
            prefix = fname[:-8].lower()
            if fname in candidate_filenames or (len(prefix) >= 3 and prefix in c_lower):
                full_path = os.path.join(PREP_DIR, fname)
                rel_path = os.path.join("prep", fname)
                try:
                    with open(full_path, "r", encoding="utf-8") as pf:
                        return (rel_path, pf.read())
                except Exception:
                    return (rel_path, "")
    return ("", "")

# Default credentials
AUTH_USERS = {
    "sudhakar": hashlib.sha256("JobHunt2026!".encode("utf-8")).hexdigest(),
    "sudhakar.r08@gmail.com": hashlib.sha256("JobHunt2026!".encode("utf-8")).hexdigest()
}
ACTIVE_SESSIONS = set()

CONFIRMATION_PHRASES = [
    "thank you for applying",
    "thanks for applying",
    "your application was sent",
    "application was sent to",
    "we received your application",
    "we have received your application",
    "application received",
    "thank you for your application",
    "your application to",
    "your application for",
    "successfully applied",
    "application submitted",
    "submitted your application"
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT NOT NULL,
        line_of_business TEXT,
        need_for_role TEXT,
        company_profile TEXT,
        reliability_rating TEXT,
        glassdoor_review TEXT,
        market_salary TEXT,
        quoted_salary TEXT,
        job_url TEXT,
        applied_date TEXT,
        status TEXT DEFAULT 'Queued',
        tailored_resume_path TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def format_inline_markdown_to_html(text):
    """Converts inline Markdown (**bold**, *italic*, `code`, [label](url)) into clean HTML with zero leftover ** or brackets."""
    escaped = html.escape(text, quote=False)
    # Convert markdown links [label](url) -> <a href="url">label</a>
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{m.group(2).strip()}" style="color:#0f172a;text-decoration:underline;">{m.group(1).strip()}</a>',
        escaped
    )
    # Convert **bold** and __bold__
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"__(.+?)__", r"<b>\1</b>", escaped)
    # Convert *italic* and _italic_
    escaped = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<i>\1</i>", escaped)
    # Convert `inline code`
    escaped = re.sub(r"`([^`]+)`", r"<span>\1</span>", escaped)
    # Clean any stray unmatched ** that might remain
    escaped = escaped.replace("**", "")
    return escaped

def markdown_to_clean_resume_html(md_text):
    """Converts a Markdown resume into clean, ATS-friendly HTML suitable for both browser printing and DOCX conversion."""
    lines = (md_text or "").splitlines()
    body_parts = []
    in_list = False
    skip_comp_section = False

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        # Skip internal Compensation & Availability section in formal printable/DOCX resumes
        if re.match(r"^#{1,4}\s*Compensation\s*&\s*Availability", stripped, re.IGNORECASE):
            if in_list:
                body_parts.append("</ul>")
                in_list = False
            skip_comp_section = True
            continue
        if skip_comp_section and re.match(r"^#{1,4}\s+", stripped):
            skip_comp_section = False
        if skip_comp_section:
            continue

        if not stripped:
            if in_list:
                body_parts.append("</ul>")
                in_list = False
            continue

        if stripped == "---":
            if in_list:
                body_parts.append("</ul>")
                in_list = False
            body_parts.append('<hr style="border:none;border-top:1px solid #cbd5e1;margin:8pt 0;"/>')
            continue

        # Headings (#, ##, ###, ####)
        m_heading = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m_heading:
            if in_list:
                body_parts.append("</ul>")
                in_list = False
            level = len(m_heading.group(1))
            heading_html = format_inline_markdown_to_html(m_heading.group(2).strip())
            if level == 1:
                body_parts.append(f'<h1 style="font-size:16pt;margin:0 0 3pt 0;color:#0f172a;">{heading_html}</h1>')
            elif level == 2:
                body_parts.append(f'<h2 style="font-size:11.5pt;border-bottom:1px solid #334155;padding-bottom:2pt;margin:10pt 0 4pt 0;color:#0f172a;text-transform:uppercase;">{heading_html}</h2>')
            else:
                body_parts.append(f'<h3 style="font-size:10.5pt;margin:8pt 0 2pt 0;color:#1e293b;">{heading_html}</h3>')
            continue

        # Bullet points (- or *)
        m_bullet = re.match(r"^(\s*)[-*]\s+(.*)$", line)
        if m_bullet:
            indent_spaces = len(m_bullet.group(1))
            item_html = format_inline_markdown_to_html(m_bullet.group(2).strip())
            if not in_list:
                body_parts.append('<ul style="margin:3pt 0 5pt 16pt;padding:0;">')
                in_list = True
            margin_left = "14pt" if indent_spaces >= 2 else "0pt"
            body_parts.append(f'<li style="margin:2pt 0 2pt {margin_left};line-height:1.4;">{item_html}</li>')
            continue

        if in_list:
            body_parts.append("</ul>")
            in_list = False

        para_html = format_inline_markdown_to_html(stripped)
        body_parts.append(f'<p style="margin:2.5pt 0;line-height:1.4;">{para_html}</p>')

    if in_list:
        body_parts.append("</ul>")

    return (
        '<!DOCTYPE html><html><head><meta charset="utf-8">'
        '<style>body{font-family:Arial,Helvetica,sans-serif;font-size:10.5pt;line-height:1.42;color:#0f172a;max-width:780px;margin:24px auto;padding:0 16px;}'
        'a{color:#0f172a;text-decoration:underline;}</style></head><body>'
        + "\n".join(body_parts)
        + "</body></html>"
    )

RESUME_DOCX_MAP = {
    "youtrip-staff-mobile-engineer.md": "Raju_Sudhakar_YouTrip_Resume",
    "nagarro-mobile-architect.md": "Raju_Sudhakar_Nagarro_Resume",
    "deloitte-mobile-lead-architect.md": "Sudhakar_Raju_Deloitte_Resume",
    "emirates-mobile-architect-dubai.md": "Raju_Sudhakar_Emirates_Resume",
    "phonepe-staff-mobile-architect.md": "Raju_Sudhakar_PhonePe_Resume",
    "careem-staff-mobile-architect.md": "Raju_Sudhakar_Careem_Resume",
    "valuelabs-lead-android-developer.md": "Raju_Sudhakar_ValueLabs_Resume",
    "talabat-lead-mobile-architect-dubai.md": "Raju_Sudhakar_Talabat_Resume",
    "speechify-team-lead-android.md": "Raju_Sudhakar_Speechify_Resume",
    "bureau-senior-android-security-sdk.md": "Raju_Sudhakar_Bureau_Resume",
}

def compile_all_resumes():
    """Compiles all resumes/*.md into clean, zero-markdown-syntax .html and .docx files."""
    if not os.path.exists(RESUMES_DIR):
        return
    for fname in os.listdir(RESUMES_DIR):
        if not fname.endswith(".md"):
            continue
        md_path = os.path.join(RESUMES_DIR, fname)
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                md_text = f.read()
        except Exception:
            continue
        clean_html = markdown_to_clean_resume_html(md_text)
        stem = fname[:-3]
        target_base = RESUME_DOCX_MAP.get(fname, f"Raju_Sudhakar_{stem.split('-')[0].capitalize()}_Resume")
        html_out_path = os.path.join(RESUMES_DIR, f"{target_base}.html")
        docx_out_path = os.path.join(RESUMES_DIR, f"{target_base}.docx")
        try:
            with open(html_out_path, "w", encoding="utf-8") as hf:
                hf.write(clean_html)
            subprocess.run(
                ["textutil", "-convert", "docx", html_out_path, "-output", docx_out_path],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass

def sync_jobs_json():
    """Exports SQLite records to data/jobs.json for GitHub Pages & Mobile sync."""
    try:
        compile_all_resumes()
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM jobs ORDER BY updated_at DESC").fetchall()
        jobs = []
        for r in rows:
            item = dict(r)
            resume_path = item.get("tailored_resume_path")
            if resume_path and os.path.exists(resume_path):
                try:
                    with open(resume_path, "r", encoding="utf-8") as rf:
                        item["tailored_resume_content"] = rf.read()
                except Exception:
                    item["tailored_resume_content"] = ""
            else:
                item["tailored_resume_content"] = ""
            prep_path, prep_content = get_prep_info_for_company(item.get("company"))
            item["prep_guide_path"] = prep_path
            item["prep_guide_content"] = prep_content
            jobs.append(item)
        conn.close()

        json_path = os.path.join(BASE_DIR, "data", "jobs.json")
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump({"jobs": jobs, "total": len(jobs)}, jf, indent=2)
    except Exception as e:
        print("Error syncing jobs.json:", e)

def load_email_config():
    if os.path.exists(EMAIL_CONFIG_PATH):
        try:
            with open(EMAIL_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    env_pw = os.environ.get("GMAIL_APP_PASSWORD", "")
    return {"email": CANDIDATE_EMAIL, "apps_script_url": "", "app_password": env_pw}

def save_email_config(email_addr, app_password=None, apps_script_url=None):
    cfg = load_email_config()
    cfg["email"] = email_addr or cfg.get("email") or CANDIDATE_EMAIL
    if app_password is not None:
        cfg["app_password"] = app_password.replace(" ", "")
    if apps_script_url is not None:
        cfg["apps_script_url"] = apps_script_url.strip()
    with open(EMAIL_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    return cfg

def decode_mime_words(s):
    if not s:
        return ""
    decoded_parts = decode_header(s)
    out = []
    for content, charset in decoded_parts:
        if isinstance(content, bytes):
            out.append(content.decode(charset or "utf-8", errors="replace"))
        else:
            out.append(str(content))
    return "".join(out)

def match_and_confirm_jobs_from_messages(messages, target_email):
    """Matches a list of {subject, from, date, snippet} email objects against jobs.db and marks them Confirmed."""
    init_db()
    conn = get_db_connection()
    jobs = [dict(r) for r in conn.execute("SELECT * FROM jobs").fetchall()]
    confirmed_jobs = []

    for m in messages:
        subject = m.get("subject", "")
        sender = m.get("from", "")
        date_str = m.get("date", "")
        snippet = m.get("snippet", "")
        combined_text = f"{subject} {sender} {snippet}".lower()

        for job in jobs:
            if job.get("status") == "Confirmed":
                continue
            company_raw = (job.get("company") or "").strip()
            if not company_raw:
                continue
            primary_token = re.split(r"[\s,/()-]+", company_raw.lower())[0]
            if len(primary_token) < 3:
                primary_token = company_raw.lower()

            if company_raw.lower() in combined_text or primary_token in combined_text:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                note_addition = f" [Email Confirmed ({target_email}): '{subject[:70]}' on {now_str}]"
                updated_notes = ((job.get("notes") or "") + note_addition).strip()
                applied_dt = job.get("applied_date") or now_str
                if "Email Verified" not in applied_dt:
                    applied_dt = f"{applied_dt} (Email Verified)"

                conn.execute(
                    "UPDATE jobs SET status = 'Confirmed', applied_date = ?, notes = ?, updated_at = ? WHERE id = ?",
                    (applied_dt, updated_notes, now_str, job["id"])
                )
                job["status"] = "Confirmed"
                confirmed_jobs.append({
                    "id": job["id"],
                    "company": job["company"],
                    "title": job["title"],
                    "subject": subject or f"Confirmed match for {job['company']}",
                    "date": date_str or now_str
                })

    conn.commit()
    conn.close()
    sync_jobs_json()
    return confirmed_jobs

def verify_gmail_confirmations(email_addr=None, app_password=None, days_back=21, apps_script_url=None, receipt_text=None):
    """
    Supports 3 ways to confirm job applications from sudhakar.r08@gmail.com:
    1. Direct receipt_text paste from Gmail (works immediately without any password/script).
    2. Google Apps Script Web App URL (works with 2FA / Passkeys when App Passwords is unavailable).
    3. Gmail IMAP with 16-char App Password.
    """
    cfg = load_email_config()
    target_email = (email_addr or cfg.get("email") or CANDIDATE_EMAIL).strip()
    target_script_url = (apps_script_url if apps_script_url is not None else cfg.get("apps_script_url", "")).strip()
    target_pw = (app_password if app_password is not None else cfg.get("app_password", "")).replace(" ", "").strip()

    if app_password or apps_script_url:
        save_email_config(target_email, app_password=target_pw if app_password else None, apps_script_url=target_script_url if apps_script_url else None)

    # Mode 1: Direct pasted email receipt text / subject
    if receipt_text and receipt_text.strip():
        lines = [l.strip() for l in receipt_text.strip().splitlines() if l.strip()]
        subj = lines[0][:90] if lines else "Pasted Email Confirmation"
        confirmed = match_and_confirm_jobs_from_messages([{
            "subject": subj,
            "from": target_email,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "snippet": receipt_text
        }], target_email)
        return {
            "success": True,
            "mode": "receipt_paste",
            "email": target_email,
            "scanned_count": 1,
            "confirmed_jobs": confirmed
        }

    # Mode 2: Google Apps Script Bridge (No App Password Required - Works with Passkeys / 2FA)
    if target_script_url:
        try:
            req = Request(target_script_url, headers={"User-Agent": "JobHuntTracker/2.0"})
            with urlopen(req, timeout=15) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            messages = payload.get("messages", [])
            confirmed = match_and_confirm_jobs_from_messages(messages, target_email)
            return {
                "success": True,
                "mode": "apps_script",
                "email": target_email,
                "scanned_count": len(messages),
                "confirmed_jobs": confirmed
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Apps Script URL Error: {str(e)}",
                "confirmed_jobs": [],
                "scanned_count": 0
            }

    # Mode 3: IMAP with App Password
    if not target_pw:
        return {
            "success": False,
            "error": "No Google Apps Script URL or email snippet provided yet. Since Google disabled App Passwords on your account, use the 1-click Google Apps Script URL or paste any email confirmation text above!",
            "confirmed_jobs": [],
            "scanned_count": 0
        }

    init_db()
    conn = get_db_connection()
    jobs = [dict(r) for r in conn.execute("SELECT * FROM jobs").fetchall()]

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(target_email, target_pw)
        mail.select("INBOX")

        since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
        status, data = mail.search(None, f'(SINCE "{since_date}")')
        if status != "OK" or not data or not data[0]:
            mail.logout()
            conn.close()
            return {"success": True, "confirmed_jobs": [], "scanned_count": 0}

        msg_ids = data[0].split()[-120:]  # Inspect up to 120 most recent emails
        confirmed_jobs = []

        for mid in reversed(msg_ids):
            res, msg_data = mail.fetch(mid, "(RFC822.HEADER BODY.PEEK[TEXT]<0.2500>)")
            if res != "OK" or not msg_data:
                continue

            raw_header = b""
            raw_body = b""
            for part in msg_data:
                if isinstance(part, tuple):
                    if b"HEADER" in part[0]:
                        raw_header = part[1]
                    else:
                        raw_body = part[1]

            msg = email.message_from_bytes(raw_header)
            subject = decode_mime_words(msg.get("Subject", ""))
            sender = decode_mime_words(msg.get("From", ""))
            date_str = msg.get("Date", "")
            body_snippet = raw_body.decode("utf-8", errors="ignore")
            combined_text = f"{subject} {sender} {body_snippet}".lower()

            is_confirmation = any(phrase in combined_text for phrase in CONFIRMATION_PHRASES)
            if not is_confirmation:
                continue

            # Match against tracked companies
            for job in jobs:
                if job.get("status") == "Confirmed":
                    continue
                company_raw = (job.get("company") or "").strip()
                if not company_raw:
                    continue
                # Normalize company token (e.g. "Emirates Group" -> "emirates", "Deloitte Digital" -> "deloitte")
                primary_token = re.split(r"[\s,/()-]+", company_raw.lower())[0]
                if len(primary_token) < 3:
                    primary_token = company_raw.lower()

                if company_raw.lower() in combined_text or primary_token in combined_text:
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    note_addition = f" [Email Confirmed ({target_email}): '{subject[:70]}' on {now_str}]"
                    updated_notes = ((job.get("notes") or "") + note_addition).strip()
                    applied_dt = job.get("applied_date") or now_str
                    if "Email Verified" not in applied_dt:
                        applied_dt = f"{applied_dt} (Email Verified)"

                    conn.execute(
                        "UPDATE jobs SET status = 'Confirmed', applied_date = ?, notes = ?, updated_at = ? WHERE id = ?",
                        (applied_dt, updated_notes, now_str, job["id"])
                    )
                    job["status"] = "Confirmed"
                    confirmed_jobs.append({
                        "id": job["id"],
                        "company": job["company"],
                        "title": job["title"],
                        "subject": subject,
                        "date": date_str
                    })

        conn.commit()
        conn.close()
        mail.logout()
        sync_jobs_json()
        return {
            "success": True,
            "email": target_email,
            "scanned_count": len(msg_ids),
            "confirmed_jobs": confirmed_jobs
        }
    except Exception as e:
        conn.close()
        return {
            "success": False,
            "error": f"IMAP Check Error for {target_email}: {str(e)}",
            "confirmed_jobs": [],
            "scanned_count": 0
        }

def infer_company_and_title_from_url(url):
    if not url:
        return ("Pending Analysis", "Queued Role (Next Session)")
    parsed = urlparse(url)
    host = parsed.netloc.lower().replace("www.", "")
    path_parts = [p for p in parsed.path.split("/") if p]
    company = "LinkedIn Job Listing" if "linkedin.com" in host else (host.split(".")[0].capitalize() or "Target Company")
    title = "Queued Job URL (Scheduled for Next Session)"
    if path_parts:
        slug = path_parts[-1].replace("-", " ").replace("_", " ").strip()
        if len(slug) > 4 and not slug.isdigit():
            title = slug.title()[:80]
    return (company, title)

def add_or_update_job(job_data):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    job_url = (job_data.get('job_url') or '').strip()
    company = (job_data.get('company') or '').strip()
    title = (job_data.get('title') or '').strip()

    if not company or not title:
        inferred_company, inferred_title = infer_company_and_title_from_url(job_url)
        if not company:
            company = inferred_company
        if not title:
            title = inferred_title

    existing = None
    if job_data.get('id'):
        cursor.execute("SELECT id FROM jobs WHERE id = ?", (job_data.get('id'),))
        existing = cursor.fetchone()
    if not existing and job_url:
        cursor.execute("SELECT id FROM jobs WHERE job_url = ?", (job_url,))
        existing = cursor.fetchone()
    if not existing and company and title and title != "Queued Job URL (Scheduled for Next Session)":
        cursor.execute("SELECT id FROM jobs WHERE company = ? AND title = ?", (company, title))
        existing = cursor.fetchone()
        
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if existing:
        job_id = existing['id']
        cursor.execute("""
            UPDATE jobs SET
                title = COALESCE(?, title),
                company = COALESCE(?, company),
                location = COALESCE(?, location),
                line_of_business = COALESCE(?, line_of_business),
                need_for_role = COALESCE(?, need_for_role),
                company_profile = COALESCE(?, company_profile),
                reliability_rating = COALESCE(?, reliability_rating),
                glassdoor_review = COALESCE(?, glassdoor_review),
                market_salary = COALESCE(?, market_salary),
                quoted_salary = COALESCE(?, quoted_salary),
                job_url = COALESCE(?, job_url),
                applied_date = COALESCE(?, applied_date),
                status = COALESCE(?, status),
                tailored_resume_path = COALESCE(?, tailored_resume_path),
                notes = COALESCE(?, notes),
                updated_at = ?
            WHERE id = ?
        """, (
            job_data.get('title') or None,
            job_data.get('company') or None,
            job_data.get('location') or None,
            job_data.get('line_of_business') or None,
            job_data.get('need_for_role') or None,
            job_data.get('company_profile') or None,
            job_data.get('reliability_rating') or None,
            job_data.get('glassdoor_review') or None,
            job_data.get('market_salary') or None,
            job_data.get('quoted_salary') or None,
            job_url or None,
            job_data.get('applied_date') if 'applied_date' in job_data else None,
            job_data.get('status') or None,
            job_data.get('tailored_resume_path') or None,
            job_data.get('notes') or None,
            now,
            job_id
        ))
    else:
        status = job_data.get('status') or 'Queued for Next Session'
        cursor.execute("""
            INSERT INTO jobs (
                title, company, location, line_of_business, need_for_role,
                company_profile, reliability_rating, glassdoor_review,
                market_salary, quoted_salary, job_url, applied_date,
                status, tailored_resume_path, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            company,
            job_data.get('location') or 'TBD (Scheduled Analysis)',
            job_data.get('line_of_business') or 'Queued for Next Session Deep-Dive',
            job_data.get('need_for_role') or 'Scheduled for automated agent extraction in next session.',
            job_data.get('company_profile') or 'Queued URL awaiting next session analysis.',
            job_data.get('reliability_rating') or 'Pending Review',
            job_data.get('glassdoor_review') or 'Will be fetched in next scheduled session.',
            job_data.get('market_salary') or 'Target: 36.4+ LPA / AED 30k+ mo',
            job_data.get('quoted_salary') or '36.4+ LPA (+30% hike baseline)',
            job_url,
            job_data.get('applied_date') or '',
            status,
            job_data.get('tailored_resume_path') or '',
            job_data.get('notes') or f'Candidate Email: {CANDIDATE_EMAIL}. Added via Job URL Queue.',
            now,
            now
        ))
        job_id = cursor.lastrowid
        
    conn.commit()
    conn.close()
    sync_jobs_json()
    return job_id

class TrackerHandler(BaseHTTPRequestHandler):
    def send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def serve_static_file(self, rel_path, content_type):
        full_path = os.path.join(BASE_DIR, rel_path)
        if os.path.exists(full_path):
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open(full_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == "/" or path == "/index.html":
            self.serve_dashboard()
        elif path == "/manifest.json":
            self.serve_static_file("manifest.json", "application/manifest+json; charset=utf-8")
        elif path == "/sw.js":
            self.serve_static_file("sw.js", "application/javascript; charset=utf-8")
        elif path == "/icon.svg":
            self.serve_static_file("icon.svg", "image/svg+xml")
        elif path == "/data/jobs.json":
            self.serve_static_file(os.path.join("data", "jobs.json"), "application/json; charset=utf-8")
        elif path == "/data/core_profile.md":
            self.serve_static_file(os.path.join("data", "core_profile.md"), "text/markdown; charset=utf-8")
        elif path == "/api/email-config":
            cfg = load_email_config()
            self.send_json({
                "email": cfg.get("email", CANDIDATE_EMAIL),
                "apps_script_url": cfg.get("apps_script_url", ""),
                "has_password": bool(cfg.get("app_password"))
            })
        elif path == "/api/profile":
            if os.path.exists(CORE_PROFILE_PATH):
                with open(CORE_PROFILE_PATH, "r", encoding="utf-8") as pf:
                    content = pf.read()
                self.send_json({"content": content, "path": CORE_PROFILE_PATH, "email": CANDIDATE_EMAIL})
            else:
                self.send_json({"error": "Profile not found"}, 404)
        elif path == "/api/jobs":
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM jobs ORDER BY updated_at DESC").fetchall()
            jobs = []
            for r in rows:
                item = dict(r)
                resume_path = item.get("tailored_resume_path")
                if resume_path and os.path.exists(resume_path):
                    try:
                        with open(resume_path, "r", encoding="utf-8") as rf:
                            item["tailored_resume_content"] = rf.read()
                    except Exception:
                        item["tailored_resume_content"] = ""
                else:
                    item["tailored_resume_content"] = ""
                prep_path, prep_content = get_prep_info_for_company(item.get("company"))
                item["prep_guide_path"] = prep_path
                item["prep_guide_content"] = prep_content
                jobs.append(item)
            conn.close()
            self.send_json({"jobs": jobs, "total": len(jobs), "candidate_email": CANDIDATE_EMAIL})
        elif path.startswith("/api/jobs/"):
            job_id = path.split("/")[-1]
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            conn.close()
            if row:
                item = dict(row)
                resume_path = item.get("tailored_resume_path")
                if resume_path and os.path.exists(resume_path):
                    try:
                        with open(resume_path, "r", encoding="utf-8") as rf:
                            item["tailored_resume_content"] = rf.read()
                    except Exception:
                        item["tailored_resume_content"] = ""
                else:
                    item["tailored_resume_content"] = ""
                prep_path, prep_content = get_prep_info_for_company(item.get("company"))
                item["prep_guide_path"] = prep_path
                item["prep_guide_content"] = prep_content
                self.send_json(item)
            else:
                self.send_json({"error": "Job not found"}, 404)
        elif path.startswith("/resumes/"):
            filename = os.path.basename(path)
            file_path = os.path.join(RESUMES_DIR, filename)
            if os.path.exists(file_path):
                self.send_response(200)
                if filename.endswith(".html"):
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                elif filename.endswith(".docx"):
                    self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
                else:
                    self.send_header("Content-Type", "text/markdown; charset=utf-8")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Resume file not found")
        elif path.startswith("/prep/"):
            filename = os.path.basename(path)
            file_path = os.path.join(PREP_DIR, filename)
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/markdown; charset=utf-8")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Prep file not found")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        
        if self.path == "/api/login":
            try:
                data = json.loads(body.decode("utf-8"))
                username = data.get("username", "").strip()
                password = data.get("password", "").strip()
                pass_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
                
                if username in AUTH_USERS and AUTH_USERS[username] == pass_hash:
                    token = secrets.token_hex(24)
                    ACTIVE_SESSIONS.add(token)
                    self.send_json({
                        "success": True,
                        "token": token,
                        "user": {
                            "name": "Sudhakar Raju",
                            "username": username,
                            "email": CANDIDATE_EMAIL
                        }
                    })
                else:
                    self.send_json({"success": False, "error": "Invalid username or password"}, 401)
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        elif self.path == "/api/verify-emails":
            try:
                data = json.loads(body.decode("utf-8")) if body else {}
                result = verify_gmail_confirmations(
                    email_addr=data.get("email", CANDIDATE_EMAIL),
                    app_password=data.get("app_password"),
                    days_back=int(data.get("days_back", 21)),
                    apps_script_url=data.get("apps_script_url"),
                    receipt_text=data.get("receipt_text")
                )
                self.send_json(result, 200 if result.get("success") else 400)
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, 400)
        elif self.path == "/api/jobs":
            try:
                data = json.loads(body.decode("utf-8"))
                job_id = add_or_update_job(data)
                conn = get_db_connection()
                row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
                conn.close()
                self.send_json({"success": True, "id": job_id, "job": dict(row) if row else {}})
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self):
        if self.path.startswith("/api/jobs/"):
            job_id = self.path.split("/")[-1]
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
                conn = get_db_connection()
                fields = []
                values = []
                for k, v in data.items():
                    if k in ["title", "company", "location", "line_of_business", "need_for_role",
                             "company_profile", "reliability_rating", "glassdoor_review",
                             "market_salary", "quoted_salary", "job_url", "applied_date",
                             "status", "tailored_resume_path", "notes"]:
                        fields.append(f"{k} = ?")
                        values.append(v)
                fields.append("updated_at = ?")
                values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                values.append(job_id)
                
                query = f"UPDATE jobs SET {', '.join(fields)} WHERE id = ?"
                conn.execute(query, values)
                conn.commit()
                row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
                conn.close()
                sync_jobs_json()
                self.send_json({"success": True, "id": job_id, "job": dict(row) if row else {}})
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        if self.path.startswith("/api/jobs/"):
            job_id = self.path.split("/")[-1]
            try:
                conn = get_db_connection()
                conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
                conn.commit()
                conn.close()
                sync_jobs_json()
                self.send_json({"success": True, "deleted_id": job_id})
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        else:
            self.send_response(404)
            self.end_headers()

    def serve_dashboard(self):
        index_file = os.path.join(BASE_DIR, "static", "index.html")
        if os.path.exists(index_file):
            with open(index_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>Job Tracker Initializing...</h1>")

def run_server(port=5050):
    init_db()
    sync_jobs_json()
    server_address = ("", port)
    httpd = HTTPServer(server_address, TrackerHandler)
    print(f"Job Hunt Tracker running at http://localhost:{port} (Candidate Email: {CANDIDATE_EMAIL})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Job Hunt Tracker Service")
    parser.add_argument("command", choices=["serve", "init", "add", "list", "verify-emails"], nargs="?", default="serve")
    parser.add_argument("--port", type=int, default=5050, help="Port to run server on")
    parser.add_argument("--data", type=str, help="JSON string of job data for 'add'")
    parser.add_argument("--app-password", type=str, help="Gmail 16-char App Password for verify-emails")
    args = parser.parse_args()

    if args.command == "init":
        init_db()
        sync_jobs_json()
        print("Database initialized at", DB_PATH)
    elif args.command == "add" and args.data:
        data = json.loads(args.data)
        jid = add_or_update_job(data)
        print(f"Added/Updated job #{jid}")
    elif args.command == "verify-emails":
        res = verify_gmail_confirmations(CANDIDATE_EMAIL, args.app_password)
        print(json.dumps(res, indent=2))
    elif args.command == "list":
        init_db()
        conn = get_db_connection()
        rows = conn.execute("SELECT id, title, company, location, status, quoted_salary, job_url FROM jobs ORDER BY id DESC").fetchall()
        for r in rows:
            print(f"[{r['id']}] {r['title']} @ {r['company']} ({r['location']}) - {r['status']} | Quoted: {r['quoted_salary']} | URL: {r['job_url']}")
        conn.close()
    else:
        run_server(args.port)
