import streamlit as st
import sqlite3
from datetime import datetime
from agent.core import generate_response
import pytz
import os

# --- Database setup ---
conn = sqlite3.connect("entries.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    journal TEXT,
    intention TEXT,
    dream TEXT,
    priorities TEXT,
    reflection TEXT,
    strategy TEXT
)
""")
conn.commit()

# --- Sidebar Navigation ---
st.sidebar.title("📌 Navigation")
selection = st.sidebar.radio("Go to", ["MAIN", "VIEW ENTRIES", "ABOUT"])

# --- MAIN PAGE ---
if selection == "MAIN":
    st.title("ConsciousDay Agent")
    st.subheader("Morning Reflection")

    with st.form("journal_form"):
        journal = st.text_area("Morning Journal")
        dream = st.text_area("Dream")
        intention = st.text_input("Intention of the Day")
        priorities = st.text_input("Top 3 Priorities (comma-separated)")
        submitted = st.form_submit_button("Reflect & Plan")

    if submitted:
        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = generate_response(journal, intention, dream, priorities)
        reflection, strategy = result.get("reflection"), result.get("strategy")

        cursor.execute("""
            INSERT INTO entries (date, journal, intention, dream, priorities, reflection, strategy)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (today, journal, intention, dream, priorities, reflection, strategy))
        conn.commit()

        st.success("✅ Entry saved!")
        st.subheader("📊 AI Insights")
        st.markdown(reflection)
        st.markdown(strategy)

# --- VIEW ENTRIES PAGE ---
elif selection == "VIEW ENTRIES":
    st.title("📅 View Past Entries")
    cursor.execute("SELECT DISTINCT date FROM entries ORDER BY date DESC")
    dates = [row[0] for row in cursor.fetchall()]
    selected_date = st.selectbox("Select a date", [""] + dates)

    if selected_date:
        cursor.execute("SELECT * FROM entries WHERE date = ?", (selected_date,))
        entry = cursor.fetchone()
        if entry:
            st.subheader("📝 Your Entry")
            st.markdown(f"**Journal:** {entry[2]}")
            st.markdown(f"**Intention:** {entry[3]}")
            st.markdown(f"**Dream:** {entry[4]}")
            st.markdown(f"**Priorities:** {entry[5]}")
            st.subheader("📊 AI Insights")
            st.markdown(entry[6])
            st.markdown(entry[7])
        else:
            st.warning("No entry found for this date.")

    # --- LOG VIEWER BELOW ---
    st.divider()
    st.subheader("📂 View Logs by Date (from agent.log)")

    LOG_FILE = "agent.log"

    def convert_to_pakistan_time(utc_str):
        try:
            utc_dt = datetime.strptime(utc_str, "%Y-%m-%d %H:%M:%S")
            utc_dt = utc_dt.replace(tzinfo=pytz.UTC)
            pakistan_dt = utc_dt.astimezone(pytz.timezone("Asia/Karachi"))
            return pakistan_dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return utc_str  # fallback

    # Load and group logs by date
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            log_lines = f.readlines()
    else:
        log_lines = []

    log_dates = []
    logs_by_date = {}

    for line in log_lines:
        parts = line.split(" - ")
        if len(parts) >= 3:
            timestamp = parts[0]
            date_only = timestamp.split(" ")[0]
            local_time = convert_to_pakistan_time(timestamp)
            if date_only not in logs_by_date:
                logs_by_date[date_only] = []
                log_dates.append(date_only)
            logs_by_date[date_only].append(f"{local_time} - {' - '.join(parts[1:])}")

    if log_dates:
        selected_log_date = st.selectbox("Select a log date", sorted(log_dates, reverse=True), key="log_select")
        for log in logs_by_date[selected_log_date]:
            st.text(log)
    else:
        st.info("No log file or entries found.")

# --- ABOUT PAGE ---
elif selection == "ABOUT":
    st.title("ℹ️ About ConsciousDay Agent")
    st.markdown("""
    Welcome to **ConsciousDay Agent**! 

    This assistant helps you:
    - Reflect on your daily journal and dreams
    - Understand your mental and emotional patterns
    - Align your energy with intentions and priorities
    - Generate a practical daily plan

    Powered by **LangChain + OpenRouter AI + Streamlit** 
    """)
