import streamlit as st
import requests
from datetime import datetime

# ────────────────────────────────────────────────
# Load Garet font from CDN + custom GOL styling
# ────────────────────────────────────────────────
st.markdown("""
    <link href="https://cdn.jsdelivr.net/gh/type-forward/garet@latest/fonts/webfonts/garet.css" rel="stylesheet">
    <style>
    /* Use Garet for header (bold) */
    .gol-header {
        font-family: 'Garet', 'Segoe UI', Arial, sans-serif !important;
        font-weight: 700 !important;
        font-size: 3rem !important;
        text-align: center !important;
        margin: 1.5rem 0 0.5rem !important;
    }
    .gol-header span.global { color: #015486 !important; }
    .gol-header span.ocean { color: #015486 !important; }
    .gol-header span.rest { color: #0d47a1 !important; }

    /* Accent color #8fd8ff */
    :root {
        --accent: #8fd8ff;
        --primary: #015486;
    }

    /* Tagline */
    .gol-tagline {
        color: var(--accent) !important;
        font-size: 1.4rem !important;
        text-align: center !important;
        margin-bottom: 2.5rem !important;
        font-weight: 500 !important;
    }

    /* Card for result */
    .result-card {
        background-color: white !important;
        border: 1px solid var(--accent) !important;
        border-left: 6px solid var(--primary) !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.08) !important;
        margin: 2rem 0 2.5rem !important;
    }

    /* Track button - using accent on hover */
    .stButton > button {
        background-color: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 1rem 2.5rem !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        max-width: 420px !important;
        margin: 2rem auto 1rem !important;
        display: block !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: var(--accent) !important;
        transform: translateY(-2px) !important;
    }

    /* Messages */
    .stSuccess {
        background-color: #e8f5e9 !important;
        border-left: 5px solid #4caf50 !important;
    }
    .stInfo {
        background-color: #e3f2fd !important;
        border-left: 5px solid var(--accent) !important;
    }
    .stError {
        background-color: #ffebee !important;
        border-left: 5px solid #f44336 !important;
    }

    /* Input */
    .stTextInput > div > div > input {
        border: 2px solid var(--accent) !important;
        border-radius: 10px !important;
        padding: 0.9rem !important;
        font-size: 1.1rem !important;
    }

    /* Footer */
    .gol-footer {
        text-align: center !important;
        color: #444 !important;
        font-size: 0.95rem !important;
        margin-top: 5rem !important;
        padding: 1.8rem !important;
        border-top: 1px solid #eee !important;
    }
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Page config
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Ocean Logistics – Air Freight Tracker",
    page_icon="✈️",
    layout="wide"
)

# Header with font & colour split
st.markdown("""
    <div class="gol-header">
        <span class="global">Global</span> 
        <span class="ocean">Ocean</span> 
        <span class="rest">Logistics</span>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="gol-tagline">Air Freight Tracker – Fast, Reliable, Global</div>', unsafe_allow_html=True)

st.markdown("Enter your **Master Air Waybill (MAWB)** number to track your shipment.")

# ────────────────────────────────────────────────
# Airline mapping
# ────────────────────────────────────────────────
PREFIX_MAP = {
    "020": {"name": "Lufthansa Cargo", "code": "LH", "has_api": True},
    "999": {"name": "Air China Cargo", "code": "CA", "has_api": False},
    "784": {"name": "China Southern Cargo", "code": "CZ", "has_api": False},
    "781": {"name": "China Eastern Cargo", "code": "MU", "has_api": False},
    "160": {"name": "Cathay Pacific Cargo", "code": "CX", "has_api": False},
    "180": {"name": "Korean Air Cargo", "code": "KE", "has_api": False},
    "695": {"name": "EVA Air Cargo", "code": "BR", "has_api": False},
}

# ────────────────────────────────────────────────
# Parse MAWB
# ────────────────────────────────────────────────
def parse_mawb(mawb_str):
    cleaned = ''.join(c for c in str(mawb_str) if c.is