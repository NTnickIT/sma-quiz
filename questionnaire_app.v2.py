import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re

# ────────────────────────────────────────────────
# Questions (your exact 64 questions)
# ────────────────────────────────────────────────
questions = [
    "I am a generous person, often giving or loaning money to others.",
    "I like calculating the pros and cons of taking a financial risk.",
    "I often find myself coming to the aide of others, financially and otherwise.",
    "I am willing to risk money for a potentially large financial gain.",
    "Despite my best efforts, something often happens to complicate my life financially.",
    "I secretly feel clever or even superior to others about money.",
    "I find myself waiting to be paid because of someone else's needs or reasons.",
    "I like gaining the upper hand with money.",
    "I love attracting money in magical or unconventional ways.",
    "I love spending money on things that enhance my image or give me a lot of visibility.",
    "Making money isn't as important to me as creating a movement, making an impact or being involved in social change.",
    "Always getting the best or being first VIP seating, flying first class, getting the latest gadgets is important to me",
    "I feel a love/hate relationship with money",
    "I project an image of wealth and success that often doesn't match my bank account balance",
    "I believe it's greedy or not spiritual to focus too much on money",
    "It's easier for me to spend money on things like jewelry, restaurants, vacations, etc. than it is for me to save money",
    "I find it easy not to think about money",
    "I love saving money",
    "I often find myself being financially supported by others",
    "I find it difficult, even painful to spend money",
    "I often avoid facing money situations, hoping they will improve on their own",
    "I make sure to always live below my means",
    "I like it best when someone else takes care of money details for me",
    "I find it difficult to trust others when investing my money",
    "I love frequently spending money on things because I feel I deserve them",
    "I never feel there's enough money and continue to create ways of making more",
    "I don't see the point in saving money, as life is to be enjoyed now",
    "I am reluctant to diversify or complicate my investments",
    "Money itself doesn't feel that serious to me",
    "I forgo spending money on things now, in order to invest in my future",
    "I love having luxurious experiences or an abundance of items",
    "I am highly ambitious and see money as a measurement of my success",
    "Being of service is more motivating than having more money",
    "At my most extreme the financial risks I take can put me in financial jeopardy",
    "I can feel resentful that I don’t make more for all that I do",
    "I am comfortable with complex financial transactions",
    "If someone needs my time I'll often give it, even if I'm not being paid",
    "Making money is a game I play to win",
    "At my most extreme I give to the point of enabling or creating debt or putting myself at financial risk",
    "Others can view my financial decisions as risky",
    "I believe people with money have unfair advantages in the world",
    "At my most extreme I create debt and spend lavishly in order to get attention and recognition",
    "I am distrustful of people who focus too much on money",
    "I am confident with day to day money management even though I may have debt or find it difficult to save or invest money",
    "Any investing I do needs to be with people or companies whose ideals match my own",
    "I love to stand out in the crowd and will use my purchases to help make that happen",
    "At my most extreme I am financially supported by someone (or something else, like a business, a spouse, a parent or a credit card) yet feel resentment or that the situation is unfair",
    "Being recognized for giving big to charities or social causes is important to me",
    "I wish I didn't have to think about making or managing money",
    "At my most extreme I limit my opportunities because of my fear of spending or investing money",
    "I have faith that somehow, things will always work out financially",
    "I love buying things on sale, closeouts or used items so I know I'm getting the best deal",
    "I don’t feel a strong connection to money",
    "Saving a lot of money makes me feel safe and protected",
    "At my most extreme I feel overwhelmed or even helpless about money and wish the need for money would just disappear",
    "I feel a strong emotional connection to money",
    "I believe in living the good life, no matter what it costs",
    "At my most extreme I am never satisfied with how much money I have and drive myself relentlessly to create more",
    "I figure since you can't take it with you, money is to be spent now",
    "I am typically decisive regarding money and its management",
    "My purchases make me feel better about myself",
    "I believe I'll be happy when I have more money (even though what I have now is more than I've had before",
    "At my most extreme, I spend money impulsively",
    "I fear losing control of or power over my money"
]

