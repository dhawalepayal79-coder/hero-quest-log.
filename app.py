import streamlit as st
import sqlite3
import pandas as pd

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('hero_tasks.db')
    c = conn.cursor()
    # Create table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS quests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  task TEXT, 
                  category TEXT, 
                  difficulty TEXT, 
                  xp INTEGER, 
                  is_done BOOLEAN)''')
    conn.commit()
    conn.close()

# --- 2. DATABASE FUNCTIONS ---
def add_quest(task, cat, diff, xp):
    conn = sqlite3.connect('hero_tasks.db')
    c = conn.cursor()
    c.execute("INSERT INTO quests (task, category, difficulty, xp, is_done) VALUES (?, ?, ?, ?, ?)",
              (task, cat, diff, xp, False))
    conn.commit()
    conn.close()

def get_quests(status):
    conn = sqlite3.connect('hero_tasks.db')
    df = pd.read_sql_query(f"SELECT * FROM quests WHERE is_done = {status}", conn)
    conn.close()
    return df

def complete_quest(quest_id):
    conn = sqlite3.connect('hero_tasks.db')
    c = conn.cursor()
    c.execute("UPDATE quests SET is_done = 1 WHERE id = ?", (quest_id,))
    conn.commit()
    conn.close()

def get_total_xp():
    conn = sqlite3.connect('hero_tasks.db')
    c = conn.cursor()
    c.execute("SELECT SUM(xp) FROM quests WHERE is_done = 1")
    result = c.fetchone()[0]
    conn.close()
    return result if result else 0

# --- 3. STREAMLIT INTERFACE ---
def main():
    st.set_page_config(page_title="Heroic Quest Log", page_icon="⚔️")
    init_db()

    # --- HEADER: STATS BAR ---
    st.title("🛡️ Heroic Quest Log")
    st.markdown("---")
    
    total_xp = get_total_xp()
    level = (total_xp // 100) + 1
    xp_towards_next_lvl = total_xp % 100
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Hero Level", f"Lvl {level}")
    col2.metric("Total XP", f"{total_xp} pts")
    col3.metric("Next Level In", f"{100 - xp_towards_next_lvl} XP")
    
    st.write(f"**XP Progress to Level {level + 1}**")
    st.progress(xp_towards_next_lvl / 100)
    st.markdown("---")

    # --- INPUT: ADD NEW QUEST ---
    with st.sidebar:
        st.header("📜 Add New Quest")
        new_task = st.text_input("What is your mission?")
        category = st.selectbox("Category", ["Academic 📚", "Coding 💻", "Health 🍎", "Personal 🏠"])
        difficulty = st.select_slider("Difficulty", options=["Easy", "Medium", "Hard"])
        
        # Difficulty to XP Mapping
        xp_map = {"Easy": 10, "Medium": 30, "Hard": 50}
        
        if st.button("Add to Board"):
            if new_task:
                add_quest(new_task, category, difficulty, xp_map[difficulty])
                st.success("Quest added to the board!")
                st.rerun()
            else:
                st.error("Quest name cannot be empty, Boss!")

    # --- DISPLAY: QUEST BOARD ---
    st.subheader("⚔️ Active Quests")
    active_df = get_quests(0)

    if active_df.empty:
        st.info("No active quests. Add one from the sidebar to start leveling up!")
    else:
        for index, row in active_df.iterrows():
            # Use columns to create a "card" feel
            q_col1, q_col2, q_col3 = st.columns([3, 1, 1])
            q_col1.write(f"**{row['task']}** ({row['category']})")
            q_col2.write(f"💎 {row['xp']} XP")
            
            if q_col3.button("Complete", key=row['id']):
                complete_quest(row['id'])
                st.balloons()
                st.toast(f"Quest Complete! +{row['xp']} XP earned!")
                st.rerun()

    # --- ARCHIVE: COMPLETED QUESTS ---
    with st.expander("📖 Completed Quest Archive"):
        done_df = get_quests(1)
        if not done_df.empty:
            st.table(done_df[['task', 'category', 'difficulty', 'xp']])
        else:
            st.write("Your history is empty. Go finish some quests!")

if __name__ == "__main__":
    main()