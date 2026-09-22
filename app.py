import streamlit as st
import requests
import os
import base64
from datetime import datetime, date, timedelta

st.set_page_config(page_title="ARHAM TRADERS", layout="wide", initial_sidebar_state="collapsed")

# --- EXACT GIRNAR BACKGROUND DETECTOR ---
def get_exact_girnar_bg():
    target_files = [
        "Screenshot_20260922-172632_Google.png",
        "girnar.jpg",
        "girnar.png"
    ]
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

st.markdown(f'''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@800;900&family=Rajdhani:wght@600;700;800&family=Teko:wght@600;700&display=swap');
    
    /* Fullscreen High-Resolution Girnar Background */
    .girnar-bg-full {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(rgba(6, 11, 23, 0.70), rgba(6, 11, 23, 0.85)), 
                    url('{girnar_bg_src}') no-repeat center center fixed !important;
        background-size: cover !important;
        z-index: -999;
    }}

    .stApp {{
        background: transparent !important;
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif !important;
    }}
    
    /* Big Wide Luxury Brand Card */
    .brand-card {{
        text-align: center;
        margin: 25px auto 22px auto;
        padding: 22px 28px;
        background: rgba(11, 18, 36, 0.92);
        backdrop-filter: blur(14px);
        border: 2.5px solid #f59e0b;
        border-radius: 18px;
        box-shadow: 0 0 50px rgba(245, 158, 11, 0.55);
        width: 98%;
        max-width: 620px;
        box-sizing: border-box;
    }}
    .brand-main {{
        font-family: 'Cinzel', serif;
        font-size: clamp(2.1rem, 6.2vw, 3rem) !important;
        font-weight: 900 !important;
        font-style: italic !important;
        white-space: nowrap !important;
        letter-spacing: 2px !important;
        color: #ffbe0b !important;
        text-shadow: 0 0 25px rgba(255, 190, 11, 0.85);
        margin: 0 !important;
        line-height: 1.2 !important;
    }}
    .brand-dev {{
        font-family: 'Teko', sans-serif;
        font-size: clamp(1.2rem, 4.4vw, 1.55rem) !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        white-space: nowrap !important;
        color: #38bdf8 !important;
        text-shadow: 0 0 16px rgba(56, 189, 248, 0.85);
        margin-top: 6px !important;
    }}
    .brand-mantra {{
        color: #f59e0b;
        font-size: clamp(0.85rem, 3.2vw, 1.05rem) !important;
        margin-top: 8px;
        font-weight: 800;
        letter-spacing: 0.8px;
        text-shadow: 0 0 10px rgba(245, 158, 11, 0.6);
        white-space: nowrap !important;
    }}
    
    .filter-panel {{
        background: rgba(11, 18, 36, 0.90);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 14px;
    }}
    .alert-panel {{
        background: rgba(8, 14, 28, 0.92);
        border: 1px solid #1c2b4d;
        border-radius: 8px;
        padding: 14px;
        margin-top: 10px;
    }}
    
    label {{
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        color: #94a3b8 !important;
        text-transform: uppercase !important;
    }}
    div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {{
        background-color: #0b1329 !important;
        color: #38bdf8 !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        border: 1px solid #1e2e50 !important;
        border-radius: 6px !important;
    }}
    
    .scan-btn > button {{
        background: #0284c7 !important;
        color: white !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 6px !important;
    }}
    .stop-btn > button {{
        background: #ef4444 !important;
        color: white !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 6px !important;
    }}
    
    .spread-card {{
        background: rgba(13, 23, 46, 0.92);
        backdrop-filter: blur(10px);
        border: 1px solid #1e2e50;
        border-left: 5px solid #38bdf8;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 12px;
    }}
    .spread-title {{
        font-size: 1.15rem;
        font-weight: 800;
        color: #ffbe0b;
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
    }}
    .spread-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 8px;
        margin: 10px 0;
    }}
    .grid-item {{
        background: #080f21;
        padding: 8px;
        border-radius: 6px;
        border: 1px solid #14223d;
        font-size: 0.85rem;
    }}
    .grid-label {{
        color: #64748b;
        font-size: 0.72rem;
        text-transform: uppercase;
        font-weight: 700;
    }}
    .grid-val {{
        color: #f8fafc;
        font-weight: 700;
        font-size: 0.92rem;
        margin-top: 2px;
    }}
    .advice-box {{
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.88rem;
        margin-top: 6px;
    }}
</style>
<div class="girnar-bg-full"></div>
''', unsafe_allow_html=True)

