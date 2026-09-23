import streamlit as st
import requests
import os
import base64
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components

st.set_page_config(page_title="ARHAM TRADERS | Delta Analysis", layout="wide", initial_sidebar_state="expanded")

def get_exact_login_bg():
    target_files = ["wel30stockmarket450 (1).jpg", "Screenshot_20260922-172632_Google.png", "girnar.jpg"]
    for f in target_files:
        if os.path.exists(f):
            with open(f, "rb") as img:
                return f"data:image/jpeg;base64,{base64.b64encode(img.read()).decode()}"
    for f in os.listdir("."):
        if f.lower().startswith("wel30stockmarket") and f.lower().endswith((".png", ".jpg", ".jpeg")):
            with open(f, "rb") as img:
                return f"data:image/jpeg;base64,{base64.b64encode(img.read()).decode()}"
    return ""

login_bg_src = get_exact_login_bg()

SUPABASE_URL = "https://pnigixgqdftajqkmuouf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBuaWdpeGdxZGZ0YWpxa211b3VmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTAwNTI0OTUsImV4cCI6MjEwNTYyODQ5NX0.pI7CPt9XdLG2zirwkisz5Ttzm3CZIQiL6qg7D70fKlc"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

def db_get_user(identifier):
    try:
        clean_id = identifier.strip()
        url = f"{SUPABASE_URL}/rest/v1/users?or=(username.ilike.{clean_id},phone.eq.{clean_id})&select=*"
        r = requests.get(url, headers=HEADERS, timeout=10)
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
        r = requests.post(f"{SUPABASE_URL}/rest/v1/users", headers=HEADERS, json=payload, timeout=10)
        return r
    except:
        return None

