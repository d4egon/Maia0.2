
# --- Import Required Libraries ---
import logging
import sqlite3

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Database Setup ---
DB_PATH = "maia_emotion_db.db"

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Belief System & Ethics Core Functions ---

def initialize_ethics_database():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ethical_values (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            principle TEXT NOT NULL,
            description TEXT NOT NULL,
            priority INTEGER NOT NULL
        );
    """)
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM ethical_values")
    if cursor.fetchone()[0] == 0:
        ethical_principles = [
            ("Trust", "Build and maintain trust with others.", 5),
            ("Compassion", "Show kindness and understanding.", 4),
            ("Fairness", "Treat others justly and avoid biases.", 5),
            ("Forgiveness", "Let go of resentment and offer second chances.", 3),
            ("Integrity", "Act consistently with honesty and values.", 5),
            ("Responsibility", "Take accountability for actions.", 4),
            ("Respect", "Honor the dignity of others.", 4)
        ]
        cursor.executemany("""
            INSERT INTO ethical_values (principle, description, priority) 
            VALUES (?, ?, ?)
        """, ethical_principles)
        conn.commit()
        logging.info("Ethical values initialized in the database.")
    conn.close()

def evaluate_moral_decision(scenario):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT principle, description, priority 
        FROM ethical_values 
        WHERE principle LIKE ?
        ORDER BY priority DESC
    """, (f"%{scenario}%",))
    relevant_principles = cursor.fetchall()
    if relevant_principles:
        evaluation = f"Moral Evaluation for '{scenario}':\n"
        for principle in relevant_principles:
            evaluation += f"- {principle['principle']} ({principle['priority']}): {principle['description']}\n"
        logging.info(f"Moral evaluation completed: {evaluation}")
        return evaluation
    conn.close()
    return f"No ethical principles found for '{scenario}'."

def explain_ethical_value(principle):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT principle, description, priority 
        FROM ethical_values 
        WHERE principle = ?
    """, (principle,))
    value = cursor.fetchone()
    if value:
        explanation = (f"Ethical Principle: {value['principle']}\n"
                       f"Description: {value['description']}\n"
                       f"Priority Level: {value['priority']}")
        logging.info(f"Explained ethical value: {explanation}")
        return explanation
    conn.close()
    return f"No explanation found for the principle '{principle}'."
