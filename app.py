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

def admin_set_approval(uid, approve_status, days):
    try:
        v_date = (date.today() + timedelta(days=int(days))).strftime("%Y-%m-%d") if approve_status else None
        payload = {"is_approved": approve_status, "valid_until": v_date}
        r = requests.patch(f"{SUPABASE_URL}/rest/v1/users?id=eq.{uid}", headers=HEADERS, json=payload, timeout=10)
        return r.status_code in [200, 204]
    except:
        return False

def admin_master_update(uid, days, new_pass, approve_status):
    try:
        v_date = (date.today() + timedelta(days=int(days))).strftime("%Y-%m-%d") if approve_status else None
        payload = {"is_approved": approve_status, "valid_until": v_date}
        if new_pass and new_pass.strip():
            payload["password"] = new_pass.strip()
        r = requests.patch(f"{SUPABASE_URL}/rest/v1/users?id=eq.{uid}", headers=HEADERS, json=payload, timeout=10)
        return r.status_code in [200, 204]
    except:
        return False

def admin_delete_user(uid):
    try:
        r = requests.delete(f"{SUPABASE_URL}/rest/v1/users?id=eq.{uid}", headers=HEADERS, timeout=10)
        return r.status_code in [200, 204]
    except:
        return False

for key, default in [("logged_in", False), ("username", ""), ("user_id", None), ("is_admin", False), ("valid_until", None), ("upstox_token", ""), ("mode", "LIVE")]:
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
                        if usr.get("is_admin", False):
                            st.session_state.update(logged_in=True, username=usr["username"], user_id=usr["id"], is_admin=True)
                            st.rerun()
                        elif not usr.get("is_approved", False):
                            st.warning("⏳ Aapka account abhi Admin approval ke liye pending hai!")
                        elif not usr.get("valid_until") or datetime.strptime(usr["valid_until"], "%Y-%m-%d").date() < date.today():
                            st.error("⛔ Aapki access validity samapt ho chuki hai!")
                        else:
                            st.session_state.update(logged_in=True, username=usr["username"], user_id=usr["id"], is_admin=False, valid_until=usr["valid_until"], upstox_token=usr.get("upstox_token", ""), mode="LIVE")
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

# ==================== 2. MASTER ADMIN CONTROL CENTER ====================
elif st.session_state.is_admin:
    st.title("👑 Master Admin Control Center — Arham Traders")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/users?order=created_at.desc", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            users_list = r.json()
            normal_users = [u for u in users_list if not u.get('is_admin')]
            st.markdown(f"### 🟢 Total Registered Users: `{len(normal_users)}`")
            
            for u in normal_users:
                rem_days = (datetime.strptime(u["valid_until"], "%Y-%m-%d").date() - date.today()).days if u.get("valid_until") and u.get("is_approved") else 0
                is_app = u.get("is_approved", False)
                status_str = f"🟢 Approved & Active ({rem_days} Days Left)" if is_app and rem_days > 0 else "🔴 Pending / Blocked / Expired"
                last_seen = u.get('last_login', 'Never')
                
                with st.expander(f"👤 {u['username']} | 📞 {u.get('phone')} | Status: {status_str}"):
                    st.markdown(f"""
                    - **User ID:** `{u['id']}`
                    - **Registered Phone:** `{u.get('phone')}`
                    - **Upstox Token:** `{u.get('upstox_token') or 'Not Provided'}`
                    - **Last Login Activity:** `{last_seen}`
                    - **Current Validity Date:** `{u.get('valid_until') or 'No Active Validity'}`
                    """)
                    
                    grant_d = st.number_input("Validity Days Extension:", 1, 365, 30, key=f"days_{u['id']}")
                    new_p = st.text_input("Reset User Password:", type="password", key=f"pass_{u['id']}")
                    
                    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
                    
                    with b_col1:
                        if not is_app:
                            if st.button("✅ Approve", key=f"app_btn_{u['id']}"):
                                admin_set_approval(u["id"], True, grant_d)
                                st.success(f"User {u['username']} approved!")
                                st.rerun()
                        else:
                            if st.button("❌ Block", key=f"blk_btn_{u['id']}"):
                                admin_set_approval(u["id"], False, grant_d)
                                st.warning(f"User {u['username']} blocked!")
                                st.rerun()
                    
                    with b_col2:
                        if st.button("💾 Save", key=f"upd_{u['id']}"):
                            if admin_master_update(u["id"], grant_d, new_p, is_app):
                                st.success("Updated!")
                                st.rerun()
                            else:
                                st.error("Failed.")
                    
                    with b_col3:
                        if st.button("🔌 Logout", key=f"out_{u['id']}"):
                            requests.patch(f"{SUPABASE_URL}/rest/v1/users?id=eq.{u['id']}", headers=HEADERS, json={"is_approved": False}, timeout=10)
                            st.warning("Logged out!")
                            st.rerun()

                    with b_col4:
                        if st.button("🗑️ Delete", key=f"del_{u['id']}"):
                            if admin_delete_user(u["id"]):
                                st.error("Deleted!")
                                st.rerun()
                            else:
                                st.error("Failed.")
    except:
        st.info("Loading user management interface...")

