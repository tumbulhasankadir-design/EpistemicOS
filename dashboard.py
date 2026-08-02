import sys
import os
import subprocess
import time
import requests
import streamlit as st
import streamlit.components.v1 as components
import dspy
from pyvis.network import Network

# ----------------------------------------------------------------
# 🚀 OTOMATİK KURULUM MOTORU (Cache eklenerek optimize edildi)
# ----------------------------------------------------------------
@st.cache_resource
def ensure_packages():
    packages = {
        "numpy": "numpy",
        "scipy": "scipy",
        "plotly": "plotly",
        "py3Dmol": "py3Dmol", 
        "stmol": "stmol",
        "pandas": "pandas"
    }
    for module, pip_name in packages.items():
        try:
            __import__(module)
        except ImportError:
            print(f"⚠️ {pip_name} bulunamadı. Yükleniyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name, "requests"])
            print(f"✅ {pip_name} başarıyla yüklendi!")

ensure_packages()

# Kurulumlardan sonra güvenli içe aktarmalar
import numpy as np
import pandas as pd
from scipy.integrate import odeint
import plotly.graph_objects as go
import py3Dmol
from stmol import showmol

# ----------------------------------------------------------------
# 1. ORTAM VE YOL AYARLARI
# ----------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Yerel modüller (Bunların proje klasörünüzde olduğundan emin olun)
from core.database import EpistemicGraph
from agents.archivist import ArchivistAgent
from core.scholar import search_papers

# ----------------------------------------------------------------
# 2. SAYFA YAPISI VE STİL
# ----------------------------------------------------------------
st.set_page_config(page_title="EpistemicOS", page_icon="🧪", layout="wide")

# Modern Premium Tema
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a3f 50%, #150f2e 100%);
    color: #f0f4ff;
}
[data-testid="stHeader"] {
    background: transparent;
    border-bottom: 1px solid rgba(168, 85, 247, 0.15);
}
[data-testid="stSidebar"] {
    background: rgba(15, 15, 35, 0.95);
    border-right: 1px solid rgba(168, 85, 247, 0.2);
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2.5rem;
    max-width: 1500px;
}
.stTabs [role="tablist"] {
    border-bottom: 1px solid rgba(168, 85, 247, 0.15);
}
.stTabs [role="tablist"] button {
    border-radius: 12px;
    padding: 0.5rem 1rem;
    color: #9ca3af;
    border: none;
    margin-right: 0.5rem;
    transition: all 0.3s ease;
}
.stTabs [role="tablist"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
}
.stTabs [role="tablist"] button:hover {
    border-bottom-color: transparent;
    background: rgba(168, 85, 247, 0.2);
}
.hero-card {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.12), rgba(139, 92, 246, 0.08));
    border: 1px solid rgba(168, 85, 247, 0.3);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(168, 85, 247, 0.15);
    margin-bottom: 1.5rem;
}
.hero-card h1 {
    margin: 0 0 0.5rem 0;
    font-size: 2rem;
    background: linear-gradient(135deg, #fbbf24 0%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-card p {
    margin: 0;
    color: #cbd5e1;
    font-size: 1rem;
    line-height: 1.5;
}
.stButton > button {
    border-radius: 12px;
    border: 1px solid rgba(168, 85, 247, 0.4);
    background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%);
    color: white;
    font-weight: 600;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(168, 85, 247, 0.4);
    border-color: rgba(168, 85, 247, 0.8);
}
.stButton > button[kind="secondary"] {
    background: rgba(168, 85, 247, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(168, 85, 247, 0.3);
}
.stTextInput > div > div > input,
.stSelectbox > div > div > select,
.stNumberInput input,
.stTextArea textarea {
    background: rgba(168, 85, 247, 0.08) !important;
    border: 1px solid rgba(168, 85, 247, 0.25) !important;
    border-radius: 12px !important;
    color: #f0f4ff !important;
}
.stTextInput > div > div > input::placeholder,
.stSelectbox > div > div > select::placeholder {
    color: rgba(241, 245, 249, 0.5);
}
[data-testid="stExpander"] {
    background: rgba(168, 85, 247, 0.08);
    border: 1px solid rgba(168, 85, 247, 0.2);
    border-radius: 12px;
}
.stExpander > button {
    color: #f0f4ff;
}
.stSuccess {
    background: rgba(34, 197, 94, 0.15) !important;
    border: 1px solid rgba(34, 197, 94, 0.3) !important;
    border-radius: 12px;
}
.stError {
    background: rgba(239, 68, 68, 0.15) !important;
    border: 1px solid rgba(239, 68, 68, 0.3) !important;
    border-radius: 12px;
}
.stInfo {
    background: rgba(59, 130, 246, 0.15) !important;
    border: 1px solid rgba(59, 130, 246, 0.3) !important;
    border-radius: 12px;
}
.stWarning {
    background: rgba(251, 191, 36, 0.15) !important;
    border: 1px solid rgba(251, 191, 36, 0.3) !important;
    border-radius: 12px;
}
h1, h2, h3, h4, h5, h6 {
    color: #f0f4ff !important;
    letter-spacing: 0.5px;
}
.stSubheader {
    color: #dbeafe !important;
}
</style>
""", unsafe_allow_html=True)

# Sidebar Menüsü
with st.sidebar:
    st.markdown("<h3 style='color: #a855f7; margin-bottom: 1.5rem;'>📚 BİLGİ İŞLEMLERİ</h3>", unsafe_allow_html=True)
    st.markdown("""<div style='font-size: 0.85rem; color: #9ca3af; margin-bottom: 0.5rem;'>Soru Oluştur</div>""", unsafe_allow_html=True)
    st.markdown("""<div style='font-size: 0.85rem; color: #9ca3af; margin-bottom: 0.5rem;'>Sözleşme Oluştur</div>""", unsafe_allow_html=True)
    st.markdown("""<div style='font-size: 0.85rem; color: #9ca3af; margin-bottom: 0.5rem;'>İhtarneme Hazırla</div>""", unsafe_allow_html=True)
    st.markdown("""<div style='font-size: 0.85rem; color: #9ca3af; margin-bottom: 0.5rem;'>CV Oluştur</div>""", unsafe_allow_html=True)
    st.markdown("""<div style='font-size: 0.85rem; color: #9ca3af;'>Kaynak Yönetimi</div>""", unsafe_allow_html=True)
    
    st.divider()
    st.markdown("<h3 style='color: #a855f7; margin: 1.5rem 0;'>🔬 DEVLETİŞLEMLERİ</h3>", unsafe_allow_html=True)
    st.markdown("""<div style='font-size: 0.85rem; color: #9ca3af; margin-bottom: 0.5rem;'>Akademik Asistan</div>""", unsafe_allow_html=True)
    st.markdown("""<div style='font-size: 0.85rem; color: #9ca3af; margin-bottom: 0.5rem;'>Formül ve Hesaplamalar</div>""", unsafe_allow_html=True)
    st.markdown("""<div style='font-size: 0.85rem; color: #9ca3af;'>Veri Görselleştir</div>""", unsafe_allow_html=True)
    
    st.divider()
    st.markdown("<h3 style='color: #a855f7; margin: 1.5rem 0;'>⚙️ SİSTEM</h3>", unsafe_allow_html=True)
    st.markdown("""<div style='font-size: 0.85rem; color: #9ca3af; margin-bottom: 0.5rem;'>Ayarlar</div>""", unsafe_allow_html=True)
    st.markdown("""<div style='font-size: 0.85rem; color: #9ca3af; margin-bottom: 0.5rem;'>Entegrasyonlar</div>""", unsafe_allow_html=True)
    st.markdown("""<div style='font-size: 0.85rem; color: #9ca3af;'>Sistem Durumu</div>""", unsafe_allow_html=True)

# Ana İçerik
st.markdown("""
<div class="hero-card">
    <h1>🧪 EpistemicOS</h1>
    <p>Yapay zeka destekli araştırma platformu — bilimsel bilgiyi organize eder, ilişkileri görselleştirir ve hipotez üretimini otomatikleştirir.</p>
</div>
""", unsafe_allow_html=True)

# Hızlı Eylemler Bölümü
st.markdown("<h2 style='color: #f0f4ff; margin: 2rem 0 1rem;'>⚡ Hızlı Eylemler</h2>", unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown("""
    <div style='background: rgba(139, 92, 246, 0.15); border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 16px; padding: 1.5rem; text-align: center;'>
        <div style='font-size: 2rem; margin-bottom: 0.5rem;'>❓</div>
        <div style='font-size: 0.9rem; color: #dbeafe; font-weight: 600;'>Soru ve Hipotez</div>
        <div style='font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem;'>Araştırma sorusu</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style='background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 16px; padding: 1.5rem; text-align: center;'>
        <div style='font-size: 2rem; margin-bottom: 0.5rem;'>📚</div>
        <div style='font-size: 0.9rem; color: #dbeafe; font-weight: 600;'>Literatür Taraması</div>
        <div style='font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem;'>Akademik kaynaklar</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div style='background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 16px; padding: 1.5rem; text-align: center;'>
        <div style='font-size: 2rem; margin-bottom: 0.5rem;'>📊</div>
        <div style='font-size: 0.9rem; color: #dbeafe; font-weight: 600;'>Veri Analizi</div>
        <div style='font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem;'>Verilerinizi görselleştir</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("""
    <div style='background: rgba(251, 146, 60, 0.15); border: 1px solid rgba(251, 146, 60, 0.3); border-radius: 16px; padding: 1.5rem; text-align: center;'>
        <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🧪</div>
        <div style='font-size: 0.9rem; color: #dbeafe; font-weight: 600;'>Deney Tasarımı</div>
        <div style='font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem;'>Deneyler ve projeler</div>
    </div>
    """, unsafe_allow_html=True)
with col5:
    st.markdown("""
    <div style='background: rgba(168, 85, 247, 0.15); border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 16px; padding: 1.5rem; text-align: center;'>
        <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🧬</div>
        <div style='font-size: 0.9rem; color: #dbeafe; font-weight: 600;'>AI Oluştur</div>
        <div style='font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem;'>Model eğitimi</div>
    </div>
    """, unsafe_allow_html=True)

# İstatistik Kartları
st.markdown("<h2 style='color: #f0f4ff; margin: 2rem 0 1rem;'>📊 Bilimsel Göstergeler</h2>", unsafe_allow_html=True)
stat_col1, stat_col2, stat_col3, stat_col4, stat_col5 = st.columns(5)
with stat_col1:
    st.markdown("""
    <div style='background: rgba(139, 92, 246, 0.12); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 14px; padding: 1.25rem; text-align: center;'>
        <div style='font-size: 2rem; font-weight: 800; color: #fbbf24; margin-bottom: 0.3rem;'>12</div>
        <div style='font-size: 0.85rem; color: #cbd5e1;'>Yapılandırılan Bilgi</div>
        <div style='font-size: 0.7rem; color: #9ca3af; margin-top: 0.3rem;'>Bu ay</div>
    </div>
    """, unsafe_allow_html=True)
with stat_col2:
    st.markdown("""
    <div style='background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 14px; padding: 1.25rem; text-align: center;'>
        <div style='font-size: 2rem; font-weight: 800; color: #60a5fa; margin-bottom: 0.3rem;'>8</div>
        <div style='font-size: 0.85rem; color: #cbd5e1;'>Tamamlanan İşlem</div>
        <div style='font-size: 0.7rem; color: #9ca3af; margin-top: 0.3rem;'>Bu ay</div>
    </div>
    """, unsafe_allow_html=True)
with stat_col3:
    st.markdown("""
    <div style='background: rgba(168, 85, 247, 0.12); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 14px; padding: 1.25rem; text-align: center;'>
        <div style='font-size: 2rem; font-weight: 800; color: #a855f7; margin-bottom: 0.3rem;'>34</div>
        <div style='font-size: 0.85rem; color: #cbd5e1;'>Soru Sorulması</div>
        <div style='font-size: 0.7rem; color: #9ca3af; margin-top: 0.3rem;'>Bu ay</div>
    </div>
    """, unsafe_allow_html=True)
with stat_col4:
    st.markdown("""
    <div style='background: rgba(34, 197, 94, 0.12); border: 1px solid rgba(34, 197, 94, 0.25); border-radius: 14px; padding: 1.25rem; text-align: center;'>
        <div style='font-size: 2rem; font-weight: 800; color: #22c55e; margin-bottom: 0.3rem;'>34</div>
        <div style='font-size: 0.85rem; color: #cbd5e1;'>Analiz Tamamlandı</div>
        <div style='font-size: 0.7rem; color: #9ca3af; margin-top: 0.3rem;'>Bu ay</div>
    </div>
    """, unsafe_allow_html=True)
with stat_col5:
    st.markdown("""
    <div style='background: rgba(236, 72, 153, 0.12); border: 1px solid rgba(236, 72, 153, 0.25); border-radius: 14px; padding: 1.25rem; text-align: center;'>
        <div style='font-size: 2rem; font-weight: 800; color: #ec4899; margin-bottom: 0.3rem;'>%82</div>
        <div style='font-size: 0.85rem; color: #cbd5e1;'>Başarı Oranı</div>
        <div style='font-size: 0.7rem; color: #9ca3af; margin-top: 0.3rem;'>Tüm zamanlar</div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------
# 3. BULUT UYUMLU ŞİFRE ÇEKME VE YAPAY ZEKA BAŞLATMA
# ----------------------------------------------------------------
try:
    groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
except Exception:
    groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("⚠️ GROQ API Anahtarı bulunamadı! Lütfen Streamlit Settings -> Secrets bölümüne ekleyin veya ortam değişkeni olarak ayarlayın.")
    st.stop()

lm = dspy.LM('groq/llama-3.1-8b-instant', api_key=groq_api_key)

@st.cache_resource
def init_system():
    return EpistemicGraph(), ArchivistAgent()

db, archivist = init_system()

# --- YAPAY ZEKA İMZALARI ---
class DockingSignature(dspy.Signature):
    entity_a = dspy.InputField(desc="Birinci biyolojik varlık (Virüs, protein, ilaç vb.)")
    entity_b = dspy.InputField(desc="İkinci biyolojik varlık (Reseptör, enzim, hedef vb.)")
    binding_affinity = dspy.OutputField(desc="Fiziksel uyum ve bağlanma gücü (Anahtar-kilit uyumu var mı?)")
    biological_outcome = dspy.OutputField(desc="Bu iki yapı çarpıştığında/birleştiğinde ortaya çıkacak gelişimsel ve hücresel sonuçlar")

class HypothesisSignature(dspy.Signature):
    indirect_link = dspy.InputField(desc="Bilinen dolaylı yollar")
    hypothesis = dspy.OutputField(desc="Test edilebilir yeni bir araştırma hipotezi")
    rationale = dspy.OutputField(desc="Bu hipotezin bilimsel gerekçesi")

# TAB SAYISI 9
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📝 Literatür", 
    "🕸️ Bilgi Ağı", 
    "⚖️ Çelişki", 
    "🧬 Petri Kabı", 
    "📅 Zaman",
    "💡 Hipotez",
    "🔬 3D Modül",
    "📊 ELN (Deney)",
    "⚔️ Çarpıştırıcı"
])

# --- MODÜL 1: LİTERATÜR TARAMA ---
with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🌐 Katman 1 & 8: Literatür Tarama")
        search_query = st.text_input("Araştırma Konusu", placeholder="Örn: cortisol immune system")
        if st.button("PubMed'de Ara", type="primary"):
            with st.spinner("Tıbbi literatür taranıyor..."):
                st.session_state.found_papers = search_papers(search_query, limit=10)
        
        if "found_papers" in st.session_state and st.session_state.found_papers:
            st.success(f"{len(st.session_state.found_papers)} makale bulundu.")
            for idx, p in enumerate(st.session_state.found_papers):
                cit_count = p.get('citations', 0)
                journal = p.get('journal', 'Bilinmeyen Dergi')
                
                # Yazar listesi boş geldiğinde çökmeyi önleyen güvenli yazar ataması
                authors_list = p.get('authors', [])
                author_name = authors_list[0].get('name', 'Bilinmeyen Yazar') if authors_list else 'Bilinmeyen Yazar'
                
                with st.expander(f"📄 {p.get('title')} ({p.get('year')}) | 📚 Atıf: {cit_count}"):
                    st.markdown(f"**Dergi:** *{journal}*")
                    st.write(p.get('abstract'))
                    
                    if st.button("Analiz Et ve Ağa Ekle", key=f"btn_{idx}"):
                        source_name = f"{author_name} ({journal})"
                        impact_score = min(1.0, 0.5 + (cit_count / 200.0))
                        
                        with st.spinner("Archivist okuyor..."):
                            with dspy.context(lm=lm):
                                result = archivist(text=p.get('abstract'))
                            
                            for line in result.triples.split('\n'):
                                if '|' in line:
                                    parts = [x.strip() for x in line.split('|')]
                                    if len(parts) >= 4:
                                        src, rel, tgt, conf_str = parts[:4]
                                        try: 
                                            llm_conf = float(conf_str)
                                        except ValueError: 
                                            llm_conf = 0.5
                                            
                                        final_conf = (llm_conf * 0.6) + (impact_score * 0.4)
                                        if rel in ["UPREGULATES", "DOWNREGULATES", "ASSOCIATES_WITH", "CAUSES", "CONTRADICTS"]:
                                            db.add_knowledge_triple(src, rel, tgt, final_conf, source_name, str(p.get('year', 'Tarihsiz')), p.get('abstract'))
                            st.success("Grafiğe işlendi!")
    with col2:
        st.subheader("Sistem Yönetimi")
        if st.button("Tüm Veritabanını Sıfırla", type="secondary"):
            db.clear_database()
            st.session_state.found_papers = []
            st.success("Veritabanı sıfırlandı!")

# --- MODÜL 2: BİLGİ AĞI ---
with tab2:
    st.subheader("İnteraktif Epistemik Ağ")
    if st.button("Grafiği Güncelle", type="secondary"):
        triples = db.get_all_triples(limit=300)
        if triples:
            net = Network(height="600px", width="100%", bgcolor="#0E1117", font_color="white", directed=True)
            for t in triples:
                net.add_node(t["source"], label=t["source"], color="#FF4B4B", size=15)
                net.add_node(t["target"], label=t["target"], color="#0068C9", size=15)
                net.add_edge(t["source"], t["target"], title=t['relation'], label=t["relation"], color="#7C7C8C")
            net.repulsion(node_distance=150, spring_length=150)
            net.save_graph("epistemic_graph.html")
            with open("epistemic_graph.html", "r", encoding="utf-8") as f:
                components.html(f.read(), height=650)

# --- MODÜL 3: ÇELİŞKİ YÖNETİMİ ---
with tab3:
    st.subheader("⚖️ Çelişki Yönetimi")
    concepts = db.get_all_concepts()
    if concepts:
        target_concept = st.selectbox("Odak Kavramı Seçin", concepts)
        if st.button("Bilimsel Çelişki Analizi Yap", type="primary"):
            factors = db.get_factors_affecting(target_concept)
            if factors:
                pos_score = sum([d.get('confidence', 0.5) for d in factors if d['relation'] not in ["CONTRADICTS", "DOWNREGULATES"]])
                neg_score = sum([d.get('confidence', 0.5) for d in factors if d['relation'] in ["CONTRADICTS", "DOWNREGULATES"]])
                total = pos_score + neg_score
                ratio = int((pos_score / total) * 100) if total > 0 else 50
                
                st.progress(ratio / 100.0) 
                cA, cB = st.columns(2)
                with cA: st.success(f"🟢 Destek Oranı: %{ratio}")
                with cB: st.error(f"🔴 Çelişki Oranı: %{100 - ratio}")
                
                for d in factors:
                    if d.get('relation') in ["CONTRADICTS", "DOWNREGULATES"]: 
                        st.error(f"**{d['source']}** ➜ ({d['relation']}) ➜ {target_concept}")
                    else: 
                        st.info(f"**{d['source']}** ➜ ({d['relation']}) ➜ {target_concept}")

# --- MODÜL 4: MEKANİSTİK SİMÜLASYON ---
with tab4:
    st.subheader("🧬 İn Silico Petri Kabı")
    concepts = db.get_all_concepts()
    if concepts:
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1: start_node = st.selectbox("Damlatılacak Molekül", concepts)
        with c2: initial_dose = st.number_input("Başlangıç Dozu (mM)", min_value=10, max_value=1000, value=100, step=10)
        with c3: sim_time = st.slider("İzleme Süresi (t)", 10, 200, 100)
        
        if st.button("Dinamik Simülasyonu Başlat 🚀", type="primary"):
            triples = db.get_all_triples(limit=1000)
            if triples:
                nodes = list(set([t['source'] for t in triples] + [t['target'] for t in triples]))
                
                def system_dynamics(y, t, nodes, edges):
                    dydt = np.zeros(len(nodes))
                    for i, node in enumerate(nodes): 
                        dydt[i] = -0.03 * y[i]
                    for edge in edges:
                        src_i, tgt_i = nodes.index(edge['source']), nodes.index(edge['target'])
                        k = edge.get('confidence', 0.5) * 0.2
                        if edge['relation'] in ["UPREGULATES", "CAUSES", "ASSOCIATES_WITH"]: 
                            dydt[tgt_i] += k * y[src_i]
                        elif edge['relation'] in ["DOWNREGULATES", "CONTRADICTS"]: 
                            dydt[tgt_i] -= k * y[src_i] * y[tgt_i] * 0.05
                    return dydt
                
                y0 = np.zeros(len(nodes))
                if start_node in nodes: 
                    y0[nodes.index(start_node)] = initial_dose
                    
                t_steps = np.linspace(0, sim_time, int(sim_time*2))
                with st.spinner("Çözümleniyor..."): 
                    solution = odeint(system_dynamics, y0, t_steps, args=(nodes, triples))
                    
                fig = go.Figure()
                for i, node in enumerate(nodes):
                    if np.max(solution[:, i]) > 1.0: 
                        fig.add_trace(go.Scatter(x=t_steps, y=solution[:, i], mode='lines', name=node, line=dict(width=3)))
                        
                fig.update_layout(title=f"'{start_node}' Enjeksiyonu Kinetiği", xaxis_title="Zaman (t)", yaxis_title="Konsantrasyon", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

# --- MODÜL 5: TARİHSEL EVRİM ---
with tab5:
    st.subheader("📅 Tarihsel Evrim")
    concepts = db.get_all_concepts()
    if concepts:
        target_concept_timeline = st.selectbox("Kavram", concepts, key="timeline_select")
        if st.button("Zaman Çizelgesini Çıkar", type="primary"):
            factors = db.get_factors_affecting(target_concept_timeline)
            if factors:
                sorted_factors = sorted(factors, key=lambda x: int(str(x.get('date', '9999'))) if str(x.get('date', '9999')).isdigit() else 9999)
                for d in sorted_factors: 
                    st.write(f"**{d.get('date', 'Bilinmeyen Yıl')}**: {d['source']} ➜ ({d['relation']}) ➜ {target_concept_timeline}")

# --- MODÜL 6: HİPOTEZ JENERATÖRÜ ---
with tab6:
    st.subheader("💡 Otonom Hipotez Jeneratörü")
    candidates = db.get_hypothesis_candidates(limit=5)
    if candidates:
        for idx, cand in enumerate(candidates):
            with st.expander(f"🔍 Keşif Fırsatı: {cand['start']} ➜ ? ➜ {cand['end']}"):
                indirect_text = f"{cand['start']}, {cand['middle']}'i {cand['rel1']} ile etkiler. {cand['middle']}, {cand['end']}'i {cand['rel2']} ile etkiler."
                st.info(indirect_text)
                if st.button("LLM ile Hipotez Üret", key=f"hyp_{idx}"):
                    with dspy.context(lm=lm):
                        res = dspy.Predict(HypothesisSignature)(indirect_link=indirect_text)
                        st.write("**Hipotez:**", res.hypothesis)
                        st.write("**Gerekçe:**", res.rationale)

# --- MODÜL 7: EKSİKSİZ 3D GÖRSELLEŞTİRME ---
with tab7:
    st.subheader("🔬 Modül 8: 3D Moleküler Görselleştirici")
    mol_type = st.radio("Molekül Türü:", ["Kimyasal", "Protein / Virüs"], horizontal=True)
    concepts = db.get_all_concepts()
    default_search = concepts[0] if concepts else "Cortisol"
    
    col_search, col_view = st.columns([1, 2])
    with col_search:
        search_term = st.text_input("Varlık İsmi veya Kodu:", value=default_search).strip()
        render_btn = st.button("Molekülü Getir ve Render Et", type="primary")
        
        st.divider()
        if "Kimyasal" in mol_type:
            with st.expander("🧪 Genişletilmiş Atom Renk Rehberi", expanded=True):
                st.markdown("""
                * ⚪ **Beyaz:** Hidrojen (H) | 🔘 **Siyah:** Karbon (C) | 🔴 **Kırmızı:** Oksijen (O)
                * 🔵 **Mavi:** Azot (N) | 🟡 **Sarı:** Kükürt (S) | 🟠 **Turuncu:** Fosfor (P)
                * 🟢 **Yeşil:** Klor/Flor | 🟤 **Koyu Kırmızı:** Brom | 🟣 **Mor:** İyot | 🪨 **Gri:** Demir
                """)
        else:
            with st.expander("🧬 Protein ve Virüs Katlanma Rehberi", expanded=True):
                st.markdown("🌈 **Renkli Şeritler:** Proteinin omurgası | 🟡 **Sarı Kesik Çizgiler:** Zayıf Hidrojen Bağları")
                
    with col_view:
        if render_btn and search_term:
            try:
                if "Kimyasal" in mol_type:
                    res = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{search_term}/cids/JSON")
                    if res.status_code == 200:
                        cid = res.json()['IdentifierList']['CID'][0]
                        st.markdown(f"### 🧪 Görüntülenen: **{search_term.upper()}** *(PubChem CID: {cid})*")
                        view = py3Dmol.view(query=f'cid:{cid}')
                        view.setStyle({'stick': {'radius': 0.15}, 'sphere': {'scale': 0.3}})
                        view.setBackgroundColor('#0E1117')
                        view.zoomTo()
                        showmol(view, height=500, width=600)
                else:
                    pdb_code = search_term.upper() if len(search_term) == 4 and search_term.isalnum() else ""
                    if not pdb_code:
                        search_res = requests.post("https://search.rcsb.org/rcsbsearch/v2/query", json={"query": {"type": "terminal", "service": "full_text", "parameters": {"value": search_term}}, "return_type": "entry"})
                        if search_res.status_code == 200 and search_res.json().get('result_set'):
                            pdb_code = search_res.json()['result_set'][0]['identifier']
                    if pdb_code:
                        st.markdown(f"### 🧬 Görüntülenen: **{search_term.upper()}** *(PDB Kodu: {pdb_code})*")
                        view = py3Dmol.view(query=f'pdb:{pdb_code.lower()}')
                        view.setStyle({'cartoon': {'color': 'spectrum'}})
                        view.addStyle({'hbond': {'colorscheme': 'yellow', 'thickness': 0.1}})
                        view.addSurface(py3Dmol.VDW, {'opacity': 0.3, 'color': 'white'})
                        view.setBackgroundColor('#0E1117')
                        view.zoomTo()
                        showmol(view, height=500, width=600)
            except Exception:
                pass

# --- MODÜL 8: ELN ---
with tab8:
    st.subheader("📊 Elektronik Laboratuvar Defteri (ELN)")
    uploaded_file = st.file_uploader("Deneysel Verinizi Yükleyin (.csv)", type=['csv'])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df, use_container_width=True)
            network_concepts = [c.lower() for c in db.get_all_concepts()]
            for index, row in df.iterrows():
                mol = str(row.get('Molekül', '')).strip()
                kontrol, deney = float(row.get('Kontrol_Miktar', 0)), float(row.get('Deney_Miktar', 0))
                lab_result = "ARTTI" if deney > kontrol * 1.1 else "AZALDI" if deney < kontrol * 0.9 else "DEĞİŞMEDİ"
                
                with st.expander(f"{mol} (Kontrol: {kontrol} ➜ Deney: {deney}) - {lab_result}"):
                    if mol.lower() in network_concepts:
                        factors = db.get_factors_affecting(mol)
                        if factors:
                            for f in factors:
                                rel, src = f['relation'], f['source']
                                if (rel in ["UPREGULATES", "CAUSES"] and lab_result == "ARTTI") or (rel in ["DOWNREGULATES", "CONTRADICTS"] and lab_result == "AZALDI"):
                                    st.success(f"✅ Doğrulandı: {src} ➜ {rel}")
                                elif (rel in ["UPREGULATES", "CAUSES"] and lab_result == "AZALDI") or (rel in ["DOWNREGULATES", "CONTRADICTS"] and lab_result == "ARTTI"):
                                    st.error(f"⚠️ ÇELİŞKİ: {src} ➜ {rel} (Ancak deneyiniz aksini söylüyor!)")
        except Exception as e:
            pass

# --- MODÜL 9: YENİ SANAL ÇARPIŞTIRICI (MOLECULAR COLLIDER) ---
with tab9:
    st.subheader("⚔️ İn Silico Biyolojik Çarpıştırıcı (Docking Simülatörü)")
    st.markdown("İki farklı biyolojik varlığı sanal arenada bir araya getirin. Sistem, aynı uzayda yapıları çarpıştırır ve Yapay Zeka bu birleşmenin biyolojik sonucunu tahmin eder.")
    
    colA, colB = st.columns(2)
    with colA:
        entity_a = st.text_input("🧪 Varlık A (Örn: SARS-CoV-2 Spike Proteini)", value="SARS-CoV-2 Spike Protein")
        pdb_a = st.text_input("Varlık A - PDB Kodu (İsteğe bağlı, örn: 6VXX)", value="6VXX")
        
    with colB:
        entity_b = st.text_input("🧬 Varlık B (Örn: İnsan ACE2 Reseptörü)", value="Human ACE2 Receptor")
        pdb_b = st.text_input("Varlık B - PDB Kodu (İsteğe bağlı, örn: 1R42)", value="1R42")
        
    if st.button("💥 Çarpıştır ve Etkileşimi Analiz Et", type="primary"):
        st.markdown("### 🔬 3D Moleküler Çarpışma Arenası")
        try:
            view = py3Dmol.view(width=800, height=500)
            if pdb_a:
                pdb_data_a = requests.get(f"https://files.rcsb.org/view/{pdb_a.upper()}.pdb").text
                if pdb_data_a and "ATOM" in pdb_data_a:
                    view.addModel(pdb_data_a, 'pdb')
                    view.setStyle({'model': 0}, {'cartoon': {'color': 'red'}})
            if pdb_b:
                pdb_data_b = requests.get(f"https://files.rcsb.org/view/{pdb_b.upper()}.pdb").text
                if pdb_data_b and "ATOM" in pdb_data_b:
                    view.addModel(pdb_data_b, 'pdb')
                    view.setStyle({'model': 1}, {'cartoon': {'color': 'blue'}})
            
            view.setBackgroundColor('#0E1117')
            view.zoomTo()
            st.info("🔴 Kırmızı: Varlık A | 🔵 Mavi: Varlık B")
            showmol(view, height=500, width=800)
        except Exception:
            st.warning("3D Modeller tam bindirilemedi ancak LLM analizi devam ediyor...")
            
        st.markdown("### 🤖 Biyolojik Etki ve Kenetlenme Raporu")
        with st.spinner(f"Archivist Yapay Zekası '{entity_a}' ve '{entity_b}' arasındaki moleküler uyumu hesaplıyor..."):
            with dspy.context(lm=lm):
                result = dspy.Predict(DockingSignature)(entity_a=entity_a, entity_b=entity_b)
                
            cA, cB = st.columns(2)
            with cA:
                st.success("🔗 **Fiziksel Uyum (Bağlanma Gücü):**")
                st.write(result.binding_affinity)
            with cB:
                st.error("⚕️ **Biyolojik Sonuç (Mutasyon/Hastalık Etkisi):**")
                st.write(result.biological_outcome)
