"""
Divytosh Upadhyay — Data Science Portfolio (single-file FastAPI, SMTP support)

Run:
    pip install fastapi uvicorn pydantic
    python portfolio_fastapi_final3.py

Open:
    http://127.0.0.1:8000

Notes:
- Single-file FastAPI app with inline HTML/CSS/JS.
- Contact feedback optionally forwards an email via SMTP when SMTP env vars are provided.
- Displayed contact email set to divyatoshupadhyay@gmail.com (as requested).
- Provide environment variables to enable SMTP:
    SMTP_HOST (optional, default smtp.gmail.com if SMTP_USER endswith @gmail.com)
    SMTP_PORT (optional, default 587)
    SMTP_USER
    SMTP_PASS
    CONTACT_RECEIVER (optional, defaults to SMTP_USER or divyatoshupadhyay@gmail.com)
"""
import json
import datetime
import os
import smtplib
from email.message import EmailMessage
from typing import List, Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel, EmailStr, ValidationError
import uvicorn

app = FastAPI(title="Divytosh Upadhyay — Portfolio (with SMTP)")

# ---------- Configuration ----------
SUBMISSIONS_FILE = "submissions.json"
DISPLAY_EMAIL = "divyatoshupadhyay@gmail.com"  # user-provided Gmail (assumed)

# SMTP config (optional). Set these as environment variables to enable email forwarding.
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT")) if os.environ.get("SMTP_PORT") else None
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
CONTACT_RECEIVER = os.environ.get("CONTACT_RECEIVER") or (SMTP_USER or DISPLAY_EMAIL)

# If SMTP_USER looks like a Gmail address and no SMTP_HOST/PORT provided, default to Gmail SMTP
if SMTP_USER and SMTP_USER.lower().endswith("@gmail.com"):
    if not SMTP_HOST:
        SMTP_HOST = "smtp.gmail.com"
    if not SMTP_PORT:
        SMTP_PORT = 587

