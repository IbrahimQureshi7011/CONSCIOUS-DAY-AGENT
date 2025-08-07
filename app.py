import streamlit as st
import sqlite3
from datetime import datetime
from agent.core import generate_response

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

    selected_date = st.date_input("Select a date")
    selected_str = selected_date.strftime("%Y-%m-%d")

    # Fetch all full datetime entries for the selected date
    cursor.execute("SELECT date FROM entries WHERE date LIKE ? ORDER BY date DESC", (f"{selected_str}%",))
    matches = cursor.fetchall()
    time_options = [row[0] for row in matches]

    if time_options:
        selected_time = st.selectbox("Select a time", time_options)
        cursor.execute("SELECT * FROM entries WHERE date = ?", (selected_time,))
        entry = cursor.fetchone()

        if entry:
            st.subheader("📝 Your Entry")
            st.markdown(f"**Timestamp:** {entry[1]}")
            st.markdown(f"**Journal:** {entry[2]}")
            st.markdown(f"**Intention:** {entry[3]}")
            st.markdown(f"**Dream:** {entry[4]}")
            st.markdown(f"**Priorities:** {entry[5]}")
            st.subheader("📊 AI Insights")
            st.markdown(entry[6])
            st.markdown(entry[7])
        else:
            st.warning("Entry not found.")
    else:
        st.info("No entries for the selected date.")

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
