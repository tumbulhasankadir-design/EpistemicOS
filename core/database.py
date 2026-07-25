from neo4j import GraphDatabase
import streamlit as st

class EpistemicGraph:
    def __init__(self):
        try:
            uri = st.secrets["NEO4J_URI"]
            user = st.secrets["NEO4J_USERNAME"]
            password = st.secrets["NEO4J_PASSWORD"]
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
        except Exception:
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def clear_database(self):
        if self.driver:
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")

    def add_knowledge_triple(self, src, rel, tgt, final_conf, source_name, date, abstract):
        if not self.driver: return
        query = """
        MERGE (s:Concept {name: $src})
        MERGE (t:Concept {name: $tgt})
        MERGE (s)-[r:RELATION {type: $rel}]->(t)
        SET r.confidence = $conf, r.source = $source_name, r.date = $date, r.abstract = $abstract
        """
        with self.driver.session() as session:
            session.run(query, src=src, tgt=tgt, rel=rel, conf=final_conf, source_name=source_name, date=date, abstract=abstract)

    def get_all_triples(self, limit=300):
        if not self.driver: return []
        query = "MATCH (s)-[r]->(t) RETURN s.name AS source, type(r) AS relation, t.name AS target, r.confidence AS confidence LIMIT $limit"
        with self.driver.session() as session:
            result = session.run(query, limit=limit)
            return [{"source": rec["source"], "relation": rec["relation"], "target": rec["target"], "confidence": rec["confidence"]} for rec in result]

    def get_all_concepts(self):
        if not self.driver: return []
        query = "MATCH (n:Concept) RETURN DISTINCT n.name AS name"
        with self.driver.session() as session:
            result = session.run(query)
            return [rec["name"] for rec in result]

    def get_factors_affecting(self, concept):
        if not self.driver: return []
        query = "MATCH (s)-[r]->(t:Concept {name: $concept}) RETURN s.name AS source, type(r) AS relation, r.confidence AS confidence, r.date AS date"
        with self.driver.session() as session:
            result = session.run(query, concept=concept)
            return [{"source": rec["source"], "relation": rec["relation"], "confidence": rec["confidence"], "date": rec["date"]} for rec in result]

    def get_hypothesis_candidates(self, limit=5):
        if not self.driver: return []
        query = """
        MATCH (a)-[r1]->(b)-[r2]->(c)
        WHERE NOT (a)-->(c) AND a <> c
        RETURN a.name AS start, type(r1) AS rel1, b.name AS middle, type(r2) AS rel2, c.name AS end
        LIMIT $limit
        """
        with self.driver.session() as session:
            result = session.run(query, limit=limit)
            return [{"start": rec["start"], "rel1": rec["rel1"], "middle": rec["middle"], "rel2": rec["rel2"], "end": rec["end"]} for rec in result]
