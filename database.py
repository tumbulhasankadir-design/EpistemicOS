import os
import streamlit as st

# Şifreleri ve linki açıkça yazmak yerine gizli kasadan çağırıyoruz
neo4j_uri = os.getenv("NEO4J_URI")
if not neo4j_uri and "NEO4J_URI" in st.secrets:
    neo4j_uri = st.secrets["NEO4J_URI"]

neo4j_user = os.getenv("NEO4J_USERNAME")
if not neo4j_user and "NEO4J_USERNAME" in st.secrets:
    neo4j_user = st.secrets["NEO4J_USERNAME"]

neo4j_password = os.getenv("NEO4J_PASSWORD")
if not neo4j_password and "NEO4J_PASSWORD" in st.secrets:
    neo4j_password = st.secrets["NEO4J_PASSWORD"]

# Sonrasında kendi bağlantı kodun (Örn: GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))) devam edebilir.

    def setup_constraints(self):
        query = "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE"
        with self.driver.session() as session:
            session.run(query)

    def close(self):
        self.driver.close()

    def add_knowledge_triple(self, source, relation, target, confidence, source_name, date, context):
        query = f"""
        MERGE (s:Concept {{name: $source}})
        MERGE (t:Concept {{name: $target}})
        MERGE (s)-[r:{relation} {{source_name: $source_name}}]->(t)
        ON CREATE SET 
            r.context = $context,
            r.confidence = toFloat($confidence),
            r.date = $date
        """
        with self.driver.session() as session:
            session.run(query, source=source, target=target, confidence=confidence, source_name=source_name, date=date, context=context)

    def get_all_triples(self, limit=300):
        query = """
        MATCH (s:Concept)-[r]->(t:Concept)
        RETURN s.name AS source, type(r) AS relation, t.name AS target, r.confidence AS confidence, r.source_name AS source_name
        LIMIT $limit
        """
        with self.driver.session() as session:
            result = session.run(query, limit=limit)
            return [{"source": rec["source"], "relation": rec["relation"], "target": rec["target"], "confidence": rec["confidence"], "source_name": rec["source_name"]} for rec in result]

    def get_all_concepts(self):
        query = "MATCH (c:Concept) RETURN DISTINCT c.name AS name ORDER BY toLower(c.name)"
        with self.driver.session() as session:
            result = session.run(query)
            return [record["name"] for record in result]

    def get_consensus_data(self, source, target):
        query = "MATCH (s:Concept {name: $source})-[r]->(t:Concept {name: $target}) RETURN type(r) AS relation, r.source_name AS source_name, r.confidence AS confidence, r.date AS date"
        with self.driver.session() as session:
            result = session.run(query, source=source, target=target)
            return [dict(record) for record in result]
            
    def clear_database(self):
        query = "MATCH (n) DETACH DELETE n"
        with self.driver.session() as session:
            session.run(query)

    def get_factors_affecting(self, target):
        query = "MATCH (s:Concept)-[r]->(t:Concept {name: $target}) RETURN s.name AS source, type(r) AS relation, r.source_name AS source_name, r.confidence AS confidence, r.date AS date"
        with self.driver.session() as session:
            result = session.run(query, target=target)
            return [dict(record) for record in result]

    # YENİ KATMAN 12 EKLENTİSİ:
    def get_hypothesis_candidates(self, limit=15):
        """Doğrudan bağı olmayan ama ortak bir düğüm üzerinden dolaylı bağlanan keşif fırsatlarını bulur."""
        query = """
        MATCH (a:Concept)-[r1]->(b:Concept)-[r2]->(c:Concept)
        WHERE NOT (a)-[]->(c) AND NOT (c)-[]->(a) AND a.name <> c.name
        RETURN a.name AS start, type(r1) AS rel1, b.name AS middle, type(r2) AS rel2, c.name AS end
        LIMIT $limit
        """
        with self.driver.session() as session:
            result = session.run(query, limit=limit)
            return [dict(record) for record in result]
