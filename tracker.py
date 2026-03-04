import streamlit as st
import requests
import webbrowser

# ────────────────────────────────────────────────
# Load Garet font from Google Fonts + custom colors
# ────────────────────────────────────────────────
PRIMARY_COLOR = "#015486"      # Global, Logistics, main text/accent
ACCENT_COLOR  = "#8fd8ff"      # Ocean highlight
BG_COLOR      = "#F8FCFF"

st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Garet:wght@400;700&display=swap" rel="stylesheet">
    <style>
        html, body, [data-testid="stAppViewContainer"], .stApp {{
            font-family: 'Garet', sans-serif !important;
            background-color: {BG_COLOR};
        }}
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Garet', sans-serif !important;
            font-weight: 700;
            color: {PRIMARY_COLOR};
        }}
        .stButton > button {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.7rem 1.4rem;
            font-weight: bold;
            font-family: 'Garet', sans-serif;
        }}
        .stButton > button:hover {{
            background-color: {ACCENT_COLOR};
            color: {PRIMARY_COLOR};
        }}
        .company-name {{
            font-family: 'Garet', sans-serif;
            font-weight: 700;
            font-size: 2.4rem;
            margin: 0;
            line-height: 1;
        }}
        .company-name .global {{ color: {PRIMARY_COLOR}; }}
        .company-name .ocean {{ color: {ACCENT_COLOR}; }}
        .company-name .logistics {{ color: {PRIMARY_COLOR}; }}
        .subtitle {{
            color: {PRIMARY_COLOR};
            font-size: 1.3rem;
            margin-top: 0.3rem;
            font-weight: 400;
        }}
        section[data-testid="stSidebar"] {{
            background-color: {PRIMARY_COLOR};
            color: white;
        }}
        .stSuccess, .stInfo {{
            background-color: rgba(1, 84, 134, 0.08);
            border-left: 4px solid {PRIMARY_COLOR};
            color: {PRIMARY_COLOR};
        }}
        hr {{ border-color: {PRIMARY_COLOR}; opacity: 0.4; }}
        footer {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Page config
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Ocean Logistics – Air Freight Tracker",
    page_icon="🌊",
    layout="wide"
)

# ────────────────────────────────────────────────
# Header with branded name
# ────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0 1rem;">
    <div class="company-name">
        <span class="global">Global</span> 
        <span class="ocean">Ocean</span> 
        <span class="logistics">Logistics</span>
    </div>
    <div class="subtitle">Air Freight Tracker</div>
</div>
<hr style="margin: 1rem 0 2rem;">
""", unsafe_allow_html=True)

st.markdown("Enter your **MAWB number** below to track air shipments. The official airline tracking page will open directly.")

# ────────────────────────────────────────────────
# Airline database (same as before – correct URLs)
# ────────────────────────────────────────────────
AIRLINES = {
    "020": ("Lufthansa Cargo", "LH", None, "api"),
    "999": ("Air China Cargo", "CA", "https://www.airchinacargo.com/cargo_en/gzcx/hkyd/list/index_pc.html", False),
    "784": ("China Southern Cargo", "CZ", "https://tang.csair.com/EN/WebFace/Tang.WebFace.Cargo/AgentAwbBrower.aspx?lan=en-us", True),
    "781": ("China Eastern Cargo", "MU", "https://cargo.ceair.com/en/track-shipment", False),
    "160": ("Cathay Pacific Cargo", "CX", "https://www.cathaycargo.com/en-us/track-and-trace.html", False),
    "180": ("Korean Air Cargo", "KE", "https://cargo.koreanair.com/tracking?awb=", True),
    "695": ("EVA Air Cargo", "BR", "https://www.brcargo.com/NEC_WEB/Tracking/QuickTracking/Index", False),
    "618": ("Singapore Airlines Cargo", "SQ", "https://www.singaporeair.com/en_UK/sg/cargo/track-shipment/?awb=", True),
    "131": ("Japan Airlines Cargo", "JL", "https://www.jalcargo.com/en/track-shipment", False),
    "988": ("Asiana Cargo", "OZ", "https://www.asianacargo.com/tracking/viewTraceAirWaybill.do?lang=en", True),
    "176": ("Emirates SkyCargo", "EK", "https://www.skycargo.com/shipping/tracking/", True),
    "157": ("Qatar Airways Cargo", "QR", "https://www.qrcargo.com/en/tracking", True),
    "235": ("Turkish Cargo", "TK", "https://www.turkishcargo.com.tr/en/tracking", True),
}

def parse_mawb(mawb_str):
    cleaned = ''.join(c for c in str(mawb_str) if c.isdigit())
    if len(cleaned) not in (10, 11):
        return None, None
    return cleaned[:3], cleaned[3:]

def fetch_lufthansa(prefix, number):
    url = f"https://api.lufthansa-cargo.com/lh/handling/shipment?aWBPrefix={prefix}&aWBNumber={number}"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def open_tracking_page(prefix, number):
    if prefix not in AIRLINES:
        st.error("Airline prefix not supported yet.")
        return

    name, code, base_url, supports_direct = AIRLINES[prefix]
    full_awb = f"{prefix}-{number}" if len(number) == 8 else f"{prefix}{number}"

    if prefix == "020":
        data = fetch_lufthansa(prefix, number)
        if "error" in data:
            st.error(f"❌ {data['error']}")
        else:
            st.subheader(f"📊 {name} Tracking Result")
            st.json(data)
        return

    url = base_url
    if supports_direct and base_url:
        if "?" in base_url or "=" in base_url:
            url += full_awb

    webbrowser.open_new_tab(url)

    st.success(f"🌊 **{name}** tracking page opened")
    st.info(f"AWB used: **{full_awb}**")
    st.caption("If not auto-filled, paste the AWB into the form on the page.")

# ────────────────────────────────────────────────
# Input area
# ────────────────────────────────────────────────
mawb_input = st.text_input(
    "MAWB Number",
    placeholder="e.g. 160-06728654  or  999-38712203  or  020-08002050",
    help="With or without dashes/spaces"
)

if st.button("Track Shipment", type="primary", use_container_width=True):
    prefix, number = parse_mawb(mawb_input)
    
    if not prefix or not number:
        st.error("❌ Please enter a valid 10 or 11-digit MAWB number.")
    else:
        if prefix in AIRLINES:
            name = AIRLINES[prefix][0]
            st.success(f"Detected: **{name}** ({AIRLINES[prefix][1]})")
            open_tracking_page(prefix, number)
        else:
            st.warning(f"Prefix **{prefix}** is not yet in our database.")

# ────────────────────────────────────────────────
# Footer
# ────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: {PRIMARY_COLOR}; font-size: 0.95rem; padding: 1.5rem 0;">
    © 2026 <span class="global">Global</span> <span class="ocean">Ocean</span> <span class="logistics">Logistics</span><br>
    Northern Ireland's Leading Logistics Partner • Air & Sea Freight • Customs • Road Transport
</div>
""", unsafe_allow_html=True)