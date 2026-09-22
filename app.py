import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Delta Analysis | Arham Traders", layout="wide", initial_sidebar_state="collapsed")

# Direct Live High-Resolution Temple Link (Girnar Ji Jain Tirth)
GIRNAR_IMG = "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1000&q=80"

# --- EXACT DARK CYBER UI CSS (MATCHING SCREENSHOT) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700;800&family=Teko:wght@600;700&display=swap');
    
    .stApp {
        background-color: #070c18 !important;
        color: #d1d5db !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    /* Top Header Bar */
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 2px 14px 2px;
        border-bottom: 1px solid #131c31;
        margin-bottom: 15px;
    }
    .top-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .top-badge {
        font-size: 0.8rem;
        font-weight: 700;
        color: #f59e0b;
        background: rgba(245, 158, 11, 0.12);
        padding: 3px 8px;
        border-radius: 6px;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    /* Panel Containers */
    .filter-panel {
        background: #0b1224;
        border: 1px solid #16223d;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 14px;
    }
    
    .alert-panel {
        background: #091020;
        border: 1px solid #1c2b4d;
        border-radius: 8px;
        padding: 14px;
        margin-top: 10px;
    }
    
    /* Inputs Styling */
    label {
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        color: #94a3b8 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 2px !important;
    }
    div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {
        background-color: #0d172e !important;
        color: #38bdf8 !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        border: 1px solid #1e2e50 !important;
        border-radius: 6px !important;
        min-height: 38px !important;
    }
    
    /* Action Buttons */
    .scan-btn > button {
        background: #0284c7 !important;
        color: white !important;
        font-weight: 800 !important;
        font-size: 0.9rem !important;
        border: none !important;
        border-radius: 6px !important;
    }
    .stop-btn > button {
        background: #ef4444 !important;
        color: white !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 6px !important;
    }
    
    /* Individual Big Spread Card */
    .spread-card {
        background: #0d172e;
        border: 1px solid #1e2e50;
        border-left: 4px solid #38bdf8;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .spread-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #ffbe0b;
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    .spread-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 8px;
        margin: 10px 0;
    }
    .grid-item {
        background: #080f21;
        padding: 8px;
        border-radius: 6px;
        border: 1px solid #14223d;
        font-size: 0.85rem;
    }
    .grid-label {
        color: #64748b;
        font-size: 0.72rem;
        text-transform: uppercase;
        font-weight: 700;
    }
    .grid-val {
        color: #f8fafc;
        font-weight: 700;
        font-size: 0.92rem;
        margin-top: 2px;
    }
    .advice-box {
        background: rgba(16, 185, 129, 0.12);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.88rem;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

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

# ==================== 1. LOGIN SCREEN WITH JAIN GIRNAR JI ====================
if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.4, 1])
    with col_mid:
        st.image(GIRNAR_IMG, caption="Jai Girnar Ji — Shri Neminath Bhagwan Tirth", use_container_width=True)
        
        st.markdown("""
        <div style='text-align: center; background: #0b1224; border: 2px solid #f59e0b; border-radius: 12px; padding: 12px; margin-bottom: 15px;'>
            <h2 style='color:#ffbe0b; margin:0; font-size:1.8rem; font-weight:900;'>ARHAM TRADERS</h2>
            <p style='color:#38bdf8; margin:2px 0 0 0; font-size:0.95rem; font-weight:700;'>⚡ DEVELOPED BY PRATHAM MEHTA ⚡</p>
        </div>
        """, unsafe_allow_html=True)
        
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
                            st.warning("⏳ आपका अकाउंट पेंडिंग है! एडमिन अप्रूवल का इंतज़ार करें।")
                        elif not usr.get("valid_until") or datetime.strptime(usr["valid_until"], "%Y-%m-%d").date() < date.today():
                            st.error("⛔ आपका एक्सेस समाप्त हो चुका है! एडमिन से संपर्क करें।")
                        else:
                            st.session_state.update(logged_in=True, username=usr["username"], is_admin=False, valid_until=usr["valid_until"])
                            st.rerun()
                    else:
                        st.error("गलत क्रेडेंशियल्स!")
                else:
                    st.warning("सभी फ़ील्ड भरें।")

        with tab_reg:
            ru = st.text_input("Desired Username", key="reg_u")
            rph = st.text_input("Mobile Number", key="reg_ph")
            rp = st.text_input("Create Password", type="password", key="reg_p")
            if st.button("SEND ACCESS REQUEST", use_container_width=True):
                if ru and rph and rp:
                    res = register_user(ru, rp, rph)
                    if res and res.status_code in [200, 201]:
                        st.success("✅ रिक्वेस्ट सबमिट हो गई! एडमिन अप्रूवल के बाद लॉगिन करें।")
                    else:
                        st.error("यूज़रनेम पहले से मौजूद है!")

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

