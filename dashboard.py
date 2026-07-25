import sys
import os
import subprocess
import time
import requests
import streamlit as st
import streamlit.components.v1 as components
import dspy
from pyvis.network import Network

# 🚀 OTOMATİK KURULUM MOTORU
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

import numpy as np
import pandas as pd
from scipy.integrate import odeint
import plotly.graph_objects as go
import py3Dmol
from stmol import showmol

# -------------------------------------------------------------
# 1. ORTAM VE YOL AYARLARI
# -------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.database import EpistemicGraph
from agents.archivist import ArchivistAgent
from core.scholar import search_papers

# -------------------------------------------------------------
# 2. BULUT UYUMLU ŞİFRE ÇEKME VE YAPAY ZEKA BAŞLATMA
# -------------------------------------------------------------
st.set_page_config(page_title="EpistemicOS", page_icon="🧪", layout="wide")
st.title("🧪 EpistemicOS - Canlı Araştırma Motoru")

# Şifreyi bulut kasasından alıyoruz (.env iptal edildi)
try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except (KeyError, FileNotFoundError):
    groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("⚠️ GROQ API Anahtarı bulunamadı! Lütfen Streamlit Settings -> Secrets bölümüne ekleyin.")
    st.stop()

# DSPy Motorunu sessizce kuruyoruz (Thread hatası verdirtmeden)
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

# SEKME SAYISI 9
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
                st.session_state.found_papers = search_papers(search_query, max_results=20)
        
        if "found_papers" in st.session_state and st.session_state.found_papers:
            st.success(f"{len(st.session_state.found_papers)} makale bulundu.")
            for idx, p in enumerate(st.session_state.found_papers):
                cit_count = p.get('citations', 0)
                journal = p.get('journal', 'Bilinmeyen Dergi')
                with st.expander(f"📄 {p.get('title')} ({p.get('year')}) | 📚 Atıf: {cit_count}"):
                    st.markdown(f"**Dergi:** *{journal}*")
                    st.write(p.get('abstract'))
                    if st.button("Analiz Et ve Ağa Ekle", key=f"btn_{idx}"):
                        source_name = f"{p.get('authors')[0]['name'] if p.get('authors') else 'Bilinmeyen'} ({journal})"
                        impact_score = min(1.0, 0.5 + (cit_count / 200.0))
                        with st.spinner("Archivist okuyor..."):
                            # İŞTE BURASI: Kendi yazdığın hatasız Yapay Zeka çalıştırma yöntemi!
                            with dspy.context(lm=lm):
                                result = archivist(text=p.get('abstract'))
                            for line in result.triples.split('\n'):
                                if '|' in line:
                                    parts = [x.strip() for x in line.split('|')]
                                    if len(parts) >= 4:
                                        src, rel, tgt, conf_str = parts[:4]
                                        try: llm_conf = float(conf_str)
                                        except: llm_conf = 0.5
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
        
        if db.driver is None:
            st.error("🚨 Bağlantı koptu.")
        else:
            triples = db.get_all_triples(limit=300)
            
            if triples:
                from pyvis.network import Network
                import streamlit.components.v1 as components
                
                net = Network(height="600px", width="100%", bgcolor="#0E1117", font_color="white", directed=True)
                for t in triples:
                    net.add_node(t["source"], label=t["source"], color="#FF4B4B", size=15)
                    net.add_node(t["target"], label=t["target"], color="#0068C9", size=15)
                    net.add_edge(t["source"], t["target"], title=t['relation'], label=t["relation"], color="#7C7C8C")
                
                net.repulsion(node_distance=150, spring_length=150)
                net.save_graph("epistemic_graph.html")
                with open("epistemic_graph.html", "r", encoding="utf-8") as f:
                    components.html(f.read(), height=650)
            else:
                st.info("📊 Veritabanı (Neo4j) şu an tamamen boş! Ağı görebilmek için lütfen 1. Sekmeden bir makaleyi analiz edip kaydedin.")
                
