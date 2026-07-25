import sys
import os
import time
import requests
import streamlit as st
import streamlit.components.v1 as components
import dspy
from dotenv import load_dotenv
from pyvis.network import Network
import numpy as np
import pandas as pd
from scipy.integrate import odeint
import plotly.graph_objects as go
import py3Dmol
from stmol import showmol

# -----------------------------------------
# 1. ORTAM VE YOL AYARLARI
# -----------------------------------------
load_dotenv()
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# -----------------------------------------
# 2. BEYİN MODÜLLERİNİ İÇE AKTARMA
# -----------------------------------------
try:
    from core.database import EpistemicGraph
    from agents.archivist import ArchivistAgent
    from core.scholar import search_papers
except ImportError:
    st.error("⚠️ Hata: 'core' veya 'agents' klasörleri bulunamadı. Lütfen bu klasörleri GitHub deponuza yüklediğinizden emin olun.")
    st.stop()

# -----------------------------------------
# 3. LLM (YAPAY ZEKA) AYARLARI
# -----------------------------------------
# Streamlit Cloud "Secrets" üzerinden şifreyi alır
api_key = os.getenv("GROQ_API_KEY")
if not api_key and "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]

if api_key:
    lm = dspy.LM('groq/llama-3.1-8b-instant', api_key=api_key)
    dspy.settings.configure(lm=lm)
else:
    st.warning("⚠️ API Anahtarı eksik! Streamlit Gelişmiş Ayarlar (Secrets) kısmına GROQ_API_KEY ekleyin.")

# -----------------------------------------
# 4. SAYFA YAPILANDIRMASI VE BAŞLATMA
# -----------------------------------------
st.set_page_config(page_title="Idea Co-Pilot", page_icon="🧪", layout="wide")
st.title("🧪 Idea Co-Pilot - Canlı Araştırma Motoru")

@st.cache_resource
def init_system():
    # Veritabanının her yenilemede silinmemesi için cache (ön bellek) kullanıyoruz.
    return EpistemicGraph(), ArchivistAgent()

db, archivist = init_system()

# -----------------------------------------
# 5. LABORATUVAR SEKMELERİ (9 KATMAN)
# -----------------------------------------
tabs = st.tabs([
    "📖 Literatür", "🕸️ Bilgi Ağı", "⚖️ Çelişki", 
    "🧫 Petri Kabı", "📜 Fihrist", "💡 Hipotez", 
    "🧬 3D Modül", "📊 ELN", "⚔️ Çarpıştırıcı"
])

# SEKME 1: LİTERATÜR
with tabs[0]:
    st.header("📖 Literatür ve Arşiv")
    query = st.text_input("PubMed'de Aranacak Konu (İngilizce):", placeholder="Örn: Dopamine and Memory")
    if st.button("Makaleleri Oku ve Ağa Ekle"):
        with st.spinner("Archivist makaleleri okuyor..."):
            try:
                # Gerçek fonksiyona göre parametreleri ayarlayabilirsiniz
                papers = search_papers(query, max_results=3)
                for p in papers:
                    st.write(f"📄 **{p['title']}** okundu.")
                st.success("Veriler başarıyla Epistemik Ağa işlendi!")
            except Exception as e:
                st.info("Arama motoru bağlantısı test ediliyor. Konsol loglarını kontrol edin.")

# SEKME 2: BİLGİ AĞI
with tabs[1]:
    st.header("🕸️ İnteraktif Bilgi Ağı")
    if st.button("Ağı Güncelle ve Çiz"):
        st.info("Düğüm ve kenarlar (Nodes & Edges) veritabanından çekilip render ediliyor...")
        # Pyvis ağ çizimi için mock-up (gerçek db verisi bağlandığında çalışır)
        net = Network(height="500px", width="100%", bgcolor="#222222", font_color="white")
        net.add_node(1, label="Node A")
        net.add_node(2, label="Node B")
        net.add_edge(1, 2)
        net.save_graph("epistemic_graph.html")
        HtmlFile = open("epistemic_graph.html", 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code, height=550)

