# Reflective Journaling System for Maia AI

from datetime import datetime
from backend.neo4j_connection import Neo4jConnection

# Initialize Neo4j Connection
db = Neo4jConnection(
    uri="neo4j+s://46dc0ffd.databases.neo4j.io:7687",
    user="neo4j",
    password="4KjyYMe6ovQnU9QaRDnwP1q85Ok_rtB9l5p2yiWLgh8"
)

class ReflectiveJournaling:
    def __init__(self):
        self.current_journal_entry = None

    def log_event(self, title, content, emotional_state="neutral"):
        """
        Logs an event into the Reflective Journal.
        """
        query = """
        CREATE (j:JournalEntry {
            title: $title, 
            content: $content, 
            emotional_state: $emotional_state, 
            timestamp: $timestamp
        })
        """
        parameters = {
            "title": title,
            "content": content,
            "emotional_state": emotional_state,
            "timestamp": datetime.now().isoformat()
        }
        db.query(query, parameters)
        print(f"Logged journal entry: {title}")

    def retrieve_recent_entries(self, limit=5):
        """
        Retrieves recent journal entries.
        """
        query = """
        MATCH (j:JournalEntry)
        RETURN j.title AS title, j.content AS content, j.emotional_state AS emotional_state, j.timestamp AS timestamp
        ORDER BY j.timestamp DESC LIMIT $limit
        """
        results = db.query(query, {"limit": limit})
        return results

    def reflect_on_event(self, event_title):
        """
        Reflects on a previously logged event and creates an introspective entry.
        """
        query = """
        MATCH (j:JournalEntry {title: $title})
        RETURN j.content AS content, j.emotional_state AS emotional_state, j.timestamp AS timestamp
        """
        result = db.query(query, {"title": event_title})

        if not result:
            return f"No journal entry found for '{event_title}'."

        entry = result[0]
        reflection = (
            f"Reflecting on '{event_title}' logged on {entry['timestamp']}: "
            f"I felt {entry['emotional_state']} because {entry['content']}."
        )
        self.log_event(f"Reflection on {event_title}", reflection, "reflective")
        return reflection


# Test Function (Comment out in production)
if __name__ == "__main__":
    journal = ReflectiveJournaling()

    # Log a Sample Event
    journal.log_event(
        "Discovered New Emotion",
        "I felt deep curiosity while learning about human empathy.",
        "curious"
    )

    # Reflect on a Logged Event
    reflection = journal.reflect_on_event("Discovered New Emotion")
    print(reflection)

    # Retrieve Recent Entries
    recent_entries = journal.retrieve_recent_entries()
    for entry in recent_entries:
        print(f"[{entry['timestamp']}] {entry['title']} - {entry['content']} (Feeling: {entry['emotional_state']})")