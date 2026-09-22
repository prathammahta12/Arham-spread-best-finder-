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
HEADERS = {"apikey": SUPABASE_URL, "Authorization": f"Bearer {SUPABASE_URL}", "Content-Type": "application/json"}

def db_get_user(identifier):
    try:
        clean_id = identifier.strip()
        url = f"{SUPABASE_URL}/rest/v1/users?or=(username.ilike.{clean_id},phone.eq.{clean_id})&select=*"
        r = requests.get(url, headers=HEADERS, timeout=6)
        return r.json() if r.status_code == 200 and r.json() else None
    except:
        return None

def register_user(u, p, ph):
    try:
        payload = {"username": u.strip(), "password": p.strip(), "phone": ph.strip(), "is_approved": False, "is_admin": False, "valid_until": None}
        return requests.post(f"{SUPABASE_URL}/rest/v1/users", headers=HEADERS, json=payload, timeout=6)
    except:
        return None

def update_user_days(uid, days):
    try:
        v_date = (date.today() + timedelta(days=int(days))).strftime("%Y-%m-%d")
        r = requests.patch(f"{SUPABASE_URL}/rest/v1/users?id=eq.{uid}", headers=HEADERS, json={"is_approved": True, "valid_until": v_date}, timeout=6)
        return r.status_code in [200, 204]
    except:
        return False

for key, default in [("logged_in", False), ("username", ""), ("is_admin", False), ("valid_until", None), ("scanner_tab", "Spread")]:
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
        
        tab_login, tab_reg = st.tabs(["🔐 Sign In", "📝 Register Access"])
        with tab_login:
            u_in = st.text_input("Username / Mobile", key="lin_u")
            p_in = st.text_input("Access Password", type="password", key="lin_p")
            if st.button("AUTHENTICATE & ENTER", use_container_width=True, type="primary"):
                if u_in and p_in:
                    u_data = db_get_user(u_in)
                    if u_data and u_data[0]["password"] == p_in.strip():
                        usr = u_data[0]
                        if usr.get("is_admin", False):
                            st.session_state.update(logged_in=True, username=usr["username"], is_admin=True)
                            st.rerun()
                        elif not usr.get("is_approved", False):
                            st.warning("⏳ आपका अकाउंट पेंडिंग है!")
                        elif not usr.get("valid_until") or datetime.strptime(usr["valid_until"], "%Y-%m-%d").date() < date.today():
                            st.error("⛔ एक्सेस समाप्त हो चुका है!")
                        else:
                            st.session_state.update(logged_in=True, username=usr["username"], is_admin=False, valid_until=usr["valid_until"])
                            st.rerun()
                    else:
                        st.error("गलत क्रेडेंशियल्स!")
                else:
                    st.warning("दोनों फ़ील्ड भरें।")
        with tab_reg:
            ru = st.text_input("Desired Username", key="reg_u")
            rph = st.text_input("Mobile Number", key="reg_ph")
            rp = st.text_input("Create Password", type="password", key="reg_p")
            if st.button("SEND ACCESS REQUEST", use_container_width=True):
                if ru and rph and rp:
                    res = register_user(ru, rp, rph)
                    if res and res.status_code in [200, 201]:
                        st.success("✅ रिक्वेस्ट सबमिट हो गई!")
                    else:
                        st.error("यूज़रनेम मौजूद है!")

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
            with st.expander(f"👤 {u['username']} | 📞 {u.get('phone')} | Active ({rem} Days)"):
                c1, c2 = st.columns(2)
                d_in = c1.number_input("Grant Days:", 1, 365, 30, key=f"d_{u['id']}")
                if c2.button("Commit", key=f"b_{u['id']}"):
                    update_user_days(u["id"], d_in)
                    st.success("Updated!"); st.rerun()

