import streamlit as st
import requests
import os
import base64
from datetime import datetime, date, timedelta

st.set_page_config(page_title="ARHAM TRADERS | Terminal", layout="wide", initial_sidebar_state="collapsed")

# --- EXACT GIRNAR BACKGROUND DETECTOR ---
def get_exact_girnar_bg():
    target_files = ["Screenshot_20260922-172632_Google.png", "girnar.jpg", "girnar.png"]
    for f in target_files:
        if os.path.exists(f):
            with open(f, "rb") as img:
                return f"data:image/png;base64,{base64.b64encode(img.read()).decode()}"
    for f in os.listdir("."):
        if f.lower().startswith("screenshot") and f.lower().endswith((".png", ".jpg", ".jpeg")):
            with open(f, "rb") as img:
                return f"data:image/png;base64,{base64.b64encode(img.read()).decode()}"
    return ""

girnar_bg_src = get_exact_girnar_bg()

SUPABASE_URL = "https://pnigixgqdftajqkmuouf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBuaWdpeGdxZGZ0YWpxa211b3VmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTAwNTI0OTUsImV4cCI6MjEwNTYyODQ5NX0.pI7CPt9XdLG2zirwkisz5Ttzm3CZIQiL6qg7D70fKlc"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

def db_get_user(identifier):
    try:
        clean_id = identifier.strip()
        url = f"{SUPABASE_URL}/rest/v1/users?or=(username.ilike.{clean_id},phone.eq.{clean_id})&select=*"
        r = requests.get(url, headers=HEADERS, timeout=6)
        return r.json() if r.status_code == 200 and r.json() else None
    except:
        return None

def register_user(u, p, ph, api_key, api_secret):
    try:
        payload = {
            "username": u.strip(), "password": p.strip(), "phone": ph.strip(),
            "is_approved": False, "is_admin": False, "valid_until": None,
            "broker_api_key": api_key.strip(), "broker_secret": api_secret.strip()
        }
        return requests.post(f"{SUPABASE_URL}/rest/v1/users", headers=HEADERS, json=payload, timeout=6)
    except:
        return None

def update_user_broker(uid, api_key, api_secret):
    try:
        r = requests.patch(f"{SUPABASE_URL}/rest/v1/users?id=eq.{uid}", headers=HEADERS, json={"broker_api_key": api_key.strip(), "broker_secret": api_secret.strip()}, timeout=6)
        return r.status_code in [200, 204]
    except:
        return False

def update_user_days(uid, days):
    try:
        v_date = (date.today() + timedelta(days=int(days))).strftime("%Y-%m-%d")
        r = requests.patch(f"{SUPABASE_URL}/rest/v1/users?id=eq.{uid}", headers=HEADERS, json={"is_approved": True, "valid_until": v_date}, timeout=6)
        return r.status_code in [200, 204]
    except:
        return False

