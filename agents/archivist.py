import dspy

class ExtractTriples(dspy.Signature):
    """Metinden bilimsel ilişkileri çıkarır."""
    text = dspy.InputField(desc="Bilimsel makale özeti")
    triples = dspy.OutputField(desc="Çıkarılan ilişkiler. Format: Kaynak | İLİŞKİ_TÜRÜ | Hedef | Güven_Skoru(0.0-1.0). Her ilişki yeni bir satırda olmalı. İlişki türleri: UPREGULATES, DOWNREGULATES, ASSOCIATES_WITH, CAUSES, CONTRADICTS")

class ArchivistAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.extractor = dspy.Predict(ExtractTriples)

    def forward(self, text):
        return self.extractor(text=text)
        
    def __call__(self, text):
        return self.forward(text=text)
