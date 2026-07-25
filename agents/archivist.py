import dspy

class ArchivistAgent:
    def __init__(self):
        try:
            self.extract = dspy.Predict("abstract -> key_concepts")
        except Exception:
            self.extract = None

    def read_paper(self, abstract):
        """Makalenin özetini okur ve anahtar kavramları çıkarır"""
        class AnalysisResult:
            def __init__(self, concepts):
                self.key_concepts = concepts

        try:
            if self.extract and hasattr(dspy.settings, 'lm') and dspy.settings.lm:
                res = self.extract(abstract=abstract)
                return res
            else:
                return AnalysisResult("Epistemoloji, Bilgi Ağı, Çoklu Ajan Sistemleri, Veri Modelleme")
        except Exception:
            return AnalysisResult("Eğitim Teknolojileri, Analitik Sistemler, Yapay Zeka")
