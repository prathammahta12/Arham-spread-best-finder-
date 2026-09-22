import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import os
import time

# Page Configuration
st.set_page_config(page_title="ARHAM TRADERS | Terminal", layout="wide", initial_sidebar_state="expanded")

# Direct Image Link (Palitana / Jain Temple)
TEMPLE_IMG_URL = "https://images.unsplash.com/photo-1622396481304-4ad7343b6794?auto=format&fit=crop&w=1920&q=80"

# --- HIGH-CONTRAST GOLDEN & NEON THEME ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Montserrat:ital,wght@0,800;1,900&family=Rajdhani:wght@600;700;800&display=swap');

    /* Global Dark Cyber & Temple Overlay Background */
    .stApp {{
        background: linear-gradient(rgba(5, 10, 24, 0.90), rgba(5, 10, 24, 0.95)), 
                    url('{TEMPLE_IMG_URL}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #ffffff;
        font-family: 'Rajdhani', sans-serif;
    }}

    /* Main Big Brand Header */
    .brand-container {{
        text-align: center;
        margin-top: 10px;
        margin-bottom: 22px;
        padding: 22px;
        background: rgba(10, 18, 38, 0.75);
        border: 2.5px solid rgba(245, 158, 11, 0.6);
        border-radius: 16px;
        box-shadow: 0 0 40px rgba(245, 158, 11, 0.35);
    }}

    .brand-title-big {{
        font-family: 'Cinzel', serif;
        font-size: 3.6rem !important;
        font-weight: 900 !important;
        font-style: italic !important;
        letter-spacing: 3px !important;
        color: #ffbe0b !important;
        text-shadow: 0 0 25px rgba(255, 190, 11, 0.8), 0 0 50px rgba(255, 110, 0, 0.5);
        margin: 0 !important;
        line-height: 1.1;
    }}

    .brand-sub-big {{
        font-family: 'Montserrat', sans-serif;
        font-size: 1.45rem !important;
        font-weight: 900 !important;
        font-style: italic !important;
        letter-spacing: 2px !important;
        color: #38bdf8 !important;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.9);
        margin-top: 8px !important;
        margin-bottom: 0px !important;
    }}

    /* Temple Header Banner Image Box */
    .temple-banner-box {{
        text-align: center;
        margin-bottom: 15px;
    }}
    .temple-banner-box img {{
        width: 100%;
        max-height: 230px;
        object-fit: cover;
        border-radius: 14px;
        border: 2px solid rgba(245, 158, 11, 0.6);
        box-shadow: 0 8px 30px rgba(0,0,0,0.7);
    }}

    /* High Visibility Input Form Styling */
    .terminal-glass-card {{
        background: rgba(13, 22, 45, 0.92);
        backdrop-filter: blur(14px);
        border: 1.5px solid rgba(56, 189, 248, 0.35);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.7);
    }}

    /* Labels & Texts */
    label, p, span {{
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #f1f5f9 !important;
        letter-spacing: 0.5px !important;
    }}

    /* Input Fields */
    div[data-baseweb="select"] > div, .stTextInput > div > div > input, .stNumberInput input {{
        background-color: #0b1329 !important;
        color: #38bdf8 !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        border: 1.5px solid #2563eb !important;
        border-radius: 8px !important;
    }}

    /* Scan Now High Glow Action Button */
    .scan-glow > button {{
        background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%) !important;
        color: #ffffff !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 1.2rem !important;
        font-weight: 900 !important;
        border: 1.5px solid #ffbe0b !important;
        box-shadow: 0 0 25px rgba(245, 158, 11, 0.7) !important;
        border-radius: 10px !important;
    }}
    .scan-glow > button:hover {{
        box-shadow: 0 0 35px rgba(255, 190, 11, 1) !important;
        transform: scale(1.02);
    }}