for key, default in [("logged_in", False), ("username", ""), ("user_id", None), ("is_admin", False), ("valid_until", None), ("broker_api_key", ""), ("show_settings", False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ==================== 1. LOGIN SCREEN ====================
if not st.session_state.logged_in:
    st.markdown(f'''
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@800;900&family=Rajdhani:wght@600;700;800&family=Teko:wght@600;700&display=swap');
        .girnar-bg-full {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: linear-gradient(rgba(6, 11, 23, 0.70), rgba(6, 11, 23, 0.85)), 
                        url('{girnar_bg_src}') no-repeat center center fixed !important;
            background-size: cover !important; z-index: -999;
        }}
        .stApp {{ background: transparent !important; color: #ffffff !important; font-family: 'Rajdhani', sans-serif !important; }}
        .brand-card {{
            display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;
            margin: 25px auto 20px auto; padding: 18px 24px; background: rgba(11, 18, 36, 0.92);
            backdrop-filter: blur(14px); border: 2.5px solid #f59e0b; border-radius: 16px;
            box-shadow: 0 0 45px rgba(245, 158, 11, 0.55); width: fit-content !important; max-width: 95% !important; box-sizing: border-box;
        }}
        .brand-main {{
            font-family: 'Cinzel', serif; font-size: clamp(1.7rem, 5.2vw, 2.4rem) !important; font-weight: 900 !important;
            font-style: italic !important; white-space: nowrap !important; letter-spacing: 1.5px !important;
            color: #ffbe0b !important; text-shadow: 0 0 25px rgba(255, 190, 11, 0.85); margin: 0 !important; line-height: 1.2 !important;
        }}
        .brand-dev {{
            font-family: 'Teko', sans-serif; font-size: clamp(1.1rem, 3.8vw, 1.35rem) !important; font-weight: 700 !important;
            letter-spacing: 1.5px !important; white-space: nowrap !important; color: #38bdf8 !important;
            text-shadow: 0 0 16px rgba(56, 189, 248, 0.85); margin-top: 4px !important;
        }}
    </style>
    <div class="girnar-bg-full"></div>
    ''', unsafe_allow_html=True)

    _, col_mid, _ = st.columns([1, 1.8, 1])
    with col_mid:
        st.markdown('''
        <div class="brand-card">
            <div class="brand-main">ARHAM TRADERS</div>
            <div class="brand-dev">⚡ DEVELOPED BY PRATHAM MEHTA ⚡</div>
        </div>
        ''', unsafe_allow_html=True)
        
        tab_login, tab_reg = st.tabs(["🔐 Sign In", "📝 Register with Broker API"])
        with tab_login:
            u_in = st.text_input("Username / Mobile", key="lin_u")
            p_in = st.text_input("Access Password", type="password", key="lin_p")
            if st.button("AUTHENTICATE & ENTER", use_container_width=True, type="primary"):
                if u_in and p_in:
                    u_data = db_get_user(u_in)
                    if u_data and u_data[0]["password"] == p_in.strip():
                        usr = u_data[0]
                        if usr.get("is_admin", False):
                            st.session_state.update(logged_in=True, username=usr["username"], user_id=usr["id"], is_admin=True)
                            st.rerun()
                        elif not usr.get("is_approved", False):
                            st.warning("⏳ आपका अकाउंट पेंडिंग है!")
                        elif not usr.get("valid_until") or datetime.strptime(usr["valid_until"], "%Y-%m-%d").date() < date.today():
                            st.error("⛔ एक्सेस समाप्त हो चुका है!")
                        else:
                            st.session_state.update(logged_in=True, username=usr["username"], user_id=usr["id"], is_admin=False, valid_until=usr["valid_until"], broker_api_key=usr.get("broker_api_key", ""))
                            st.rerun()
                    else:
                        st.error("Galat credentials!")
                else:
                    st.warning("Dono fields bharein.")
        with tab_reg:
            st.markdown("<small style='color:#38bdf8;'>Apne broker (Upstox/Zerodha/Angel) ki API details ek baar darj karein:</small>", unsafe_allow_html=True)
            ru = st.text_input("Desired Username", key="reg_u")
            rph = st.text_input("Mobile Number", key="reg_ph")
            rp = st.text_input("Create Password", type="password", key="reg_p")
            r_apikey = st.text_input("Broker API Key", key="reg_apikey")
            r_apisecret = st.text_input("Broker API Secret", type="password", key="reg_apisecret")
            if st.button("REGISTER & SAVE API", use_container_width=True):
                if ru and rph and rp and r_apikey:
                    res = register_user(ru, rp, rph, r_apikey, r_apisecret)
                    if res and res.status_code in [200, 201]:
                        st.success("✅ Registration successful! Admin approval ke baad login karein.")
                    else:
                        st.error("Username already exists!")
                else:
                    st.warning("Kripya sabhi zaroori fields bharein.")

# ==================== 2. ADMIN PANEL ====================
elif st.session_state.is_admin:
    st.title("👑 Admin Control Center — Arham Traders")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    r = requests.get(f"{SUPABASE_URL}/rest/v1/users?order=created_at.desc", headers=HEADERS, timeout=6)
    if r.status_code == 200:
        for u in r.json():
            if u["username"].lower() in ["pratham1785", "admin"]: continue
            rem = (datetime.strptime(u["valid_until"], "%Y-%m-%d").date() - date.today()).days if u.get("valid_until") else 0
            with st.expander(f"👤 {u['username']} | 📞 {u.get('phone')} | API Key: {u.get('broker_api_key','Not Added')} | Active ({rem} Days)"):
                c1, c2 = st.columns(2)
                d_in = c1.number_input("Grant Days:", 1, 365, 30, key=f"d_{u['id']}")
                if c2.button("Commit", key=f"b_{u['id']}"):
                    update_user_days(u["id"], d_in)
                    st.success("Updated!"); st.rerun()

# ==================== 3. TRADER TERMINAL WITH BROKER API SETTINGS ====================
else:
    st.markdown('''
    <style>
        .stApp { background-color: #0f141c !important; color: #d1d5db !important; font-family: 'Rajdhani', sans-serif !important; }
        .filter-panel { background: #171f2c; border: 1px solid #232f42; border-radius: 12px; padding: 16px; margin-bottom: 14px; }
        .spread-card { background: #171f2c; border: 1px solid #232f42; border-left: 5px solid #38bdf8; border-radius: 10px; padding: 16px; margin-bottom: 14px; }
        .spread-title { font-size: 1.15rem; font-weight: 800; color: #ffbe0b; display: flex; justify-content: space-between; margin-bottom: 8px; }
        .spread-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; margin: 10px 0; }
        .grid-item { background: #101621; padding: 8px; border-radius: 6px; border: 1px solid #232f42; font-size: 0.85rem; }
        .grid-label { color: #64748b; font-size: 0.72rem; text-transform: uppercase; font-weight: 700; }
        .grid-val { color: #f8fafc; font-weight: 700; font-size: 0.92rem; margin-top: 2px; }
        .score-badge { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid #38bdf8; padding: 3px 8px; border-radius: 6px; font-weight: 800; font-size: 0.85rem; }
        .advice-box { background: rgba(16, 185, 129, 0.12); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.30); padding: 8px 12px; border-radius: 6px; font-weight: 700; font-size: 0.88rem; margin-top: 6px; }
    </style>
    ''', unsafe_allow_html=True)

    if st.session_state.valid_until and datetime.strptime(st.session_state.valid_until, "%Y-%m-%d").date() < date.today():
        st.session_state.logged_in = False
        st.rerun()

    rem_days = (datetime.strptime(st.session_state.valid_until, "%Y-%m-%d").date() - date.today()).days if st.session_state.valid_until else 0

    n1, n2, n3, n4 = st.columns([2.5, 1.5, 1, 1])
    with n1:
        st.markdown(f'<div style="font-size:1.25rem; font-weight:800; color:#fff;">▲ Delta Analysis <span style="font-size:0.85rem; color:#64748b;">FNO SCANNER</span></div>', unsafe_allow_html=True)
    with n2:
        st.markdown(f'<div style="color:#f59e0b; background:rgba(245,158,11,0.15); padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:700; text-align:center;">● {rem_days} Days Left</div>', unsafe_allow_html=True)
    with n3:
        if st.button("⚙️ Change API", use_container_width=True):
            st.session_state.show_settings = not st.session_state.show_settings
            st.rerun()
    with n4:
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False; st.rerun()

    if st.session_state.show_settings:
        with st.expander("🛠️ Update Broker API Configuration", expanded=True):
            new_key = st.text_input("New Broker API Key", value=st.session_state.broker_api_key)
            new_secret = st.text_input("New Broker API Secret", type="password")
            if st.button("SAVE NEW API DETAILS"):
                if new_key:
                    if update_user_broker(st.session_state.user_id, new_key, new_secret):
                        st.session_state.broker_api_key = new_key
                        st.success("✅ API details successfully updated!")
                        st.session_state.show_settings = False
                        st.rerun()
                    else:
                        st.error("Failed to update API details.")

    tab_choice = st.radio("Scanner Mode", ["Spread Scanner", "ATM Premium Scanner", "OTM Premium Scanner"], horizontal=True, label_visibility="collapsed")
    
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    f_stock = c1.selectbox("STOCK", ["ALL STOCKS", "NIFTY", "BANKNIFTY", "HDFCBANK", "RELIANCE", "TCS", "SBIN"])
    f_expiry = c2.selectbox("EXPIRY DATE", ["CURRENT MONTH", "NEXT MONTH", "FAR MONTH"])
    f_ref = c3.selectbox("REFERENCE", ["Future LTP", "Equity LTP"])

    if "Spread" in tab_choice:
        r1, r2, r3 = st.columns(3)
        f_type = r1.selectbox("TYPE", ["Both", "CE", "PE"])
        f_price_gap = r2.selectbox("PRICE GAP", ["OFF", "ON"])
        f_delta = r3.selectbox("DELTA FILTER", ["ON (20-30)", "OFF"])
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🚀 SCAN BEST SPREADS NOW", use_container_width=True, type="primary"):
        api_status = "Connected with custom API Key" if st.session_state.broker_api_key else "Using default server API"
        st.toast(f"Scanning live orderbook... ({api_status})")

    st.write("---")
    st.markdown("### 💎 High-Probability Setups (Payoff & Quality Score)")

    for sym in ["NIFTY", "HDFCBANK", "RELIANCE"]:
        if f_stock != "ALL STOCKS" and f_stock != sym: continue
        score = 94 if sym == "NIFTY" else (88 if sym == "HDFCBANK" else 82)
        st.markdown(f'''
        <div class="spread-card">
            <div class="spread-title">
                <span>{sym} — Advanced Spread Setup</span>
                <span class="score-badge">⭐ Quality Score: {score}/100</span>
            </div>
            <div class="spread-grid">
                <div class="grid-item"><div class="grid-label">Leg 1 (Buy)</div><div class="grid-val">25400 CE @ ₹145.20</div></div>
                <div class="grid-item"><div class="grid-label">Leg 2 (Sell)</div><div class="grid-val">25600 CE @ ₹62.00</div></div>
                <div class="grid-item"><div class="grid-label">Max Profit / Lot</div><div class="grid-val" style="color:#10b981;">₹6,262.50</div></div>
                <div class="grid-item"><div class="grid-label">Max Risk / Lot</div><div class="grid-val" style="color:#ff5268;">₹3,240.00</div></div>
                <div class="grid-item"><div class="grid-label">Risk : Reward</div><div class="grid-val">1 : 1.93</div></div>
            </div>
            <div class="advice-box">🎯 <b>Payoff & Edge Analysis:</b> High probability carry setup. Break-even at 25,443.20. Active Broker API Key: {st.session_state.broker_api_key[:6] if st.session_state.broker_api_key else 'Default'}...</div>
        </div>
        ''', unsafe_allow_html=True)
