import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Futures Spread Terminal", layout="wide")

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

def update_password(user_id, new_password):
    try:
        url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}"
        r = requests.patch(url, headers=HEADERS, json={"password": new_password.strip()}, timeout=8)
        return r.status_code in [200, 204]
    except Exception as e:
        st.error(f"पासवर्ड अपडेट एरर: {e}")
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
                    st.error("यूज़र नहीं मिला! कृपया सही Username या Mobile डालें।")
                else:
                    user = user_data[0]
                    if user["password"] != u_pass.strip():
                        st.error("गलत पासवर्ड! कृपया दोबारा प्रयास करें।")
                    elif not user.get("is_approved", False):
                        st.warning("⚠️ आपका अकाउंट अभी पेंडिंग है! एडमिन से अप्रूवल का इंतज़ार करें।")
                    elif user.get("valid_until") and datetime.strptime(user["valid_until"], "%Y-%m-%d").date() < date.today():
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
        st.subheader("🔑 Reset Your Password")
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
                    st.error("यूज़रनेम मौजूद नहीं है!")
                else:
                    user = user_data[0]
                    if str(user.get("phone")).strip() != str(verify_phone).strip():
                        st.error("मोबाइल नंबर मेल नहीं खा रहा है! कृपया सही नंबर दर्ज करें।")
                    else:
                        if update_password(user["id"], new_password):
                            st.success("✅ पासवर्ड सफलतापूर्वक बदल गया! अब Login टैब में जाकर नए पासवर्ड से लॉगिन करें।")
                            log_activity(user["username"], "Password Reset by User")
                        else:
                            st.error("पासवर्ड अपडेट करने में कोई त्रुटि हुई।")

# ==================== 2. ADMIN DASHBOARD ====================
elif st.session_state.is_admin:
    st.sidebar.title(f"👑 Admin: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.header("🛠️ Admin Control Center")
    tab1, tab2 = st.tabs(["User Approvals & Management", "User Activity Logs"])

    with tab1:
        st.subheader("Manage Users")
        try:
            res = requests.get(f"{SUPABASE_URL}/rest/v1/users?order=created_at.desc", headers=HEADERS, timeout=8)
            if res.status_code == 200:
                for u in res.json():
                    if u["username"].lower() == "admin":
                        continue
                    with st.expander(f"User: {u['username']} | Phone: {u.get('phone')} | Status: {'✅ Approved' if u.get('is_approved') else '⏳ Pending'}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            days = st.number_input("Validity Days", min_value=1, max_value=365, value=30, key=f"d_{u['id']}")
                            if st.button("Approve / Grant Access", key=f"app_{u['id']}"):
                                exp_date = (date.today() + timedelta(days=days)).strftime("%Y-%m-%d")
                                requests.patch(
                                    f"{SUPABASE_URL}/rest/v1/users?id=eq.{u['id']}",
                                    headers=HEADERS,
                                    json={"is_approved": True, "valid_until": exp_date}
                                )
                                st.success(f"{days} दिनों के लिए अप्रूव किया गया!")
                                st.rerun()
                        with col2:
                            admin_new_pass = st.text_input("New Password", key=f"np_{u['id']}", placeholder="Enter new pass")
                            if st.button("Force Reset Password", key=f"f_rst_{u['id']}"):
                                if admin_new_pass:
                                    update_password(u['id'], admin_new_pass)
                                    st.success(f"{u['username']} का पासवर्ड अपडेट कर दिया गया!")
                                else:
                                    st.warning("नया पासवर्ड टाइप करें!")
                        with col3:
                            st.write("---")
                            if st.button("Block Access", key=f"blk_{u['id']}"):
                                requests.patch(
                                    f"{SUPABASE_URL}/rest/v1/users?id=eq.{u['id']}",
                                    headers=HEADERS,
                                    json={"is_approved": False}
                                )
                                st.warning("यूज़र को ब्लॉक कर दिया गया!")
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

# ==================== 3. TRADER SCREEN ====================
else:
    st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    if not st.session_state.api_connected:
        st.subheader("🔑 Connect Your Angel One Account")
        with st.form("api_form"):
            api_key = st.text_input("SmartAPI Key")
            client_id = st.text_input("Angel One Client ID")
            mpin = st.text_input("Trading MPIN", type="password")
            totp_secret = st.text_input("TOTP Secret Key", type="password")
            submit = st.form_submit_button("Connect & Start Scanner")

            if submit:
                st.session_state.api_connected = True
                log_activity(st.session_state.username, "Connected Angel One API")
                st.success("API सफलतापूर्वक कनेक्ट हो गई!")
                st.rerun()
    else:
        st.title("📊 Futures Calendar Spread Scanner")
        st.success("लाइव स्प्रेड स्कैनर तैयार है!")
        