</style>
""", unsafe_allow_html=True)

def play_alert_sound():
    st.markdown("""
    <audio autoplay>
        <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
    </audio>
    """, unsafe_allow_html=True)

# --- SUPABASE REST CONFIG ---
SUPABASE_URL = "https://pnigixgqdftajqkmuouf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBuaWdpeGdxZGZ0YWpxa211b3VmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTAwNTI0OTUsImV4cCI6MjEwNTYyODQ5NX0.pI7CPt9XdLG2zirwkisz5Ttzm3CZIQiL6qg7D70fKlc"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- DATABASE HELPERS ---
def get_user(identifier):
    try:
        clean_id = identifier.strip()
        url = f"{SUPABASE_URL}/rest/v1/users?or=(username.ilike.{clean_id},phone.eq.{clean_id})&select=*"
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            d = r.json()
            return d if len(d) > 0 else None
        return None
    except:
        return None

def register_user(username, password, phone):
    try:
        url = f"{SUPABASE_URL}/rest/v1/users"
        payload = {"username": username.strip(), "password": password.strip(), "phone": phone.strip(), "is_approved": False, "is_admin": False, "valid_until": None}
        return requests.post(url, headers=HEADERS, json=payload, timeout=8)
    except:
        return None

def update_user_access(user_id, is_approved, days):
    try:
        valid_date = (date.today() + timedelta(days=int(days))).strftime("%Y-%m-%d")
        url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}"
        r = requests.patch(url, headers=HEADERS, json={"is_approved": is_approved, "valid_until": valid_date}, timeout=8)
        return r.status_code in [200, 204]
    except:
        return False

def update_user_full(user_id, username, phone, password, valid_until, is_approved):
    try:
        url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}"
        payload = {"username": username.strip(), "phone": str(phone).strip(), "password": password.strip(), "valid_until": valid_until, "is_approved": is_approved}
        r = requests.patch(url, headers=HEADERS, json=payload, timeout=8)
        return r.status_code in [200, 204]
    except:
        return False

def delete_user(user_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}"
        r = requests.delete(url, headers=HEADERS, timeout=8)
        return r.status_code in [200, 204]
    except:
        return False

def log_activity(username, action):
    try:
        url = f"{SUPABASE_URL}/rest/v1/activity_logs"
        requests.post(url, headers=HEADERS, json={"username": username, "action": action}, timeout=3)
    except:
        pass

# --- SESSION STATES ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "valid_until" not in st.session_state:
    st.session_state.valid_until = None
if "auto_scan" not in st.session_state:
    st.session_state.auto_scan = False

# ==================== 1. BRANDED LOGIN SCREEN ====================
if not st.session_state.logged_in:
    col_l, col_center, col_r = st.columns([1, 1.4, 1])
    with col_center:
        st.markdown(f"""
        <div class='temple-banner-box'>
            <img src='{TEMPLE_IMG_URL}' alt='Temple Peak'>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='brand-container'>
            <div class='brand-title-big'>ARHAM TRADERS</div>
            <div class='brand-sub-big'>⚡ DEVELOPED BY PRATHAM MEHTA ⚡</div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_reg, tab_rst = st.tabs(["Trader Login", "New Registration", "Reset Access Key"])
        
        with tab_login:
            u_name = st.text_input("Username / Mobile", key="l_name")
            u_pass = st.text_input("Access Password", type="password", key="l_pass")
            
            if st.button("AUTHENTICATE & ENTER TERMINAL", use_container_width=True, type="primary"):
                if not u_name or not u_pass:
                    st.warning("कृपया Username और Password दोनों भरें।")
                else:
                    u_data = get_user(u_name)
                    if not u_data:
                        st.error("यूज़र नहीं मिला! सही डिटेल्स डालें।")
                    else:
                        u = u_data[0]
                        if u["password"] != u_pass.strip():
                            st.error("गलत पासवर्ड!")
                        elif u.get("is_admin", False):
                            st.session_state.logged_in = True
                            st.session_state.username = u["username"]
                            st.session_state.is_admin = True
                            log_activity(u["username"], "Admin Logged In")
                            st.rerun()
                        elif not u.get("is_approved", False):
                            st.warning("⏳ आपका अकाउंट अभी पेंडिंग है! एडमिन (Admin) से अप्रूवल का इंतज़ार करें।")
                        elif not u.get("valid_until") or datetime.strptime(u["valid_until"], "%Y-%m-%d").date() < date.today():
                            st.error(f"⛔ आपका एक्सेस समाप्त हो चुका है ({u.get('valid_until')})! रिन्यू के लिए एडमिन से संपर्क करें।")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.username = u["username"]
                            st.session_state.is_admin = False
                            st.session_state.valid_until = u.get("valid_until")
                            log_activity(u["username"], "Trader Logged In")
                            st.rerun()

        with tab_reg:
            r_user = st.text_input("Desired Username", key="r_user")
            r_phone = st.text_input("Mobile Number", key="r_phone")
            r_pass = st.text_input("Password", type="password", key="r_pass")
            if st.button("REQUEST TERMINAL ACCESS", use_container_width=True):
                if r_user and r_phone and r_pass:
                    res = register_user(r_user, r_pass, r_phone)
                    if res and res.status_code in [200, 201]:
                        st.success("✅ रिक्वेस्ट सबमिट हो गई! एडमिन अप्रूव करते ही आप लॉगिन कर सकेंगे।")
                    else:
                        st.error("यूज़रनेम पहले से मौजूद है!")
                else:
                    st.warning("सभी फ़ील्ड भरें।")

        with tab_rst:
            f_user = st.text_input("Username", key="f_user")
            f_phone = st.text_input("Mobile Number", key="f_phone")
            f_pass = st.text_input("New Password", type="password", key="f_pass")
            if st.button("RESET SECURITY KEY", use_container_width=True):
                if f_user and f_phone and f_pass:
                    u_d = get_user(f_user)
                    if u_d and str(u_d[0].get("phone")).strip() == str(f_phone).strip():
                        update_user_full(u_d[0]["id"], u_d[0]["username"], u_d[0]["phone"], f_pass, u_d[0].get("valid_until"), u_d[0].get("is_approved", False))
                        st.success("पासवर्ड अपडेट हो गया! अब लॉगिन करें।")
                    else:
                        st.error("डिटेल्स मेल नहीं खा रहीं!")