# ---------- Persistence ----------
def load_submissions() -> List[dict]:
    try:
        if os.path.exists(SUBMISSIONS_FILE):
            with open(SUBMISSIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_submission(entry: dict):
    arr = load_submissions()
    arr.append(entry)
    try:
        with open(SUBMISSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(arr, f, indent=2)
    except Exception:
        pass

FEEDBACKS = load_submissions()

# ---------- Content (projects, skills, certs) ----------
PROJECTS = [
    {"id":"usa-sales","title":"USA Sales Dashboard","summary":"Regional sales analytics using Power BI.","github":"https://github.com/Divya-techie-cmd","tags":["Power BI","Dashboard","Sales"],"year":"2023"},
    {"id":"flipkart-insights","title":"Flipkart Data Insights","summary":"Customer behavior & pricing trends analysis.","github":"https://github.com/Divya-techie-cmd","tags":["E-commerce","Analysis"],"year":"2024"},
    {"id":"amazon-sales","title":"Amazon Sales Analysis","summary":"E-commerce performance dashboard.","github":"https://github.com/Divya-techie-cmd","tags":["E-commerce","Dashboard"],"year":"2024"},
    {"id":"sheguard","title":"SheGuard AI","summary":"AI-based women's safety app (ML + Computer Vision).","github":"https://github.com/Divya-techie-cmd","tags":["AI","Computer Vision","Mobile"],"year":"2024"},
    {"id":"order-dashboard","title":"Order Dashboard","summary":"Order Tracker for operational monitoring.","github":"https://github.com/Divya-techie-cmd","tags":["Dashboard","Operations"],"year":"2023"},
    {"id":"jobseeker-crm","title":"Job Seeker Data & CRM Management System Plan","summary":"Job Seeker Data Dashboard in India.","github":"https://github.com/Divya-techie-cmd","tags":["Data Product","CRM"],"year":"2024"},
    {"id":"export-india","title":"Total Export of India 1988-2020","summary":"Export of India 1988 - 2020 Dashboard.","github":"https://github.com/Divya-techie-cmd","tags":["Time Series","Visualization"],"year":"2022"},
    {"id":"cancer-detect","title":"Cancer Detection","summary":"ML classification model for early prediction.","github":"https://github.com/Divya-techie-cmd","tags":["ML","Healthcare"],"year":"2024"},
    {"id":"hr-analytics","title":"HR Analytics","summary":"Attrition and employee satisfaction dashboard.","github":"https://github.com/Divya-techie-cmd","tags":["HR","Dashboard"],"year":"2023"},
    {"id":"complaint-dashboard","title":"Customer Complaint Dashboard","summary":"Insights on complaint frequency & channels.","github":"https://github.com/Divya-techie-cmd","tags":["CX","Dashboard"],"year":"2023"},
    {"id":"ipl-dashboard","title":"IPL Dashboard","summary":"Sports analytics for players and teams.","github":"https://github.com/Divya-techie-cmd","tags":["Sports Analytics","Visualization"],"year":"2021"},
    {"id":"corporate-health","title":"Corporate Health Survey","summary":"Employee wellness trends & insights.","github":"https://github.com/Divya-techie-cmd","tags":["Survey","Insights"],"year":"2022"},
    {"id":"netflix-summary","title":"Netflix Summary","summary":"User behavior, trends, and content insights.","github":"https://github.com/Divya-techie-cmd","tags":["Content Analytics"],"year":"2022"},
    {"id":"traffic-pattern","title":"Traffic Pattern Analysis","summary":"Peak hour and congestion insights.","github":"https://github.com/Divya-techie-cmd","tags":["Geospatial","Traffic"],"year":"2020"},
    {"id":"student-performance","title":"Student Performance","summary":"Academic trends and improvements.","github":"https://github.com/Divya-techie-cmd","tags":["Education","Analytics"],"year":"2021"},
    {"id":"covid-india","title":"COVID-19 India","summary":"Case analysis and regional impact tracking.","github":"https://github.com/Divya-techie-cmd","tags":["Epidemiology","Visualization"],"year":"2020"},
    {"id":"customer-seg","title":"Customer Segmentation","summary":"Customer Segmentation Using K-Means.","github":"https://github.com/Divya-techie-cmd","tags":["Clustering","ML"],"year":"2023"},
    {"id":"sales-forecast","title":"Sales Forecasting","summary":"Forecasting with linear regression.","github":"https://github.com/Divya-techie-cmd","tags":["Forecasting","Time Series"],"year":"2023"}
]

SKILLS_TECHNICAL = [
    "SQL", "Python", "Statistics", "ETL", "Data Visualization", "AI Automation",
    "Machine Learning", "NLP", "Software Development"
]

SKILLS_TOOLS = [
    "GCP", "AWS (S3, Athena, EC2)", "dbt", "Tableau", "Power BI", "Excel (proficient)", "GA4"
]

CERTIFICATES = [
    "Cisco: Introduction to Data Science",
    "Simplilearn: Introduction - MS Excel",
    "Simplilearn: Data Analyst 101 - MS Excel Formulas & Functions",
    "Simplilearn: Microsoft Learn Power BI Basics",
    "Deloitte Virtual Internship (Forage)",
    "Acme Grade: Netflix Data Analysis",
    "GDSC Workshop – Google Developer Clubs",
    "Hack the Mountain – Marwadi University",
    "Tamizhan Skills – Internship Program",
    "Tata (Forage) - Data visualisation",
    "IBM - Data Analysis Using Python"
]

ADDITIONAL_ACHIEVEMENTS = [
    "Built a Fire Detection Robot — integrated sensors, control systems and automation.",
    "Developed a Smart Car (visible in the second image) — perception, control and path logic; required coordination, patience, and technical problem-solving."
]

# ---------- Models ----------
class FeedbackModel(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    message: str

# ---------- SMTP helper ----------
def send_email_via_smtp(subject: str, body: str, reply_to: Optional[str] = None) -> bool:
    """
    Send an email using configured SMTP. Returns True if sent, False otherwise.
    Uses SMTP_USER as auth username if provided; otherwise does nothing.
    """
    if not SMTP_USER or not SMTP_PASS or not SMTP_HOST or not SMTP_PORT:
        return False
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = CONTACT_RECEIVER
        if reply_to:
            msg["Reply-To"] = reply_to
        msg.set_content(body)
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("SMTP send failed:", e)
        return False

# ---------- Resume HTML (light theme) ----------
RESUME_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Resume - Divytosh Upadhyay</title>
<style>
body{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial;margin:0;background:#f7f9fc;color:#061022;padding:28px}
.container{max-width:900px;margin:0 auto;background:#ffffff;padding:26px;border-radius:12px;border:1px solid #e6eef8;box-shadow:0 8px 30px rgba(10,20,40,0.04)}
h1{margin:0} .muted{color:#4b5563}
.section{margin-top:14px}
</style>
</head><body>
<div class="container">
<h1>Divytosh Upadhyay</h1>
<div class="muted">Data Analyst | Data Scientist | Machine Learning Engineer</div>

<div class="section"><strong>Education</strong>
<div>B.Tech in Artificial Intelligence & Data Science — Guru Gobind Singh Indraprastha University (GGSIPU)</div>
<div class="muted">Overall CGPA: 8.4 · Semester 5 SGPA: 9.0</div>
</div>

<div class="section"><strong>Experience</strong>
<ul>
<li>Machine Learning Intern — Tamizhan Skills: Statistical analysis on 10,000+ records, NLP models improving performance by 18%</li>
<li>Data Analyst Intern — Update Education Technology Pvt. Ltd.: Power BI & Tableau dashboards, automated reporting</li>
<li>Data Analyst Intern — Tamizhan Skills: Demand forecasting reducing costs by 10%</li>
</ul>
</div>

<div class="section"><strong>Skills</strong>
<div>""" + ", ".join(SKILLS_TECHNICAL + SKILLS_TOOLS) + """</div>
</div>

<div class="section"><strong>Selected Projects</strong>
<ul>
<li>Resource Utilization & GMV Growth Strategy Report — Analyzed 5,000+ records; interactive dashboards; optimization insights</li>
<li>USA Sales Dashboard — Regional sales analytics using Power BI</li>
<li>SheGuard AI — AI-based women's safety app (ML + CV)</li>
</ul>
</div>

<div class="section"><strong>Certifications</strong>
<ul>
""" + "".join(f"<li>{c}</li>" for c in CERTIFICATES) + """
</ul>
</div>

<div class="section"><strong>Achievements</strong>
<ul>
<li>Runner-up — Hack the Mountain Hackathon (2000+ participants)</li>
<li>Built a Fire Detection Robot</li>
<li>Developed a Smart Car (see second image)</li>
</ul>
</div>

<div class="section muted"><small>Generated: """ + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC") + """</small></div>

</div></body></html>
"""

# ---------- Main HTML template ----------
MAIN_HTML_TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Divytosh Upadhyay — Portfolio</title>
<style>
:root{--bg:#070828;--card:rgba(255,255,255,0.03);--accent-cyan:#4EE8E8;--accent-violet:#9B5CFF;--muted:#98a0b3}
html,body{height:100%;margin:0;background:var(--bg);color:#e6eef8;font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto,Arial}
.bg-ai { position:fixed; inset:0; z-index:-1; pointer-events:none; background:
 radial-gradient(700px 240px at 10% 10%, rgba(155,92,255,0.08), transparent),
 radial-gradient(520px 200px at 90% 90%, rgba(78,232,232,0.06), transparent),
 linear-gradient(180deg,#020617, #061033); animation: bgShift 14s ease-in-out infinite; }
@keyframes bgShift { 0%{transform:scale(1)}50%{transform:scale(1.02) translateY(-8px)}100%{transform:scale(1)}}
.container{max-width:1100px;margin:28px auto;padding:22px;position:relative;z-index:1}
.header{display:flex;align-items:center;justify-content:space-between;padding:16px;border-radius:12px;background:linear-gradient(180deg,rgba(255,255,255,0.02),rgba(255,255,255,0.01));border:1px solid rgba(255,255,255,0.03)}
.brand{display:flex;gap:12px;align-items:center}
.logo{width:64px;height:64px;border-radius:12px;background:linear-gradient(135deg,var(--accent-violet),var(--accent-cyan));display:flex;align-items:center;justify-content:center;font-weight:800;color:#040617;font-size:20px;box-shadow:0 10px 40px rgba(107,33,255,0.08)}
.hero-title{font-size:28px;font-weight:800;margin:0}
.hero-sub{color:var(--muted);margin-top:4px}
.cta{display:flex;gap:10px}
.btn{padding:10px 14px;border-radius:10px;font-weight:700;cursor:pointer;border:none;color:#040617;background:linear-gradient(90deg,var(--accent-cyan),var(--accent-violet));box-shadow:0 10px 30px rgba(0,0,0,0.6)}
.btn.ghost{background:transparent;color:#e6eef8;border:1px solid rgba(255,255,255,0.06)}
.btn.gitlight{background:#ffffff;color:#071028;border:1px solid rgba(0,0,0,0.06);box-shadow:0 6px 18px rgba(7,16,40,0.12)}
.layout{display:grid;grid-template-columns:1fr 360px;gap:22px;margin-top:20px}
.section-card{background:var(--card);padding:16px;border-radius:12px;border:1px solid rgba(255,255,255,0.03);transition:transform .18s ease}
.section-card:hover{transform:translateY(-8px);box-shadow:0 20px 50px rgba(0,0,0,0.6)}
.muted{color:var(--muted)}
.skill-chip{display:inline-block;padding:8px 10px;border-radius:999px;margin:6px;background:linear-gradient(90deg,rgba(155,92,255,0.12),rgba(78,232,232,0.05));font-weight:700;color:#eaf6ff;font-size:13px}
.progress{height:12px;background:rgba(255,255,255,0.03);border-radius:999px;overflow:hidden}
.progress>i{display:block;height:100%;background:linear-gradient(90deg,var(--accent-violet),var(--accent-cyan));width:0%;transition:width 900ms}
.project-card{display:flex;justify-content:space-between;align-items:center;padding:12px;border-radius:10px;background:linear-gradient(180deg,rgba(255,255,255,0.01),transparent);border:1px solid rgba(255,255,255,0.03);gap:12px}
.social-link{display:inline-flex;align-items:center;gap:8px;padding:8px 10px;border-radius:10px;background:rgba(255,255,255,0.02);color:var(--muted);text-decoration:none}
.ach-normal{padding:12px;border-radius:10px;border:1px solid rgba(255,255,255,0.03); background:var(--card); color:inherit}
.footer{margin-top:28px;padding:16px;border-radius:10px;text-align:center;color:var(--muted);border:1px solid rgba(255,255,255,0.02)}
.contact-card input,.contact-card textarea{background:transparent;border:1px solid rgba(255,255,255,0.06);padding:10px;border-radius:10px;color:inherit;width:100%}
.contact-card textarea{min-height:110px;resize:vertical}
@media(max-width:980px){.layout{grid-template-columns:1fr}.header{flex-direction:column;align-items:flex-start;gap:12px}}
</style>
</head><body>
<div class="bg-ai" aria-hidden="true"></div>
<div class="container">
  <header class="header">
    <div class="brand">
      <div class="logo">DU</div>
      <div>
        <div class="hero-title">Divytosh Upadhyay</div>
        <div class="hero-sub">Data Analyst | Data Scientist | Machine Learning Engineer</div>
      </div>
    </div>
    <div class="cta">
      <a href="#projects"><button class="btn">View Projects ▶</button></a>
      <a id="downloadResumeBtn"><button class="btn ghost">Download Resume ⬇</button></a>
    </div>
  </header>

  <div class="layout">
    <main>
      <section id="about-section">
        <div class="section-card">
          <strong>Tagline</strong>
          <div class="muted" style="margin-top:8px">Transforming complex datasets into actionable business insights using analytics, machine learning, and AI.</div>
        </div>
      </section>

      <section id="about" style="margin-top:14px">
        <h2>About Me</h2>
        <div class="section-card">
          <strong>Data Analyst & Machine Learning Intern</strong>
          <div class="muted" style="margin-top:8px">Strong analytical thinking and structured problem-solving. Experienced in converting raw data into business insights. Focused on data-driven decision-making.</div>
        </div>
      </section>

      <section id="education" style="margin-top:14px">
        <h2>Education</h2>
        <div class="section-card">
          <strong>B.Tech in Artificial Intelligence & Data Science</strong><br>
          Guru Gobind Singh Indraprastha University (GGSIPU), Delhi<br><br>
          <span class="muted">Overall CGPA:</span> 8.4 (till Semester 5) · <span class="muted">Semester 5 SGPA:</span> 9.0 · <span class="muted">Semester 6:</span> Ongoing
        </div>
      </section>

      <section id="skills" style="margin-top:14px">
        <h2>Skills</h2>
        <div class="section-card">
          <strong>Technical</strong>
          <div style="margin-top:8px">{skills_technical_html}</div>
          <hr style="opacity:0.06;margin:12px 0">
          <strong>Tools</strong>
          <div style="margin-top:8px">{skills_tools_html}</div>
        </div>

        <div style="display:flex;gap:12px;margin-top:12px">
          <div style="flex:1" class="section-card">
            <div style="font-weight:800">Programming & Analytics</div>
            <div class="progress" style="margin-top:8px"><i data-width="92"></i></div>
          </div>
          <div style="flex:1" class="section-card">
            <div style="font-weight:800">Machine Learning & NLP</div>
            <div class="progress" style="margin-top:8px"><i data-width="84"></i></div>
          </div>
          <div style="flex:1" class="section-card">
            <div style="font-weight:800">Visualization & BI</div>
            <div class="progress" style="margin-top:8px"><i data-width="88"></i></div>
          </div>
        </div>
      </section>

      <section id="experience" style="margin-top:14px">
        <h2>Experience</h2>
        <div class="section-card" style="margin-top:10px">
          <strong>Machine Learning Intern — Tamizhan Skills (Remote)</strong>
          <ul class="muted" style="margin-top:8px">
            <li>Statistical analysis on 10,000+ records</li>
            <li>NLP models improving business performance by 18%</li>
            <li>Forecasting and performance metrics</li>
          </ul>
        </div>

        <div class="section-card" style="margin-top:10px">
          <strong>Data Analyst Intern — Update Education Technology Pvt. Ltd. (Remote)</strong>
          <ul class="muted" style="margin-top:8px">
            <li>Power BI & Tableau dashboards</li>
            <li>Automated reporting workflows</li>
          </ul>
        </div>

        <div class="section-card" style="margin-top:10px">
          <strong>Data Analyst Intern — Tamizhan Skills (Remote)</strong>
          <ul class="muted" style="margin-top:8px">
            <li>Demand forecasting reducing cost by 10%</li>
            <li>Optimized Tableau dashboards</li>
          </ul>
        </div>
      </section>

      <section id="projects" style="margin-top:14px">
        <h2>Projects</h2>
        {projects_html}
      </section>

      <section id="certifications" style="margin-top:14px">
        <h2>Certifications</h2>
        <div class="section-card">
          <ul class="muted" style="margin:0;padding-left:18px">{certificates_html}</ul>
        </div>
      </section>

      <section id="achievements" style="margin-top:14px">
        <h2>Achievements</h2>
        <div class="section-card" style="margin-bottom:10px">
          <strong>🏆 Runner-up — Hack the Mountain Hackathon</strong>
          <div class="muted" style="margin-top:8px">2000+ participants</div>
        </div>

        <!-- Robotics & Hardware Projects (normal, not highlighted) -->
        <div class="section-card" style="margin-top:10px">
          <strong style="color:var(--accent-cyan)">Robotics & Hardware Projects</strong>
          <ul style="margin:8px 0 0 18px">
            <li>Built a Fire Detection Robot — integrated sensors, control systems and automation.</li>
            <li>Developed a Smart Car  — perception, control and path logic; required coordination, patience, and technical problem-solving.</li>
          </ul>
        </div>

      </section>

      <section id="contact" style="margin-top:14px">
        <h2>Contact</h2>
        <div class="section-card contact-card">
          <div style="font-weight:800">Get in touch</div>
          <div class="muted" style="margin-top:8px">📧 <a class="social-link" href="mailto:{display_email}">{display_email}</a></div>
          <div style="margin-top:8px">
            <a class="social-link" href="https://github.com/Divya-techie-cmd" target="_blank">🐙 GitHub</a>
            <a class="social-link" href="https://www.linkedin.com/in/divytosh-upadhyay-250387290" target="_blank">🔗 LinkedIn</a>
          </div>
        </div>
      </section>

      <section id="feedback" style="margin-top:14px">
        <h2>Response / Feedback</h2>
        <div class="section-card" id="feedbackFormCard">
          <div style="display:flex;flex-direction:column;gap:10px">
            <input type="text" id="fb_name" placeholder="Name" style="padding:10px;border-radius:10px;border:1px solid rgba(255,255,255,0.06);background:transparent;color:inherit">
            <input type="email" id="fb_email" placeholder="Email" style="padding:10px;border-radius:10px;border:1px solid rgba(255,255,255,0.06);background:transparent;color:inherit">
            <textarea id="fb_message" placeholder="Message / Feedback" style="padding:10px;border-radius:10px;border:1px solid rgba(255,255,255,0.06);background:transparent;color:inherit"></textarea>
            <div style="display:flex;gap:10px">
              <button class="btn" id="fb_submit">Submit</button>
              <button class="btn ghost" id="fb_clear">Clear</button>
            </div>
            <div id="fb_status" class="muted" style="margin-top:6px"></div>
          </div>
        </div>

        <div id="feedbackList" style="margin-top:12px">{initial_feedbacks_html}</div>
      </section>

    </main>

    <aside>
      <div class="section-card" style="margin-bottom:12px">
        <div style="font-weight:800">Quick Info</div>
        <div class="muted" style="margin-top:6px">Seeking: Internships & Entry-level Data Science / ML roles</div>
      </div>

      <div class="section-card">
        <div style="font-weight:800">Contact & Links</div>
        <div style="margin-top:8px">
          <a class="social-link" href="mailto:{display_email}">✉ {display_email}</a><br><br>
          <a class="social-link" href="https://www.linkedin.com/in/divytosh-upadhyay-250387290" target="_blank">🔗 LinkedIn</a><br><br>
          <a class="social-link" href="https://github.com/Divya-techie-cmd" target="_blank">🐙 GitHub</a>
        </div>
      </div>

      <div class="footer" style="margin-top:18px">
        © {year} Divytosh Upadhyay · Built with FastAPI · AI-inspired design
      </div>
    </aside>

  </div>
</div>

<script>
const PROJECTS = {projects_json};
const FEEDBACKS = {feedbacks_json};

// Download resume
document.getElementById('downloadResumeBtn').addEventListener('click', function(){
  const content = `{resume_html}`;
  const blob = new Blob([content], {{type: 'text/html'}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'Divytosh_Resume.html';
  document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
});

// Feedback handling
const fbSubmit = document.getElementById('fb_submit');
const fbClear = document.getElementById('fb_clear');
const fbStatus = document.getElementById('fb_status');
const feedbackList = document.getElementById('feedbackList');

fbClear.addEventListener('click', () => {
  document.getElementById('fb_name').value = '';
  document.getElementById('fb_email').value = '';
  document.getElementById('fb_message').value = '';
  fbStatus.textContent = '';
});

fbSubmit.addEventListener('click', async () => {
  fbStatus.textContent = 'Sending...';
  fbSubmit.disabled = true;
  const payload = {
    name: document.getElementById('fb_name').value.trim(),
    email: document.getElementById('fb_email').value.trim(),
    message: document.getElementById('fb_message').value.trim()
  };
  try {
    const res = await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if(res.ok){
      fbStatus.textContent = data.detail || 'Thanks — your feedback was received.';
      fbStatus.style.color = '#aee1c6';
      const node = document.createElement('div');
      node.className = 'section-card';
      node.style.marginTop = '8px';
      node.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center"><div><strong>${payload.name || 'Anonymous'}</strong> <span class="muted" style="margin-left:8px">${payload.email || ''}</span></div><div class="muted" style="font-size:12px">${data.ts}</div></div><div style="margin-top:8px">${payload.message}</div>`;
      feedbackList.insertBefore(node, feedbackList.firstChild);
      document.getElementById('fb_name').value='';
      document.getElementById('fb_email').value='';
      document.getElementById('fb_message').value='';
    } else {
      fbStatus.textContent = data.detail || 'Failed to send feedback';
      fbStatus.style.color = '#ffb4b4';
    }
  } catch(err) {
    fbStatus.textContent = 'Network error. Try again.';
    fbStatus.style.color = '#ffb4b4';
  } finally {
    fbSubmit.disabled = false;
  }
});

// animate progress bars
window.addEventListener('load', () => {
  document.querySelectorAll('.progress i').forEach(el => {
    const w = el.getAttribute('data-width') || 70;
    setTimeout(()=> el.style.width = w + '%', 120);
  });
});

// smooth anchors
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', (e) => {
    const target = document.querySelector(a.getAttribute('href'));
    if(target) {
      e.preventDefault();
      target.scrollIntoView({behavior:'smooth', block:'start'});
    }
  });
});
</script>
</body>
</html>
"""

# ---------- Helpers ----------
def escape_html(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&#39;")
    )

def build_projects_html(projects):
    parts = []
    for p in projects:
        part = (
            "<div class='project-card' style='margin-top:10px'>"
            "<div style='max-width:75%'>"
            f"<div style='font-weight:800'>{escape_html(p['title'])}</div>"
            f"<div class='muted' style='margin-top:6px'>{escape_html(p['summary'])}</div>"
            f"<div style='margin-top:8px'><span class='muted'>Tags:</span> {' · '.join(escape_html(t) for t in p.get('tags',[]))}</div>"
            "</div>"
            "<div style='display:flex;flex-direction:column;gap:8px;align-items:flex-end'>"
            f"<a class='btn gitlight' href='{p.get('github','#')}' target='_blank'>View on GitHub</a>"
            "</div></div>"
        )
        parts.append(part)
    return "\n".join(parts)

def build_skills_html(skill_list):
    return " ".join(f"<span class='skill-chip'>{escape_html(s)}</span>" for s in skill_list)

def build_certificates_html(cert_list):
    return "\n".join(f"<li>{escape_html(c)}</li>" for c in cert_list)

def build_feedbacks_html(feedbacks):
    if not feedbacks:
        return "<div class='muted'>No feedback yet.</div>"
    items = []
    for fb in reversed(feedbacks[-20:]):
        name = escape_html(fb.get("name") or "Anonymous")
        email = escape_html(fb.get("email") or "")
        ts = escape_html(fb.get("_received_at") or fb.get("ts") or "")
        msg = escape_html(fb.get("message") or "").replace("\n", "<br>")
        item = (
            "<div class='section-card' style='margin-top:8px'>"
            f"<div style='display:flex;justify-content:space-between;align-items:center'><div><strong>{name}</strong> <span class='muted' style='margin-left:8px'>{email}</span></div><div class='muted' style='font-size:12px'>{ts}</div></div>"
            f"<div style='margin-top:8px'>{msg}</div>"
            "</div>"
        )
        items.append(item)
    return "\n".join(items)

# Build HTML fragments and JSON for scripts
PROJECTS_HTML = build_projects_html(PROJECTS)
SKILLS_TECH_HTML = build_skills_html(SKILLS_TECHNICAL)
SKILLS_TOOLS_HTML = build_skills_html(SKILLS_TOOLS)
CERTS_HTML = build_certificates_html(CERTIFICATES)
FEEDBACKS_HTML = build_feedbacks_html(FEEDBACKS)
PROJECTS_JSON = json.dumps(PROJECTS).replace("</", "<\\/")
FEEDBACKS_JSON = json.dumps(FEEDBACKS).replace("</", "<\\/")

MAIN_HTML = (MAIN_HTML_TEMPLATE
             .replace("{projects_html}", PROJECTS_HTML)
             .replace("{skills_technical_html}", SKILLS_TECH_HTML)
             .replace("{skills_tools_html}", SKILLS_TOOLS_HTML)
             .replace("{certificates_html}", CERTS_HTML)
             .replace("{initial_feedbacks_html}", FEEDBACKS_HTML)
             .replace("{projects_json}", PROJECTS_JSON)
             .replace("{feedbacks_json}", FEEDBACKS_JSON)
             .replace("{resume_html}", RESUME_HTML.replace("</", "<\\/").replace("`", "\\`"))
             .replace("{display_email}", escape_html(DISPLAY_EMAIL))
             .replace("{year}", str(datetime.datetime.utcnow().year))
             )

# ---------- Routes ----------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return HTMLResponse(content=MAIN_HTML, status_code=200)

@app.get("/resume", response_class=Response)
async def download_resume():
    headers = {
        "Content-Type": "text/html; charset=utf-8",
        "Content-Disposition": 'attachment; filename="Divytosh_Resume.html"'
    }
    return Response(content=RESUME_HTML, headers=headers)

@app.post("/api/feedback")
async def submit_feedback(req: Request):
    try:
        payload = await req.json()
    except Exception:
        return JSONResponse(status_code=400, content={"detail": "Invalid JSON payload"})
    try:
        fb = FeedbackModel(**payload)
    except ValidationError:
        return JSONResponse(status_code=422, content={"detail": "Validation error"})
    entry = {
        "name": fb.name or "Anonymous",
        "email": fb.email or "",
        "message": fb.message,
        "_received_at": datetime.datetime.utcnow().isoformat() + "Z",
        "ts": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    }
    FEEDBACKS.append(entry)
    try:
        save_submission(entry)
    except Exception:
        pass

    # Try to forward via SMTP if configured
    sent = False
    smtp_info = ""
    try:
        subject = f"[Portfolio] New feedback from {entry['name']}"
        body = f"Name: {entry['name']}\nEmail: {entry['email']}\nReceived: {entry['_received_at']}\n\nMessage:\n{entry['message']}"
        sent = send_email_via_smtp(subject=subject, body=body, reply_to=entry['email'] or None)
        smtp_info = " (forwarded via email)" if sent else ""
    except Exception:
        smtp_info = ""

    return JSONResponse(status_code=200, content={"detail": "Thanks — your feedback was received." + smtp_info, "ts": entry["ts"]})

@app.get("/health")
async def health():
    return JSONResponse(content={"status": "ok", "timestamp": datetime.datetime.utcnow().isoformat() + "Z"})

@app.get("/robots.txt")
async def robots():
    return Response(content="User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n", media_type="text/plain")

@app.get("/sitemap.xml")
async def sitemap():
    host = "http://127.0.0.1:8000"
    urls = [f"{host}/"]
    items = "\n".join(f"<url><loc>{u}</loc><changefreq>monthly</changefreq></url>" for u in urls)
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}\n</urlset>'
    return Response(content=xml, media_type="application/xml")

# ---------- Run ----------
if __name__ == "__main__":
    uvicorn.run("portfolio_fastapi_final3:app", host="127.0.0.1", port=8000, reload=False)