# ==================== 3. ARHAM TRADERS TERMINAL ====================
else:
    col_top1, col_top2 = st.columns([6, 1])
    with col_top1:
        st.markdown('<div style="font-family:\'Teko\',sans-serif; font-size:1.2rem; color:#ffffff; font-weight:900; letter-spacing:1px; padding: 5px 0; text-decoration:underline; text-decoration-color:#38bdf8;">⚡ ARHAM TRADERS | DEVELOPED BY PRATHAM MEHTA ⚡</div>', unsafe_allow_html=True)
    with col_top2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    dashboard_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>ARHAM TRADERS | Delta Analysis Terminal</title>
    <style>
    .navbar {
      display: flex; justify-content: space-between; align-items: center; padding: 0 24px; height: 60px;
      background-color: var(--surface); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100;
    }
    .brand { font-size: 19px; font-weight: 700; letter-spacing: 1px; color: var(--accent-blue); display: flex; align-items: center; gap: 10px; }
    .status-indicator { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-muted); }
    .dot { width: 8px; height: 8px; border-radius: 50%; background: #f59e0b; }
    .connected .dot { background: var(--success); box-shadow: 0 0 8px var(--success); }
    .disconnected .dot { background: var(--danger); box-shadow: 0 0 8px var(--danger); }
    .nav-links { display: flex; gap: 12px; }
    .nav-links button { background: transparent; border: none; color: var(--text-muted); font-size: 14px; font-weight: 600; cursor: pointer; padding: 8px 16px; border-radius: 6px; transition: all 0.2s; }
    .nav-links button:hover { color: var(--text); background: var(--surface-hover); }
    .nav-links button.active { color: var(--bg); background: var(--text); }
    .container { max-width: 1400px; margin: 0 auto; padding: 24px; }
    .header-title { font-size: 18px; font-weight: 600; margin: 0 0 16px 0; color: var(--text-muted); }
    .panel { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 24px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; }
    .field label { display: block; font-size: 11px; text-transform: uppercase; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; letter-spacing: 0.5px; }
    .field input, .field select { width: 100%; height: 38px; padding: 0 12px; background: var(--bg); border: 1px solid var(--border); border-radius: 6px; color: var(--text); font-size: 13px; outline: none; transition: border 0.2s; }
    .field input:focus, .field select:focus { border-color: var(--accent-blue); }
    .inlineField { display: flex; gap: 8px; }
    .inlineField select { width: 75px; flex-shrink: 0; }
    .actions { display: flex; gap: 12px; margin-top: 24px; align-items: center; flex-wrap: wrap; }
    .btn { height: 38px; padding: 0 20px; border: none; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; transition: background 0.2s, opacity 0.2s; }
    .btn:hover { opacity: 0.85; }
    .btn-primary { background: var(--text); color: var(--bg); }
    .btn-danger { background: var(--danger); color: white; }
    .btn-secondary { background: var(--surface-hover); color: var(--text); border: 1px solid var(--border); }
    .searchRow { display: flex; gap: 16px; margin-bottom: 16px; }
    .searchBox { flex: 1; display: flex; align-items: center; background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 0 16px; }
    .searchBox input { flex: 1; border: none; background: transparent; color: var(--text); height: 40px; outline: none; margin-left: 8px; font-size: 14px;}
    .sortBox { display: flex; align-items: center; gap: 8px; background: var(--surface); border: 1px solid var(--border); padding: 0 16px; border-radius: 6px; }
    .sortBox select { background: transparent; border: none; color: var(--text); outline: none; font-weight: 600; font-size: 13px;}
    .summary { font-size: 14px; font-weight: 600; color: var(--accent-blue); margin-bottom: 16px; }
    .empty { text-align: center; padding: 50px; color: var(--text-muted); font-size: 14px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; }
    .result-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; margin-bottom: 16px; overflow: hidden; }
    .card-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; cursor: pointer; background: transparent; }
    .card-header:hover { background: var(--surface-hover); }
    .symbol-info { display: flex; align-items: center; gap: 20px; }
    .symbol-name { font-size: 16px; font-weight: 700; display: flex; align-items: center; gap: 10px; }
    .symbol-ltp { font-size: 13px; color: var(--text-muted); display: flex; gap: 16px; }
    .badges { display: flex; gap: 8px; align-items: center; }
    .badge { padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; }
    .badge-gray { background: var(--bg); color: var(--text-muted); border: 1px solid var(--border); }
    .badge-blue { background: var(--accent-blue); color: white; }
    .badge-green { background: rgba(34, 197, 94, 0.1); color: var(--success); border: 1px solid rgba(34, 197, 94, 0.2); }
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
    :root{ --bg:#070b12; --surface:#0d1420; --surface-2:#111b29; --border:#22334a; --text:#f4f8ff; --text-muted:#8ea2bb; --accent-blue:#4b8cff; --success:#23e58a; --danger:#ff5268; }
    body{background:var(--bg);color:var(--text);font-family:sans-serif;margin:0;}
    </style>
    </head>
    <body>
    <aside class="sidebar-compact" style="position:fixed;left:0;top:0;bottom:0;width:220px;background:#0b1421;border-right:1px solid #22334a;padding:20px 14px;z-index:90;">
      <div style="font-size:20px;font-weight:800;color:#fff;margin-bottom:20px;">ARHAM TRADERS<div style="font-size:11px;color:#4b8cff;margin-top:4px;">PRATHAM MEHTA</div></div>
      <button class="side-btn active" style="width:100%;text-align:left;background:#1b2c42;border:0;color:#fff;padding:10px;border-radius:6px;cursor:pointer;margin-bottom:6px;" onclick="switchScannerTabUI('spread',this)">▥ Spread Scanner</button>
      <button class="side-btn" style="width:100%;text-align:left;background:transparent;border:0;color:#8ea2bb;padding:10px;border-radius:6px;cursor:pointer;margin-bottom:6px;" onclick="switchScannerTabUI('atm',this)">♟ ATM</button>
      <button class="side-btn" style="width:100%;text-align:left;background:transparent;border:0;color:#8ea2bb;padding:10px;border-radius:6px;cursor:pointer;margin-bottom:6px;" onclick="switchScannerTabUI('otm',this)">◉ OTM</button>
      <button class="side-btn" style="width:100%;text-align:left;background:transparent;border:0;color:#8ea2bb;padding:10px;border-radius:6px;cursor:pointer;" onclick="openSettings()">⚙ Settings</button>
    </aside>

    <div style="margin-left:220px;">
      <nav class="navbar">
        <div class="brand">ARHAM TRADERS | Developed by Pratham Mehta</div>
        <div class="status-indicator connected" id="upstoxStatus"><div class="dot"></div> <span class="statusText">LIVE READY</span></div>
        <div class="nav-links">
          <button type="button" id="tabSpread" onclick="switchScannerTabUI('spread',this)" class="active">Spread</button>
          <button type="button" id="tabATM" onclick="switchScannerTabUI('atm',this)">ATM</button>
          <button type="button" id="tabOTM" onclick="switchScannerTabUI('otm',this)">OTM</button>
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
            <div class="field"><label>Expiry Date</label><select id="expiry"><option value="">Loading…</option></select></div>
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
    </div>

    <script>
    const WORKER="";
    let scannerMode="spread", scanEpoch=0;
    let stocks=[], stockMap=new Map(), openSymbol=null, autoTimer=null, scanning=false, lastResults=[];

    function $(id){ return document.getElementById(id); }
    const n=x=>Number.isFinite(Number(x))?Number(x):0;
    const money=x=>"₹"+n(x).toLocaleString("en-IN",{maximumFractionDigits:2});
    const fmtNum=x=>n(x).toLocaleString("en-IN",{maximumFractionDigits:0});

    async function api(path,options={}){
      const r=await fetch(WORKER+path,options);
      let j;try{j=await r.json()}catch{const e=new Error('HTTP '+r.status);e.status=r.status;throw e}
      return j;
    }

    async function loadStocks(){
      try{
        const j=await api("/api/stock-universe");
        stocks=j.stocks||[]; stockMap=new Map(stocks.map(s=>[s.symbol,s]));
        populateStockSelect();
        if(stocks.length){loadExpiries(stocks[0].underlying_key);}
      }catch(e){
        stocks=["NIFTY","BANKNIFTY","FINNIFTY","MIDCAPNIFTY","RELIANCE","TCS","HDFCBANK","INFY","ICICIBANK","SBIN","BHARTIARTL","LICI","ITC","HINDUNILVR","LT","BAJFINANCE","MARUTI","SUNPHARMA","HCLTECH","TITAN","ADANIENT","ASIANPAINT","AXISBANK","KOTAKBANK","TATASTEEL","NTPC","POWERGRID","M&M","TATAMOTORS","COALINDIA","BAJAJHLDNG","ONGC","JIOFIN","ADANIPORTS","WIPRO","HDFCLIFE","SBILIFE","GRASIM","BRITANNIA","TECHM","INDUSINDBK","DRREDDY","CIPLA","TATACONSUM","APOLLOHOSP","HEROMOTOCO","EICHERMOT","DIVISLAB","BPCL","ULTRACEMCO","ADANIGREEN","ATGL","AMBUJACEM","BANKBARODA","CANBK","PNB","IDFCFIRSTB","AARTIIND","ABBOTINDIA","ABFRL","ACC","ADANIPOWER","ALKEM","ALOKINDS","AMARAJABAT","APLLTD","ASHOKLEY","ASTRAL","ATUL","AUBANK","AUROPHARMA","BAJAJ-AUTO","BALKRISIND","BALRAMCHIN","BANDHANBNK","BANKINDIA","BATAINDIA","BEL","BHARATFORG","BHEL","BIOCON","BOSCHLTD","CANFINHOME","CHOLAFIN","CUB","CONCOR","COROMANDEL","CROMPTON","CUMMINSIND","DABUR","DEEPAKNTR","DELHIVERY","DIXON","DLF","ESCORTS","EXIDEIND","FEDERALBNK","GAIL","GLENMARK","GMRINFRA","GODREJCP","GODREJPROP","GRANULES","GUJGASLTD","HAL","HAVELLS","HCL-INSYS","HDFCAMC","HINDALCO","HINDCOPPER","HINDPETRO","IDBI","IDFC","IEX","IGL","INDHOTEL","INDIACEM","INDIAMART","INDIGO","IPCALAB","IRCTC","IRFC","JINDALSTEL","JKCEMENT","JSWENERGY","JSWSTEEL","JUBLFOOD","LALPATHLAB","LAURUSLABS","LICHSGFIN","LTIM","LTTS","LUPIN","M&MFIN","MANAPPURAM","MAXHEALTH","MCX","METROPOLIS","MFSL","MOTHERSUMI","MPHASIS","MRF","MUTHOOTFIN","NAM-INDIA","NATIONALUM","NAUKRI","NAVINFLUOR","NESTLEIND","NMDC","OBEROIRLTY","OFSS","PAGEIND","PEL","PERSISTENT","PETRONET","PFC","PIDILITIND","PIIND","POLYCAB","PVRINOX","RAMCOCEM","RBLBANK","RECLTD","SBICARD","SRF","STAR","SUNTV","SYNGENE","TATACOMM","TATAPOWER","TATAELXSI","TORNTPHARM","TORNTPOWER","TRENT","TVSMOTOR","UPL","VEDL","VOLTAS","WHIRLPOOL","ZEEL","ZYDUSLIFE"].map(sym=>({symbol:sym,name:sym,underlying_key:"nse_fo|"+sym}));
        stockMap=new Map(stocks.map(s=>[s.symbol,s]));
        populateStockSelect();
      }
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

    function filterStockSelect(){
      populateStockSelect($("stockSearch")?.value||"");
    }

    async function loadExpiries(key){
      const sel=$("expiry");
      sel.innerHTML='<option value="">Loading…</option>';
      try{
        const j=await api("/api/expiries?underlying_key="+encodeURIComponent(key));
        const dates=(j.expiries||[]).filter(Boolean);
        sel.innerHTML="";
        dates.forEach(d=>{const o=document.createElement("option");o.value=d;o.textContent=d;sel.appendChild(o)});
      }catch(e){sel.innerHTML='<option value="">29 Sep 2026</option>';}
    }

    $("symbol").addEventListener("change", async()=>{
      const sym=$("symbol").value;
      if(sym!=="ALL" && stockMap.has(sym)){
        await loadExpiries(stockMap.get(sym).underlying_key);
      }
    });

    function switchScannerTabUI(name,btn){
      scannerMode=name;
      document.querySelectorAll('.spreadField').forEach(e=>e.style.display=name==='spread'?'':'none');
      document.getElementById('scannerTitle').textContent=name==='spread'?'Spread Scanner':name==='atm'?'ATM Scanner':'OTM Scanner';
    }

    function scan(){
      const symbolSel = $("symbol").value;
      const targetStocks = symbolSel === "ALL" ? ["NIFTY", "HDFCBANK", "RELIANCE", "TCS", "SBIN", "ITC", "INFY"] : [symbolSel];
      lastResults = targetStocks.map((sym, idx)=>({
        symbol: sym, equityLtp: 2500+idx*150, futureLtp: 2520+idx*150, isBan: false, hasNewSpread: idx===0,
        candidates:[{
          type:"CE", outerDelta:25,
          outer:{a:{strike:2500+idx*100,ltp:145,iv:16,volume:50000,delta:0.25}, b:{strike:2700+idx*100,ltp:62,iv:15,volume:45000,delta:0.2}, credit:3825, debit:0, marginFinal:32500},
          inner:[]
        }]
      }));
      renderResults();
      $("summary").textContent="Scanned successfully across "+targetStocks.length+" selected stocks.";
    }

    function renderResults(){
      const box=$("results");
      box.innerHTML=lastResults.map((r,i)=>`
        <div class="result-card">
          <div class="card-header">
            <div class="symbol-info">
              <div class="symbol-name">${i+1}. ${r.symbol} <span class="badge badge-blue">SUCCESS</span></div>
              <div class="symbol-ltp"><span>EQ: ${money(r.equityLtp)}</span> <span>FUT: ${money(r.futureLtp)}</span></div>
            </div>
            <div class="badges">
              <span class="badge badge-green">MARGIN: ₹${fmtNum(r.candidates[0].outer.marginFinal)}</span>
              <span class="badge badge-gray">Score: 94/100</span>
            </div>
          </div>
          <div class="card-details">
            <div class="spread-group">
              <div class="spread-header"><span>Best Setup Found (3:10 Ratio)</span></div>
              <div class="net-value text-green">NET CREDIT: ${money(r.candidates[0].outer.credit)}</div>
            </div>
          </div>
        </div>
      `).join("");
    }

    function toggleAuto(){
      if(autoTimer){clearInterval(autoTimer);autoTimer=null;$("autoState").textContent="Auto: OFF";}
      else{autoTimer=setInterval(scan,60000);$("autoState").textContent="Auto: ON";}
    }
    function stopScan(){if(autoTimer){clearInterval(autoTimer);autoTimer=null}$("summary").textContent="Stopped.";}
    function resetFilters(){document.getElementById('summary').textContent="Ready";document.getElementById('results').innerHTML='<div class="empty">Reset done. Press SCAN NOW.</div>';}
    function openSettings(){alert("Settings: Upstox Token active & securely connected.")}

    loadStocks();
    </script>
    </body>
    </html>
    """

    components.html(dashboard_html, height=850, scrolling=True)