# ==================== 2. ADMIN CONTROL CENTER ====================
elif st.session_state.is_admin:
    st.sidebar.markdown(f"### Superadmin: `{st.session_state.username}`")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🛠️ Admin Control Center — Arham Traders")
    a_tab1, a_tab2 = st.tabs(["Trader Accounts & Days Validity", "Audit Logs"])

    with a_tab1:
        st.subheader("Manage Active Users")
        try:
            r = requests.get(f"{SUPABASE_URL}/rest/v1/users?order=created_at.desc", headers=HEADERS, timeout=8)
            if r.status_code == 200:
                for u in r.json():
                    if u["username"].lower() in ["pratham1785", "admin"]:
                        continue

                    rem_d = 0
                    if u.get("valid_until"):
                        try:
                            rem_d = max(0, (datetime.strptime(u["valid_until"], "%Y-%m-%d").date() - date.today()).days)
                        except:
                            pass

                    st_badge = f"🟢 Active ({rem_d} Days)" if u.get("is_approved") and rem_d > 0 else "⏳ Blocked / Expired"
                    with st.expander(f"{u['username']} | 📞 {u.get('phone')} | {st_badge}"):
                        c1, c2, c3 = st.columns([1.5, 1.5, 1])
                        with c1:
                            val_d = st.number_input("Set Validity Days:", min_value=1, max_value=365, value=30, key=f"d_{u['id']}")
                            if st.button(f"Grant {val_d} Days Access", key=f"btn_d_{u['id']}", use_container_width=True):
                                update_user_access(u['id'], True, val_d)
                                st.success(f"{val_d} दिनों का एक्सेस दे दिया गया!")
                                st.rerun()
                        with c2:
                            np = st.text_input("Force Reset Pass", key=f"np_{u['id']}")
                            if st.button("Commit Pass", key=f"b_np_{u['id']}", use_container_width=True):
                                if np:
                                    update_user_full(u['id'], u['username'], u['phone'], np, u.get('valid_until'), u.get('is_approved', False))
                                    st.success("पासवर्ड बदल दिया गया!")
                                    st.rerun()
                        with c3:
                            if st.button("Revoke Access", key=f"b_rvk_{u['id']}", use_container_width=True):
                                update_user_access(u['id'], False, 0)
                                st.rerun()
                            if st.button("Delete User", key=f"b_dl_{u['id']}", use_container_width=True):
                                delete_user(u['id'])
                                st.rerun()
        except Exception as e:
            st.error(f"एरर: {e}")

    with a_tab2:
        res_l = requests.get(f"{SUPABASE_URL}/rest/v1/activity_logs?order=logged_at.desc&limit=50", headers=HEADERS, timeout=8)
        if res_l.status_code == 200 and res_l.json():
            st.dataframe(pd.DataFrame(res_l.json()), use_container_width=True)

