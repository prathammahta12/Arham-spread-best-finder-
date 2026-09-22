import streamlit as st
import requests
from datetime import datetime, date, timedelta

st.set_page_config(page_title="ARHAM TRADERS", layout="wide")

GIRNAR_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Neminath_Temple_Girnar_02.jpg/1280px-Neminath_Temple_Girnar_02.jpg"

st.markdown('''
<style>
    .stApp { background-color: #060b17; color: #ffffff; }
    .brand-box { text-align:center; padding:12px; background:#0e172e; border:2px solid #f59e0b; border-radius:14px; margin-bottom:15px; }
    .brand-title { color:#ffbe0b; font-size:2rem; font-weight:900; margin:0; }
    .brand-sub { color:#38bdf8; font-size:1.1rem; font-weight:700; margin:4px 0 0 0; }
    .spread-card { background:#0d1833; border:1px solid #1e293b; border-left:5px solid #38bdf8; border-radius:12px; padding:14px; margin-bottom:14px; }
    .card-title { font-size:1.25rem; font-weight:800; color:#ffbe0b; display:flex; justify-content:space-between; }
    .card-row { display:flex; flex-wrap:wrap; gap:10px; margin:10px 0; }
    .card-col { flex:1; min-width:130px; background:#070d1d; padding:8px; border-radius:8px; border:1px solid #1e293b; }
    .card-advice { background:rgba(16,185,129,0.15); color:#10b981; border:1px solid #10b981; padding:8px; border-radius:8px; font-weight:700; }
    div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input { background:#0b1329 !important; color:#38bdf8 !important; border:1px solid #2563eb !important; }
</style>
''', unsafe_allow_html=True)

S_URL = "https://pnigixgqdftajqkmuouf.supabase.co"
S_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBuaWdpeGdxZGZ0YWpxa211b3VmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTAwNTI0OTUsImV4cCI6MjEwNTYyODQ5NX0.pI7CPt9XdLG2zirwkisz5Ttzm3CZIQiL6qg7D70fKlc"
HDR = {"apikey": S_KEY, "Authorization": f"Bearer {S_KEY}", "Content-Type": "application/json"}

def db_get_user(u):
    try:
        r = requests.get(f"{S_URL}/rest/v1/users?or=(username.ilike.{u},phone.eq.{u})&select=*", headers=HDR, timeout=5)
        return r.json() if r.status_code == 200 and r.json() else None
    except: return None

for k, v in [("auth", False), ("user", ""), ("admin", False), ("valid", None)]:
    if k not in st.session_state: st.session_state[k] = v