# --- MODÜL 3: ÇELİŞKİ YÖNETİMİ ---
with tab3:
    st.subheader("⚖️ Çelişki Yönetimi")
    concepts = db.get_all_concepts()
    if concepts:
        target_concept = st.selectbox("Odak Kavramı Seçin", concepts)
        if st.button("Bilimsel Çelişki Analizi Yap", type="primary"):
            factors = db.get_factors_affecting(target_concept)
            if factors:
                pos_score = sum([d.get('confidence',0.5) for d in factors if d['relation'] not in ["CONTRADICTS", "DOWNREGULATES"]])
                neg_score = sum([d.get('confidence',0.5) for d in factors if d['relation'] in ["CONTRADICTS", "DOWNREGULATES"]])
                total = pos_score + neg_score
                ratio = int((pos_score / total) * 100) if total > 0 else 50
                st.progress(ratio / 100.0) 
                cA, cB = st.columns(2)
                with cA: st.success(f"🟢 Destek Oranı: %{ratio}")
                with cB: st.error(f"🔴 Çelişki Oranı: %{100 - ratio}")
                for d in factors:
                    if d.get('relation') in ["CONTRADICTS", "DOWNREGULATES"]: st.error(f"**{d['source']}** ➜ ({d['relation']}) ➜ {target_concept}")
                    else: st.info(f"**{d['source']}** ➜ ({d['relation']}) ➜ {target_concept}")

# --- MODÜL 4: MEKANİSTİK SİMÜLASYON ---
with tab4:
    st.subheader("🧬 İn Silico Petri Kabı")
    concepts = db.get_all_concepts()
    if concepts:
        # EKRANI İKİYE BÖLÜYORUZ: sim_col (Simülasyon), list_col (Molekül Listesi)
        sim_col, list_col = st.columns([3, 1])
        
        with list_col:
            st.markdown("##### 🧫 Keşfedilen Yapılar")
            st.caption(f"Veritabanındaki {len(concepts)} yapı:")
            # Yapıları sağ tarafta şık bir liste olarak gösteriyoruz
            for c in sorted(concepts):
                st.markdown(f"- `{c}`")
                
        with sim_col:
            # BURADAN AŞAĞISI SENİN ORİJİNAL KODUNUN BİREBİR AYNISIDIR
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
                        for i, node in enumerate(nodes): dydt[i] = -0.03 * y[i]
                        for edge in edges:
                            src_i, tgt_i = nodes.index(edge['source']), nodes.index(edge['target'])
                            k = edge.get('confidence', 0.5) * 0.2
                            if edge['relation'] in ["UPREGULATES", "CAUSES", "ASSOCIATES_WITH"]: dydt[tgt_i] += k * y[src_i]
                            elif edge['relation'] in ["DOWNREGULATES", "CONTRADICTS"]: dydt[tgt_i] -= k * y[src_i] * y[tgt_i] * 0.05
                        return dydt
                    y0 = np.zeros(len(nodes))
                    if start_node in nodes: y0[nodes.index(start_node)] = initial_dose
                    t_steps = np.linspace(0, sim_time, int(sim_time*2))
                    with st.spinner("Çözümleniyor..."): solution = odeint(system_dynamics, y0, t_steps, args=(nodes, triples))
                    fig = go.Figure()
                    for i, node in enumerate(nodes):
                        if np.max(solution[:, i]) > 1.0: fig.add_trace(go.Scatter(x=t_steps, y=solution[:, i], mode='lines', name=node, line=dict(width=3)))
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
                for d in sorted_factors: st.write(f"**{d.get('date', 'Bilinmeyen Yıl')}**: {d['source']} ➜ ({d['relation']}) ➜ {target_concept_timeline}")

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
                st.markdown("Protein omurgası, amino asitlerin yan grupları (R grupları) hariç tutulduğunda, tekrar eden ana atom zincirini (azot, alfa-karbon ve karbonil karbonu) ve aralarındaki peptit bağlarını ifade eder. Bu temel yapı, proteine temel şeklini ve sarmal/tabaka gibi ikincil yapısal düzenini kazandırır. **CHON:** Proteinin omurgası | 🟡 **Sarı Kesik Çizgiler:** Zayıf Hidrojen Bağları")

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
            except Exception: pass

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
                                if (rel in ["UPREGULATES", "CAUSES"] and lab_result == "ARTTI") or (rel in ["DOWNREGULATES", "CONTRADIcripts"] and lab_result == "AZALDI"):
                                    st.success(f"✅ Doğrulandı: {src} ➜ {rel}")
                                elif (rel in ["UPREGULATES", "CAUSES"] and lab_result == "AZALDI") or (rel in ["DOWNREGULATES", "CONTRADICTS"] and lab_result == "ARTTI"):
                                    st.error(f"⚠️ ÇELİŞKİ: {src} ➜ {rel} (Ancak deneyiniz aksini söylüyor!)")
        except Exception as e: pass

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
            # YİNE BURASI: Hatasız AI çalıştırma bloğu!
            with dspy.context(lm=lm):
                result = dspy.Predict(DockingSignature)(entity_a=entity_a, entity_b=entity_b)
                
                cA, cB = st.columns(2)
                with cA:
                    st.success("🔗 **Fiziksel Uyum (Bağlanma Gücü):**")
                    st.write(result.binding_affinity)
                with cB:
                    st.error("⚕️ **Biyolojik Sonuç (Mutasyon/Hastalık Etkisi):**")
                    st.write(result.biological_outcome)