# ==================== 3. EXACT SCANNER LAYOUT (MATCHING SCREENSHOT) ====================
else:
    # Auto-Logout check
    if st.session_state.valid_until and datetime.strptime(st.session_state.valid_until, "%Y-%m-%d").date() < date.today():
        st.session_state.logged_in = False
        st.rerun()

    # Top Header matching image
    rem_days = (datetime.strptime(st.session_state.valid_until, "%Y-%m-%d").date() - date.today()).days if st.session_state.valid_until else 0
    st.markdown(f"""
    <div class="top-header">
        <div class="top-title"><span>▲</span> Delta Analysis <span style='font-size:0.85rem; color:#64748b;'>FNO SCANNER</span></div>
        <div style='display:flex; align-items:center; gap:10px;'>
            <span class="top-badge">● LIVE MARKET</span>
            <span style='font-size:0.85rem; color:#94a3b8;'>Validity: <b>{rem_days} Days</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Main Filter Box (Screenshot replica rows)
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    
    # Row 1: Stock, Expiry Date, Reference
    r1_1, r1_2, r1_3 = st.columns(3)
    f_stock = r1_1.selectbox("STOCK", ["ALL STOCKS", "NIFTY", "BANKNIFTY", "HDFCBANK", "RELIANCE", "TCS", "SBIN"])
    f_expiry = r1_2.selectbox("EXPIRY DATE", ["CURRENT MONTH", "NEXT MONTH", "FAR MONTH"])
    f_ref = r1_3.selectbox("REFERENCE", ["Future LTP", "Spot Index", "VWAP"])

    # Row 2: Type, Price Gap, Delta Filter
    r2_1, r2_2, r2_3 = st.columns(3)
    f_type = r2_1.selectbox("TYPE", ["Futures Calendar Spread", "Both (CE & PE)", "Call Spread (CE)", "Put Spread (PE)"])
    f_price_gap = r2_2.selectbox("PRICE GAP", ["OFF", "1 pt", "2 pts", "3 pts", "5 pts"])
    f_delta = r2_3.selectbox("DELTA FILTER", ["ON (20-30 Delta)", "ON (30-40 Delta)", "OFF"])

    # Row 3: Strike Gap %, IV Gap %, Min Volume (Lots)
    r3_1, r3_2, r3_3 = st.columns(3)
    f_strike_gap = r3_1.number_input("STRIKE GAP %", min_value=1.0, max_value=20.0, value=5.0, step=0.5)
    f_iv_gap = r3_2.number_input("IV GAP %", min_value=1.0, max_value=50.0, value=5.0, step=0.5)
    f_min_vol = r3_3.number_input("MIN VOLUME (LOTS)", min_value=1, max_value=10000, value=1, step=1)

    # Row 4: Ratio, Limit Type, Limit Value ₹
    r4_1, r4_2, r4_3 = st.columns(3)
    f_ratio = r4_1.selectbox("RATIO", ["3:10", "1:1", "1:2", "2:1"])
    f_limit_type = r4_2.selectbox("LIMIT TYPE", ["Max Debit", "Min Credit", "Zero Cost"])
    f_limit_val = r4_3.number_input("LIMIT VALUE ₹", min_value=0, max_value=100000, value=1000, step=100)

    # Row 5: Direction
    f_dir = st.selectbox("DIRECTION", ["Buy → Sell", "Sell → Buy", "Arbitrage Spread"])

    # Nested Box: Custom Spread Alert — Specific Company / Strike (Screenshot match)
    st.markdown("""
    <div class="alert-panel">
        <div style='color:#ef4444; font-size:0.9rem; font-weight:800; margin-bottom:10px;'>
            🎯 Custom Spread Alert — Specific Company / Strike
        </div>
    """, unsafe_allow_html=True)
    
    a1, a2, a3, a4, a5, a6 = st.columns(6)
    a_comp = a1.selectbox("COMPANY", ["Select Co..", "HDFCBANK", "NIFTY", "BANKNIFTY", "RELIANCE"])
    a_opt = a2.selectbox("OPTION", ["CE", "PE", "FUT"])
    a_buy = a3.number_input("BUY STRIKE", value=1900, step=50)
    a_sell = a4.number_input("SELL STRIKE", value=2000, step=50)
    a_ratio = a5.selectbox("RATIO BUY:SELL", ["1:2", "1:1", "3:10"])
    a_debit = a6.number_input("TARGET DEBIT ₹", value=0, step=1)

    b_al1, b_al2 = st.columns([1, 1])
    with b_al1:
        st.button("🔔 START CUSTOM ALERT", use_container_width=True)
    with b_al2:
        check_now = st.button("CHECK NOW", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Action Toolbar Buttons (Exact Screenshot layout)
    btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = st.columns([1.5, 1.5, 1.5, 1, 1])
    with btn_col1:
        st.markdown('<div class="scan-btn">', unsafe_allow_html=True)
        if st.button("SCAN NOW", use_container_width=True):
            st.session_state.scanned = True
        st.markdown('</div>', unsafe_allow_html=True)
    with btn_col2:
        st.button("START AUTO SCAN", use_container_width=True)
    with btn_col3:
        st.button("🔔 ENABLE NOTIFICATIONS", use_container_width=True)
    with btn_col4:
        st.markdown('<div class="stop-btn">', unsafe_allow_html=True)
        if st.button("STOP", use_container_width=True):
            st.session_state.scanned = False
        st.markdown('</div>', unsafe_allow_html=True)
    with btn_col5:
        if st.button("RESET", use_container_width=True):
            st.session_state.scanned = False

    st.write("---")

    # --- RESULTS: SEPARATE BIG CARDS (NO WHITE TABLE BUG) ---
    st.markdown("### 💎 Detected Spread Opportunities (Individual Analysis)")

    market_data = {
        "NIFTY": {"near": 25380.50, "far": 25515.20, "lot": 75, "step": 50},
        "BANKNIFTY": {"near": 53680.00, "far": 53995.00, "lot": 35, "step": 100},
        "HDFCBANK": {"near": 1664.20, "far": 1678.80, "lot": 550, "step": 10},
        "RELIANCE": {"near": 1399.10, "far": 1413.50, "lot": 250, "step": 10},
        "TCS": {"near": 4265.00, "far": 4302.00, "lot": 175, "step": 50},
        "SBIN": {"near": 823.40, "far": 831.20, "lot": 750, "step": 5}
    }

    target_list = list(market_data.keys()) if f_stock == "ALL STOCKS" else [f_stock]

    for sym in target_list:
        info = market_data.get(sym, {"near": 1000, "far": 1010, "lot": 100, "step": 10})
        lot = info["lot"]
        
        if f_type == "Futures Calendar Spread":
            pts = round(info["far"] - info["near"], 2)
            tot_pnl = round(pts * lot, 2)
            carry_pct = round((pts / info["near"]) * 100, 2)
            advice = "⭐ High Premium Carry! Sell Far / Buy Near (Reverse Calendar)" if carry_pct > 0.8 else ("🔥 Cheap Carry! Buy Far / Sell Near (Long Calendar)" if carry_pct < 0.4 else "✅ Balanced Spread. Low-risk Carry Setup.")
            
            # Big Clean Box
            st.markdown(f"""
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
            """, unsafe_allow_html=True)
            
        else:
            diff = 12.50
            st.markdown(f"""
            <div class="spread-card">
                <div class="spread-title">
                    <span>{sym} — Option {f_type.split(' ')[0]} ({f_ratio})</span>
                    <span style="color:#38bdf8;">Net Diff: ₹{diff}</span>
                </div>
                <div class="spread-grid">
                    <div class="grid-item"><div class="grid-label">Buy Strike</div><div class="grid-val">ATM @ ₹24.50</div></div>
                    <div class="grid-item"><div class="grid-label">Sell Strike</div><div class="grid-val">OTM (x{f_ratio.split(':')[-1]}) @ ₹12.00</div></div>
                    <div class="grid-item"><div class="grid-label">Lot Size</div><div class="grid-val">{lot} qty</div></div>
                    <div class="grid-item"><div class="grid-label">Total Max Risk / Lot</div><div class="grid-val" style="color:#10b981;">₹{round(diff * lot, 2)}</div></div>
                    <div class="grid-item"><div class="grid-label">Delta Target</div><div class="grid-val">20-30 Delta Edge</div></div>
                </div>
                <div class="advice-box">🎯 <b>Action Advice:</b> ✅ Defined Risk Spread. Theta decay advantage on sell leg.</div>
            </div>
            """, unsafe_allow_html=True)

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
        
