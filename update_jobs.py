import sqlite3

db_path = "/Users/sudhakarraju/.gemini/antigravity/scratch/job-hunt-tracker/data/jobs.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Exact matching boolean search strings on LinkedIn with quoted exact job title
updates = [
    (
        "https://www.linkedin.com/jobs/search/?keywords=%22Staff+Mobile+Engineer%22+YouTrip&location=Bengaluru%2C+Karnataka%2C+India&sortBy=R",
        1
    ),
    (
        "https://www.linkedin.com/jobs/search/?keywords=%22Mobile+Architect%22+Nagarro&location=Hyderabad%2C+Telangana%2C+India&sortBy=R",
        2
    ),
    (
        "https://www.linkedin.com/jobs/search/?keywords=%22Mobile+Architect%22+Deloitte&location=Chennai%2C+Tamil+Nadu%2C+India&sortBy=R",
        3
    ),
    (
        "https://www.linkedin.com/jobs/search/?keywords=%22Mobile+Architect%22+Emirates&location=Dubai%2C+United+Arab+Emirates&sortBy=R",
        4
    ),
    (
        "https://www.linkedin.com/jobs/search/?keywords=%22Staff+Software+Engineer%22+Mobile+PhonePe&location=Bengaluru%2C+Karnataka%2C+India&sortBy=R",
        5
    ),
    (
        "https://www.linkedin.com/jobs/search/?keywords=%22Staff+Mobile+Engineer%22+Careem&location=Dubai%2C+United+Arab+Emirates&sortBy=R",
        6
    )
]

for url, jid in updates:
    cursor.execute("UPDATE jobs SET job_url = ? WHERE id = ?", (url, jid))

conn.commit()
conn.close()
print("Updated jobs with exact boolean quoted search URLs.")