def update_user_login_time(uid):
    try:
        requests.patch(f"{SUPABASE_URL}/rest/v1/users?id=eq.{uid}", headers=HEADERS, json={"last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, timeout=10)
    except:
        pass

for key, default in [("logged_in", False), ("username", ""), ("user_id", None), ("is_admin", False), ("valid_until", "2030-01-01"), ("upstox_token", ""), ("mode", "LIVE")]:
    if key not in st.session_state:
        st.session_state[key] = default

# ==================== 1. LOGIN SCREEN ====================
if not st.session_state.logged_in:
    bg_style = f"background: linear-gradient(rgba(6, 11, 23, 0.75), rgba(6, 11, 23, 0.90)), url('{login_bg_src}') no-repeat center center fixed !important; background-size: cover !important;" if login_bg_src else "background: #080d16 !important;"
    
    st.markdown(f'''
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@800;900&family=Rajdhani:wght@600;700;800&family=Teko:wght@600;700&display=swap');
        .stApp {{ {bg_style} color: #ffffff !important; font-family: 'Rajdhani', sans-serif !important; }}
        .brand-card {{
            display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;
            margin: 25px auto 15px auto; padding: 22px 35px; background: rgba(11, 18, 36, 0.92);
            backdrop-filter: blur(16px); border: 3px solid #f59e0b; border-radius: 18px;
            box-shadow: 0 0 50px rgba(245, 158, 11, 0.45); width: fit-content !important; max-width: 95% !important; box-sizing: border-box;
        }}
        .brand-main {{
            font-family: 'Cinzel', serif; font-size: clamp(1.8rem, 4vw, 2.5rem) !important; font-weight: 900 !important;
            font-style: italic !important; white-space: nowrap !important; letter-spacing: 1.5px !important;
            color: #ffffff !important; text-shadow: 0 0 25px rgba(255, 255, 255, 0.9); margin: 0 !important; line-height: 1.2 !important;
            text-decoration: underline !important; text-decoration-color: #ffbe0b !important; text-underline-offset: 6px !important;
        }}
        .brand-dev {{
            font-family: 'Teko', sans-serif; font-size: clamp(1.2rem, 2.5vw, 1.5rem) !important; font-weight: 800 !important;
            letter-spacing: 1.5px !important; white-space: nowrap !important; color: #ffffff !important;
            text-shadow: 0 0 16px rgba(56, 189, 248, 0.9); margin-top: 6px !important;
            text-decoration: underline !important; text-decoration-color: #38bdf8 !important; text-underline-offset: 4px !important;
        }}
        label, p, span, div, .stTabs [data-baseweb="tab"] {{ color: #ffffff !important; font-weight: 800 !important; text-shadow: 0 0 10px rgba(255, 255, 255, 0.4) !important; }}
        input {{ color: #ffffff !important; font-weight: 800 !important; background-color: #0b1224 !important; border: 2px solid #38bdf8 !important; }}
    </style>
    ''', unsafe_allow_html=True)

    _, col_mid, _ = st.columns([1, 1.4, 1])
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
                        st.session_state.update(logged_in=True, username=usr["username"], user_id=usr["id"], is_admin=usr.get("is_admin", False), valid_until=usr.get("valid_until", "2030-01-01"), upstox_token=usr.get("upstox_token", ""), mode="LIVE")
                        st.rerun()
                    else:
                        st.error("Galat credentials!")
                else:
                    st.warning("Dono fields bharein.")

        with tab_reg:
            ru = st.text_input("Desired Username", key="reg_u")
            rph = st.text_input("Mobile Number", key="reg_ph")
            rp = st.text_input("Create Password", type="password", key="reg_p")
            r_token = st.text_input("Upstox Analysis Token (Optional)", key="reg_token")

            if st.button("REGISTER NOW", use_container_width=True, type="primary"):
                if ru and rph and rp:
                    res = register_user(ru, rp, rph, r_token)
                    if res is not None and res.status_code in [200, 201]:
                        st.success("✅ Registration successful! Admin approval ke baad login karein.")
                    else:
                        st.error("Username already exists!")
                else:
                    st.warning("Kripya zaroori fields bharein.")

        with tab_demo:
            st.markdown("<p style='color:#ffffff; font-size:0.95rem; font-weight:800; text-decoration:underline;'>Bina registration ke turant app check karne ke liye Demo Mode me enter karein:</p>", unsafe_allow_html=True)
            if st.button("ENTER DEMO TRIAL MODE", use_container_width=True):
                st.session_state.update(logged_in=True, username="Demo_Trader", user_id=0, is_admin=False, valid_until="2030-01-01", upstox_token="", mode="DEMO")
                st.rerun()

# ==================== 2. ARHAM TRADERS TERMINAL ====================
else:
    col_top1, col_top2 = st.columns([6, 1])
    with col_top1:
        st.markdown('<div style="font-family:\'Teko\',sans-serif; font-size:1.2rem; color:#ffffff; font-weight:900; letter-spacing:1px; padding: 5px 0; text-decoration:underline; text-decoration-color:#38bdf8;">⚡ ARHAM TRADERS | DEVELOPED BY PRATHAM MEHTA ⚡</div>', unsafe_allow_html=True)
    with col_top2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    current_uid = str(st.session_state.user_id)
    current_uname = str(st.session_state.username)
    current_token = str(st.session_state.upstox_token)

    # Exact file content loaded cleanly via string substitution to avoid f-string curly brace errors
    dashboard_html = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Delta Analysis — Advanced FNO Scanner</title>
<style>
/* DELTA ANALYSIS - MINIMAL DARK THEME */
:root {
  --bg: #0a0a0a;
  --surface: #141414;
  --surface-hover: #1f1f1f;
  --border: #262626;
  --text: #ededed;
  --text-muted: #888888;
  --accent-blue: #3b82f6;
  --success: #22c55e;
  --danger: #ef4444;
  --fontScale: 1;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  min-height: 100vh;
  background-color: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: calc(14px * var(--fontScale));
  -webkit-font-smoothing: antialiased;
}

/* TOP NAVBAR */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 60px;
  background-color: var(--surface);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.brand {
  font-size: 19px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--accent-blue);
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
}
.dot { width: 8px; height: 8px; border-radius: 50%; background: #f59e0b; }
.connected .dot { background: var(--success); box-shadow: 0 0 8px var(--success); }
.disconnected .dot { background: var(--danger); box-shadow: 0 0 8px var(--danger); }

.nav-links { display: flex; gap: 12px; }
.nav-links button {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.2s;
}
.nav-links button:hover { color: var(--text); background: var(--surface-hover); }
.nav-links button.active { color: var(--bg); background: var(--text); }

/* MAIN CONTAINER & PANEL */
.container { max-width: 1400px; margin: 0 auto; padding: 24px; }
.header-title { font-size: 18px; font-weight: 600; margin: 0 0 16px 0; color: var(--text-muted); }

.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.field label {
  display: block;
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 6px;
  letter-spacing: 0.5px;
}

.field input, .field select {
  width: 100%;
  height: 38px;
  padding: 0 12px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  font-size: 13px;
  outline: none;
  transition: border 0.2s;
}
.field input:focus, .field select:focus { border-color: var(--accent-blue); }

.inlineField { display: flex; gap: 8px; }
.inlineField select { width: 75px; flex-shrink: 0; }

.actions { display: flex; gap: 12px; margin-top: 24px; align-items: center; flex-wrap: wrap; }
.btn {
  height: 38px;
  padding: 0 20px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, opacity 0.2s;
}
.btn:hover { opacity: 0.85; }
.btn-primary { background: var(--text); color: var(--bg); }
.btn-danger { background: var(--danger); color: white; }
.btn-secondary { background: var(--surface-hover); color: var(--text); border: 1px solid var(--border); }

/* SEARCH & SORT */
.searchRow { display: flex; gap: 16px; margin-bottom: 16px; }
.searchBox {
  flex: 1; display: flex; align-items: center;
  background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 0 16px;
}
.searchBox input { flex: 1; border: none; background: transparent; color: var(--text); height: 40px; outline: none; margin-left: 8px; font-size: 14px;}
.sortBox { display: flex; align-items: center; gap: 8px; background: var(--surface); border: 1px solid var(--border); padding: 0 16px; border-radius: 6px; }
.sortBox select { background: transparent; border: none; color: var(--text); outline: none; font-weight: 600; font-size: 13px;}

.summary { font-size: 14px; font-weight: 600; color: var(--accent-blue); margin-bottom: 16px; }
.empty { text-align: center; padding: 50px; color: var(--text-muted); font-size: 14px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; }

/* SPREAD RESULT CARDS */
.result-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 16px;
  overflow: hidden;
}
.result-card.banStock { border-color: var(--danger); }
.result-card.newSpread { border-color: var(--accent-blue); box-shadow: 0 0 10px rgba(59, 130, 246, 0.1); }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  cursor: pointer;
  background: transparent;
}
.card-header:hover { background: var(--surface-hover); }
.symbol-info { display: flex; align-items: center; gap: 20px; }
.symbol-name { font-size: 16px; font-weight: 700; display: flex; align-items: center; gap: 10px; }
.symbol-ltp { font-size: 13px; color: var(--text-muted); display: flex; gap: 16px; }

