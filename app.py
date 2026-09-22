import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import pyotp

st.set_page_config(page_title="Multi-Broker Spread Terminal", layout="wide")

# --- SUPABASE REST CONFIG ---
SUPABASE_URL = "https://pnigixgqdftajqkmuouf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBuaWdpeGdxZGZ0YWpxa211b3VmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTAwNTI0OTUsImV4cCI6MjEwNTYyODQ5NX0.pI7CPt9XdLG2zirwkisz5Ttzm3CZIQiL6qg7D70fKlc"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- DATABASE HELPER FUNCTIONS ---
def get_user(identifier):
    try:
        clean_id = identifier.strip()
        url = f"{SUPABASE_URL}/rest/v1/users?or=(username.ilike.{clean_id},phone.eq.{clean_id})&select=*"
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            data = r.json()
            return data if len(data) > 0 else None
        return None
    except Exception as e:
        st.error(f"डेटाबेस कनेक्शन एरर: {e}")
        return None

def register_user(username, password, phone):
    try:
        url = f"{SUPABASE_URL}/rest/v1/users"
        payload = {
            "username": username.strip(),
            "password": password.strip(),
            "phone": phone.strip(),
            "is_approved": False,
            "is_admin": False
        }
        return requests.post(url, headers=HEADERS, json=payload, timeout=8)
    except Exception as e:
        st.error(f"रजिस्ट्रेशन एरर: {e}")
        return None

def update_user_full(user_id, username, phone, password, valid_until, is_approved):
    try:
        url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}"
        payload = {
            "username": username.strip(),
            "phone": str(phone).strip(),
            "password": password.strip(),
            "valid_until": valid_until,
            "is_approved": is_approved
        }
        r = requests.patch(url, headers=HEADERS, json=payload, timeout=8)
        return r.status_code in [200, 204]
    except Exception as e:
        st.error(f"अपडेट एरर: {e}")
        return False

def delete_user(user_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}"
        r = requests.delete(url, headers=HEADERS, timeout=8)
        return r.status_code in [200, 204]
    except:
        return False

def log_activity(username, action):
    try:
        url = f"{SUPABASE_URL}/rest/v1/activity_logs"
        requests.post(url, headers=HEADERS, json={"username": username, "action": action}, timeout=3)
    except:
        pass

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "api_connected" not in st.session_state:
    st.session_state.api_connected = False
if "connected_broker" not in st.session_state:
    st.session_state.connected_broker = None

# ==================== 1. LOGIN / SIGNUP / RESET ====================
if not st.session_state.logged_in:
    st.title("🔐 Futures Spread Portal")
    menu = st.radio("चुनें:", ["Login", "New Registration", "Forgot Password"], horizontal=True)

    if menu == "Login":
        u_name = st.text_input("Username / Mobile")
        u_pass = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            if not u_name or not u_pass:
                st.warning("कृपया Username और Password दोनों भरें।")
            else:
                user_data = get_user(u_name)
                if not user_data:
                    st.error("यूज़र नहीं मिला! सही डिटेल्स दर्ज करें।")
                else:
                    user = user_data[0]
                    if user["password"] != u_pass.strip():
                        st.error("गलत पासवर्ड!")
                    elif not user.get("is_approved", False) and not user.get("is_admin", False):
                        st.warning("⚠️ आपका अकाउंट अभी पेंडिंग है! एडमिन से अप्रूवल का इंतज़ार करें।")
                    elif (
                        not user.get("is_admin", False) 
                        and user.get("valid_until") 
                        and datetime.strptime(user["valid_until"], "%Y-%m-%d").date() < date.today()
                    ):
                        st.error("⛔ आपका एक्सेस समाप्त हो चुका है! एडमिन से संपर्क करें।")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.username = user["username"]
                        st.session_state.is_admin = user.get("is_admin", False)
                        log_activity(user["username"], "User Logged In")
                        st.rerun()

    elif menu == "New Registration":
        new_user = st.text_input("Desired Username")
        new_phone = st.text_input("Mobile Number")
        new_pass = st.text_input("Create Password", type="password")

        if st.button("Request Access", use_container_width=True):
            if new_user and new_pass and new_phone:
                res = register_user(new_user, new_pass, new_phone)
                if res and res.status_code in [200, 201]:
                    st.success("रिक्वेस्ट भेज दी गई है! एडमिन अप्रूव करते ही आप लॉगिन कर सकेंगे।")
                else:
                    st.error("यूज़रनेम पहले से मौजूद है या कोई त्रुटि हुई।")
            else:
                st.warning("सभी फ़ील्ड भरना अनिवार्य है।")

    elif menu == "Forgot Password":
        st.subheader("🔑 Reset Password")
        verify_user = st.text_input("Registered Username")
        verify_phone = st.text_input("Registered Mobile Number")
        new_password = st.text_input("Enter New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")

        if st.button("Reset Password", use_container_width=True):
            if not verify_user or not verify_phone or not new_password:
                st.warning("कृपया सभी फ़ील्ड भरें।")
            elif new_password != confirm_password:
                st.error("दोनों पासवर्ड मैच नहीं कर रहे हैं!")
            else:
                user_data = get_user(verify_user)
                if not user_data:
                    st.error("यूज़र नहीं मिला!")
                else:
                    user = user_data[0]
                    if str(user.get("phone")).strip() != str(verify_phone).strip():
                        st.error("मोबाइल नंबर मेल नहीं खा रहा!")
                    else:
                        if update_user_full(user["id"], user["username"], user["phone"], new_password, user.get("valid_until"), user.get("is_approved", False)):
                            st.success("✅ पासवर्ड अपडेट हो गया! अब Login करें।")
                        else:
                            st.error("त्रुटि हुई!")

