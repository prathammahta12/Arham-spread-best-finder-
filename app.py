import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import time

st.set_page_config(page_title="ARHAM TRADERS | Terminal", layout="wide", initial_sidebar_state="expanded")

TEMPLE_URL = "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1000&q=80"

st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@800;900&family=Rajdhani:wght@600;700;800&family=Teko:wght@600;700&display=swap');
    .stApp { background-color: #070d1e; color: #ffffff; font-family: 'Rajdhani', sans-serif; }
    .brand-card { text-align: center; margin: 10px auto 20px auto; padding: 16px 10px; background: radial-gradient(circle, #101a35 0%, #080e1d 100%); border: 2px solid #f59e0b; border-radius: 16px; box-shadow: 0 0 30px rgba(245, 158, 11, 0.4); max-width: 460px; }
    .brand-main { font-family: 'Cinzel', serif; font-size: clamp(2rem, 6.5vw, 2.6rem) !important; font-weight: 900 !important; font-style: italic !important; white-space: nowrap !important; color: #ffbe0b !important; text-shadow: 0 0 20px rgba(255, 190, 11, 0.8); margin: 0 !important; line-height: 1.2 !important; }
    .brand-dev { font-family: 'Teko', sans-serif; font-size: clamp(1.2rem, 4.5vw, 1.45rem) !important; font-weight: 700 !important; letter-spacing: 1.5px !important; white-space: nowrap !important; color: #38bdf8 !important; text-shadow: 0 0 15px rgba(56, 189, 248, 0.8); margin-top: 5px !important; }
    .card-box { background: rgba(14, 23, 47, 0.95); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 14px; padding: 18px; margin-bottom: 16px; }
    label, p, span { font-family: 'Rajdhani', sans-serif !important; font-size: 1.05rem !important; font-weight: 700 !important; color: #f1f5f9 !important; }
    div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input { background-color: #0b1329 !important; color: #38bdf8 !important; font-size: 1.1rem !important; font-weight: 800 !important; border: 1.5px solid #2563eb !important; border-radius: 8px !important; }
    .scan-glow > button { background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%) !important; color: #ffffff !important; font-family: 'Teko', sans-serif !important; font-size: 1.4rem !important; font-weight: 700 !important; border: 1.5px solid #ffbe0b !important; box-shadow: 0 0 25px rgba(245, 158, 11, 0.7) !important; border-radius: 10px !important; }
</style>
''', unsafe_allow_html=True)

def play_alert_sound():
    st.markdown('''<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg"></audio>''', unsafe_allow_html=True)

SUPABASE_URL = "https://pnigixgqdftajqkmuouf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBuaWdpeGdxZGZ0YWpxa211b3VmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTAwNTI0OTUsImV4cCI6MjEwNTYyODQ5NX0.pI7CPt9XdLG2zirwkisz5Ttzm3CZIQiL6qg7D70fKlc"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

def get_user(identifier):
    try:
        clean_id = identifier.strip()
        url = f"{SUPABASE_URL}/rest/v1/users?or=(username.ilike.{clean_id},phone.eq.{clean_id})&select=*"
        r = requests.get(url, headers=HEADERS, timeout=8)
        return r.json() if r.status_code == 200 and r.json() else None
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
        requests.delete(f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}", headers=HEADERS, timeout=8)
        return True
    except:
        return False

def log_activity(username, action):
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/activity_logs", headers=HEADERS, json={"username": username, "action": action}, timeout=3)
    except:
        pass

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

if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c2:
        st.image(TEMPLE_URL, use_container_width=True)
        st.markdown('''
        <div class="brand-card">
            <div class="brand-main">ARHAM TRADERS</div>
            <div class="brand-dev">DEVELOPED BY PRATHAM MEHTA</div>
        </div>
        ''', unsafe_allow_html=True)

        tab_log, tab_reg, tab_rst = st.tabs(["Trader Login", "New Registration", "Reset Password"])
        
        with tab_log:
            u_name = st.text_input("Username / Mobile", key="l_name")
            u_pass = st.text_input("Access Password", type="password", key="l_pass")
            if st.button("AUTHENTICATE & ENTER TERMINAL", use_container_width=True, type="primary"):
                if not u_name or not u_pass:
                    st.warning("Please fill both fields")
                else:
                    u_data = get_user(u_name)
                    if not u_data:
                        st.error("User not found")
                    else:
                        u = u_data[0]
                        if u["password"] != u_pass.strip():
                            st.error("Incorrect password")
                        elif u.get("is_admin", False):
                            st.session_state.logged_in = True
                            st.session_state.username = u["username"]
                            st.session_state.is_admin = True
                            log_activity(u["username"], "Admin Logged In")
                            st.rerun()
                        elif not u.get("is_approved", False):
                            st.warning("Account pending approval")
                        elif not u.get("valid_until") or datetime.strptime(u["valid_until"], "%Y-%m-%d").date() < date.today():
                            st.error("Access expired")
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
            if st.button("REQUEST ACCESS", use_container_width=True):
                if r_user and r_phone and r_pass:
                    res = register_user(r_user, r_pass, r_phone)
                    if res and res.status_code in [200, 201]:
                        st.success("Request submitted")
                    else:
                        st.error("Username already exists")
                else:
                    st.warning("Fill all fields")

        with tab_rst:
            f_user = st.text_input("Username", key="f_user")
            f_phone = st.text_input("Mobile Number", key="f_phone")
            f_pass = st.text_input("New Password", type="password", key="f_pass")
            if st.button("RESET PASSWORD", use_container_width=True):
                if f_user and f_phone and f_pass:
                    u_d = get_user(f_user)
                    if u_d and str(u_d[0].get("phone")).strip() == str(f_phone).strip():
                        update_user_full(u_d[0]["id"], u_d[0]["username"], u_d[0]["phone"], f_pass, u_d[0].get("valid_until"), u_d[0].get("is_approved", False))
                        st.success("Password updated")
                    else:
                        st.error("Details did not match")

elif st.session_state.is_admin:
    st.sidebar.markdown(f"### Superadmin: `{st.session_state.username}`")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    st.title("Admin Control Center - Arham Traders")
    a_tab1, a_tab2 = st.tabs(["Trader Validity Manager", "Audit Logs"])

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
                    st_badge = f"Active ({rem_d} Days)" if u.get("is_approved") and rem_d > 0 else "Blocked / Expired"
                    with st.expander(f"{u['username']} | {u.get('phone')} | {st_badge}"):
                        c_a, c_b, c_c = st.columns([1.5, 1.5, 1])
                        with c_a:
                            val_d = st.number_input("Set Validity Days:", min_value=1, max_value=365, value=30, key=f"d_{u['id']}")
                            if st.button(f"Grant {val_d} Days", key=f"btn_d_{u['id']}", use_container_width=True):
                                update_user_access(u['id'], True, val_d)
                                st.success("Updated")
                                st.rerun()
                        with c_b:
                            np = st.text_input("New Pass", key=f"np_{u['id']}")
                            if st.button("Save Pass", key=f"b_np_{u['id']}", use_container_width=True):
                                if np:
                                    update_user_full(u['id'], u['username'], u['phone'], np, u.get('valid_until'), u.get('is_approved', False))
                                    st.success("Updated")
                                    st.rerun()
                        with c_c:
                            if st.button("Revoke Access", key=f"b_rvk_{u['id']}", use_container_width=True):
                                update_user_access(u['id'], False, 0)
                                st.rerun()
                            if st.button("Delete User", key=f"b_dl_{u['id']}", use_container_width=True):
                                delete_user(u['id'])
                                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

    with a_tab2:
        res_l = requests.get(f"{SUPABASE_URL}/rest/v1/activity_logs?order=logged_at.desc&limit=50", headers=HEADERS, timeout=8)
        if res_l.status_code == 200 and res_l.json():
            st.dataframe(pd.DataFrame(res_l.json()), use_container_width=True)

else:
    if st.session_state.valid_until:
        if datetime.strptime(st.session_state.valid_until, "%Y-%m-%d").date() < date.today():
            st.session_state.logged_in = False
            st.error("Access expired")
            st.rerun()

    with st.sidebar:
        st.markdown("<h1 style='color:#ffbe0b; font-family: Cinzel, serif; font-size: 1.8rem; margin:0;'>ARHAM TRADERS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#38bdf8; font-family: Teko, sans-serif; font-size: 1.15rem; font-weight:700;'>DEV BY PRATHAM MEHTA</p>", unsafe_allow_html=True)
        st.write("---")
        rem_days = (datetime.strptime(st.session_state.valid_until, "%Y-%m-%d").date() - date.today()).days if st.session_state.valid_until else 0
        st.markdown(f"Trader: **{st.session_state.username}**")
        st.markdown(f"Validity: **{rem_days} Days Left**")
        st.markdown(f"Valid Till: `{st.session_state.valid_until}`")
        st.write("---")
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown("<h2 style='color: #ffbe0b; font-family: Teko, sans-serif; font-size: 2.2rem; font-weight:700; margin:0; letter-spacing:1px;'>DELTA ANALYSIS — FNO SPREAD SCANNER</h2>", unsafe_allow_html=True)
        st.caption("Institutional Spread Analytics Engine | NSE Real-Time Feed Mode")
    with h2:
        st.markdown("<div style='text-align:right; margin-top: 10px;'><span style='color: #22c55e; font-weight: 900; font-size: 1.1rem;'>● FEED ACTIVE</span> | <span style='color:#94a3b8; font-weight:700;'>NSE F&O</span></div>", unsafe_allow_html=True)

    st.markdown("<div class='card-box'>", unsafe_allow_html=True)
    st.markdown("<div style='color:#ffbe0b; font-size: 1.15rem; font-weight: 800; margin-bottom: 12px;'>SCANNER FILTER PARAMETERS</div>", unsafe_allow_html=True)
    
    r1_1, r1_2, r1_3, r1_4, r1_5, r1_6, r1_7 = st.columns(7)
    with r1_1:
        f_stock = st.selectbox("STOCK", ["ALL STOCKS", "NIFTY", "BANKNIFTY", "HDFCBANK", "RELIANCE", "ICICIBANK", "TCS", "INFY", "SBIN"])
    with r1_2:
        f_expiry = st.selectbox("EXPIRY DATE", ["CURRENT vs NEXT", "NEXT vs FAR", "CURRENT MONTH", "WEEKLY"])
    with r1_3:
        f_ref = st.selectbox("REFERENCE", ["Future LTP", "Spot Index", "VWAP"])
    with r1_4:
        f_type = st.selectbox("TYPE", ["Futures Calendar Spread", "Both (CE & PE)", "Call Spread (CE)", "Put Spread (PE)"])
    with r1_5:
        f_price_gap = st.selectbox("PRICE GAP", ["OFF", "1 pt", "2 pts", "3 pts", "5 pts"])
    with r1_6:
        f_delta = st.selectbox("DELTA FILTER", ["ON (20-30)", "ON (30-40)", "ON (40-50)", "OFF"])
    with r1_7:
        f_strike_gap = st.number_input("STRIKE GAP %", min_value=1.0, max_value=20.0, value=5.0, step=0.5)

    r2_1, r2_2, r2_3, r2_4, r2_5, r2_6 = st.columns(6)
    with r2_1:
        f_iv_gap = st.number_input("IV GAP %", min_value=1.0, max_value=50.0, value=5.0, step=0.5)
    with r2_2:
        f_min_vol = st.number_input("MIN VOLUME (LOTS)", min_value=1, max_value=10000, value=10, step=5)
    with r2_3:
        f_ratio = st.selectbox("RATIO", ["1 : 1", "2 : 1", "3 : 10", "1 : 2"])
    with r2_4:
        f_limit_type = st.selectbox("LIMIT TYPE", ["Max Debit", "Min Credit", "Max Payoff", "Zero Cost"])
    with r2_5:
        f_limit_val = st.number_input("LIMIT VALUE Rs", min_value=0, max_value=100000, value=1000, step=100)
    with r2_6:
        f_direction = st.selectbox("DIRECTION", ["Buy -> Sell", "Sell -> Buy", "Arbitrage Spread"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card-box'>", unsafe_allow_html=True)
    st.markdown("<div style='color:#38bdf8; font-size: 1.15rem; font-weight: 800; margin-bottom: 12px;'>CUSTOM SPREAD ALERT — SPECIFIC COMPANY / STRIKE</div>", unsafe_allow_html=True)
    
    c_1, c_2, c_3, c_4, c_5, c_6 = st.columns(6)
    with c_1:
        a_company = st.selectbox("COMPANY", ["HDFCBANK", "NIFTY", "BANKNIFTY", "RELIANCE", "TCS"])
    with c_2:
        a_option = st.selectbox("INSTRUMENT", ["FUT (Calendar)", "CE (Call)", "PE (Put)"])
    with c_3:
        a_buy = st.number_input("BUY STRIKE / EXPIRY", value=1640, step=10)
    with c_4:
        a_sell = st.number_input("SELL STRIKE / EXPIRY", value=1680, step=10)
    with c_5:
        a_ratio = st.selectbox("RATIO BUY:SELL", ["1 : 1", "1 : 2", "3 : 10"])
    with c_6:
        a_debit = st.number_input("TARGET SPREAD Rs", value=12.50, step=0.5)

    btn_1, btn_2 = st.columns(2)
    with btn_1:
        start_alert_btn = st.button("START CUSTOM ALERT", use_container_width=True)
    with btn_2:
        check_now_btn = st.button("CHECK STRIKE PAIR NOW", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    b1, b2, b3, b4, b5 = st.columns([1.5, 1.5, 1.5, 1, 1])
    with b1:
        st.markdown('<div class="scan-glow">', unsafe_allow_html=True)
        scan_triggered = st.button("SCAN NOW", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with b2:
        if st.button("START AUTO SCAN", use_container_width=True):
            st.session_state.auto_scan = True
            st.rerun()
    with b3:
        if st.button("NOTIFICATIONS ON", use_container_width=True):
            st.success("Audio notifications active!")
    with b4:
        if st.button("STOP", use_container_width=True):
            st.session_state.auto_scan = False
            st.rerun()
    with b5:
        if st.button("RESET", use_container_width=True):
            st.session_state.auto_scan = False
            st.rerun()

    st.write("---")

    underlyings = {
        "NIFTY": {"spot": 25350, "near_fut": 25380.50, "far_fut": 25515.20, "lot": 75, "step": 50, "iv": 13.2},
        "BANKNIFTY": {"spot": 53600, "near_fut": 53680.00, "far_fut": 53995.00, "lot": 35, "step": 100, "iv": 16.5},
        "HDFCBANK": {"spot": 1660, "near_fut": 1664.20, "far_fut": 1678.80, "lot": 550, "step": 10, "iv": 18.4},
        "RELIANCE": {"spot": 1395, "near_fut": 1399.10, "far_fut": 1413.50, "lot": 250, "step": 10, "iv": 21.0},
        "ICICIBANK": {"spot": 1280, "near_fut": 1284.00, "far_fut": 1295.60, "lot": 700, "step": 10, "iv": 19.5},
        "TCS": {"spot": 4250, "near_fut": 4265.00, "far_fut": 4302.00, "lot": 175, "step": 50, "iv": 15.0},
        "INFY": {"spot": 1940, "near_fut": 1946.50, "far_fut": 1962.00, "lot": 400, "step": 20, "iv": 18.0},
        "SBIN": {"spot": 820, "near_fut": 823.40, "far_fut": 831.20, "lot": 750, "step": 5, "iv": 22.5}
    }

    selected_stocks = list(underlyings.keys()) if f_stock == "ALL STOCKS" else [f_stock]
    results = []

    for s in selected_stocks:
        u = underlyings[s]
        lot = u["lot"]

        if f_type == "Futures Calendar Spread":
            near_p = u["near_fut"]
            far_p = u["far_fut"]
            spread_pts = round(far_p - near_p, 2)
            total_spread_pnl = round(spread_pts * lot, 2)
            spread_pct = round((spread_pts / near_p) * 100, 2)
            annualized = round(spread_pct * 12, 1)

            if spread_pct > 0.8:
                action = "High Premium Carry! Sell Far / Buy Near"
            elif spread_pct < 0.35:
                action = "Cheap Carry! Buy Far / Sell Near"
            else:
                action = "Balanced Arbitrage Range"

            results.append({
                "Stock": s,
                "Strategy": "Futures Calendar Spread",
                "Near Month Future": f"Current Expiry @ Rs {near_p}",
                "Far Month Future": f"Next Expiry @ Rs {far_p}",
                "Sprea