# --- SUPABASE CONFIG ---
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

# Session States
for key, default in [("logged_in", False), ("username", ""), ("is_admin", False), ("valid_until", None), ("scanned", False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ==================== 1. LOGIN SCREEN ====================
if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.8, 1])
    with col_mid:
        st.markdown('''
        <div class="brand-card">
            <div class="brand-main">ARHAM TRADERS</div>
            <div class="brand-dev">⚡ DEVELOPED BY PRATHAM MEHTA ⚡</div>
            <div class="brand-mantra">🙏 Shree Girnar Mandal Shree Neminath Bhagwan Ne Namah 🙏</div>
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
                            st.warning("⏳ Aapka account pending hai! Admin approval ka intezar karein.")
                        elif not usr.get("valid_until") or datetime.strptime(usr["valid_until"], "%Y-%m-%d").date() < date.today():
                            st.error("⛔ Access validity samapt ho chuki hai!")
                        else:
                            st.session_state.update(logged_in=True, username=usr["username"], is_admin=False, valid_until=usr["valid_until"])
                            st.rerun()
                    else:
                        st.error("Galat credentials!")
                else:
                    st.warning("Dono fields bharein.")

        with tab_reg:
            ru = st.text_input("Desired Username", key="reg_u")
            rph = st.text_input("Mobile Number", key="reg_ph")
            rp = st.text_input("Create Password", type="password", key="reg_p")
            if st.button("SEND ACCESS REQUEST", use_container_width=True):
                if ru and rph and rp:
                    res = register_user(ru, rp, rph)
                    if res and res.status_code in [200, 201]:
                        st.success("✅ Request submit ho gayi! Admin approval ke baad login karein.")
                    else:
                        st.error("Username already exist karta hai!")

# ==================== 2. ADMIN CONTROL PANEL ====================
elif st.session_state.is_admin:
    st.title("👑 Admin Control Panel — Arham Traders")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    r = requests.get(f"{SUPABASE_URL}/rest/v1/users?order=created_at.desc", headers=HEADERS, timeout=6)
    if r.status_code == 200:
        for u in r.json():
            if u["username"].lower() in ["pratham1785", "admin"]: continue
            rem = (datetime.strptime(u["valid_until"], "%Y-%m-%d").date() - date.today()).days if u.get("valid_until") else 0
            stat = f"🟢 Active ({rem} Days)" if u.get("is_approved") and rem > 0 else "⏳ Expired / Pending"
            with st.expander(f"👤 {u['username']} | 📞 {u.get('phone')} | {stat}"):
                c1, c2 = st.columns(2)
                d_in = c1.number_input("Grant Days:", 1, 365, 30, key=f"d_{u['id']}")
                if c2.button("Commit Approval", key=f"b_{u['id']}"):
                    update_user_days(u["id"], d_in)
                    st.success("Days Updated!")
                    st.rerun()

# ==================== 3. TRADER TERMINAL ====================
else:
    if st.session_state.valid_until and datetime.strptime(st.session_state.valid_until, "%Y-%m-%d").date() < date.today():
        st.session_state.logged_in = False
        st.rerun()

    rem_days = (datetime.strptime(st.session_state.valid_until, "%Y-%m-%d").date() - date.today()).days if st.session_state.valid_until else 0
    
    st.markdown(f'''
    <div style="display:flex; justify-content:space-between; align-items:center; padding:4px 0 12px 0; border-bottom:1px solid #131c31; margin-bottom:15px;">
        <div style="font-size:1.25rem; font-weight:800; color:#fff;">▲ Delta Analysis <span style="font-size:0.85rem; color:#64748b;">FNO SCANNER</span></div>
        <div style="display:flex; align-items:center; gap:10px;">
            <span style="color:#f59e0b; background:rgba(245,158,11,0.15); padding:3px 8px; border-radius:6px; font-size:0.8rem; font-weight:700;">● LIVE MARKET</span>
            <span style="font-size:0.85rem; color:#94a3b8;">Validity: <b>{rem_days} Days</b></span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # Filter Box
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    
    r1_1, r1_2, r1_3 = st.columns(3)
    f_stock = r1_1.selectbox("STOCK", ["ALL STOCKS", "NIFTY", "BANKNIFTY", "HDFCBANK", "RELIANCE", "TCS", "SBIN"])
    f_expiry = r1_2.selectbox("EXPIRY DATE", ["CURRENT MONTH", "NEXT MONTH", "FAR MONTH"])
    f_ref = r1_3.selectbox("REFERENCE", ["Future LTP", "Spot Index", "VWAP"])

    r2_1, r2_2, r2_3 = st.columns(3)
    f_type = r2_1.selectbox("TYPE", ["Futures Calendar Spread", "Both (CE & PE)", "Call Spread (CE)", "Put Spread (PE)"])
    f_price_gap = r2_2.selectbox("PRICE GAP", ["OFF", "1 pt", "2 pts", "3 pts", "5 pts"])
    f_delta = r2_3.selectbox("DELTA FILTER", ["ON (20-30 Delta)", "ON (30-40 Delta)", "OFF"])

    r3_1, r3_2, r3_3 = st.columns(3)
    f_strike_gap = r3_1.number_input("STRIKE GAP %", min_value=1.0, max_value=20.0, value=5.0, step=0.5)
    f_iv_gap = r3_2.number_input("IV GAP %", min_value=1.0, max_value=50.0, value=5.0, step=0.5)
    f_min_vol = r3_3.number_input("MIN VOLUME (LOTS)", min_value=1, max_value=10000, value=1, step=1)

    r4_1, r4_2, r4_3 = st.columns(3)
    f_ratio = r4_1.selectbox("RATIO", ["3:10", "1:1", "1:2", "2:1"])
    f_limit_type = r4_2.selectbox("LIMIT TYPE", ["Max Debit", "Min Credit", "Zero Cost"])
    f_limit_val = r4_3.number_input("LIMIT VALUE ₹", min_value=0, max_value=100000, value=1000, step=100)

    f_dir = st.selectbox("DIRECTION", ["Buy → Sell", "Sell → Buy", "Arbitrage Spread"])

    st.markdown('''
    <div class="alert-panel">
        <div style="color:#ef4444; font-size:0.9rem; font-weight:800; margin-bottom:10px;">
            🎯 Custom Spread Alert — Specific Company / Strike
        </div>
    ''', unsafe_allow_html=True)
    
    a1, a2, a3, a4, a5, a6 = st.columns(6)
    a_comp = a1.selectbox("COMPANY", ["Select Co..", "HDFCBANK", "NIFTY", "BANKNIFTY", "RELIANCE"])
    a_opt = a2.selectbox("OPTION", ["CE", "PE", "FUT"])
    a_buy = a3.number_input("BUY STRIKE", value=1900, step=50)
    a_sell = a4.number_input("SELL STRIKE", value=2000, step=50)
    a_ratio = a5.selectbox("RATIO BUY:SELL", ["1:2", "1:1", "3:10"])
    a_debit = a6.number_input("TARGET DEBIT ₹", value=0, step=1)

    b_al1, b_al2 = st.columns(2)
    with b_al1:
        st.button("🔔 START CUSTOM ALERT", use_container_width=True)
    with b_al2:
        st.button("CHECK NOW", use_container_width=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # Action Toolbar Buttons
    btn1, btn2, btn3, btn4, btn5 = st.columns([1.5, 1.5, 1.5, 1, 1])
    with btn1:
        st.markdown('<div class="scan-btn">', unsafe_allow_html=True)
        if st.button("SCAN NOW", use_container_width=True):
            st.session_state.scanned = True
        st.markdown('</div>', unsafe_allow_html=True)
    with btn2:
        st.button("START AUTO SCAN", use_container_width=True)
    with btn3:
        st.button("🔔 ENABLE NOTIFICATIONS", use_container_width=True)
    with btn4:
        st.markdown('<div class="stop-btn">', unsafe_allow_html=True)
        if st.button("STOP", use_container_width=True):
            st.session_state.scanned = False
        st.markdown('</div>', unsafe_allow_html=True)
    with btn5:
        if st.button("RESET", use_container_width=True):
            st.session_state.scanned = False

    st.write("---")

    # Output Cards
    st.markdown("### 💎 Detected Spread Opportunities (Individual Analysis)")

    market_data = {
        "NIFTY": {"near": 25380.50, "far": 25515.20, "lot": 75},
        "BANKNIFTY": {"near": 53680.00, "far": 53995.00, "lot": 35},
        "HDFCBANK": {"near": 1664.20, "far": 1678.80, "lot": 550},
        "RELIANCE": {"near": 1399.10, "far": 1413.50, "lot": 250},
        "TCS": {"near": 4265.00, "far": 4302.00, "lot": 175},
        "SBIN": {"near": 823.40, "far": 831.20, "lot": 750}
    }

    target_list = list(market_data.keys()) if f_stock == "ALL STOCKS" else [f_stock]

    for sym in target_list:
        info = market_data.get(sym, {"near": 1000, "far": 1010, "lot": 100})
        lot = info["lot"]
        
        if f_type == "Futures Calendar Spread":
            pts = round(info["far"] - info["near"], 2)
            tot_pnl = round(pts * lot, 2)
            carry_pct = round((pts / info["near"]) * 100, 2)
            advice = "⭐ High Premium Carry! Sell Far / Buy Near (Reverse Calendar)" if carry_pct > 0.8 else ("🔥 Cheap Carry! Buy Far / Sell Near (Long Calendar)" if carry_pct < 0.4 else "✅ Balanced Spread. Low-risk Carry Setup.")
            
            st.markdown(f'''
            <div class="spread-card">
                <div class="spread-title">
                    <span>{sym} — Futures Calendar Spread</span>
                    <span style="color:#38bdf8;">Spread: +{pts} pts</span>
                </div>
                <div class="spread-grid">
                    <div class="grid-item"><div class="grid-label">Current Expiry</div><div class="grid-val">₹{info['near']}</div></div>
                    <div class="grid-item"><div class="grid-label">Next Expiry</div><div class="grid-val">₹{info['far']}</div></div>
                    <div class="grid-item"><div class="grid-label">Lot Size</div><div class="grid-val">{lot} qty</div></div>
                    <div class="grid-item"><div class="grid-label">Total Spread Risk / Lot</div><div class="grid-val" style="color:#10b981;">₹{tot_pnl}</div></div>
                    <div class="grid-item"><div class="grid-label">Carry % (Annualized)</div><div class="grid-val">{carry_pct}% ({round(carry_pct*12, 1)}% p.a.)</div></div>
                </div>
                <div class="advice-box">🎯 <b>Action Advice:</b> {advice}</div>
            </div>
            ''', unsafe_allow_html=True)
            
        else:
            diff = 12.50
            st.markdown(f'''
            <div class="spread-card">
                <div class="spread-title">
                    <span>{sym} — Option {f_type.split(' ')[0]} ({f_ratio})</span>
                    <span style="color:#38bdf8;">Net Diff: ₹{diff}</span>
                </div>
                <div class="spread-grid">
                    <div class="grid-item"><div class="grid-label">Buy Strike</div><div class="grid-val">ATM @ ₹24.50</div></div>
                    <div class="grid-item"><div class="grid-label">Sell Strike</div><div class="grid-val">OTM @ ₹12.00</div></div>
                    <div class="grid-item"><div class="grid-label">Lot Size</div><div class="grid-val">{lot} qty</div></div>
                    <div class="grid-item"><div class="grid-label">Total Max Risk / Lot</div><div class="grid-val" style="color:#10b981;">₹{round(diff * lot, 2)}</div></div>
                    <div class="grid-item"><div class="grid-label">Delta Target</div><div class="grid-val">20-30 Delta Edge</div></div>
                </div>
                <div class="advice-box">🎯 <b>Action Advice:</b> ✅ Defined Risk Spread. Theta decay advantage on sell leg.</div>
            </div>
            ''', unsafe_allow_html=True)

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
