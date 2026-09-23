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

# ==================== 2. TERMINAL PAGE ====================
else:
    col_top1, col_top2 = st.columns([6, 1])
    with col_top1:
        st.markdown('<div style="font-family:\'Teko\',sans-serif; font-size:1.2rem; color:#ffffff; font-weight:900; letter-spacing:1px; padding: 5px 0; text-decoration:underline; text-decoration-color:#38bdf8;">⚡ ARHAM TRADERS | DEVELOPED BY PRATHAM MEHTA ⚡</div>', unsafe_allow_html=True)
    with col_top2:
        if st.button("🚪 Logout", use_keyword=False, use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    if os.path.exists("terminal.html"):
        # Explicitly reading with utf-8 encoding to prevent mojibake/garbled characters
        with open("terminal.html", "r", encoding="utf-8", errors="ignore") as f:
            html_content = f.read()
        
        html_content = html_content.replace("USER_NAME_PLACEHOLDER", str(st.session_state.username))
        html_content = html_content.replace("USER_TOKEN_PLACEHOLDER", str(st.session_state.upstox_token))
        html_content = html_content.replace("USER_ID_PLACEHOLDER", str(st.session_state.user_id))
        
        components.html(html_content, height=850, scrolling=True)
    else:
        st.error("⚠️ Error: GitHub repository mein 'terminal.html' file nahi mili! Kripya terminal.html file create karke apna poora code wahan save karein.")
        