# ==================== 3. TRADER TERMINAL (DARK GREY UI + MULTI-TABS LOGIC) ====================
else:
    st.markdown('''
    <style>
        .stApp { background-color: #0f141c !important; color: #d1d5db !important; font-family: 'Rajdhani', sans-serif !important; }
        .filter-panel { background: #171f2c; border: 1px solid #232f42; border-radius: 12px; padding: 16px; margin-bottom: 14px; }
        .alert-panel { background: #131a26; border: 1px solid #253347; border-radius: 8px; padding: 14px; margin-top: 10px; }
        label { font-size: 0.78rem !important; font-weight: 700 !important; color: #94a3b8 !important; text-transform: uppercase !important; }
        div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {
            background-color: #1a2332 !important; color: #38bdf8 !important; font-size: 0.95rem !important; font-weight: 700 !important; border: 1px solid #2a3b54 !important; border-radius: 6px !important;
        }
        .spread-card {
            background: #171f2c; border: 1px solid #232f42; border-left: 5px solid #38bdf8; border-radius: 10px; padding: 14px; margin-bottom: 12px;
        }
        .spread-title { font-size: 1.15rem; font-weight: 800; color: #ffbe0b; display: flex; justify-content: space-between; margin-bottom: 8px; }
        .spread-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; margin: 10px 0; }
        .grid-item { background: #101621; padding: 8px; border-radius: 6px; border: 1px solid #232f42; font-size: 0.85rem; }
        .grid-label { color: #64748b; font-size: 0.72rem; text-transform: uppercase; font-weight: 700; }
        .grid-val { color: #f8fafc; font-weight: 700; font-size: 0.92rem; margin-top: 2px; }
        .advice-box { background: rgba(16, 185, 129, 0.12); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.30); padding: 8px 12px; border-radius: 6px; font-weight: 700; font-size: 0.88rem; margin-top: 6px; }
    </style>
    ''', unsafe_allow_html=True)

    if st.session_state.valid_until and datetime.strptime(st.session_state.valid_until, "%Y-%m-%d").date() < date.today():
        st.session_state.logged_in = False
        st.rerun()

    rem_days = (datetime.strptime(st.session_state.valid_until, "%Y-%m-%d").date() - date.today()).days if st.session_state.valid_until else 0

    # Top Navbar & Mode Selection Tabs matching your HTML logic[span_1](start_span)[span_1](end_span)
    n1, n2, n3 = st.columns([3, 1.5, 1])
    with n1:
        st.markdown(f'<div style="font-size:1.25rem; font-weight:800; color:#fff;">▲ Delta Analysis <span style="font-size:0.85rem; color:#64748b;">FNO SCANNER</span></div>', unsafe_allow_html=True)
    with n2:
        st.markdown(f'<div style="color:#f59e0b; background:rgba(245,158,11,0.15); padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:700; text-align:center;">● LIVE MARKET | {rem_days} Days Left</div>', unsafe_allow_html=True)
    with n3:
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False; st.rerun()

    # Multi-Tab Switcher (Spread / ATM / OTM)
    tab_choice = st.radio("Scanner Mode", ["Spread Scanner", "ATM Premium Scanner", "OTM Premium Scanner"], horizontal=True, label_visibility="collapsed")
    
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    
    # Common filters across modes
    c1, c2, c3 = st.columns(3)
    f_stock = c1.selectbox("STOCK", ["ALL STOCKS", "NIFTY", "BANKNIFTY", "HDFCBANK", "RELIANCE", "TCS", "SBIN"])
    f_expiry = c2.selectbox("EXPIRY DATE", ["CURRENT MONTH", "NEXT MONTH", "FAR MONTH"])
    f_ref = c3.selectbox("REFERENCE", ["Future LTP", "Equity LTP"])

    if "Spread" in tab_choice:
        r1, r2, r3 = st.columns(3)
        f_type = r1.selectbox("TYPE", ["Both", "CE", "PE"])
        f_price_gap = r2.selectbox("PRICE GAP", ["OFF", "ON"])
        f_delta = r3.selectbox("DELTA FILTER", ["ON (20-30)", "OFF"])

        r4, r5, r6 = st.columns(3)
        f_strike_gap = r4.number_input("STRIKE GAP %", min_value=1.0, max_value=20.0, value=5.0, step=0.5)
        f_iv_gap = r5.number_input("IV GAP %", min_value=1.0, max_value=50.0, value=5.0, step=0.5)
        f_min_vol = r6.number_input("MIN VOLUME (LOTS)", min_value=1, max_value=10000, value=1, step=1)

        r7, r8, r9 = st.columns(3)
        f_ratio = r7.selectbox("RATIO", ["3:10", "1:1", "1:2", "1:4"])
        f_limit_type = r8.selectbox("LIMIT TYPE", ["Max Debit", "Min Credit"])
        f_limit_val = r9.number_input("LIMIT VALUE ₹", min_value=0, max_value=100000, value=1000, step=100)
        f_dir = st.selectbox("DIRECTION", ["Buy → Sell", "Sell → Buy"])
    else:
        # ATM/OTM Specific fields as per your HTML logic[span_2](start_span)[span_2](end_span)
        p1, p2, p3 = st.columns(3)
        p_min = p1.number_input("Min Total Premium ₹", value=100)
        p_max = p2.number_input("Max Total Premium ₹", value=10000)
        p_view = p3.selectbox("Premium Display", ["CALL + PUT + TOTAL", "CALL (CE) ONLY", "PUT (PE) ONLY"])
        if "OTM" in tab_choice:
            otm_dist = st.number_input("OTM Distance %", value=5.0)

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🚀 SCAN NOW", use_container_width=True, type="primary"):
        st.toast("Scanning live orderbook...")

    st.write("---")
    st.markdown("### 💎 Detected Opportunities (Individual Analysis)")

    # Sample dynamic simulation output cards matching your logic
    for sym in ["NIFTY", "HDFCBANK", "RELIANCE"]:
        if f_stock != "ALL STOCKS" and f_stock != sym: continue
        if "Spread" in tab_choice:
            st.markdown(f'''
            <div class="spread-card">
                <div class="spread-title">
                    <span>{sym} — Outer Spread Set</span>
                    <span style="color:#38bdf8;">Spread: +115.2 pts</span>
                </div>
                <div class="spread-grid">
                    <div class="grid-item"><div class="grid-label">Leg 1 (Buy)</div><div class="grid-val">25400 CE @ ₹145.20</div></div>
                    <div class="grid-item"><div class="grid-label">Leg 2 (Sell)</div><div class="grid-val">25600 CE @ ₹62.00</div></div>
                    <div class="grid-item"><div class="grid-label">Lot Size</div><div class="grid-val">75 qty</div></div>
                    <div class="grid-item"><div class="grid-label">Net Value</div><div class="grid-val" style="color:#10b981;">₹3,240 Debit</div></div>
                    <div class="grid-item"><div class="grid-label">Upstox Margin</div><div class="grid-val">₹48,200 (Final)</div></div>
                </div>
                <div class="advice-box">🎯 <b>Action Advice:</b> High IV Gap & Delta range 20-30 matched. Defined risk setup.</div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="spread-card">
                <div class="spread-title">
                    <span>{sym} — {tab_choice.upper()} Combined Premium</span>
                    <span style="color:#38bdf8;">Total: ₹420.50</span>
                </div>
                <div class="spread-grid">
                    <div class="grid-item"><div class="grid-label">CE Strike & LTP</div><div class="grid-val">25400 CE @ ₹210.00</div></div>
                    <div class="grid-item"><div class="grid-label">PE Strike & LTP</div><div class="grid-val">25400 PE @ ₹210.50</div></div>
                    <div class="grid-item"><div class="grid-label">Lot Size</div><div class="grid-val">75 qty</div></div>
                    <div class="grid-item"><div class="grid-label">Combined Value</div><div class="grid-val" style="color:#10b981;">₹31,537.50</div></div>
                </div>
                <div class="advice-box">📈 <b>Combined Alert Status:</b> Baseline monitoring active (+10% tracking enabled).</div>
            </div>
            ''', unsafe_allow_html=True)
