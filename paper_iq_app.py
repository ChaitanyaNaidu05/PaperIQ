import streamlit as st
import json
import database
import auth
import styles
import pdf_processor
import text_analyzer
import time
import datetime

st.set_page_config(
    page_title="PaperIQ",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "user" not in st.session_state:
    st.session_state["user"] = None
if "current_analysis" not in st.session_state:
    st.session_state["current_analysis"] = None

database.init_db()

st.markdown(styles.get_app_styles(), unsafe_allow_html=True)

def navigate_to(page):
    st.session_state["page"] = page
    st.rerun()

def handle_login(username, password):
    user = database.get_user_by_username(username)
    if user and auth.verify_password(user['password_hash'], user['salt'], password):
        st.session_state["user"] = user
        st.session_state["page"] = "dashboard"
        st.toast(f"Welcome back, {user['username']}!")
        time.sleep(1)
        st.rerun()
    else:
        st.error("Invalid username or password")

def handle_signup(username, email, password, confirm_password):
    if password != confirm_password:
        st.error("Passwords do not match")
        return

    if len(password) < 6:
        st.error("Password must be at least 6 characters")
        return

    salt = auth.generate_salt()
    password_hash = auth.hash_password(password, salt)
    
    if database.create_user(username, email, password_hash, salt):
        st.success("Account created successfully! Please login.")
        time.sleep(2)
        navigate_to("login")
    else:
        st.error("Username or Email already exists")

def handle_logout():
    st.session_state["user"] = None
    st.session_state["page"] = "login"
    st.session_state["current_analysis"] = None
    st.rerun()

def load_analysis_from_history(analysis_id):
    analysis = database.get_analysis_details(analysis_id)
    if analysis:
        st.session_state["current_analysis"] = {
            "filename": analysis["filename"],
            "sections": json.loads(analysis["sections_json"]),
            "keywords": json.loads(analysis["keywords_json"]),
            "timestamp": analysis["upload_time"]
        }

def render_login_page():
    st.markdown('<div class="main-header">PaperIQ Login</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.container(border=True):
            st.markdown("### Sign In")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login", type="primary"):
                handle_login(username, password)
            
            st.markdown("---")
            st.markdown("Don't have an account?")
            if st.button("Create Account"):
                navigate_to("signup")

def render_signup_page():
    st.markdown('<div class="main-header">PaperIQ Signup</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.container(border=True):
            st.markdown("### Create Account")
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.button("Sign Up", type="primary"):
                handle_signup(username, email, password, confirm_password)
            
            st.markdown("---")
            if st.button("Back to Login"):
                navigate_to("login")

def render_dashboard():
    user = st.session_state["user"]
    
    with st.sidebar:
        st.markdown(f"### Hello, {user['username']}")
        if st.button("Logout"):
            handle_logout()
        
        st.markdown("---")
        st.markdown("### Analysis History")
        
        if st.button("New Analysis", type="primary"):
            st.session_state["current_analysis"] = None
            st.rerun()
            
        history = database.get_user_history(user['id'])
        if history:
            for item in history:
                date_str = item['upload_time'].split(' ')[0]
                label = f"{item['filename']} ({date_str})"
                if st.button(label, key=f"history_{item['id']}"):
                    load_analysis_from_history(item['id'])
                    st.rerun()
        else:
            st.info("No history yet.")

    st.markdown('<div class="main-header">PaperIQ Dashboard</div>', unsafe_allow_html=True)
    
    current_analysis = st.session_state.get("current_analysis")
    
    if current_analysis:
        st.info(f"Viewing analysis for: **{current_analysis['filename']}**")
        
        sections = current_analysis["sections"]
        
        col1, col2 = st.columns([3, 1]) 
        
        with col2:
            st.markdown('<div class="keywords-container">', unsafe_allow_html=True)
            st.write("**Top Keywords:**")
            all_keywords = set()
            for s in sections.values():
                for k in s.get("keywords", []):
                    all_keywords.add(k)
            
            keywords_list = list(all_keywords)[:15]
            keywords_html = " ".join([f'<span class="keyword-chip">{kw}</span>' for kw in keywords_list])
            st.markdown(keywords_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col1:
             for section_name, section_data in sections.items():
                content = section_data.get("content", "")
                keywords = section_data.get("keywords", [])
                
                with st.expander(f"{section_name}", expanded=False):
                    if content:
                        st.write(content[:2000] + ("..." if len(content) > 2000 else ""))
                        if keywords:
                             st.caption(f"Keywords: {', '.join(keywords)}")
    
    else:
        st.write("Upload a research paper PDF to dynamically extract sections and keywords.")
        
        uploaded_file = st.file_uploader("Select a research paper", type=["pdf"])
        
        if uploaded_file is not None:
            st.success("PDF Uploaded Successfully!")
            
            if st.button("Start Analysis"):
                with st.spinner("Processing PDF and analyzing structure..."):
                    raw_text = pdf_processor.extract_text_from_pdf(uploaded_file)
                    
                    if raw_text:
                        cleaned_text = pdf_processor.preprocess_text(raw_text)
                        
                        sections = text_analyzer.identify_sections_dynamic(cleaned_text)
                        
                        detected_count = len(sections)
                        
                        summary_keywords = text_analyzer.extract_keywords(cleaned_text, top_n=10)
                        
                        database.save_analysis(
                            user_id=user['id'],
                            filename=uploaded_file.name,
                            sections_count=detected_count,
                            keywords=summary_keywords,
                            sections_data=sections
                        )
                        
                        st.session_state["current_analysis"] = {
                            "filename": uploaded_file.name,
                            "sections": sections,
                            "keywords": summary_keywords,
                            "timestamp": str(datetime.datetime.now())
                        }
                        
                        st.toast("Analysis complete and saved!")
                        st.rerun()
                    else:
                        st.error("Could not extract text from this PDF.")

if st.session_state["page"] == "login":
    render_login_page()
elif st.session_state["page"] == "signup":
    render_signup_page()
elif st.session_state["page"] == "dashboard":
    render_dashboard()

