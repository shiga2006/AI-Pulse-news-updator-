"""
app.py
Main entry point for AI Pulse. Handles login/signup gate.
Once logged in, users are directed to the Feed page (see pages/ folder).
"""
import streamlit as st
from dotenv import load_dotenv
from db.database import init_db
from auth.auth_utils import create_user, authenticate_user
from fetcher.scheduler import start_scheduler

load_dotenv()

st.set_page_config(page_title="AI Pulse", page_icon="🧠", layout="wide")


@st.cache_resource
def _init_background_scheduler():
    """
    st.cache_resource ensures this runs exactly once per server process,
    no matter how many times Streamlit reruns the script (which happens on
    every click) or how many users/sessions connect. Without this, every
    rerun would call start_scheduler() again - harmless thanks to its own
    internal guard, but wasteful.
    """
    return start_scheduler()


_init_background_scheduler()

# Ensure DB and tables exist before anything else runs
init_db()

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None


def show_login_form():
    st.subheader("Log In")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")

        if submitted:
            success, message, user_id = authenticate_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.success(message)
                st.rerun()
            else:
                st.error(message)


def show_signup_form():
    st.subheader("Create an Account")
    with st.form("signup_form"):
        username = st.text_input("Choose a username")
        email = st.text_input("Email")
        password = st.text_input("Choose a password", type="password")
        confirm_password = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Sign Up")

        if submitted:
            if not username or not email or not password:
                st.error("All fields are required.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                success, message = create_user(username, email, password)
                if success:
                    st.success(message + " Please log in.")
                else:
                    st.error(message)


def show_auth_gate():
    st.title("🧠 AI Pulse")
    st.caption("Your daily dose of AI updates, explained simply.")

    tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])
    with tab_login:
        show_login_form()
    with tab_signup:
        show_signup_form()


def show_logged_in_home():
    st.title(f"Welcome back, {st.session_state.username} 👋")
    st.write("Use the sidebar to navigate to **Feed**, **Assistant**, or **Preferences**.")

    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()


# Main routing logic
if not st.session_state.logged_in:
    show_auth_gate()
else:
    show_logged_in_home()
