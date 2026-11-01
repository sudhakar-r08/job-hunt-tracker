#!/usr/bin/env python3
"""
Job Hunt Tracker - Local Dashboard & Storage with Authentication
Manages jobs applied/queued, company profiles, market salaries, reviews, and tailored resumes.
"""
import os
import json
import sqlite3
import argparse
import hashlib
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "jobs.db")
RESUMES_DIR = os.path.join(BASE_DIR, "resumes")
CORE_PROFILE_PATH = os.path.join(BASE_DIR, "data", "core_profile.md")

os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
os.makedirs(RESUMES_DIR, exist_ok=True)

# Default credentials
AUTH_USERS = {
    "sudhakar": hashlib.sha256("JobHunt2026!".encode("utf-8")).hexdigest(),
    "sudhakar.r08@gmail.com": hashlib.sha256("JobHunt2026!".encode("utf-8")).hexdigest()
}
ACTIVE_SESSIONS = set()

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

def add_or_update_job(job_data):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    job_url = job_data.get('job_url', '')
    company = job_data.get('company', '')
    title = job_data.get('title', '')
    
    existing = None
    if job_url:
        cursor.execute("SELECT id FROM jobs WHERE job_url = ?", (job_url,))
        existing = cursor.fetchone()
    if not existing and company and title:
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
            job_data.get('title'),
            job_data.get('company'),
            job_data.get('location'),
            job_data.get('line_of_business'),
            job_data.get('need_for_role'),
            job_data.get('company_profile'),
            job_data.get('reliability_rating'),
            job_data.get('glassdoor_review'),
            job_data.get('market_salary'),
            job_data.get('quoted_salary'),
            job_data.get('job_url'),
            job_data.get('applied_date'),
            job_data.get('status'),
            job_data.get('tailored_resume_path'),
            job_data.get('notes'),
            now,
            job_id
        ))
    else:
        cursor.execute("""
            INSERT INTO jobs (
                title, company, location, line_of_business, need_for_role,
                company_profile, reliability_rating, glassdoor_review,
                market_salary, quoted_salary, job_url, applied_date,
                status, tailored_resume_path, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job_data.get('title', 'Unknown Title'),
            job_data.get('company', 'Unknown Company'),
            job_data.get('location', ''),
            job_data.get('line_of_business', ''),
            job_data.get('need_for_role', ''),
            job_data.get('company_profile', ''),
            job_data.get('reliability_rating', ''),
            job_data.get('glassdoor_review', ''),
            job_data.get('market_salary', ''),
            job_data.get('quoted_salary', ''),
            job_data.get('job_url', ''),
            job_data.get('applied_date', now),
            job_data.get('status', 'Queued'),
            job_data.get('tailored_resume_path', ''),
            job_data.get('notes', ''),
            now,
            now
        ))
        job_id = cursor.lastrowid
        
    conn.commit()
    conn.close()
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
        elif path == "/api/profile":
            if os.path.exists(CORE_PROFILE_PATH):
                with open(CORE_PROFILE_PATH, "r", encoding="utf-8") as pf:
                    content = pf.read()
                self.send_json({"content": content, "path": CORE_PROFILE_PATH})
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
                jobs.append(item)
            conn.close()
            self.send_json({"jobs": jobs, "total": len(jobs)})
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
                self.send_json(item)
            else:
                self.send_json({"error": "Job not found"}, 404)
        elif path.startswith("/resumes/"):
            filename = os.path.basename(path)
            file_path = os.path.join(RESUMES_DIR, filename)
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/markdown; charset=utf-8")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Resume file not found")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
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
                            "email": "sudhakar.r08@gmail.com"
                        }
                    })
                else:
                    self.send_json({"success": False, "error": "Invalid username or password"}, 401)
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        elif self.path == "/api/jobs":
            try:
                data = json.loads(body.decode("utf-8"))
                job_id = add_or_update_job(data)
                self.send_json({"success": True, "id": job_id})
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
                conn.close()
                self.send_json({"success": True, "id": job_id})
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
    server_address = ("", port)
    httpd = HTTPServer(server_address, TrackerHandler)
    print(f"Job Hunt Tracker running at http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Job Hunt Tracker Service")
    parser.add_argument("command", choices=["serve", "init", "add", "list"], nargs="?", default="serve")
    parser.add_argument("--port", type=int, default=5050, help="Port to run server on")
    parser.add_argument("--data", type=str, help="JSON string of job data for 'add'")
    args = parser.parse_args()

    if args.command == "init":
        init_db()
        print("Database initialized at", DB_PATH)
    elif args.command == "add" and args.data:
        data = json.loads(args.data)
        jid = add_or_update_job(data)
        print(f"Added/Updated job #{jid}")
    elif args.command == "list":
        init_db()
        conn = get_db_connection()
        rows = conn.execute("SELECT id, title, company, location, status, quoted_salary FROM jobs ORDER BY id DESC").fetchall()
        for r in rows:
            print(f"[{r['id']}] {r['title']} @ {r['company']} ({r['location']}) - {r['status']} | Quoted: {r['quoted_salary']}")
        conn.close()
    else:
        run_server(args.port)
