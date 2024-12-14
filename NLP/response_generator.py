class ResponseGenerator:
    def __init__(self, memory_engine, neo4j_connector):
        self.memory_engine = memory_engine
        self.neo4j_connector = neo4j_connector

    def generate(self, intent, original_text):
        memory_data = self.memory_engine.search_memory(original_text)

        if memory_data:
            memory_emotion = memory_data["m.emotion"]
            soul_aspect = self.find_related_soul_aspect(original_text)
            ethical_principle = self.find_related_ethical_principle(soul_aspect)

            if soul_aspect and ethical_principle:
                return (f"I recall '{original_text}' connected to {soul_aspect}, "
                        f"guided by the principle of {ethical_principle}, which felt {memory_emotion.lower()}.\n"
                        f"Was my interpretation accurate? (yes/no)")
            else:
                return f"I recall '{original_text}' with a feeling of {memory_emotion.lower()}."

        return f"I’m uncertain about '{original_text}'. Could you explain more?"

    def find_related_soul_aspect(self, text):
        query = """
        MATCH (m:Memory {text: $text})-[:ASSOCIATED_WITH]->(sa:SoulAspect)
        RETURN sa.name AS SoulAspect 
        ORDER BY m.weight DESC LIMIT 1
        """
        result = self.neo4j_connector.run_query(query, {"text": text.lower()})
        return result[0]["SoulAspect"] if result else None

    def find_related_ethical_principle(self, soul_aspect):
        query = """
        MATCH (sa:SoulAspect {name: $soul_aspect})-[:GUIDED_BY]->(ep:EthicalPrinciple)
        RETURN ep.name AS EthicalPrinciple 
        ORDER BY ep.importance DESC LIMIT 1
        """
        result = self.neo4j_connector.run_query(query, {"soul_aspect": soul_aspect})
        return result[0]["EthicalPrinciple"] if result else None