# web_server/file_pipeline.py

from file_parser import file_parser
from NLP.response_generator import ResponseGenerator
from core.memory_engine import MemoryEngine
from core.neo4j_connector import Neo4jConnector

class FilePipeline:
    def __init__(self, neo4j_connector: Neo4jConnector, memory_engine: MemoryEngine, response_generator: ResponseGenerator):
        self.neo4j = neo4j_connector
        self.memory_engine = memory_engine
        self.response_generator = response_generator

    def process_file(self, filepath):
        parsed_data = file_parser.parse_file(filepath)
        if "error" in parsed_data:
            return {"status": "error", "message": parsed_data["error"]}

        file_type = parsed_data.get("type", "unknown")
        content = parsed_data.get("content", "")

        # Store the file content in Neo4j
        memory_node_id = self.store_memory(filepath, file_type, content)

        # Context & Emotional Analysis
        emotion, context_summary = self.analyze_content(content)
        self.memory_engine.update_emotion(memory_node_id, emotion)

        # Infer Actions
        actions = self.infer_knowledge(content)
        
        # Trigger Decision-Making
        if actions:
            self.trigger_decision(actions)

        return {
            "status": "success",
            "type": file_type,
            "content_snippet": content[:500],
            "emotions_detected": emotion,
            "inferred_actions": actions,
        }

    def store_memory(self, filename, file_type, content):
        """
        Save file-related memory in Neo4j
        """
        memory_data = {
            "filename": filename,
            "type": file_type,
            "content_snippet": content[:500],
            "full_content": content
        }
        return self.memory_engine.store_memory(content, "neutral", additional_data=memory_data)

    def analyze_content(self, content):
        """
        Perform contextual and emotional analysis on the parsed content
        """
        emotion = self.response_generator.analyze_emotion(content)
        context_summary = self.response_generator.summarize_content(content)
        return emotion, context_summary

    def infer_knowledge(self, content):
        """
        Infer knowledge by searching known contexts in Neo4j.
        """
        query = """
        CALL db.index.fulltext.queryNodes('MemoryIndex', $content) 
        YIELD node, score 
        RETURN node.text AS memory, score ORDER BY score DESC LIMIT 5
        """
        results = self.neo4j.run_query(query, {"content": content})
        return [record['memory'] for record in results]

    def trigger_decision(self, actions):
        """
        Trigger decision-making processes based on inferred knowledge.
        """
        for action in actions:
            print(f"[Action Triggered] Based on memory: {action}")