# --- MODÜL 6: 3D MOLEKÜLER KENETLENME VE YAPI GÖRÜNTÜLEYİCİ ---
st.markdown("---")
st.subheader("🔬 3D Moleküler Kenetlenme ve Yapı Görüntüleyici (PDB Viewer)")
st.caption("Bilinen biyolojik yapıların ve reseptör-ligand kilitlenmelerinin (örneğin Spike proteini ve ACE2) üç boyutlu atomik analizi.")

# Örnek ve çarpıcı PDB (Protein Data Bank) kodları
pdb_options = {
    "SARS-CoV-2 Spike / ACE2 Reseptör Kilitlenmesi (6M0J)": "6M0J",
    "İnsülin ve Reseptör Kompleksi (3W7Y)": "3W7Y",
    "Hemoglobin Oksijen Bağlanma Yapısı (2HHB)": "2HHB",
    "DNA Çift Sarmal Yapısı (1BNA)": "1BNA"
}

selected_complex = st.selectbox("İncelenecek Moleküler Kompleks / Virüs Eşleşmesi", list(pdb_options.keys()))
pdb_id = pdb_options[selected_complex]

# Saf JavaScript (Fetch API) kullanan kusursuz 3Dmol.js Entegrasyonu
viewer_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.0.3/3Dmol-min.js"></script>
    <style>
        body {{ margin: 0; background-color: #0E1117; color: white; font-family: sans-serif; }}
        #container {{ width: 100%; height: 500px; position: relative; }}
    </style>
</head>
<body>
    <div id="container"></div>
    <script>
        let element = document.getElementById("container");
        let config = {{ backgroundColor: "#0E1117" }};
        let viewer = $3Dmol.createViewer(element, config);
        
        // Yerleşik Fetch API ile RCSB PDB veritabanından modeli çekiyoruz
        fetch("https://files.rcsb.org/download/{pdb_id}.pdb")
            .then(response => {{
                if (!response.ok) throw new Error("Ağ hatası");
                return response.text();
            }})
            .then(data => {{
                viewer.addModel(data, "pdb");
                viewer.setStyle({{}}, {{cartoon: {{color: 'spectrum'}} }});
                viewer.zoomTo();
                viewer.render();
            }})
            .catch(error => {{
                element.innerHTML = "<p style='color:red; text-align:center; padding-top:200px;'>3D PDB Verisi yüklenirken bir sorun oluştu.</p>";
            }});
    </script>
</body>
</html>
"""

import streamlit.components.v1 as components
components.html(viewer_html, height=520)

st.info("💡 **İpucu:** Farenizin sol tuşuyla molekülü dilediğiniz gibi döndürebilir, tekerleğiyle yakınlaşıp uzaklaşarak atomik yapıyı inceleyebilirsiniz.")
