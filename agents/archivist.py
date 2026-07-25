import dspy

class EpistemicExtraction(dspy.Signature):
    """
    Metinden bilimsel bilgi üçlüleri çıkarır ve VARLIK NORMALİZASYONU (Layer 6) yapar.
    
    VARLIK NORMALİZASYONU KURALI (ÇOK ÖNEMLİ):
    Kavram_A ve Kavram_B'yi oluştururken kesinlikle metindeki günlük kelimeleri, marka isimlerini veya kısaltmaları (Örn: 'Vit-C', 'heart attack', 'blood sugar', 'COVID') kullanma. 
    Her kavramı, biyoloji ve tıp dünyasındaki en standart ve evrensel İngilizce terminolojiye (MeSH / UniProt normlarına, örn: 'Ascorbic Acid', 'Myocardial Infarction', 'Blood Glucose', 'SARS-CoV-2') dönüştür. 
    Büyük/küçük harf tutarlılığını koru (İlk Harfler Büyük). Bu sayede farklı makaleler aynı kavramı farklı ansa bile grafik parçalanmayacaktır.
    
    Her ilişki için bilginin kesinliğine göre 0.1 ile 1.0 arası bir Güven Skoru belirle.
    """
    
    text = dspy.InputField(desc="Analiz edilecek makale veya not.")
    triples = dspy.OutputField(desc="Çıkarılan ilişkiler. Her biri ayrı satırda: Kavram_A | İLİŞKİ | Kavram_B | Güven_Skoru. Örnek: 'Ascorbic Acid | DOWNREGULATES | Oxidative Stress | 0.95'")

class ArchivistAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.extractor = dspy.Predict(EpistemicExtraction)
        
    def forward(self, text):
        return self.extractor(text=text)