if not st.session_state.auth:
    _, mid, _ = st.columns([1, 1.3, 1])
    with mid:
        st.image(GIRNAR_IMG, caption="Jai Girnar Ji - Neminath Bhagwan Tirth", use_container_width=True)
        st.markdown('<div class="brand-box"><h2 class="brand-title">ARHAM TRADERS</h2><p class="brand-sub">⚡ DEV BY PRATHAM MEHTA ⚡</p></div>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        with tab1:
            u_name = st.text_input("Username / Mobile")
            u_pass = st.text_input("Password", type="password")
            if st.button("ENTER TERMINAL", use_container_width=True, type="primary"):
                u = db_get_user(u_name)
                if u and u[0]["password"] == u_pass.strip():
                    usr = u[0]
                    if usr.get("is_admin", False):
                        st.session_state.update(auth=True, user=usr["username"], admin=True)
                        st.rerun()
                    elif not usr.get("is_approved"):
                        st.warning("Admin approval pending!")
                    elif not usr.get("valid_until") or datetime.strptime(usr["valid_until"], "%Y-%m-%d").date() < date.today():
                        st.error("Access plan expired!")
                    else:
                        st.session_state.update(auth=True, user=usr["username"], admin=False, valid=usr["valid_until"])
                        st.rerun()
                else: st.error("Invalid Credentials!")
        with tab2:
            ru = st.text_input("New Username")
            rp = st.text_input("Mobile Number")
            rpw = st.text_input("New Password", type="password")
            if st.button("REGISTER"):
                r = requests.post(f"{S_URL}/rest/v1/users", headers=HDR, json={"username":ru,"phone":rp,"password":rpw,"is_approved":False,"is_admin":False})
                st.success("Request sent!") if r.status_code in [200,201] else st.error("Error/Exists!")

elif st.session_state.admin:
    st.title("👑 Admin Control Center")
    if st.button("Logout"): st.session_state.auth = False; st.rerun()
    r = requests.get(f"{S_URL}/rest/v1/users?order=created_at.desc", headers=HDR, timeout=5)
    if r.status_code == 200:
        for u in r.json():
            if u["username"].lower() in ["pratham1785", "admin"]: continue
            with st.expander(f"{u['username']} (📞 {u.get('phone')})"):
                d = st.number_input("Days:", 1, 365, 30, key=f"d_{u['id']}")
                if st.button("Approve Days", key=f"b_{u['id']}"):
                    nd = (date.today() + timedelta(days=int(d))).strftime("%Y-%m-%d")
                    requests.patch(f"{S_URL}/rest/v1/users?id=eq.{u['id']}", headers=HDR, json={"is_approved":True, "valid_until":nd})
                    st.success("Approved!"); st.rerun()

else:
    if st.session_state.valid and datetime.strptime(st.session_state.valid, "%Y-%m-%d").date() < date.today():
        st.session_state.auth = False; st.rerun()

    with st.sidebar:
        st.markdown("<h2 style='color:#ffbe0b; margin:0;'>ARHAM TRADERS</h2><p style='color:#38bdf8;'>DEV BY PRATHAM MEHTA</p>", unsafe_allow_html=True)
        rem = (datetime.strptime(st.session_state.valid, "%Y-%m-%d").date() - date.today()).days if st.session_state.valid else 0
        st.write(f"👤 Trader: **{st.session_state.user}**")
        st.write(f"⏳ **{rem} Days Left**")
        if st.button("Logout", use_container_width=True): st.session_state.auth = False; st.rerun()

    st.markdown("<h2 style='color:#ffbe0b; margin:0;'>⚡ DELTA ANALYSIS — SPREAD RADAR</h2>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    f_stock = c1.selectbox("STOCK", ["ALL STOCKS", "NIFTY", "BANKNIFTY", "HDFCBANK", "RELIANCE", "TCS", "SBIN"])
    f_type = c2.selectbox("TYPE", ["Futures Calendar Spread", "Call Spread (CE)", "Put Spread (PE)"])
    f_ratio = c3.selectbox("RATIO", ["1 : 1", "1 : 2", "2 : 1"])
    f_limit = c4.number_input("MAX DEBIT LIMIT Rs", value=2000, step=100)

    if st.button("🚀 SCAN BEST SPREADS NOW", use_container_width=True, type="primary"):
        st.toast("Refreshed!")

    st.markdown("---")
    st.subheader("💎 Best High-Probability Spreads (Individual Analysis)")

    data = {
        "NIFTY": {"near": 25380.5, "far": 25515.2, "lot": 75},
        "BANKNIFTY": {"near": 53680.0, "far": 53995.0, "lot": 35},
        "HDFCBANK": {"near": 1664.2, "far": 1678.8, "lot": 550},
        "RELIANCE": {"near": 1399.1, "far": 1413.5, "lot": 250},
        "TCS": {"near": 4265.0, "far": 4302.0, "lot": 175},
        "SBIN": {"near": 823.4, "far": 831.2, "lot": 750}
    }

    stocks = list(data.keys()) if f_stock == "ALL STOCKS" else [f_stock]
    for s in stocks:
        info = data[s]
        lot = info["lot"]
        if f_type == "Futures Calendar Spread":
            pts = round(info["far"] - info["near"], 2)
            pnl = round(pts * lot, 2)
            pct = round((pts / info["near"]) * 100, 2)
            advice = "⭐ High Premium Carry! Sell Far / Buy Near" if pct > 0.8 else ("🔥 Cheap Carry! Buy Far / Sell Near" if pct < 0.4 else "✅ Balanced Spread Range")

            st.markdown(f'''
            <div class="spread-card">
                <div class="card-title">
                    <span>{s} — Futures Calendar Spread</span>
                    <span style="color:#38bdf8;">Spread: +{pts} pts</span>
                </div>
                <div class="card-row">
                    <div class="card-col"><b>Leg 1 (Near):</b><br>Current Expiry @ Rs {info['near']}</div>
                    <div class="card-col"><b>Leg 2 (Far):</b><br>Next Expiry @ Rs {info['far']}</div>
                    <div class="card-col"><b>Lot Size:</b><br>{lot} shares</div>
                    <div class="card-col"><b>Total Risk / PnL:</b><br><span style="color:#10b981; font-weight:bold;">Rs {pnl}</span></div>
                    <div class="card-col"><b>Carry %:</b><br>{pct}% ({round(pct*12,1)}% p.a.)</div>
                </div>
                <div class="card-advice">🎯 <b>Action Advice:</b> {advice}</div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            diff = 12.50
            st.markdown(f'''
            <div class="spread-card">
                <div class="card-title">
                    <span>{s} — Option Spread ({f_ratio})</span>
                    <span style="color:#38bdf8;">Net Diff: Rs {diff}</span>
                </div>
                <div class="card-row">
                    <div class="card-col"><b>Buy Strike:</b><br>ATM Strike @ Rs 24.50</div>
                    <div class="card-col"><b>Sell Strike:</b><br>OTM Strike @ Rs 12.00</div>
                    <div class="card-col"><b>Lot Size:</b><br>{lot} shares</div>
                    <div class="card-col"><b>Total Risk / Lot:</b><br>Rs {round(diff * lot, 2)}</div>
                </div>
                <div class="card-advice">🎯 <b>Action Advice:</b> ✅ Defined Risk Spread. Good Theta Decay edge.</div>
            </div>
            ''', unsafe_allow_html=True)
            