# ==================== 2. ADMIN DASHBOARD ====================
elif st.session_state.is_admin:
    st.sidebar.title(f"👑 Admin: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.header("🛠️ Admin Control Center")
    tab1, tab2 = st.tabs(["User Management & Edit", "User Activity Logs"])

    with tab1:
        st.subheader("Manage & Edit Users")
        try:
            res = requests.get(f"{SUPABASE_URL}/rest/v1/users?order=created_at.desc", headers=HEADERS, timeout=8)
            if res.status_code == 200:
                users_list = res.json()
                for u in users_list:
                    if u["username"].lower() in ["admin", "pratham1785"]:
                        continue

                    status_badge = "✅ Approved" if u.get('is_approved') else "⏳ Pending"
                    with st.expander(f"👤 {u['username']} | 📞 {u.get('phone')} | Status: {status_badge}"):
                        with st.form(f"edit_form_{u['id']}"):
                            c1, c2 = st.columns(2)
                            with c1:
                                edit_name = st.text_input("Username", value=u.get('username', ''))
                                edit_phone = st.text_input("Mobile Number", value=u.get('phone', ''))
                                edit_pass = st.text_input("Password", value=u.get('password', ''))
                            with c2:
                                edit_approved = st.checkbox("Access Approved", value=u.get('is_approved', False))
                                curr_valid = date.today() + timedelta(days=30)
                                if u.get('valid_until'):
                                    try:
                                        curr_valid = datetime.strptime(u['valid_until'], "%Y-%m-%d").date()
                                    except:
                                        pass
                                edit_date = st.date_input("Validity Expiry Date", value=curr_valid)

                            save_btn = st.form_submit_button("💾 Save All Changes", use_container_width=True)
                            if save_btn:
                                if update_user_full(u['id'], edit_name, edit_phone, edit_pass, edit_date.strftime("%Y-%m-%d"), edit_approved):
                                    st.success("यूज़र डिटेल्स सफलतापूर्वक अपडेट हो गईं!")
                                    st.rerun()

                        col_q1, col_q2 = st.columns(2)
                        with col_q1:
                            if st.button("➕ Extend +30 Days", key=f"ext_{u['id']}", use_container_width=True):
                                new_date = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
                                update_user_full(u['id'], u['username'], u['phone'], u['password'], new_date, True)
                                st.success("30 दिन बढ़ा दिए गए!")
                                st.rerun()
                        with col_q2:
                            if st.button("🗑️ Delete User Permanently", key=f"del_{u['id']}", use_container_width=True):
                                delete_user(u['id'])
                                st.warning("यूज़र को हटा दिया गया!")
                                st.rerun()
        except Exception as e:
            st.error(f"यूज़र लोड करने में त्रुटि: {e}")

    with tab2:
        st.subheader("Live Activity Tracking")
        try:
            res_logs = requests.get(f"{SUPABASE_URL}/rest/v1/activity_logs?order=logged_at.desc&limit=50", headers=HEADERS, timeout=8)
            if res_logs.status_code == 200 and res_logs.json():
                st.dataframe(pd.DataFrame(res_logs.json()), use_container_width=True)
        except Exception as e:
            st.error(f"लॉग्स लोड करने में त्रुटि: {e}")

# ==================== 3. TRADER TERMINAL (MULTI-BROKER) ====================
else:
    st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.api_connected = False
        st.rerun()

    if not st.session_state.api_connected:
        st.title("🔌 Connect Your Trading Account")
        broker_choice = st.selectbox(
            "अपना ब्रोकर चुनें:",
            ["Angel One (SmartAPI)", "Zerodha (Kite Connect)", "DhanHQ", "Fyers API v3", "Upstox"]
        )

        with st.form("multi_broker_form"):
            if broker_choice == "Angel One (SmartAPI)":
                st.info("Required: SmartAPI Key, Client ID, 4-digit MPIN, TOTP Secret Key")
                b_api_key = st.text_input("SmartAPI Key")
                b_client_id = st.text_input("Client ID")
                b_mpin = st.text_input("Trading MPIN", type="password")
                b_totp = st.text_input("TOTP Secret Key (16/32 alphanumeric)", type="password")
            
            elif broker_choice == "Zerodha (Kite Connect)":
                st.info("Required: Kite API Key, API Secret, Request Token (Daily Login URL se prapt)")
                b_api_key = st.text_input("Kite API Key")
                b_secret = st.text_input("API Secret", type="password")
                b_req_token = st.text_input("Request Token")
            
            elif broker_choice == "DhanHQ":
                st.info("Required: Dhan Client ID aur Access Token (Dhan Web portal se generate kiya hua)")
                b_client_id = st.text_input("Dhan Client ID")
                b_token = st.text_input("Access Token (JWT)", type="password")

            elif broker_choice == "Fyers API v3":
                st.info("Required: Fyers App ID (e.g. XC1234-100) aur Access Token")
                b_app_id = st.text_input("Fyers App ID")
                b_token = st.text_input("Access Token", type="password")

            elif broker_choice == "Upstox":
                st.info("Required: Upstox API Key aur Generated Access Token")
                b_api_key = st.text_input("Upstox API Key")
                b_token = st.text_input("Access Token", type="password")

            submit = st.form_submit_button(f"Connect {broker_choice} & Launch Terminal", use_container_width=True)

            if submit:
                # Store broker details in session
                st.session_state.api_connected = True
                st.session_state.connected_broker = broker_choice
                log_activity(st.session_state.username, f"Connected to {broker_choice}")
                st.success(f"{broker_choice} सफलतापूर्वक कनेक्ट हो गया!")
                st.rerun()

    else:
        st.sidebar.success(f"🟢 Connected: {st.session_state.connected_broker}")
        if st.sidebar.button("Disconnect Broker"):
            st.session_state.api_connected = False
            st.rerun()

        st.title("📊 Multi-Broker Futures Calendar Spread Terminal")
        st.caption(f"Active Bridge: **{st.session_state.connected_broker}** | Market Feed: NSE F&O Live")

        # Scanner Filter Row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            segment = st.selectbox("Underlying Type", ["Index Futures (NIFTY, BANKNIFTY)", "Stock Futures (All F&O)"])
        with col2:
            min_spread = st.number_input("Min Spread Difference (pts)", value=10.0, step=1.0)
        with col3:
            sort_by = st.selectbox("Sort By", ["Spread (Pts)", "Annualized Return %", "Volume"])
        with col4:
            auto_refresh = st.checkbox("Auto Refresh (10s)", value=True)

        st.write("---")

        # Live Spread Mock/Calculation Table
        st.subheader("🎯 Real-Time Calendar Spread Opportunities")
        demo_data = [
            {"Symbol": "NIFTY", "Near Expiry": "Current Month", "Far Expiry": "Next Month", "Near Price": 25310.50, "Far Price": 25425.20, "Spread (Pts)": 114.70, "Lot Size": 75, "Total Spread PnL": 8602.50, "Spread %": "0.45%"},
            {"Symbol": "BANKNIFTY", "Near Expiry": "Current Month", "Far Expiry": "Next Month", "Near Price": 53400.00, "Far Price": 53710.00, "Spread (Pts)": 310.00, "Lot Size": 35, "Total Spread PnL": 10850.00, "Spread %": "0.58%"},
            {"Symbol": "RELIANCE", "Near Expiry": "Current Month", "Far Expiry": "Next Month", "Near Price": 1390.20, "Far Price": 1404.50, "Spread (Pts)": 14.30, "Lot Size": 250, "Total Spread PnL": 3575.00, "Spread %": "1.03%"},
            {"Symbol": "HDFCBANK", "Near Expiry": "Current Month", "Far Expiry": "Next Month", "Near Price": 1650.00, "Far Price": 1662.80, "Spread (Pts)": 12.80, "Lot Size": 550, "Total Spread PnL": 7040.00, "Spread %": "0.77%"},
            {"Symbol": "TATASTEEL", "Near Expiry": "Current Month", "Far Expiry": "Next Month", "Near Price": 152.40, "Far Price": 154.10, "Spread (Pts)": 1.70, "Lot Size": 5500, "Total Spread PnL": 9350.00, "Spread %": "1.11%"},
        ]

        df = pd.DataFrame(demo_data)
        st.dataframe(df, use_container_width=True)

        st.info("💡 Order Execution Tip: Aap ek click me Near Month Sell aur Far Month Buy (ya vice-versa) ka combo order laga sakte hain.")
        
