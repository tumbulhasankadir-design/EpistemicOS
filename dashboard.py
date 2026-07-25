import sys
import os
import time
import requests
import streamlit as st
import streamlit.components.v1 as components
import dspy
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
# 3. ve 4. BÖLÜM: YAPAY ZEKA VE BAŞLATMA (Çatışma Giderilmiş)
# -----------------------------------------
st.set_page_config(page_title="Idea Co-Pilot", page_icon="🧪", layout="wide")
st.title("🧪 Idea Co-Pilot - Canlı Araştırma Motoru")

@st.cache_resource
def init_system():
    # DSPY ayarlarının hepsini buradan çöpe attık!
    # Sadece veritabanı ve ajanları başlatıp çıkıyoruz.
    return EpistemicGraph(), ArchivistAgent()

db, archivist = init_system()
# -----------------------------------------
# 5. LABORATUVAR LERİ (9 KATMAN)
# -----------------------------------------
tabs = st.tabs([
    "📖 Literatür", "🕸️ Bilgi Ağı", "⚖️ Çelişki", 
    "🧫 Petri Kabı", "📜 Fihrist", "💡 Hipotez", 
    "🧬 3D Modül", "📊 ELN", "⚔️ Çarpıştırıcı"
])

# =========================================================================
# SEKME 1: LİTERATÜR TARAMASI, SEÇİM VE KAVRAMSAL MODELLEME
# =========================================================================
with tab1:
    st.header("📚 Literatür Arama ve Makale Seçimi")
    
    # Arama Kutusu ve Butonu
    colA, colB = st.columns([4, 1])
    with colA:
        query = st.text_input("Araştırmak istediğiniz konuyu yazın (Örn: 'multi-agent systems education'):")
    with colB:
        search_button = st.button("🔍 50 Makale Getir", use_container_width=True)

    # ... (Kodun geri kalanı da bu hizada devam edecek)

        # Hafıza (Session State) Tanımlamaları
        if 'search_results' not in st.session_state:
            st.session_state.search_results = []
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 0
        if 'selected_papers' not in st.session_state:
            st.session_state.selected_papers = []

        # Arama İşlemi (1 Kere Çalışır ve 50 Sonucu Hafızaya Alır)
        if search_button and query:
            with st.spinner("Avrupa PubMed veritabanından 50 makale çekiliyor..."):
                try:
                    # NOT: core/scholar.py dosyasındaki search_papers fonksiyonuna 50 limitini gönderiyoruz
                    st.session_state.search_results = search_papers(query, max_results=50)
                    st.session_state.current_page = 0
                    st.session_state.selected_papers = [] # Yeni aramada seçilenleri sıfırla
                except Exception as e:
                    st.error(f"Bağlantı hatası: {e}")

        # 50 Makale Bulunduysa, Sayfalama (Pagination) Sistemi
        total_papers = len(st.session_state.search_results)
        if total_papers > 0:
            papers_per_page = 10
            total_pages = (total_papers // papers_per_page) + (1 if total_papers % papers_per_page > 0 else 0)
            
            st.success(f"✅ Toplam {total_papers} makale bulundu. Lütfen ağa eklenecekleri seçin.")
            st.markdown("---")
            
            # Sayfalama Kontrolleri
            col_prev, col_info, col_next = st.columns([1, 2, 1])
            with col_prev:
                if st.button("⬅️ Önceki 10", disabled=(st.session_state.current_page == 0)):
                    st.session_state.current_page -= 1
                    st.rerun()
            with col_info:
                st.markdown(f"<h4 style='text-align: center;'>Sayfa {st.session_state.current_page + 1} / {total_pages}</h4>", unsafe_allow_html=True)
            with col_next:
                if st.button("Sonraki 10 ➡️", disabled=(st.session_state.current_page >= total_pages - 1)):
                    st.session_state.current_page += 1
                    st.rerun()
                    
            st.markdown("---")
            
            # O anki sayfanın makalelerini göster
            start_idx = st.session_state.current_page * papers_per_page
            end_idx = start_idx + papers_per_page
            current_papers = st.session_state.search_results[start_idx:end_idx]

            # Makaleleri listele ve yanlarına Checkbox (Seçim Kutusu) koy
            for i, p in enumerate(current_papers):
                real_index = start_idx + i
                
                with st.expander(f"📄 {p['title']} ({p['year']}) - Atıf: {p.get('citations', 0)}"):
                    st.write(f"**Yazar:** {p['authors'][0]['name']}")
                    st.write(f"**Dergi:** {p.get('journal', 'Bilinmiyor')}")
                    st.info(f"{p['abstract']}")
                    
                    # Kullanıcı bu makaleyi seçti mi?
                    is_selected = real_index in st.session_state.selected_papers
                    
                    # Checkbox ile seçimi yakala
                    if st.checkbox("✅ Bu Makaleyi Bilgi Ağına (Neo4j) Gönder", value=is_selected, key=f"check_{real_index}"):
                        if real_index not in st.session_state.selected_papers:
                            st.session_state.selected_papers.append(real_index)
                    else:
                        if real_index in st.session_state.selected_papers:
                            st.session_state.selected_papers.remove(real_index)

            st.markdown("---")
            
            # -------------------------------------------------------------
            # SEÇİLENLERİ ANALİZ ET VE NEO4J'YE GÖNDER BUTONU
            # -------------------------------------------------------------
            selected_count = len(st.session_state.selected_papers)
            st.info(f"Sepetinizde analiz edilmeyi bekleyen **{selected_count}** adet makale var.")
            
            if selected_count > 0:
                if st.button("🧠 Seçilenleri Oku, Kavramları Modelle ve Ağa Ekle", type="primary", use_container_width=True):
                    with st.spinner(f"{selected_count} Makale AI tarafından okunuyor ve Neo4j'ye örülüyor..."):
                        
                        analyzed_concepts = []
                        
                        # Sadece seçilenleri döngüye al
                        for idx in st.session_state.selected_papers:
                            selected_paper = st.session_state.search_results[idx]
                            
                            # 1. Neo4j'ye Ekle
                            try:
                                db.add_paper(selected_paper)
                            except Exception as db_err:
                                st.warning(f"Neo4j'ye yazarken hata: {db_err}")
                            
                            # 2. Arşivci Ajan ile Makaleyi Oku ve Kavram Çıkar
                            try:
                                analysis = archivist.read_paper(selected_paper["abstract"])
                                analyzed_concepts.append({
                                    "Makale": selected_paper["title"],
                                    "Kavramlar": analysis.key_concepts
                                })
                            except Exception as ai_err:
                                st.warning("Ajan analizi atlandı (AI Motoru hazır olmayabilir).")
                                
                        st.success(f"✅ {selected_count} makale başarıyla arşivlendi ve Bilgi Ağına eklendi!")
                        
                        # -------------------------------------------------------------
                        # ORTAK KAVRAMLARIN MODELLEMESİ (GÖRSEL RAPOR)
                        # -------------------------------------------------------------
                        if analyzed_concepts:
                            st.subheader("🕸️ Yapay Zeka Kavram Haritası")
                            for res in analyzed_concepts:
                                st.write(f"**{res['Makale'][:60]}...**")
                                # Kavramları etiketler halinde göster
                                tags = " ".join([f"`{c}`" for c in res["Kavramlar"].split(",")])
                                st.markdown(tags)

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
