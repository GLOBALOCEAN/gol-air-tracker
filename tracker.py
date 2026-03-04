import streamlit as st
import requests
from datetime import datetime

# ────────────────────────────────────────────────
# Load Garet font from CDN + GOL styling
# ────────────────────────────────────────────────
st.markdown("""
    <link href="https://cdn.jsdelivr.net/gh/type-forward/garet@latest/fonts/webfonts/garet.css" rel="stylesheet">
    <style>
    /* Garet header with your colors */
    .gol-header {
        font-family: 'Garet', 'Segoe UI', Arial, sans-serif !important;
        font-weight: 700 !important;
        font-size: 3.2rem !important;
        text-align: center !important;
        margin: 1.5rem 0 0.5rem !important;
    }
    .gol-header .global, .gol-header .ocean {
        color: #015486 !important;
    }
    .gol-header .rest {
        color: #0d47a1 !important;
    }

    /* Accent color */
    :root {
        --accent: #8fd8ff;
        --primary: #015486;
    }

    /* Tagline */
    .gol-tagline {
        color: var(--accent) !important;
        font-size: 1.45rem !important;
        text-align: center !important;
        margin-bottom: 2.5rem !important;
        font-weight: 500 !important;
    }

    /* Result card */
    .result-card {
        background-color: white !important;
        border: 1px solid var(--accent) !important;
        border-left: 6px solid var(--primary) !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.08) !important;
        margin: 2rem 0 2.5rem !important;
    }

    /* Track button */
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
        color: var(--primary) !important;
    }

    /* Messages & input */
    .stSuccess, .stInfo, .stError {
        border-radius: 8px !important;
        padding: 1.2rem !important;
    }
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
# Page setup
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Ocean Logistics – Air Freight Tracker",
    page_icon="✈️",
    layout="wide"
)

# Header with Garet + your colors
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
# Parse MAWB - fixed version
# ────────────────────────────────────────────────
def parse_mawb(mawb_str):
    cleaned = ''.join(c for c in str(mawb_str) if c.isdigit())
    if len(cleaned) not in (10, 11):
        return None, None
    prefix = cleaned[:3]
    number = cleaned[3:]
    return prefix, number

# ────────────────────────────────────────────────
# Tracking link generator
# ────────────────────────────────────────────────
def get_tracking_link(airline_name, prefix, number):
    full_awb = f"{prefix}-{number}" if len(number) == 8 else f"{prefix}{number}"
    
    if "Air China" in airline_name:
        return f"https://www.airchinacargo.com/cargo_en/gzcx/hkyd/list/index_pc.html", full_awb
    if "China Southern" in airline_name:
        return f"https://tang.csair.com/EN/WebFace/Tang.WebFace.Cargo/AgentAw