# ────────────────────────────────────────────────
# Scoring & Archetype Data
# ────────────────────────────────────────────────
scoring_map = {
    "Strongly Disagree": 1,
    "Disagree": 2,
    "Neutral": 3,
    "Agree": 4,
    "Strongly Agree": 5
}

archetype_indices = {
    "Nurturer":   [0,2,4,6, 32,34,36,38],
    "Maverick":   [1,3,5,7, 33,35,37,39],
    "Alchemist":  [8,10,12,14, 40,42,44,46],
    "Celebrity":  [9,11,13,15, 41,43,45,47],
    "Connector":  [16,18,20,22, 48,50,52,54],
    "Accumulator": [17,19,21,23, 49,51,53,55],
    "Romantic":   [24,26,28,30, 56,58,60,62],
    "Ruler":      [25,27,29,31, 57,59,61,63]
}

archetype_descriptions = {
    "Nurturer": "Generous, caring giver who finds joy in supporting others financially and emotionally.",
    "Maverick": "Clever risk-taker who enjoys financial games, deals and independence.",
    "Alchemist": "Visionary who attracts/transforms money in unconventional ways for impact and change.",
    "Celebrity": "Charismatic spotlight lover who spends on image, luxury and visibility.",
    "Connector": "Relationship-focused; trusts flow and service over accumulation.",
    "Accumulator": "Disciplined saver who feels secure with frugality and planning.",
    "Romantic": "Pleasure-oriented; lives for the moment and immediate enjoyment.",
    "Ruler": "Ambitious empire-builder who sees money as power and success."
}

# ────────────────────────────────────────────────
# Email Results Function
# ────────────────────────────────────────────────
def send_results_email(to_email, ranked):
    from_email = st.secrets.get("SMTP_EMAIL", "your.email@gmail.com")
    password = st.secrets.get("SMTP_PASSWORD", "your-app-password-here")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Your Sacred Money Archetypes® Results"

    body = "Thank you for completing the Sacred Money Archetypes® Questionnaire!\n\n"
    body += "Your ranked results (highest to lowest):\n\n"

    for rank, (arch, score) in enumerate(ranked, 1):
        perc = (score / 40) * 100
        desc = archetype_descriptions[arch]
        body += f"{rank}. {arch}\n"
        body += f"   Score: {score}/40 ({perc:.1f}%)\n"
        body += f"   {desc}\n\n"

    body += "Your top 1–3 archetypes usually represent your primary money personality.\n"
    body += "Lower ones may highlight growth areas or shadows.\n\n"
    body += "This is an unofficial recreation based on the public format.\n"
    body += "For the official assessment and coaching: sacredmoneyarchetypes.com"

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

# ────────────────────────────────────────────────
# Streamlit App
# ────────────────────────────────────────────────
st.title("Sacred Money Archetypes® Questionnaire")
st.markdown("**Scale:** 1 = Strongly Disagree • 2 = Disagree • 3 = Neutral • 4 = Agree • 5 = Strongly Agree")
st.info("This is an unofficial recreation based on the public Sacred Money Archetypes® format.")

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
        for arch, indices in archetype_indices.items():
            score = sum(scoring_map[answers[idx]] for idx in indices)
            archetype_scores[arch] = score

        ranked = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)

        st.success("**Your Sacred Money Archetypes® Results** (Ranked from Highest to Lowest)")

        table_data = []
        for rank, (arch, score) in enumerate(ranked, 1):
            perc = (score / 40) * 100
            table_data.append({
                "Rank": rank,
                "Archetype": arch,
                "Score": f"{score} / 40",
                "%": f"{perc:.1f}%",
                "Description": archetype_descriptions[arch]
            })

        st.dataframe(table_data, use_container_width=True, hide_index=True)
        st.caption("Your top 1–3 archetypes usually represent your primary money personality. Lower ones may highlight growth areas or shadows.")

        # Email section
        st.markdown("---")
        email = st.text_input("Email address to receive results (optional):")
        if st.button("Email Results") and email:
            if not re.match(r"^\S+@\S+\.\S+$", email):
                st.warning("Please enter a valid email address.")
            else:
                if send_results_email(email, ranked):
                    st.success(f"Results emailed to {email}!")
                else:
                    st.error("Failed to send email. Check your app password / Gmail settings.")