# ==================== 3. TRADER SPREAD SCANNER TERMINAL ====================
else:
    # Auto-Logout Check
    if st.session_state.valid_until:
        if datetime.strptime(st.session_state.valid_until, "%Y-%m-%d").date() < date.today():
            st.session_state.logged_in = False
            st.error("⛔ आपका एक्सेस समाप्त हो चुका है!")
            st.rerun()

    # Sidebar
    with st.sidebar:
        st.markdown("<h1 style='color:#ffbe0b; font-family: Cinzel; font-size: 1.8rem; margin:0;'>ARHAM TRADERS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#38bdf8; font-size: 0.95rem; font-weight:800; margin-bottom: 15px;'>DEV BY PRATHAM MEHTA</p>", unsafe_allow_html=True)
        st.write("---")
        
        rem_days = (datetime.strptime(st.session_state.valid_until, "%Y-%m-%d").date() - date.today()).days if st.session_state.valid_until else 0
        st.markdown(f"Trader: **{st.session_state.username}**")
        st.markdown(f"Plan Validity: **{rem_days} Days Remaining**")
        st.markdown(f"Valid Till: `{st.session_state.valid_until}`")
        st.write("---")
        
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # Terminal Header
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown("<h2 style='color: #ffbe0b; font-family: Montserrat; font-weight:900; margin:0;'>DELTA ANALYSIS — FNO SPREAD SCANNER</h2>", unsafe_allow_html=True)
        st.caption("Institutional Spread Analytics Engine | NSE Real-Time Feed Mode")
    with h2:
        st.markdown("<div style='text-align:right; margin-top: 10px;'><span style='color: #22c55e; font-weight: 900; font-size: 1.1rem;'>● FEED ACTIVE</span> | <span style='color:#94a3b8; font-weight:700;'>NSE F&O</span></div>", unsafe_allow_html=True)

    # --- TOP SCANNER FILTERS PANEL ---
    st.markdown("<div class='terminal-glass-card'>", unsafe_allow_html=True)
    st.markdown("<div style='color:#ffbe0b; font-size: 1.15rem; font-weight: 800; margin-bottom: 12px;'>SCANNER FILTER PARAMETERS</div>", unsafe_allow_html=True)
    
    r1_c1, r1_c2, r1_c3, r1_c4, r1_c5, r1_c6, r1_c7 = st.columns(7)
    with r1_c1:
        f_stock = st.selectbox("STOCK", ["ALL STOCKS", "NIFTY", "BANKNIFTY", "HDFCBANK", "RELIANCE", "ICICIBANK", "TCS", "INFY", "SBIN"])
    with r1_c2:
        f_expiry = st.selectbox("EXPIRY DATE", ["CURRENT vs NEXT", "NEXT vs FAR", "CURRENT MONTH", "WEEKLY"])
    with r1_c3:
        f_ref = st.selectbox("REFERENCE", ["Future LTP", "Spot Index", "VWAP", "Synthetic Future"])
    with r1_c4:
        f_type = st.selectbox("TYPE", ["Futures Calendar Spread", "Both (CE & PE)", "Call Spread (CE)", "Put Spread (PE)"])
    with r1_c5:
        f_price_gap = st.selectbox("PRICE GAP", ["OFF", "1 pt", "2 pts", "3 pts", "5 pts"])
    with r1_c6:
        f_delta = st.selectbox("DELTA FILTER", ["ON (20-30)", "ON (30-40)", "ON (40-50)", "OFF"])
    with r1_c7:
        f_strike_gap = st.number_input("STRIKE GAP %", min_value=1.0, max_value=20.0, value=5.0, step=0.5)

    r2_c1, r2_c2, r2_c3, r2_c4, r2_c5, r2_c6 = st.columns(6)
    with r2_c1:
        f_iv_gap = st.number_input("IV GAP %", min_value=1.0, max_value=50.0, value=5.0, step=0.5)
    with r2_c2:
        f_min_vol = st.number_input("MIN VOLUME (LOTS)", min_value=1, max_value=10000, value=10, step=5)
    with r2_c3:
        f_ratio = st.selectbox("RATIO", ["1 : 1", "2 : 1", "3 : 10", "1 : 2", "1 : 3"])
    with r2_c4:
        f_limit_type = st.selectbox("LIMIT TYPE", ["Max Debit", "Min Credit", "Max Payoff", "Zero Cost"])
    with r2_c5:
        f_limit_val = st.number_input("LIMIT VALUE Rs", min_value=0, max_value=100000, value=1000, step=100)
    with r2_c6:
        f_direction = st.selectbox("DIRECTION", ["Buy -> Sell", "Sell -> Buy", "Arbitrage Spread"])
    st.markdown("</div>", unsafe_allow_html=True)

    # --- CUSTOM ALERT PANEL ---
    st.markdown("<div class='terminal-glass-card'>", unsafe_allow_html=True)
    st.markdown("<div style='color:#38bdf8; font-size: 1.15rem; font-weight: 800; margin-bottom: 12px;'>CUSTOM SPREAD ALERT — SPECIFIC COMPANY / STRIKE</div>", unsafe_allow_html=True)
    
    c_col1, c_col2, c_col3, c_col4, c_col5, c_col6 = st.columns(6)
    with c_col1:
        a_company = st.selectbox("COMPANY", ["HDFCBANK", "NIFTY", "BANKNIFTY", "RELIANCE", "TCS"])
    with c_col2:
        a_option = st.selectbox("INSTRUMENT", ["FUT (Calendar)", "CE (Call)", "PE (Put)"])
    with c_col3:
        a_buy = st.number_input("BUY STRIKE / EXPIRY", value=1640, step=10)
    with c_col4:
        a_sell = st.number_input("SELL STRIKE / EXPIRY", value=1680, step=10)
    with c_col5:
        a_ratio = st.selectbox("RATIO BUY:SELL", ["1 : 1", "1 : 2", "3 : 10"])
    with c_col6:
        a_debit = st.number_input("TARGET SPREAD Rs", value=12.50, step=0.5)

    btn_ca1, btn_ca2 = st.columns(2)
    with btn_ca1:
        start_alert_btn = st.button("START CUSTOM ALERT", use_container_width=True)
    with btn_ca2:
        check_now_btn = st.button("CHECK STRIKE PAIR NOW", u
