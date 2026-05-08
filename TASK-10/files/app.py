from flask import Flask, render_template, request, jsonify
import json
import re
from datetime import datetime

app = Flask(__name__)

# University knowledge base
UNIVERSITY_DATA = {
    "programs": {
        "computer science": {
            "name": "Bachelor of Science in Computer Science",
            "duration": "4 years",
            "credits": 120,
            "gpa_requirement": 3.2,
            "sat_requirement": 1250,
            "ielts_requirement": 6.5,
            "tuition": "$18,500/year",
            "description": "Covers algorithms, software engineering, AI, and systems design.",
            "deadline": "January 15, 2026",
            "seats": 120
        },
        "business administration": {
            "name": "Bachelor of Business Administration",
            "duration": "4 years",
            "credits": 120,
            "gpa_requirement": 3.0,
            "sat_requirement": 1150,
            "ielts_requirement": 6.0,
            "tuition": "$16,000/year",
            "description": "Covers management, finance, marketing, and entrepreneurship.",
            "deadline": "February 1, 2026",
            "seats": 150
        },
        "data science": {
            "name": "Bachelor of Science in Data Science",
            "duration": "4 years",
            "credits": 128,
            "gpa_requirement": 3.3,
            "sat_requirement": 1280,
            "ielts_requirement": 6.5,
            "tuition": "$19,000/year",
            "description": "Covers statistics, machine learning, data engineering, and visualization.",
            "deadline": "January 15, 2026",
            "seats": 80
        },
        "mechanical engineering": {
            "name": "Bachelor of Science in Mechanical Engineering",
            "duration": "4 years",
            "credits": 132,
            "gpa_requirement": 3.4,
            "sat_requirement": 1300,
            "ielts_requirement": 6.5,
            "tuition": "$20,000/year",
            "description": "Covers thermodynamics, fluid mechanics, materials science, and robotics.",
            "deadline": "January 15, 2026",
            "seats": 100
        },
        "psychology": {
            "name": "Bachelor of Science in Psychology",
            "duration": "4 years",
            "credits": 120,
            "gpa_requirement": 2.8,
            "sat_requirement": 1100,
            "ielts_requirement": 6.0,
            "tuition": "$14,500/year",
            "description": "Covers cognitive, developmental, clinical, and social psychology.",
            "deadline": "February 15, 2026",
            "seats": 120
        },
        "medicine": {
            "name": "Doctor of Medicine (MD)",
            "duration": "6 years",
            "credits": 220,
            "gpa_requirement": 3.8,
            "sat_requirement": 1500,
            "ielts_requirement": 7.0,
            "tuition": "$35,000/year",
            "description": "Comprehensive medical education including clinical rotations.",
            "deadline": "November 1, 2025",
            "seats": 60
        }
    },
    "general_deadlines": {
        "early_decision": "November 1, 2025",
        "early_action": "November 15, 2025",
        "regular_decision": "January 15, 2026",
        "financial_aid": "February 1, 2026",
        "scholarship": "December 1, 2025",
        "transfer": "March 1, 2026"
    },
    "requirements": {
        "documents": [
            "Completed application form",
            "Official high school transcripts",
            "SAT/ACT scores",
            "Two letters of recommendation",
            "Personal statement (500–650 words)",
            "English proficiency test (IELTS/TOEFL) for international students",
            "Copy of passport (international students)",
            "Application fee: $75"
        ],
        "general_gpa": "Minimum 2.7 GPA on a 4.0 scale",
        "age": "Applicants must be at least 17 years old",
        "high_school": "Must have completed or be completing high school/secondary education"
    },
    "financial_aid": {
        "merit_scholarships": "Available for students with GPA 3.5+, up to $10,000/year",
        "need_based": "Need-based grants available, apply via FAFSA",
        "international_scholarship": "Merit scholarships for international students up to $8,000/year",
        "work_study": "On-campus work-study programs available",
        "loans": "Federal and private loans available for eligible students"
    },
    "contact": {
        "email": "admissions@stateuniversity.edu",
        "phone": "+1 (555) 234-5678",
        "office": "Admissions Building, Room 101",
        "hours": "Monday–Friday, 8:00 AM – 5:00 PM"
    }
}


