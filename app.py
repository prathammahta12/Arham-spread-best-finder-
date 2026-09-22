import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import math
import time

# Page Setup
st.set_page_config(page_title="Delta Analysis | Pro FNO Spread Engine", layout="wide", initial_sidebar_state="expanded")

# --- CYBER FINTECH DARK THEME & AUDIO ALERT CSS ---
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .panel-box {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 18px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.35);
    }
    .panel-title {
        color: #38bdf8;
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    div[data-baseweb="select"] > div, .stTextInput > div > div > input, .stNumberInput input {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .scan-btn > button {
        background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        border: none !important;
    }
    .scan-btn > button:hover {
        box-shadow: 0 0 15px rgba(37, 99, 235, 0.6) !important;
    }
    .stop-btn > button {
        background-color: #ef4444 !important;
        color: white !important;
        border: none !important;
    }
    .badge-bull {
        color: #10b981;
        font-weight: bold;
        background: rgba(16, 185, 129, 0.1);
        padding: 4px 8px;
        border-radius: 4px;
    }
    .badge-bear {
        color: #f43f5e;
        font-weight: bold;
        background: rgba(244, 63, 94, 0.1);
        padding: 4px 8px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Audio Beep Generator (HTML5 audio)
def play_sound():
    sound_html = """
    <audio autoplay>
        <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
    </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# --- SUPABASE CONFIG ---
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
        payload = {
            "username": username.strip(),
            "password": password.strip(),
            "phone": phone.strip(),
            "is_approved": False,
            "is_admin": False,
            "valid_until": None
        }
        return requests.post(url, headers=HEADERS, json=payload, timeout=8)
    except:
        return None

def update_user_access(user_id, is_approved, days):
    try:
        valid_date = (date.today() + timedelta(days=int(days))).strftime("%Y-%m-%d")
        url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}"
        payload = {"is_approved": is_approved, "valid_until": valid_date}
        r = requests.patch(url, headers=HEADERS, json=payload, timeout=8)
        return r.status_code in [200, 204]
    except:
        return False

def update_user_full(user_id, username, phone, password, valid_until, is_approved):
    try:
        url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}"
        payload = {
            "username": username.strip(),
            "phone": str(phone).strip(),
            "password": password.strip(),
            "valid_until": valid_until,
            "is_approved": is_approved
        }
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
if "sound_enabled" not in st.session_state:
    st.session_state.sound_enabled = True

# ==================== 1. ACCESS CONTROL (LOGIN / REGISTRATION) ====================
if not st.session_state.logged_in:
    col_l, col_center, col_r = st.columns([1, 1.3, 1])
    with col_center:
        st.markdown("<div style='text-align: center; margin-top: 35px; margin-bottom: 25px;'><h1 style='color: #38bdf8; margin:0;'>⚡ DELTA ANALYSIS</h1><p style='color: #64748b;'>Private Membership FNO Spread Terminal</p></div>", unsafe_allow_html=True)
        
        tab_login, tab_reg, tab_rst = st.tabs(["🔐 Sign In", "📝 Request Access", "🔄 Forgot Password"])
        
        with tab_login:
            u_name = st.text_input("Username / Mobile Number", key="l_name")
            u_pass = st.text_input("Password", type="password", key="l_pass")
            
            if st.button("Enter Terminal", use_container_width=True, type="primary"):
                if not u_name or not u_pass:
                    st.warning("कृपया दोनों फ़ील्ड भरें।")
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
                            st.warning("⏳ आपका अकाउंट अभी पेंडिंग है! एडमिन अप्रूवल का इंतज़ार करें।")
                        elif not u.get("valid_until") or datetime.strptime(u["valid_until"], "%Y-%m-%d").date() < date.today():
                            st.error(f"⛔ आपका एक्सेस समाप्त हो चुका है ({u.get('valid_until')})! एडमिन से संपर्क करें।")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.username = u["username"]
                            st.session_state.is_admin = False
                            st.session_state.valid_until = u.get("valid_until")
                            log_activity(u["username"], "Trader Logged In")
                            st.rerun()

        with tab_reg:
            r_user = st.text_input("New Username", key="r_user")
            r_phone = st.text_input("Mobile Number", key="r_phone")
            r_pass = st.text_input("Password", type="password", key="r_pass")
            if st.button("Send Access Request", use_container_width=True):
                if r_user and r_phone and r_pass:
                    res = register_user(r_user, r_pass, r_phone)
                    if res and res.status_code in [200, 201]:
                        st.success("✅ रिक्वेस्ट भेज दी गई है! एडमिन अप्रूवल के बाद लॉगिन करें।")
                    else:
                        st.error("यूज़रनेम पहले से मौजूद है!")
                else:
                    st.warning("सभी फ़ील्ड भरें।")

        with tab_rst:
            f_user = st.text_input("Username", key="f_user")
            f_phone = st.text_input("Registered Mobile", key="f_phone")
            f_pass = st.text_input("New Password", type="password", key="f_pass")
            if st.button("Reset Password", use_container_width=True):
                if f_user and f_phone and f_pass:
                    u_d = get_user(f_user)
                    if u_d and str(u_d[0].get("phone")).strip() == str(f_phone).strip():
                        update_user_full(u_d[0]["id"], u_d[0]["username"], u_d[0]["phone"], f_pass, u_d[0].get("valid_until"), u_d[0].get("is_approved", False))
                        st.success("पासवर्ड बदल गया! अब लॉगिन करें।")
                    else:
                        st.error("डिटेल्स मैच नहीं हुईं!")

# ==================== 2. ADMIN CONTROL CENTER ====================
elif st.session_state.is_admin:
    st.sidebar.markdown(f"### 👑 Superadmin: `{st.session_state.username}`")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🛠️ Admin Control Center — Traders Validity Limiter")
    
    a_tab1, a_tab2 = st.tabs(["👥 User Approvals & Expiry Manager", "📜 Live Audit Logs"])

    with a_tab1:
        st.subheader("Manage Traders Access")
        try:
            r = requests.get(f"{SUPABASE_URL}/rest/v1/users?order=created_at.desc", headers=HEADERS, timeout=8)
            if r.status_code == 200:
                users = r.json()
                for u in users:
                    if u["username"].lower() in ["pratham1785", "admin"]:
                        continue

                    is_app = u.get("is_approved", False)
                    v_date = u.get("valid_until")
                    days_left = 0
                    if v_date:
                        try:
                            rem = (datetime.strptime(v_date, "%Y-%m-%d").date() - date.today()).days
                            days_left = max(0, rem)
                        except:
                            pass
                    
                    badge = f"🟢 Active ({days_left} Days Left)" if is_app and days_left > 0 else "⏳ Pending / Expired"

                    with st.expander(f"👤 {u['username']} | 📞 {u.get('phone')} | Status: {badge}"):
                        c1, c2, c3 = st.columns([1.5, 1.5, 1])
                        with c1:
                            set_days = st.number_input("Grant Access (Days):", min_value=1, max_value=365, value=30, key=f"days_{u['id']}")
                            if st.button(f"✅ Approve {set_days} Days", key=f"app_btn_{u['id']}", use_container_width=True):
                                update_user_access(u['id'], True, set_days)
                                st.success(f"एक्सेस {set_days} दिनों के लिए एक्टिव!")
                                st.rerun()

                        with c2:
                            new_pass_edit = st.text_input("Reset Password", key=f"np_{u['id']}")
                            if st.button("Update Pass", key=f"snp_{u['id']}", use_container_width=True):
                                if new_pass_edit:
                                    update_user_full(u['id'], u['username'], u['phone'], new_pass_edit, u.get('valid_until'), u.get('is_approved', False))
                                    st.success("पासवर्ड अपडेटेड!")
                                    st.rerun()

                        with c3:
                            if st.button("⛔ Block", key=f"blk_{u['id']}", use_container_width=True):
                                update_user_access(u['id'], False, 0)
                                st.rerun()
                            if st.button("🗑️ Delete", key=f"del_{u['id']}", use_container_width=True):
                                delete_user(u['id'])
                                st.rerun()
        except Exception as e:
            st.error(f"एरर: {e}")

    with a_tab2:
        res_l = requests.get(f"{SUPABASE_URL}/rest/v1/activity_logs?order=logged_at.desc&limit=50", headers=HEADERS, timeout=8)
        if res_l.status_code == 200 and res_l.json():
            st.dataframe(pd.DataFrame(res_l.json()), use_container_width=True)

# ==================== 3. TRADER SCREEN: SPREAD SCANNER & ENGINE ====================
else:
    # Auto-Logout Check
    if st.session_state.valid_until:
        exp_date_obj = datetime.strptime(st.session_state.valid_until, "%Y-%m-%d").date()
        if exp_date_obj < date.today():
            st.session_state.logged_in = False
            st.error("⛔ आपका एक्सेस समाप्त हो चुका है!")
            st.rerun()

    # Sidebar
    with st.sidebar:
        st.markdown("<h2 style='color:#38bdf8; margin-bottom: 0px;'>⚡ DELTA ANALYSIS</h2>", unsafe_allow_html=True)
        st.caption("AI FNO SPREAD SCANNER")
        st.write("---")
        rem_days = (datetime.strptime(st.session_state.valid_until, "%Y-%m-%d").date() - date.today()).days if st.session_state.valid_until else 0
        st.markdown(f"👤 Trader: **{st.session_state.username}**")
        st.markdown(f"⏳ Plan Validity: **{rem_days} Days Left**")
        st.markdown(f"📅 Expiry Date: `{st.session_state.valid_until}`")
        st.write("---")

        st.session_state.sound_enabled = st.checkbox("🔔 Audio Alerts", value=st.session_state.sound_enabled)
        
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # Header Bar
    t_col1, t_col2 = st.columns([3, 1])
    with t_col1:
        st.markdown("### 🔍 Delta Analysis — Advanced Multi-Expiry Spread Scanner")
    with t_col2:
        st.markdown("<div style='text-align:right; margin-top: 10px;'><span style='color: #22c55e;'>● ENGINE READY</span> | <span style='color:#94a3b8;'>NSE F&O LIVE</span></div>", unsafe_allow_html=True)

    # --- TOP SCANNER PARAMETERS (SCREENSHOT REPLICA) ---
    st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>⚙️ Scanner Filter Parameters</div>", unsafe_allow_html=True)
    
    r1_c1, r1_c2, r1_c3, r1_c4, r1_c5, r1_c6, r1_c7 = st.columns(7)
    with r1_c1:
        f_stock = st.selectbox("STOCK", ["ALL STOCKS", "NIFTY", "BANKNIFTY", "HDFCBANK", "RELIANCE", "ICICIBANK", "TCS", "INFY", "SBIN"])
    with r1_c2:
        f_expiry = st.selectbox("EXPIRY DATE", ["CURRENT MONTH", "NEXT MONTH", "FAR MONTH", "WEEKLY"])
    with r1_c3:
        f_ref = st.selectbox("REFERENCE", ["Future LTP", "Spot Index", "VWAP", "Synthetic Future"])
    with r1_c4:
        f_type = st.selectbox("TYPE", ["Both (CE & PE)", "Call Spread (CE)", "Put Spread (PE)", "Calendar Futures"])
    with r1_c5:
        f_price_gap = st.selectbox("PRICE GAP", ["OFF", "1 pt", "2 pts", "3 pts", "5 pts"])
    with r1_c6:
        f_delta = st.selectbox("DELTA FILTER", ["ON (20-30 Delta)", "ON (30-40 Delta)", "ON (40-50 Delta)", "OFF"])
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
        f_limit_val = st.number_input("LIMIT VALUE ₹", min_value=0, max_value=100000, value=1000, step=100)
    with r2_c6:
        f_direction = st.selectbox("DIRECTION", ["Buy → Sell", "Sell → Buy", "Arbitrage Spread"])
    st.markdown("</div>", unsafe_allow_html=True)

    # --- CUSTOM SPREAD ALERT (SPECIFIC COMPANY / STRIKE) ---
    st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>🎯 Custom Spread Alert — Specific Company / Strike</div>", unsafe_allow_html=True)
    
    c_col1, c_col2, c_col3, c_col4, c_col5, c_col6 = st.columns(6)
    with c_col1:
        a_company = st.selectbox("COMPANY", ["HDFCBANK", "NIFTY", "BANKNIFTY", "RELIANCE", "TCS"])
    with c_col2:
        a_option = st.selectbox("OPTION", ["CE", "PE", "FUT"])
    with c_col3:
        a_buy = st.number_input("BUY STRIKE", value=1640, step=10)
    with c_col4:
        a_sell = st.number_input("SELL STRIKE", value=1680, step=10)
    with c_col5:
        a_ratio = st.selectbox("RATIO BUY:SELL", ["1 : 1", "1 : 2", "3 : 10"])
    with c_col6:
        a_debit = st.number_input("TARGET DEBIT ₹", value=12.50, step=0.5)

    ca_col1, ca_col2 = st.columns(2)
    with ca_col1:
        alert_btn = st.button("🔔 START CUSTOM ALERT", use_container_width=True)
    with ca_col2:
        check_now_btn = st.button("🔎 CHECK STRIKE PAIR NOW", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- ACTION BUTTONS ---
    st.write("")
    b1, b2, b3, b4, b5 = st.columns([1.5, 1.5, 1.5, 1, 1])
    with b1:
        st.markdown('<div class="scan-btn">', unsafe_allow_html=True)
        scan_now_clicked = st.button("🚀 SCAN NOW", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with b2:
        if st.button("⚡ START AUTO SCAN", use_container_width=True):
            st.session_state.auto_scan = True
            st.rerun()
    with b3:
        if st.button("🔔 NOTIFICATIONS ON", use_container_width=True):
            st.session_state.sound_enabled = True
            st.success("Notifications Enabled!")
    with b4:
        st.markdown('<div class="stop-btn">', unsafe_allow_html=True)
        if st.button("⏹ STOP", use_container_width=True):
            st.session_state.auto_scan = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with b5:
        if st.button("🔄 RESET", use_container_width=True):
            st.session_state.auto_scan = False
            st.rerun()

    st.write("---")

    # --- DYNAMIC CALCULATION & FILTERING ENGINE ---
    # Master underlying mock base for calculations
    stock_profiles = {
        "NIFTY": {"spot": 25350, "step": 50, "lot": 75, "iv": 13.2},
        "BANKNIFTY": {"spot": 53600, "step": 100, "lot": 35, "iv": 16.5},
        "HDFCBANK": {"spot": 1660, "step": 10, "lot": 550, "iv": 18.4},
        "RELIANCE": {"spot": 1395, "step": 10, "lot": 250, "iv": 21.0},
        "ICICIBANK": {"spot": 1280, "step": 10, "lot": 700, "iv": 19.5},
        "TCS": {"spot": 4250, "step": 50, "lot": 175, "iv": 15.0},
        "INFY": {"spot": 1940, "step": 20, "lot": 400, "iv": 18.0},
        "SBIN": {"spot": 820, "step": 5, "lot": 750, "iv": 22.5}
    }

    selected_list = list(stock_profiles.keys()) if f_stock == "ALL STOCKS" else [f_stock]
    all_generated_spreads = []
    target_hit = False

    # Extract target delta
    d_min, d_max = 0.