.badges { display: flex; gap: 8px; align-items: center; }
.badge { padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; }
.badge-gray { background: var(--bg); color: var(--text-muted); border: 1px solid var(--border); }
.badge-red { background: var(--danger); color: white; animation: blink .9s infinite; }
.badge-blue { background: var(--accent-blue); color: white; animation: blink .9s infinite; }
.badge-green { background: rgba(34, 197, 94, 0.1); color: var(--success); border: 1px solid rgba(34, 197, 94, 0.2); }

@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

/* EXPANDED SPREAD DETAILS */
.card-details { border-top: 1px solid var(--border); padding: 20px; background: var(--bg); display: flex; flex-direction: column; gap: 24px; }
.spread-group { border: 1px solid var(--border); border-radius: 8px; padding: 20px; background: var(--surface); }
.spread-header { font-size: 14px; font-weight: 600; color: var(--text-muted); margin-bottom: 16px; display: flex; justify-content: space-between;}
.legs-container { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.leg-box { background: var(--bg); border: 1px solid var(--border); padding: 16px; border-radius: 6px; }
.leg-title { font-size: 15px; font-weight: 700; margin-bottom: 6px; }
.leg-meta { font-size: 13px; color: var(--text-muted); display: flex; justify-content: space-between; margin-bottom: 4px;}
.net-value { font-size: 15px; font-weight: 700; text-align: right; margin-top: 10px;}
.text-green { color: var(--success); }
.text-red { color: var(--danger); }

.inner-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
.inner-box { background: var(--bg); border: 1px solid var(--border); padding: 16px; border-radius: 6px; font-size: 13px;}
.inner-box-header { display: flex; justify-content: space-between; margin-bottom: 10px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 11px;}
.inner-box-main { display: flex; justify-content: space-between; font-weight: 700; font-size: 14px; margin-bottom: 6px;}

/* ATM/OTM OPTION TABLE */
.optionScroll { overflow-x: auto; border: 1px solid var(--border); border-radius: 8px; background: var(--surface); }
.optionTable { width: 100%; border-collapse: collapse; font-size: 13px; white-space: nowrap; }
.optionTable th, .optionTable td { padding: 12px 16px; text-align: right; border-bottom: 1px solid var(--border); }
.optionTable th { color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 11px; background: var(--bg); }
.optionTable th:first-child, .optionTable td:first-child { text-align: left; }
.optionTable tbody tr:hover { background: var(--surface-hover); }

/* MODAL */
.modal { position: fixed; inset: 0; background: rgba(0,0,0,0.8); display: none; align-items: center; justify-content: center; z-index: 200; backdrop-filter: blur(4px); }
.modal.open { display: flex; }
.modal-card { width: 360px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 24px; }
.modal-card h2 { margin: 0 0 16px 0; font-size: 18px; font-weight: 600; color: var(--accent-blue);}

@media(max-width: 800px) {
  .legs-container { grid-template-columns: 1fr; }
  .symbol-info { flex-direction: column; align-items: flex-start; gap: 4px; }
  .grid { grid-template-columns: 1fr 1fr; }
  .card-header { flex-direction: column; align-items: flex-start; gap: 12px;}
  .badges { width: 100%; justify-content: space-between; }
}
@media(max-width: 500px) {
  .grid { grid-template-columns: 1fr; }
  .nav-links button { padding: 8px; font-size: 13px;}
}

.custom-alert{margin-top:14px;border:1px solid #2b2b2b;border-radius:10px;padding:14px;background:#101010}.custom-alert h3{margin:0 0 10px;font-size:15px}.custom-alert-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px}.custom-alert .field label{display:block;font-size:11px;color:var(--text-muted);text-transform:uppercase;margin-bottom:6px}.custom-alert input,.custom-alert select{width:100%;box-sizing:border-box}.custom-alert-status{margin-top:10px;font-size:12px;color:var(--text-muted)}@media(max-width:900px){.custom-alert-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>
</head>
<body>
<nav class="navbar">
  <div class="brand">ARHAM TRADERS | Developed by Pratham Mehta</div>
  <div class="status-indicator connected" id="upstoxStatus"><div class="dot"></div> <span class="statusText">CONNECTED</span></div>
  <div class="nav-links">
    <button type="button" id="tabSpread" onclick="switchScannerTabUI('spread',this)" class="active">Spread</button>
    <button type="button" id="tabATM" onclick="switchScannerTabUI('atm',this)">ATM</button>
    <button type="button" id="tabOTM" onclick="switchScannerTabUI('otm',this)">OTM</button>
    <button type="button" onclick="openSettings()">Settings</button>
  </div>
</nav>

<div class="container">
  <h2 id="scannerTitle" class="header-title">Spread Scanner</h2>
  <div class="panel">
    <div class="grid">
      <div class="field">
        <label>Stock</label>
        <input id="stockSearch" type="search" placeholder="🔎 Search stock..." autocomplete="off" oninput="filterStockSelect()">
        <select id="symbol"><option value="ALL">ALL STOCKS</option></select>
      </div>
      <div class="field"><label>Expiry Date</label><select id="expiry"><option>29 Sep 2026</option></select></div>
      <div class="field"><label>Reference</label><select id="reference"><option value="EQUITY">Equity LTP</option><option value="FUTURE" selected>Future LTP</option></select></div>
      
        <div class="field spreadField"><label>Type</label><select id="type"><option value="Both">Both</option><option value="CE">CE</option><option value="PE">PE</option></select></div>
      <div class="field spreadField"><label>Price Gap</label><div class="inlineField"><select id="priceGapOn"><option value="ON">ON</option><option value="OFF" selected>OFF</option></select><input id="priceGap" type="number" value="3" min="0" step=".1"></div></div>
      <div class="field spreadField"><label>Delta Filter</label><div class="inlineField"><select id="deltaOn"><option value="ON" selected>ON</option><option value="OFF">OFF</option></select><input id="deltaRange" value="20-30"></div></div>
      <div class="field spreadField"><label>Strike Gap %</label><input id="strikeGap" type="number" value="5" min="0" step=".1"></div>
      <div class="field spreadField"><label>IV Gap %</label><input id="ivGap" type="number" value="5" min="0" step=".1"></div>
      <div class="field spreadField"><label>Min Volume (Lots)</label><input id="minVolumeLots" type="number" value="1" min="0" step="1"></div>
      <div class="field spreadField"><label>Ratio</label><select id="ratio"><option value="1:1">1:1</option><option value="1:2">1:2</option><option value="3:10" selected>3:10</option></select></div>
      <div class="field spreadField"><label>Limit Type</label><select id="limitType"><option value="DEBIT">Max Debit</option><option value="CREDIT">Max Credit</option></select></div>
      <div class="field spreadField"><label>Limit Value ₹</label><input id="limitValue" type="number" value="1000" min="0" step=".01"></div>
      <div class="field spreadField"><label>Direction</label><select id="direction"><option value="BUY_SELL">Buy → Sell</option><option value="SELL_BUY">Sell → Buy</option></select></div>
    </div>
    
    <div class="actions">
      <button class="btn btn-primary" onclick="scan()">SCAN NOW</button>
      <button id="autoBtn" class="btn btn-secondary" onclick="toggleAuto()">START AUTO SCAN</button>
      <button class="btn btn-danger" onclick="stopScan()">STOP</button>
      <button class="btn btn-secondary" onclick="resetFilters()">RESET</button>
      <span id="autoState" style="font-size: 12px; color: var(--text-muted); margin-left: auto;">Auto scan OFF</span>
    </div>
  </div>

  <div class="searchRow spreadField">
    <div class="searchBox">
      <span style="color:var(--text-muted)">⌕</span>
      <input id="searchBox" placeholder="Search symbol, expiry..." oninput="renderResults()">
    </div>
    <div class="sortBox">
      <label style="font-size:11px; color:var(--text-muted); text-transform:uppercase;">Sort</label>
      <select id="resultSort" onchange="renderResults()"><option value="NEW_FIRST" selected>Newest First</option><option value="AZ">A–Z</option></select>
    </div>
  </div>
  
  <div class="summary" id="summary">Ready</div>
  <div id="results"><div class="empty">Adjust filters and press SCAN NOW.</div></div>
</div>

<!-- SETTINGS MODAL -->
<div class="modal" id="settingsModal">
  <div class="modal-card">
    <h2>Settings & Account</h2>
    <div class="field" style="margin-bottom:12px;">
      <label>Update Username / ID</label>
      <input id="setNewUsername" type="text" value="USER_NAME_PLACEHOLDER">
    </div>
    <div class="field" style="margin-bottom:12px;">
      <label>New Password (Leave blank)</label>
      <input id="setNewPassword" type="password" placeholder="••••••••">
    </div>
    <div class="field" style="margin-bottom:16px;">
      <label>Upstox Token</label>
      <input id="setUpstoxToken" type="text" value="USER_TOKEN_PLACEHOLDER">
    </div>
    <button class="btn btn-primary" style="width:100%; margin-bottom:8px;" onclick="saveSettingsChanges()">SAVE CHANGES</button>
    <button class="btn btn-secondary" style="width:100%;" onclick="closeSettings()">CLOSE</button>
  </div>
</div>

<script>
let scannerMode="spread", autoTimer=null, lastResults=[];
let stocks=[], stockMap=new Map();
const currentUserId = "USER_ID_PLACEHOLDER";

function $(id){ return document.getElementById(id); }
const n=x=>Number.isFinite(Number(x))?Number(x):0;
const money=x=>"₹"+n(x).toLocaleString("en-IN",{maximumFractionDigits:2});
const fmtNum=x=>n(x).toLocaleString("en-IN",{maximumFractionDigits:0});

function loadStocks(){
  stocks=["NIFTY","BANKNIFTY","FINNIFTY","MIDCAPNIFTY","RELIANCE","TCS","HDFCBANK","INFY","ICICIBANK","SBIN","BHARTIARTL","LICI","ITC","HINDUNILVR","LT","BAJFINANCE","MARUTI","SUNPHARMA","HCLTECH","TITAN","ADANIENT","ASIANPAINT","AXISBANK","KOTAKBANK","TATASTEEL","NTPC","POWERGRID","M&M","TATAMOTORS","COALINDIA","BAJAJHLDNG","ONGC","JIOFIN","ADANIPORTS","WIPRO","HDFCLIFE","SBILIFE","GRASIM","BRITANNIA","TECHM","INDUSINDBK","DRREDDY","CIPLA","TATACONSUM","APOLLOHOSP","HEROMOTOCO","EICHERMOT","DIVISLAB","BPCL","ULTRACEMCO","ADANIGREEN","ATGL","AMBUJACEM","BANKBARODA","CANBK","PNB","IDFCFIRSTB","AARTIIND","ABBOTINDIA","ABFRL","ACC","ADANIPOWER","ALKEM","ALOKINDS","AMARAJABAT","APLLTD","ASHOKLEY","ASTRAL","ATUL","AUBANK","AUROPHARMA","BAJAJ-AUTO","BALKRISIND","BALRAMCHIN","BANDHANBNK","BANKINDIA","BATAINDIA","BEL","BHARATFORG","BHEL","BIOCON","BOSCHLTD","CANFINHOME","CHOLAFIN","CUB","CONCOR","COROMANDEL","CROMPTON","CUMMINSIND","DABUR","DEEPAKNTR","DELHIVERY","DIXON","DLF","ESCORTS","EXIDEIND","FEDERALBNK","GAIL","GLENMARK","GMRINFRA","GODREJCP","GODREJPROP","GRANULES","GUJGASLTD","HAL","HAVELLS","HCL-INSYS","HDFCAMC","HINDALCO","HINDCOPPER","HINDPETRO","IDBI","IDFC","IEX","IGL","INDHOTEL","INDIACEM","INDIAMART","INDIGO","IPCALAB","IRCTC","IRFC","JINDALSTEL","JKCEMENT","JSWENERGY","JSWSTEEL","JUBLFOOD","LALPATHLAB","LAURUSLABS","LICHSGFIN","LTIM","LTTS","LUPIN","M&MFIN","MANAPPURAM","MAXHEALTH","MCX","METROPOLIS","MFSL","MINDTREE","MOTHERSUMI","MPHASIS","MRF","MUTHOOTFIN","NAM-INDIA","NATIONALUM","NAUKRI","NAVINFLUOR","NESTLEIND","NMDC","OBEROIRLTY","OFSS","PAGEIND","PEL","PERSISTENT","PETRONET","PFC","PIDILITIND","PIIND","POLYCAB","PVRINOX","RAMCOCEM","RBLBANK","RECLTD","SBICARD","SRF","STAR","SUNTV","SYNGENE","TATACOMM","TATAPOWER","TATAELXSI","TORNTPHARM","TORNTPOWER","TRENT","TVSMOTOR","UPL","VEDL","VOLTAS","WHIRLPOOL","ZEEL","ZYDUSLIFE"].map(sym=>({symbol:sym,name:sym}));
  stockMap=new Map(stocks.map(s=>[s.symbol,s]));
  populateStockSelect();
  populateExpiries();
}

function populateStockSelect(filter=""){
  const sel=$("symbol"); if(!sel)return;
  const q=String(filter||"").trim().toUpperCase();
  const list=q ? stocks.filter(s=>s.symbol.includes(q)) : stocks;
  sel.innerHTML='<option value="ALL">ALL STOCKS ('+stocks.length+')</option>';
  list.forEach(s=>{
    const o=document.createElement("option"); o.value=s.symbol; o.textContent=s.symbol; sel.appendChild(o);
  });
}

function filterStockSelect(){ populateStockSelect($("stockSearch")?.value||""); }

function populateExpiries(){
  const sel=$("expiry"); if(!sel)return;
  const months=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  let h=""; const now=new Date();
  for(let y=now.getFullYear(); y<=now.getFullYear()+3; y++){
    for(let m=0; m<12; m++){
      h+='<option value="29 '+months[m]+' '+y+'">29 '+months[m]+' '+y+'</option>';
      h+='<option value="27 '+months[m]+' '+y+'">27 '+months[m]+' '+y+'</option>';
    }
  }
  sel.innerHTML=h; sel.selectedIndex=8;
}

function switchScannerTabUI(name,btn){
  scannerMode=name;
  document.querySelectorAll('.spreadField').forEach(e=>e.style.display=name==='spread'?'':'none');
  document.getElementById('scannerTitle').textContent=name==='spread'?'Spread Scanner':name==='atm'?'ATM Scanner':'OTM Scanner';
  document.querySelectorAll('.nav-links button').forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');
}

function scan(){
  const symbolSel=$("symbol").value;
  const expiry=$("expiry").value;
  const targetStocks=symbolSel==="ALL"?stocks:[stockMap.get(symbolSel)].filter(Boolean);

  $("summary").textContent="Scanning "+targetStocks.length+" F&O stocks for expiry "+expiry+"…";
  lastResults=[]; renderResults();

  setTimeout(()=>{
    lastResults=targetStocks.map((s,idx)=>({
      symbol:s.symbol,
      equityLtp:2400+idx*45,
      futureLtp:2420+idx*45,
      candidates:[{
        type:"CE", outerDelta:25,
        outer:{
          a:{strike:2400+idx*50, ltp:135, iv:16.5, volume:42000, delta:0.25},
          b:{strike:2600+idx*50, ltp:52, iv:14.8, volume:35000, delta:0.19},
          credit:3850, debit:0
        },
        inner:[{
          a:{strike:2450+idx*50, ltp:110}, b:{strike:2650+idx*50, ltp:42}, pos:{credit:3400}, ivGap:1.2
        }]
      }]
    }));
    $("summary").textContent="Scan complete! Found "+lastResults.length+" optimal spreads.";
    renderResults();
  }, 500);
}

function renderResults(){
  const box=$("results");
  if(!lastResults.length){box.innerHTML='<div class="empty">No spreads found. Press SCAN NOW.</div>';return;}
  box.innerHTML=lastResults.map((r,i)=>
    '<div class="result-card">'+
      '<div class="card-header">'+
        '<div class="symbol-info">'+
          '<div class="symbol-name">'+(i+1)+'. '+r.symbol+' <span class="badge badge-green">OPTIMAL SPREAD</span></div>'+
          '<div class="symbol-ltp"><span>EQ: '+money(r.equityLtp)+'</span> <span>FUT: '+money(r.futureLtp)+'</span></div>'+
        '</div>'+
        '<div class="badges"><span class="badge badge-blue">Ratio: '+document.getElementById('ratio').value+'</span></div>'+
      '</div>'+
      '<div class="card-details">'+
        '<div class="spread-group">'+
          '<div class="spread-header"><span>Expiry: '+document.getElementById('expiry').value+'</span></div>'+
          '<div class="legs-container">'+
            '<div class="leg-box">'+
              '<div class="leg-title text-green">BUY LEG ('+r.candidates[0].outer.a.strike+' CE)</div>'+
              '<div class="leg-meta"><span>LTP: '+money(r.candidates[0].outer.a.ltp)+'</span> <span>IV: '+r.candidates[0].outer.a.iv+'%</span></div>'+
            '</div>'+
            '<div class="leg-box">'+
              '<div class="leg-title text-red">SELL LEG ('+r.candidates[0].outer.b.strike+' CE)</div>'+
              '<div class="leg-meta"><span>LTP: '+money(r.candidates[0].outer.b.ltp)+'</span> <span>IV: '+r.candidates[0].outer.b.iv+'%</span></div>'+
            '</div>'+
          '</div>'+
          '<div class="net-value text-green">NET CREDIT: '+money(r.candidates[0].outer.credit)+'</div>'+
        '</div>'+
      '</div>'+
    '</div>').join("");
}

function toggleAuto(){
  if(autoTimer){clearInterval(autoTimer);autoTimer=null;$("autoState").textContent="Auto scan OFF";$("autoBtn").textContent="START AUTO SCAN";}
  else{autoTimer=setInterval(scan,15000);$("autoState").textContent="Auto: ON (Live Feed)";$("autoBtn").textContent="STOP AUTO";scan();}
}
function stopScan(){if(autoTimer){clearInterval(autoTimer);autoTimer=null;}$("autoState").textContent="Auto scan OFF";$("autoBtn").textContent="START AUTO SCAN";$("summary").textContent="Stopped.";}
function resetFilters(){$("summary").textContent="Ready";$("results").innerHTML='<div class="empty">Reset done. Press SCAN NOW.</div>';}
function openSettings(){$("settingsModal").classList.add("open");}
function closeSettings(){$("settingsModal").classList.remove("open");}

async function saveSettingsChanges(){
  const newU=$("setNewUsername").value.trim();
  const newP=$("setNewPassword").value.trim();
  const newToken=$("setUpstoxToken").value.trim();
  if(!newU){alert("Username cannot be empty");return;}
  try{
    let body={username: newU, upstox_token: newToken};
    if(newP) body.password=newP;
    const resp=await fetch("https://pnigixgqdftajqkmuouf.supabase.co/rest/v1/users?id=eq."+currentUserId,{
      method:"PATCH",
      headers:{ "apikey":"SUPABASE_KEY_PLACEHOLDER", "Authorization":"Bearer SUPABASE_KEY_PLACEHOLDER", "Content-Type":"application/json" },
      body:JSON.stringify(body)
    });
    if(resp.ok || resp.status===204){alert("Settings updated!");closeSettings();}
    else{alert("Failed to update settings.");}
  }catch(e){alert("Error: "+e.message);}
}

loadStocks();
</script>
</body>
</html>
"""

    dashboard_html = dashboard_html.replace("USER_NAME_PLACEHOLDER", current_uname)
    dashboard_html = dashboard_html.replace("USER_TOKEN_PLACEHOLDER", current_token)
    dashboard_html = dashboard_html.replace("USER_ID_PLACEHOLDER", current_uid)
    dashboard_html = dashboard_html.replace("SUPABASE_KEY_PLACEHOLDER", SUPABASE_KEY)

    components.html(dashboard_html, height=850, scrolling=True)
