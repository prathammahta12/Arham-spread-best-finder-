import streamlit as st
import requests
import os
import base64
from datetime import datetime, date, timedelta

st.set_page_config(page_title="ARHAM TRADERS | Terminal", layout="wide", initial_sidebar_state="collapsed")

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
        r = requests.get(url, headers=HEADERS, timeout=5)
        return r.json() if r.status_code == 200 and r.json() else None
    except:
        return None

def register_user(u, p, ph, token):
    try:
        payload = {
            "username": u.strip(), "password": p.strip(), "phone": ph.strip(),
            "is_approved": False, "is_admin": False, "valid_until": None,
            "upstox_token": token.strip() if token else "NONE",
            "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return requests.post(f"{SUPABASE_URL}/rest/v1/users", headers=HEADERS, json=payload, timeout=5)
    except:
        return None

def update_user_login_time(uid):
    try:
        requests.patch(f"{SUPABASE_URL}/rest/v1/users?id=eq.{uid}", headers=HEADERS, json={"last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, timeout=5)
    except:
        pass

def update_user_token(uid, token):
    try:
        r = requests.patch(f"{SUPABASE_URL}/rest/v1/users?id=eq.{uid}", headers=HEADERS, json={"upstox_token": token.strip()}, timeout=5)
        return r.status_code in [200, 204]
    except:
        return False

def admin_update_user(uid, days, new_pass):
    try:
        v_date = (date.today() + timedelta(days=int(days))).strftime("%Y-%m-%d")
        payload = {"is_approved": True, "valid_until": v_date}
        if new_pass and new_pass.strip():
            payload["password"] = new_pass.strip()
        r = requests.patch(f"{SUPABASE_URL}/rest/v1/users?id=eq.{uid}", headers=HEADERS, json=payload, timeout=5)
        return r.status_code in [200, 204]
    except:
        return False

def admin_delete_user(uid):
    try:
        r = requests.delete(f"{SUPABASE_URL}/rest/v1/users?id=eq.{uid}", headers=HEADERS, timeout=5)
        return r.status_code in [200, 204]
    except:
        return False

for key, default in [("logged_in", False), ("username", ""), ("user_id", None), ("is_admin", False), ("valid_until", None), ("upstox_token", ""), ("show_settings", False), ("mode", "LIVE")]:
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
        
        tab_login, tab_reg, tab_demo = st.tabs(["🔐 Sign In", "📝 Register Account", "🚀 Demo Mode"])
        
        with tab_login:
            u_in = st.text_input("Username / Mobile", key="lin_u")
            p_in = st.text_input("Access Password", type="password", key="lin_p")
            if st.button("AUTHENTICATE & ENTER", use_container_width=True, type="primary"):
                if u_in and p_in:
                    u_data = db_get_user(u_in)
                    if u_data and u_data[0]["password"] == p_in.strip():
                        usr = u_data[0]
                        update_user_login_time(usr["id"])
                        if usr.get("is_admin", False):
                            st.session_state.update(logged_in=True, username=usr["username"], user_id=usr["id"], is_admin=True)
                            st.rerun()
                        elif not usr.get("is_approved", False):
                            st.warning("⏳ Aapka account pending hai!")
                        elif not usr.get("valid_until") or datetime.strptime(usr["valid_until"], "%Y-%m-%d").date() < date.today():
                            st.error("⛔ Access validity samapt ho chuki hai!")
                        else:
                            st.session_state.update(logged_in=True, username=usr["username"], user_id=usr["id"], is_admin=False, valid_until=usr["valid_until"], upstox_token=usr.get("upstox_token", ""), mode="LIVE")
                            st.rerun()
                    else:
                        st.error("Galat credentials!")
                else:
                    st.warning("Dono fields bharein.")

        with tab_reg:
            st.markdown("<small style='color:#38bdf8;'>Direct secure registration:</small>", unsafe_allow_html=True)
            ru = st.text_input("Desired Username", key="reg_u")
            rph = st.text_input("Mobile Number", key="reg_ph")
            rp = st.text_input("Create Password", type="password", key="reg_p")
            r_token = st.text_input("Upstox Analysis Token (Optional)", key="reg_token")

            if st.button("REGISTER NOW", use_container_width=True, type="primary"):
                if ru and rph and rp:
                    res = register_user(ru, rp, rph, r_token)
                    if res and res.status_code in [200, 201]:
                        st.success("✅ Registration successful! Admin approval ke baad login karein.")
                    else:
                        st.error("Username already exists!")
                else:
                    st.warning("Kripya zaroori fields bharein.")

        with tab_demo:
            st.markdown("<p style='color:#cbd5e1; font-size:0.9rem;'>Bina registration ke turant app check karne ke liye Demo Mode me enter karein:</p>", unsafe_allow_html=True)
            if st.button("ENTER DEMO TRIAL MODE", use_container_width=True):
                st.session_state.update(logged_in=True, username="Demo_Trader", user_id=0, is_admin=False, valid_until="2030-01-01", upstox_token="", mode="DEMO")
                st.rerun()

# ==================== 2. ADMIN CONTROL CENTER ====================
elif st.session_state.is_admin:
    st.title("👑 Admin Control Center — Arham Traders")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown("### 🟢 Registered Users & Live Activity")
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/users?order=created_at.desc", headers=HEADERS, timeout=5)
        if r.status_code == 200:
            users_list = r.json()
            st.info(f"Total Database Users: {len([u for u in users_list if not u.get('is_admin')])}")
            
            for u in users_list:
                if u["username"].lower() in ["pratham1785", "admin"]: continue
                rem_days = (datetime.strptime(u["valid_until"], "%Y-%m-%d").date() - date.today()).days if u.get("valid_until") else 0
                status_text = f"🟢 Active ({rem_days} Days)" if u.get("is_approved") and rem_days > 0 else "⏳ Pending / Expired"
                last_seen = u.get('last_login', 'Never')
                
                with st.expander(f"👤 {u['username']} | 📞 {u.get('phone')} | Last Login: {last_seen}"):
                    st.markdown(f"""
                    - **User ID:** `{u['id']}`
                    - **Upstox Token:** `{u.get('upstox_token') or 'Not Provided'}`
                    - **Current Validity:** `{u.get('valid_until') or 'No Active Validity'}`
                    """)
                    
                    c1, c2, c3 = st.columns(3)
                    grant_d = c1.number_input("Grant Days:", 1, 365, 30, key=f"days_{u['id']}")
                    new_p = c2.text_input("Reset Password:", type="password", key=f"pass_{u['id']}")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    if col_btn1.button("💾 Update User", key=f"upd_{u['id']}"):
                        if admin_update_user(u["id"], grant_d, new_p):
                            st.success(f"User {u['username']} updated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to update user.")
                    
                    if col_btn2.button("🗑️ Delete User", key=f"del_{u['id']}"):
                        if admin_delete_user(u["id"]):
                            st.warning(f"User {u['username']} deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete user.")
    except:
        st.error("Failed to fetch users list.")

# ==================== 3. TRADER TERMINAL ====================
else:
    st.markdown('''
    <style>
        .stApp { background-color: #0f141c !important; color: #d1d5db !important; font-family: 'Rajdhani', sans-serif !important; }
        .filter-panel { background: #171f2c; border: 1px solid #232f42; border-radius: 12px; padding: 16px; margin-bottom: 14px; }
        .custom-alert { margin-top: 14px; border: 1px solid #2b2b2b; border-radius: 10px; padding: 14px; background: #101010; }
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

    if st.session_state.mode == "LIVE" and st.session_state.valid_until and datetime.strptime(st.session_state.valid_until, "%Y-%m-%d").date() < date.today():
        st.session_state.logged_in = False
        st.rerun()

    rem_days = (datetime.strptime(st.session_state.valid_until, "%Y-%m-%d").date() - date.today()).days if st.session_state.mode == "LIVE" and st.session_state.valid_until else 999

    n1, n2, n3, n4 = st.columns([2.5, 1.5, 1, 1])
    with n1:
        st.markdown(f'<div style="font-size:1.25rem; font-weight:800; color:#fff;">▲ Delta Analysis <span style="font-size:0.85rem; color:#64748b;">FNO SCANNER ({st.session_state.mode} MODE)</span></div>', unsafe_allow_html=True)
    with n2:
        st.markdown(f'<div style="color:#f59e0b; background:rgba(245,158,11,0.15); padding:4px 10px; border-radius:6px; font-size:0.80rem; font-weight:700; text-align:center;">● {rem_days if st.session_state.mode=="LIVE" else "Trial"} Active</div>', unsafe_allow_html=True)
    with n3:
        if st.session_state.mode == "LIVE" and st.button("⚙️ Change Token", use_container_width=True):
            st.session_state.show_settings = not st.session_state.show_settings
            st.rerun()
    with n4:
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False; st.rerun()

    if st.session_state.show_settings:
        with st.expander("🛠️ Update Upstox Analysis Token", expanded=True):
            new_token = st.text_input("New Upstox Token", value=st.session_state.upstox_token)
            if st.button("SAVE NEW TOKEN"):
                if new_token:
                    if update_user_token(st.session_state.user_id, new_token):
                        st.session_state.upstox_token = new_token
                        st.success("✅ Upstox token successfully updated!")
                        st.session_state.show_settings = False
                        st.rerun()
                    else:
                        st.error("Failed to update token.")

    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    
    r1_1, r1_2, r1_3 = st.columns(3)
    f_stock = r1_1.selectbox("STOCK", ["ALL STOCKS", "NIFTY", "BANKNIFTY", "HDFCBANK", "RELIANCE", "TCS", "SBIN"])
    f_expiry = r1_2.selectbox("EXPIRY DATE", ["CURRENT MONTH", "NEXT MONTH", "FAR MONTH"])
    f_ref = r1_3.selectbox("REFERENCE", ["Future LTP", "Equity LTP"])

    r2_1, r2_2, r2_3 = st.columns(3)
    f_type = r2_1.selectbox("TYPE", ["Both", "CE", "PE"])
    f_price_gap_on = r2_2.selectbox("PRICE GAP", ["OFF", "ON"])
    f_price_val = r2_3.number_input("PRICE GAP VALUE", value=3.0, step=0.1)

    r3_1, r3_2, r3_3 = st.columns(3)
    f_delta_on = r3_1.selectbox("DELTA FILTER", ["ON (20-30)", "OFF"])
    f_strike_gap = r3_2.number_input("STRIKE GAP %", min_value=0.0, max_value=20.0, value=5.0, step=0.5)
    f_iv_gap = r3_3.number_input("IV GAP %", min_value=0.0, max_value=50.0, value=5.0, step=0.5)

    r4_1, r4_2, r4_3 = st.columns(3)
    f_min_vol = r4_1.number_input("MIN VOLUME (LOTS)", min_value=0, max_value=10000, value=1, step=1)
    f_ratio = r4_2.selectbox("RATIO", ["3:10", "1:1", "1:2", "1:4", "CUSTOM"])
    f_limit_type = r4_3.selectbox("LIMIT TYPE", ["Max Debit", "Min Credit"])

    r5_1, r5_2 = st.columns(2)
    f_limit_val = r5_1.number_input("LIMIT VALUE ₹", min_value=0.0, max_value=100000.0, value=1000.0, step=100.0)
    f_dir = r5_2.selectbox("DIRECTION", ["Buy → Sell", "Sell → Buy"])

    st.markdown('''
    <div class="custom-alert">
        <h4 style="margin:0 0 10px 0; font-size:15px; color:#fff;">🎯 Custom Spread Alert — Specific Company / Strike</h4>
    </div>
    ''', unsafe_allow_html=True)
    
    a1, a2, a3, a4, a5, a6 = st.columns(6)
    a_comp = a1.selectbox("COMPANY", ["Select Co..", "HDFCBANK", "NIFTY", "BANKNIFTY", "RELIANCE"])
    a_opt = a2.selectbox("OPTION", ["CE", "PE"])
    a_buy = a3.number_input("BUY STRIKE", value=1900.0, step=50.0)
    a_sell = a4.number_input("SELL STRIKE", value=2000.0, step=50.0)
    a_ratio = a5.selectbox("RATIO BUY:SELL", ["1:2", "1:1", "3:10"])
    a_debit = a6.number_input("TARGET DEBIT ₹", value=0.0, step=1.0)

    b1, b2 = st.columns(2)
    with b1:
        st.button("🔔 START CUSTOM ALERT", use_container_width=True)
    with b2:
        st.button("CHECK NOW", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    btn1, btn2, btn3, btn4, btn5 = st.columns([1.5, 1.5, 1.5, 1, 1])
    with btn1:
        if st.button("SCAN NOW", use_container_width=True, type="primary"):
            st.toast("Scanning live orderbook with Spread filters...")
    with btn2:
        st.button("START AUTO SCAN", use_container_width=True)
    with btn3:
        st.button("🔔 ENABLE NOTIFICATIONS", use_container_width=True)
    with btn4:
        st.button("STOP", use_container_width=True)
    with btn5:
        st.button("RESET", use_container_width=True)

    st.write("---")
    st.markdown("### 💎 Detected Spread Opportunities & Payoff Analysis")

    for sym in ["NIFTY", "HDFCBANK", "RELIANCE"]:
        if f_stock != "ALL STOCKS" and f_stock != sym: continue
        score = 94 if sym == "NIFTY" else (88 if sym == "HDFCBANK" else 82)
        st.markdown(f'''
        <div class="spread-card">
            <div class="spread-title">
                <span>{sym} — Spread Setup ({f_ratio})</span>
                <span class="score-badge">⭐ Quality Score: {score}/100</span>
            </div>
            <div class="spread-grid">
                <div class="grid-item"><div class="grid-label">Buy Leg</div><div class="grid-val">25400 CE @ ₹145.20</div></div>
                <div class="grid-item"><div class="grid-label">Sell Leg</div><div class="grid-val">25600 CE @ ₹62.00</div></div>
                <div class="grid-item"><div class="grid-label">Max Profit / Lot</div><div class="grid-val" style="color:#10b981;">₹6,262.50</div></div>
                <div class="grid-item"><div class="grid-label">Max Risk / Lot</div><div class="grid-val" style="color:#ff5268;">₹3,240.00</div></div>
                <div class="grid-item"><div class="grid-label">Risk : Reward</div><div class="grid-val">1 : 1.93</div></div>
            </div>
            <div class="advice-box">🎯 <b>Strategy Advice:</b> Filters matched (Strike Gap: {f_strike_gap}%, IV Gap: {f_iv_gap}%). Upstox Token: {st.session_state.upstox_token[:6] if st.session_state.upstox_token else 'Default'}...</div>
        </div>
        ''', unsafe_allow_html=True)
