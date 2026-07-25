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

load_dotenv()
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.database import EpistemicGraph
from agents.archivist import ArchivistAgent
from core.scholar import search_papers

lm = dspy.LM('groq/llama-3.1-8b-instant', api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Idea Co-Pilot", page_icon="🧪", layout="wide")
st.title("🧪 Idea Co-Pilot - Canlı Araştırma Motoru")

@st.cache_resource
def init_system():
    return EpistemicGraph(), ArchivistAgent()

db, archivist = init_system()