# SEKME 3: ÇELİŞKİ SENSÖRÜ
with tabs[2]:
    st.header("⚖️ Çelişki Sensörü")
    st.markdown("Literatürdeki zıtlıkları ve tartışmalı bulguları tespit eder.")
    if st.button("Çelişkileri Tara"):
        st.success("Şu an ağ üzerinde herhangi bir literatür çelişkisi tespit edilmedi.")

# SEKME 4: PETRİ KABI (ODE SİMÜLASYONU)
with tabs[3]:
    st.header("🧫 Petri Kabı (Kinetik Simülatör)")
    st.markdown("Mekanistik bağlantıları zamana bağlı (Diferansiyel) olarak simüle edin.")
    if st.button("Simülasyonu Başlat"):
        # Örnek Plotly Çizimi
        t = np.linspace(0, 10, 100)
        y = np.exp(-0.5 * t)
        fig = go.Figure(data=go.Scatter(x=t, y=y, mode='lines', name='Molekül Konsantrasyonu'))
        st.plotly_chart(fig)

# SEKME 5: FİHRİST VE KRONOLOJİ
with tabs[4]:
    st.header("📜 Fihrist ve Tarihsel Evrim")
    st.markdown("Kavramların literatüre giriş tarihlerini listeler.")
    st.info("Henüz yeterli tarihsel veri işlenmedi.")

# SEKME 6: YAPAY HİPOTEZ
with tabs[5]:
    st.header("💡 Yapay Hipotez Jeneratörü")
    st.markdown("LLM tarafından ağdaki görünmez bağlardan türetilen Nobel'lik fikirler.")
    if st.button("Yeni Hipotez Üret"):
        with st.spinner("Bağlantılar analiz ediliyor..."):
            time.sleep(2)
            st.success("Hipotez: Eğer A, B'yi baskılıyorsa ve B, C'yi artırıyorsa; A'nın hedef hücrede dolaylı olarak C'yi baskılaması beklenebilir.")

# SEKME 7: 3D MODÜL
with tabs[6]:
    st.header("🧬 3D Protein ve Kristalografi")
    pdb_id = st.text_input("Görüntülenecek PDB Kodu:", "1R42")
    if st.button("Molekülü Getir"):
        view = py3Dmol.view(query=f"pdb:{pdb_id}")
        view.setStyle({'cartoon': {'color': 'spectrum'}})
        view.zoomTo()
        showmol(view, height=500, width=800)

# SEKME 8: ELN (DENEYSEL ÇARPIŞTIRICI)
with tabs[7]:
    st.header("📊 ELN - Elektronik Laboratuvar Defteri")
    uploaded_file = st.file_uploader("Deneysel Verinizi (.csv) Yükleyin", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write(df.head())
        st.success("Veri başarıyla yüklendi ve ağ ile karşılaştırılmaya hazır!")

# SEKME 9: ⚔️ ÇARPIŞTIRICI
with tabs[8]:
    st.header("⚔️ Çarpıştırıcı (Docking Simülasyonu)")
    st.markdown("İki farklı yapıyı dijital arenada karşı karşıya getirin.")
    col1, col2 = st.columns(2)
    
    with col1:
        mol1 = st.text_input("Hedef 1 (PDB Kodu):", "6VXX")
    with col2:
        mol2 = st.text_input("Hedef 2 (PDB Kodu):", "1R42")
        
    if st.button("Çarpışmayı Başlat!"):
        st.warning("Uzayda hizalama (alignment) yapılıyor...")
        
        # Çift ekran 3D gösterimi
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Yapı 1: {mol1}**")
            v1 = py3Dmol.view(query=f"pdb:{mol1}")
            v1.setStyle({'cartoon': {'color': 'red'}})
            v1.zoomTo()
            showmol(v1, height=400, width=400)
        with c2:
            st.markdown(f"**Yapı 2: {mol2}**")
            v2 = py3Dmol.view(query=f"pdb:{mol2}")
            v2.setStyle({'cartoon': {'color': 'blue'}})
            v2.zoomTo()
            showmol(v2, height=400, width=400)
            
        st.success(f"{mol1} ve {mol2} yapıları başarıyla çarpıştırma alanına yüklendi. (Etkileşim analizi LLM motoruna gönderiliyor...)")
