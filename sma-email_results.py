import streamlit as st
from fpdf import FPDF
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import re

# ────────────────────────────────────────────────
# Your data (questions, archetypes, etc.)
# ────────────────────────────────────────────────
questions = [
    "I am a generous person, often giving or loaning money to others.",
    # ... (paste your full 64 questions here from earlier messages)
    "I fear losing control of or power over my money"  # last one
]  # ← Make sure this list has exactly 64 items

scoring_map = {
    "Strongly Disagree": 1,
    "Disagree": 2,
    "Neutral": 3,
    "Agree": 4,
    "Strongly Agree": 5
}

archetype_indices = {
    "Nurturer": [0, 2, 4, 6, 32, 34, 36, 38],
    "Maverick": [1, 3, 5, 7, 33, 35, 37, 39],
    "Alchemist": [8, 10, 12, 14, 40, 42, 44, 46],
    "Celebrity": [9, 11, 13, 15, 41, 43, 45, 47],
    "Connector": [16, 18, 20, 22, 48, 50, 52, 54],
    "Accumulator": [17, 19, 21, 23, 49, 51, 53, 55],
    "Romantic": [24, 26, 28, 30, 56, 58, 60, 62],
    "Ruler": [25, 27, 29, 31, 57, 59, 61, 63]
}

archetype_descriptions = {
    "Nurturer": "Generous, caring giver who finds joy in supporting others financially and emotionally. Can overgive or enable dependency.",
    "Maverick": "Clever risk-taker who enjoys financial games, deals and independence. May take big risks or manipulate situations.",
    "Alchemist": "Visionary who attracts/transforms money in unconventional ways for impact and change. Can undervalue money or be inconsistent.",
    "Celebrity": "Charismatic spotlight lover who spends on image, luxury and visibility. Can overspend to maintain status.",
    "Connector": "Relationship-focused; trusts flow and service over accumulation. May avoid money details or become dependent.",
    "Accumulator": "Disciplined saver who feels secure with frugality and planning. Can limit experiences due to fear of spending.",
    "Romantic": "Pleasure-oriented; lives for the moment and immediate enjoyment. Can be impulsive and neglect long-term saving.",
    "Ruler": "Ambitious empire-builder who sees money as power and success. Can become workaholic or controlling."
}


# ────────────────────────────────────────────────
# PDF Generation
# ────────────────────────────────────────────────
def generate_results_pdf(ranked, max_per_archetype=40):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Sacred Money Archetypes® Results", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 8, "Your ranked archetypes (highest to lowest). Each is scored out of 40 based on 8 questions.")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(30, 10, "Rank", border=1)
    pdf.cell(50, 10, "Archetype", border=1)
    pdf.cell(30, 10, "Score", border=1)
    pdf.cell(30, 10, "%", border=1)
    pdf.cell(0, 10, "Description", border=1)
    pdf.ln()

    pdf.set_font("Helvetica", size=11)
    for rank, (arch, score) in enumerate(ranked, 1):
        perc = (score / max_per_archetype) * 100
        desc = archetype_descriptions[arch]
        pdf.cell(30, 10, str(rank), border=1)
        pdf.cell(50, 10, arch, border=1)
        pdf.cell(30, 10, f"{score}/40", border=1)
        pdf.cell(30, 10, f"{perc:.1f}%", border=1)
        pdf.multi_cell(0, 10, desc, border=1)

    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 6,
                   "Unofficial recreation. Official assessments: sacredmoneyarchetypes.com © Heart of Success, Inc.")

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output


# ────────────────────────────────────────────────
# Email Function
# ────────────────────────────────────────────────
def send_pdf_email(to_email, pdf_bytes):
    # Use Streamlit secrets for production (see below)
    from_email = st.secrets.get("SMTP_EMAIL", "your.email@gmail.com")
    password = st.secrets.get("SMTP_PASSWORD", "your-app-password")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Your Sacred Money Archetypes® Results PDF"

    body = "Attached is your personalized results PDF.\n\nThank you for completing the quiz!"
    msg.attach(MIMEText(body, 'plain'))

    attach = MIMEApplication(pdf_bytes.read(), _subtype="pdf")
    attach.add_header('Content-Disposition', 'attachment', filename="sma_results.pdf")
    msg.attach(attach)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email failed: {str(e)} (check app password / 2FA settings)")
        return False


# ────────────────────────────────────────────────
# Main App
# ────────────────────────────────────────────────
st.title("Sacred Money Archetypes® Questionnaire")
st.markdown("**Scale:** 1 = Strongly Disagree • 2 = Disagree • 3 = Neutral • 4 = Agree • 5 = Strongly Agree")
st.info("Unofficial recreation based on public Sacred Money Archetypes® format.")

with st.form("sma_quiz"):
    answers = [None] * len(questions)

    groups = [
        ("GROUP 1 (Questions 1–8)", 0, 8),
        ("GROUP 2 (Questions 9–16)", 8, 16),
        ("GROUP 3 (Questions 17–24)", 16, 24),
        ("GROUP 4 (Questions 25–32)", 24, 32),
        ("GROUP 5 (Questions 33–40)", 32, 40),
        ("GROUP 6 (Questions 41–48)", 40, 48),
        ("GROUP 7 (Questions 49–56)", 48, 56),
        ("GROUP 8 (Questions 57–64)", 56, 64),
    ]

    for group_name, start, end in groups:
        with st.expander(group_name, expanded=(start == 0)):
            for i in range(start, end):
                q_num = i + 1
                selected = st.radio(
                    f"**Q{q_num}**: {questions[i]}",
                    ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                    index=None,
                    key=f"q_{i}",
                    horizontal=False
                )
                if selected is not None:
                    answers[i] = selected

    submitted = st.form_submit_button("Calculate My Archetypes", type="primary")

if submitted:
    if None in answers:
        st.error(f"Please answer **all 64 questions**. {answers.count(None)} missing.")
    else:
        archetype_scores = {}
        max_per_archetype = 40

        for arch, indices in archetype_indices.items():
            score = sum(scoring_map[answers[idx]] for idx in indices)
            archetype_scores[arch] = score

        ranked = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)

        st.success("**Your Sacred Money Archetypes® Results**")

        table_data = []
        for rank, (arch, score) in enumerate(ranked, 1):
            perc = (score / max_per_archetype) * 100
            table_data.append({
                "Rank": rank,
                "Archetype": arch,
                "Score": f"{score} / 40",
                "%": f"{perc:.1f}%",
                "Description": archetype_descriptions[arch]
            })

        st.dataframe(table_data, use_container_width=True, hide_index=True)

        pdf_buffer = generate_results_pdf(ranked)

        st.download_button(
            label="Download Results PDF",
            data=pdf_buffer,
            file_name="sma_results.pdf",
            mime="application/pdf"
        )

        st.markdown("---")
        email = st.text_input("Enter your email to receive PDF results (optional):")
        if st.button("Send PDF via Email") and email:
            if not re.match(r"^\S+@\S+\.\S+$", email):
                st.warning("Invalid email format.")
            else:
                pdf_buffer.seek(0)
                if send_pdf_email(email, pdf_buffer):
                    st.success(f"PDF sent to {email}!")
                else:
                    st.error("Email send failed – check credentials or Gmail settings.")