def find_program(text):
    text_lower = text.lower()
    for key in UNIVERSITY_DATA["programs"]:
        if key in text_lower:
            return key, UNIVERSITY_DATA["programs"][key]
    # Fuzzy matches
    aliases = {
        "cs": "computer science", "compsci": "computer science", "coding": "computer science",
        "bba": "business administration", "business": "business administration", "management": "business administration",
        "ds": "data science", "ml": "data science", "analytics": "data science",
        "mech": "mechanical engineering", "engineering": "mechanical engineering",
        "psych": "psychology", "mental health": "psychology",
        "med": "medicine", "doctor": "medicine", "mbbs": "medicine"
    }
    for alias, program in aliases.items():
        if alias in text_lower:
            return program, UNIVERSITY_DATA["programs"][program]
    return None, None


def generate_response(user_message):
    msg = user_message.lower().strip()

    # Greetings
    if any(w in msg for w in ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "start"]):
        return (
            "👋 Welcome to <strong>State University Admissions!</strong><br><br>"
            "I'm your virtual admissions assistant. I can help you with:<br>"
            "• 📚 <strong>Program information</strong> (CS, Business, Medicine, etc.)<br>"
            "• 📅 <strong>Application deadlines</strong><br>"
            "• 📋 <strong>Admission requirements</strong><br>"
            "• 💰 <strong>Financial aid & scholarships</strong><br>"
            "• 📞 <strong>Contact information</strong><br><br>"
            "What would you like to know?"
        )

    # List all programs
    if any(w in msg for w in ["programs", "courses", "majors", "degrees", "what do you offer", "available programs"]):
        programs_list = "".join(
            f"<li><strong>{p['name']}</strong> — {p['tuition']}, Deadline: {p['deadline']}</li>"
            for p in UNIVERSITY_DATA["programs"].values()
        )
        return f"🎓 <strong>Available Programs at State University:</strong><br><ul>{programs_list}</ul>Ask me about any specific program for more details!"

    # Specific program info
    prog_key, prog = find_program(msg)
    if prog_key:
        if any(w in msg for w in ["requirement", "gpa", "sat", "score", "ielts", "toefl", "qualify", "eligible"]):
            return (
                f"📋 <strong>Requirements for {prog['name']}:</strong><br><br>"
                f"• Minimum GPA: <strong>{prog['gpa_requirement']}</strong><br>"
                f"• SAT Score: <strong>{prog['sat_requirement']}+</strong><br>"
                f"• IELTS (International): <strong>{prog['ielts_requirement']}+</strong><br>"
                f"• Application Deadline: <strong>{prog['deadline']}</strong><br>"
                f"• Available Seats: <strong>{prog['seats']}</strong>"
            )
        elif any(w in msg for w in ["deadline", "when", "date", "apply", "last date"]):
            return (
                f"📅 <strong>Application Deadline for {prog['name']}:</strong><br><br>"
                f"⏰ <strong>{prog['deadline']}</strong><br><br>"
                f"Make sure to also check the financial aid deadline: <strong>{UNIVERSITY_DATA['general_deadlines']['financial_aid']}</strong>"
            )
        elif any(w in msg for w in ["fee", "cost", "tuition", "price", "expensive", "money"]):
            return (
                f"💰 <strong>Tuition for {prog['name']}:</strong><br><br>"
                f"📌 <strong>{prog['tuition']}</strong><br>"
                f"Duration: {prog['duration']} | Credits: {prog['credits']}<br><br>"
                f"Merit scholarships are available for GPA 3.5+. Ask me about financial aid!"
            )
        else:
            return (
                f"🎓 <strong>{prog['name']}</strong><br><br>"
                f"📖 {prog['description']}<br><br>"
                f"• ⏱ Duration: <strong>{prog['duration']}</strong> ({prog['credits']} credits)<br>"
                f"• 💰 Tuition: <strong>{prog['tuition']}</strong><br>"
                f"• 📅 Deadline: <strong>{prog['deadline']}</strong><br>"
                f"• 📊 Min GPA: <strong>{prog['gpa_requirement']}</strong> | SAT: <strong>{prog['sat_requirement']}+</strong><br>"
                f"• 🌍 IELTS (Intl): <strong>{prog['ielts_requirement']}+</strong><br><br>"
                f"Would you like info on requirements, fees, or deadlines?"
            )

    # Deadlines
    if any(w in msg for w in ["deadline", "when", "last date", "due date", "date"]):
        d = UNIVERSITY_DATA["general_deadlines"]
        return (
            f"📅 <strong>Key Application Deadlines 2025–2026:</strong><br><br>"
            f"• 🌟 Early Decision: <strong>{d['early_decision']}</strong><br>"
            f"• ⚡ Early Action: <strong>{d['early_action']}</strong><br>"
            f"• 📋 Regular Decision: <strong>{d['regular_decision']}</strong><br>"
            f"• 💰 Financial Aid: <strong>{d['financial_aid']}</strong><br>"
            f"• 🏆 Scholarships: <strong>{d['scholarship']}</strong><br>"
            f"• 🔄 Transfer Students: <strong>{d['transfer']}</strong><br><br>"
            f"Individual programs may have different deadlines — ask about a specific program!"
        )

    # Requirements
    if any(w in msg for w in ["requirement", "document", "need", "what do i need", "apply", "application"]):
        docs = "".join(f"<li>{doc}</li>" for doc in UNIVERSITY_DATA["requirements"]["documents"])
        return (
            f"📋 <strong>General Admission Requirements:</strong><br><br>"
            f"<ul>{docs}</ul>"
            f"📌 <strong>GPA:</strong> {UNIVERSITY_DATA['requirements']['general_gpa']}<br>"
            f"📌 <strong>Age:</strong> {UNIVERSITY_DATA['requirements']['age']}"
        )

    # Financial aid
    if any(w in msg for w in ["scholarship", "financial aid", "grant", "funding", "fee waiver", "money", "cost", "afford", "loan"]):
        fa = UNIVERSITY_DATA["financial_aid"]
        return (
            f"💰 <strong>Financial Aid & Scholarships:</strong><br><br>"
            f"🏆 <strong>Merit Scholarship:</strong> {fa['merit_scholarships']}<br>"
            f"📝 <strong>Need-Based Aid:</strong> {fa['need_based']}<br>"
            f"🌍 <strong>International Scholarship:</strong> {fa['international_scholarship']}<br>"
            f"💼 <strong>Work-Study:</strong> {fa['work_study']}<br>"
            f"🏦 <strong>Loans:</strong> {fa['loans']}<br><br>"
            f"Scholarship application deadline: <strong>{UNIVERSITY_DATA['general_deadlines']['scholarship']}</strong>"
        )

    # Contact
    if any(w in msg for w in ["contact", "email", "phone", "office", "reach", "talk to", "human", "advisor"]):
        c = UNIVERSITY_DATA["contact"]
        return (
            f"📞 <strong>Contact Admissions Office:</strong><br><br>"
            f"📧 Email: <strong>{c['email']}</strong><br>"
            f"📱 Phone: <strong>{c['phone']}</strong><br>"
            f"🏢 Office: <strong>{c['office']}</strong><br>"
            f"🕐 Hours: <strong>{c['hours']}</strong>"
        )

    # International students
    if any(w in msg for w in ["international", "foreign", "visa", "overseas", "abroad"]):
        return (
            "🌍 <strong>Information for International Students:</strong><br><br>"
            "• IELTS minimum score: <strong>6.0–7.0</strong> (varies by program)<br>"
            "• TOEFL minimum: <strong>80 iBT</strong><br>"
            "• Copy of valid passport required<br>"
            "• Student visa (F-1) support available through our International Office<br>"
            "• Merit scholarships up to <strong>$8,000/year</strong> available<br><br>"
            "📧 Contact: <strong>international@stateuniversity.edu</strong>"
        )

    # Tuition general
    if any(w in msg for w in ["fee", "tuition", "cost", "price", "expensive"]):
        lines = "".join(
            f"<li><strong>{p['name'].split('Bachelor')[-1].strip() or p['name']}</strong>: {p['tuition']}</li>"
            for p in UNIVERSITY_DATA["programs"].values()
        )
        return f"💰 <strong>Tuition Fees by Program:</strong><br><ul>{lines}</ul>Ask about scholarships & financial aid to reduce costs!"

    # Thanks / bye
    if any(w in msg for w in ["thank", "thanks", "bye", "goodbye", "see you", "great"]):
        return "😊 You're welcome! Best of luck with your application. Feel free to return anytime — we're here to help! 🎓"

    # Fallback
    return (
        "🤔 I'm not sure I understood that. Here's what I can help with:<br><br>"
        "• Type a <strong>program name</strong> (e.g., 'Computer Science', 'Medicine')<br>"
        "• Ask about <strong>deadlines</strong>, <strong>requirements</strong>, or <strong>fees</strong><br>"
        "• Ask about <strong>scholarships</strong> or <strong>financial aid</strong><br>"
        "• Ask for <strong>contact information</strong><br><br>"
        "Try: <em>\"Tell me about Computer Science\"</em> or <em>\"What are the deadlines?\"</em>"
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"response": "Please enter a message."})
    response = generate_response(user_message)
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
