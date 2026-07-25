from neo4j import GraphDatabase
import streamlit as st

class EpistemicGraph:
    def __init__(self):
        # Streamlit secrets üzerinden Neo4j şifrelerini güvenle çekiyoruz
        try:
            uri = st.secrets["NEO4J_URI"]
            user = st.secrets["NEO4J_USERNAME"]
            password = st.secrets["NEO4J_PASSWORD"]
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
        except Exception as e:
            print("Neo4j bağlantısı kurulamadı. Simülasyon modunda çalışacak.", e)
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def add_paper(self, paper):
        """Makaleyi Neo4j bilgi ağına düğüm olarak ekler"""
        try:
            if self.driver:
                with self.driver.session() as session:
                    session.run(
                        "MERGE (p:Paper {title: $title}) "
                        "SET p.year = $year, p.abstract = $abstract, p.journal = $journal, p.citations = $citations",
                        title=paper.get("title", "Başlıksız"),
                        year=str(paper.get("year", "Tarihsiz")),
                        abstract=paper.get("abstract", ""),
                        journal=paper.get("journal", "Bilinmeyen Dergi"),
                        citations=paper.get("citations", 0)
                    )
            else:
                print(f"Simülasyon - Makale eklendi: {paper.get('title')}")
        except Exception as e:
            print(f"Neo4j yazma hatası: {e}")
            raise e
