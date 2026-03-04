import streamlit as st
import requests
from datetime import datetime

# ────────────────────────────────────────────────
# GOL branding + styling (matches sea portal feel)
# ────────────────────────────────────────────────
st.markdown("""
    <style>
    /* Header */
    .gol-header {
        color: #0d47a1;
        font-size: 2.8rem;
        font-weight: bold;
        text-align: center;
        margin: 20px 0 8px;
    }
    .gol-tagline {
        color: #1976d2;
        font-size: 1.3rem;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* Blue button */
    .stButton > button {
        background-color: #0d47a1;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 14px 32px;
        font-size: 1.15rem;
        font-weight: bold;
        width: 100%;
        max-width: 400px;
        margin: 20px auto;
        display: block;
    }
    .stButton > button:hover {
        background-color: #1565c0;
    }
    
    /* Result card */
    .result-card {
        background-color: #f8fbff;
        padding: 24px;
        border-radius: 10px;
        border: 1px solid #bbdefb;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin: 20px 0;
    }
    
    /* Messages */
    .stSuccess, .stInfo, .stError {
        border-radius: 8px;
        padding: 16px !important;
        margin: 16px 0;
    }
    
    /* Footer */
    .gol-footer {
        text-align: center;
        color: #555;
        font-size: 0.9rem;
        margin-top: 60px;
        padding: 20px;
        border-top: 1px solid #eee;
    }
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Page config
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Ocean Logistics - Air Freight Tracker",
    page_icon="✈️",
    layout="wide"
)

# Header
st.markdown('<div class="gol-header">Global Ocean Logistics</div>', unsafe_allow_html=True)
st.markdown('<div class="gol-tagline">Air Freight Tracker – Reliable Global Solutions</div>', unsafe_allow_html=True)

st.markdown("Enter your **Master Air Waybill (MAWB)** number to track your shipment.")

# ────────────────────────────────────────────────
# Airline mapping (expand as needed)
# ────────────────────────────────────────────────
PREFIX_MAP = {
    "020": {"name": "Lufthansa Cargo", "code": "LH", "has_api": True},
    "999": {"name": "Air China Cargo", "code": "CA", "has_api": False},
    "784": {"name": "China Southern Cargo", "code": "CZ", "has_api": False},
    "781": {"name": "China Eastern Cargo", "code": "MU", "has_api": False},
    "160": {"name": "Cathay Pacific Cargo", "code": "CX", "has_api": False},
    "180": {"name": "Korean Air Cargo", "code": "KE", "has_api": False},
    "695": {"name": "EVA Air Cargo", "code": "BR", "has_api": False},
    # Add more prefixes here
}

# ────────────────────────────────────────────────
# Helper: parse MAWB
# ────────────────────────────────────────────────
def parse_mawb(mawb_str):
    cleaned = ''.join(c for c in str(mawb_str) if c.isdigit())
    if len(cleaned) not in (10, 11):
        return None, None
    prefix = cleaned[:3]
    number = cleaned[3:]
    return prefix, number

# ────────────────────────────────────────────────
# Get tracking link for non-API airlines
# ────────────────────────────────────────────────
def get_tracking_link(airline_name, prefix, number):
    full_awb = f"{prefix}-{number}" if len(number) == 8 else f"{prefix}{number}"
    
    # Specific known links (add more when you find them)
    if "Air China" in airline_name:
        return f"https://www.airchinacargo.com/cargo_en/gzcx/hkyd/list/index_pc.html", full_awb
    if "China Southern" in airline_name:
        return f"https://tang.csair.com/EN/WebFace/Tang.WebFace.Cargo/AgentAwbBrower.aspx?lan=en-us&AWB={full_awb}", full_awb
    if "Cathay Pacific" in airline_name:
        return f"https://www.cathaycargo.com/en-us/track-and-trace.html?awb={full_awb}", full_awb
    
    # Fallback: Google search for tracking page
    return f"https://www.google.com/search?q={airline_name.replace(' ', '+')}+cargo+tracking+{full_awb}", full_awb

# ────────────────────────────────────────────────
# Main input
# ────────────────────────────────────────────────
mawb_input = st.text_input(
    "MAWB Number",
    placeholder="e.g. 999-38712203 or 020-08002050",
    help="With or without dashes/spaces"
)

if st.button("Track Shipment"):
    prefix, number = parse_mawb(mawb_input)
    
    if not prefix or not number:
        st.error("Invalid MAWB format. Please enter 10 or 11 digits.")
    else:
        airline = PREFIX_MAP.get(prefix, {"name": f"Carrier ({prefix})", "code": prefix, "has_api": False})
        
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        
        st.success(f"**Detected:** {airline['name']} ({airline['code']}) – AWB {prefix}-{number}")
        
        if airline.get("has_api", False) and prefix == "020":
            # Lufthansa API placeholder
            st.info("Querying Lufthansa Cargo API... (result would appear here)")
            # You can add real API call here if desired
        else:
            url, full_awb = get_tracking_link(airline["name"], prefix, number)
            
            st.markdown(f"""
                <p style="font-size:1.1rem; margin:20px 0 10px;">
                    Open the official {airline['name']} tracking page:
                </p>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <a href="{url}" target="_blank" style="
                    background-color: #0d47a1;
                    color: white;
                    padding: 16px 32px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-size: 1.2rem;
                    font-weight: bold;
                    display: inline-block;
                ">
                    Open Tracking Page → {full_awb}
                </a>
            """, unsafe_allow_html=True)
            
            st.caption("Click the button above – it will open in a new tab.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="gol-footer">
        © Global Ocean Logistics NI • Air & Sea Freight Solutions<br>
        Belfast / Newtownards • contact@globaloceanlogisticsni.com
    </div>
""", unsafe_allow_html=True)