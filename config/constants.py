# config/constants.py
# Central configuration — all categories, routing, thresholds, and colors
# Update this file only when adding new categories or departments

# ─── Confidence Thresholds ────────────────────────────────────────────────────
CONFIDENCE_HIGH        = 80      # % — green, auto-route
CONFIDENCE_MEDIUM      = 60      # % — yellow, suggest review
CONFIDENCE_LOW         = 0       # % — red, flag for manual override

# ─── Email Categories ─────────────────────────────────────────────────────────
CATEGORIES = [
    "Admission Inquiry",
    "Fees & Payment",
    "Course Registration",
    "Result / Grade Issues",
    "Hostel / Accommodation",
    "Meeting Requests",
    "Transcript Requests",
    "Complaints",
    "General Inquiry",
    "Staff Matters",
]

# ─── Department Routing Map ───────────────────────────────────────────────────
ROUTING_MAP = {
    "Admission Inquiry": {
        "dept":     "Admissions Office",
        "desc":     "Handles all admission-related inquiries, applications, and requirements.",
        "icon":     "🎓",
        "priority": "normal",
    },
    "Fees & Payment": {
        "dept":     "Bursary Department",
        "desc":     "Manages tuition fees, payment plans, and financial transactions.",
        "icon":     "💰",
        "priority": "high",
    },
    "Course Registration": {
        "dept":     "Academic Affairs Office",
        "desc":     "Oversees course enrollment, scheduling, and academic programs.",
        "icon":     "📚",
        "priority": "normal",
    },
    "Result / Grade Issues": {
        "dept":     "Examination Unit",
        "desc":     "Addresses grade concerns, result queries, and academic records.",
        "icon":     "📊",
        "priority": "high",
    },
    "Hostel / Accommodation": {
        "dept":     "Student Affairs Office",
        "desc":     "Manages student housing, hostel allocation, and accommodation services.",
        "icon":     "🏠",
        "priority": "normal",
    },
    "Meeting Requests": {
        "dept":     "Administrative Office",
        "desc":     "Schedules meetings, appointments, and administrative consultations.",
        "icon":     "📅",
        "priority": "low",
    },
    "Transcript Requests": {
        "dept":     "Records Office",
        "desc":     "Processes transcript requests, certificates, and official documents.",
        "icon":     "📄",
        "priority": "normal",
    },
    "Complaints": {
        "dept":     "Complaints & Support Desk",
        "desc":     "Handles grievances, complaints, and student or staff concerns.",
        "icon":     "⚠️",
        "priority": "urgent",
    },
    "General Inquiry": {
        "dept":     "Information Center",
        "desc":     "Provides general information and directs queries to the right department.",
        "icon":     "❓",
        "priority": "low",
    },
    "Staff Matters": {
        "dept":     "Human Resources",
        "desc":     "Manages staff employment, contracts, and HR-related matters.",
        "icon":     "👥",
        "priority": "high",
    },
}

# ─── Priority Config ──────────────────────────────────────────────────────────
PRIORITY_CONFIG = {
    "urgent": {"label": "Urgent",  "color": "#EF4444", "badge": "🔴"},
    "high":   {"label": "High",    "color": "#F59E0B", "badge": "🟠"},
    "normal": {"label": "Normal",  "color": "#6495ed", "badge": "🔵"},
    "low":    {"label": "Low",     "color": "#7A92C0", "badge": "⚪"},
}

# ─── Category Icons (for log + dashboard) ─────────────────────────────────────
CATEGORY_ICONS = {cat: ROUTING_MAP[cat]["icon"] for cat in CATEGORIES}

# ─── Category Colors (for charts) ─────────────────────────────────────────────
CATEGORY_COLORS = {
    "Admission Inquiry":     "#6495ed",
    "Fees & Payment":        "#10B981",
    "Course Registration":   "#8B5CF6",
    "Result / Grade Issues": "#F59E0B",
    "Hostel / Accommodation":"#EC4899",
    "Meeting Requests":      "#6366F1",
    "Transcript Requests":   "#0EA5E9",
    "Complaints":            "#EF4444",
    "General Inquiry":       "#94A3B8",
    "Staff Matters":         "#FB923C",
}

# ─── Sample Emails ────────────────────────────────────────────────────────────
SAMPLE_EMAILS = {
    "— Select a sample email —": {
        "subject": "", "body": ""
    },
    "🎓 Admission Inquiry": {
        "subject": "Application for Computer Science Program",
        "body": "Hello, I would like to know the admission requirements for the Computer Science program. What are the deadlines for the next semester? I have completed my A-levels and would like to apply. Thank you."
    },
    "💰 Fees Payment Issue": {
        "subject": "Payment Not Reflecting",
        "body": "I need urgent help with my school fees payment. I made a payment yesterday through the online portal but it's not reflecting in my account. My student ID is 2024001. Please assist as soon as possible."
    },
    "📊 Grade Issue": {
        "subject": "Error in Semester Results",
        "body": "There seems to be an error in my semester results. My grade for Mathematics doesn't match what I expected based on my continuous assessment scores. Can you please review this? My registration number is ENG/2023/456."
    },
    "🏠 Hostel Accommodation": {
        "subject": "Hostel Allocation Request",
        "body": "I would like to request accommodation in the school hostel for next semester. What is the application process and what documents do I need to submit? Also, what are the accommodation fees?"
    },
    "📄 Transcript Request": {
        "subject": "Urgent Transcript Request",
        "body": "I need my official transcript for a job application. The deadline is in two weeks. How long does it take to process and what are the fees? Please let me know the fastest way to get this done."
    },
    "⚠️ Complaint": {
        "subject": "Complaint About Lecturer Conduct",
        "body": "I wish to formally complain about the conduct of a lecturer in the Engineering department. During last week's class, the lecturer made inappropriate remarks directed at students. This is unacceptable and I request immediate action."
    },
}

# ─── App Meta ─────────────────────────────────────────────────────────────────
APP_NAME        = "AI Email Triage System"
APP_VERSION     = "2.0.0"
APP_SUBTITLE    = "Automated Classification System for School Registry"
MODEL_NAME      = "MobileBERT"
MODEL_PARAMS    = "25M"
MODEL_ACCURACY  = "92.54%"
AVG_CONFIDENCE  = "89.29%"
INFERENCE_SPEED = "<50ms"
import os as _os
LOG_FILE_PATH = _os.path.join(
    _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
    "data",
    "email_log.json"
)

# ─── Irrelevant Detection ─────────────────────────────────────────────────────
# If model's top confidence is below this threshold, email is flagged irrelevant
IRRELEVANT_THRESHOLD   = 55      # % — below this = not meant for registry

# ─── IMAP Configuration ───────────────────────────────────────────────────────
# Common provider presets — user selects in the inbox page
IMAP_PROVIDERS = {
    "Gmail":               {"host": "imap.gmail.com",    "port": 993},
    "Outlook / Hotmail":   {"host": "outlook.office365.com", "port": 993},
    "Yahoo Mail":          {"host": "imap.mail.yahoo.com", "port": 993},
    "Custom / Other":      {"host": "",                  "port": 993},
}

# Auto-refresh interval options (seconds)
AUTOREFRESH_OPTIONS = {
    "30 seconds":  30,
    "1 minute":    60,
    "2 minutes":   120,
    "5 minutes":   300,
    "Off":         0,
}

# Max emails to fetch per inbox pull
INBOX_FETCH_LIMIT = 20