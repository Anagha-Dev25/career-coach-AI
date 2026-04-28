import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.graph_objects as go
import PyPDF2
import io
from fpdf import FPDF
from src.agents.analyzer import CareerAnalyzer
from run_coach import analyze_sample_resume

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="PathFinder AI Pro", page_icon="✨", layout="wide")

def add_home_link():
    """Navigation helper for inner pages"""
    if st.button("← Back to Dashboard", use_container_width=False):
        st.session_state.page = "Dashboard"
        st.rerun()

# --- 2. COMPREHENSIVE SESSION STATE INITIALIZATION ---
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to your 2026 Executive Career Suite. How can I assist you today?"}]

# Analyzer state
if 'target_job' not in st.session_state:
    st.session_state.target_job = ""
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

# Predictions state
if 'pred_inputs' not in st.session_state:
    st.session_state.pred_inputs = {
        'years_exp': 2, 'gpa': 8.2, 'coding_rating': 7, 'projects': 3, 'internships': 1,
        'hackathons': 2, 'skills': ['Python', 'ML', 'React'], 'interests': ['AI/ML', 'Cybersecurity'],
        'location_pref': 'Bangalore', 'risk_tolerance': 'Moderate'
    }
if 'model_results' not in st.session_state:
    st.session_state.model_results = {}
if 'predictions_run' not in st.session_state:
    st.session_state.predictions_run = False

# Chat state
if 'deep_chat' not in st.session_state:
    st.session_state.deep_chat = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        'name': 'Ammu', 'year': 3, 'college': 'JSSATEB', 'branch': 'ISE',
        'skills': ['Python', 'Web Dev'], 'goals': 'FAANG 2027'
    }


# --- 3. PREMIUM CSS (THE "NUCLEAR" FIX) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    /* 1. Global Font - applied safely */
    html, body, [class*="st-"] { 
        font-family: 'Plus Jakarta Sans', sans-serif; 
    }

    /* 2. THE FIX: Hide the leaked text labels for icons globally */
    /* This targets the specific text labels Streamlit uses for ligatures */
    [data-testid="stIcon"] svg + span,
    [data-testid="stExpanderIcon"] + span,
    .st-emotion-cache-v0 p {
        display: none !important;
        visibility: hidden !important;
        font-size: 0 !important;
    }

    /* Ensure the actual SVG icons remain visible */
    [data-testid="stIcon"] svg, 
    [data-testid="stExpanderIcon"] svg {
        display: inline-block !important;
        visibility: visible !important;
    }

    .premium-card {
    background: var(--background-color);
    color: var(--text-color);
    border-radius: 24px;
    padding: 32px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    text-align: center;
    margin-bottom: 20px;
    border: 1px solid rgba(128, 128, 128, 0.2);
}

    /* Premium Button Style */
    .stButton>button {
        background: linear-gradient(90deg, #6366F1 0%, #A855F7 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CONDITIONAL TOP NAVIGATION ---
nav_col1, nav_col2 = st.columns([1, 3])
with nav_col1:
    st.markdown("### 🧬 **PathFinder AI**")

with nav_col2:
    # Only show the option menu if we are ON the Dashboard
    if st.session_state.page == "Dashboard":
        page_options = ["Dashboard", "Predictions", "Analyzer", "Chat Advisor"]
        selected = option_menu(
            menu_title=None,
            options=page_options,
            icons=["house", "magic", "file-earmark-person", "robot"],
            default_index=0,
            orientation="horizontal",
            key='top_nav'
        )
        if selected != st.session_state.page:
            st.session_state.page = selected
            st.rerun()
    else:
        # Show an empty space or a simple status indicator when not on dashboard
        st.markdown("<p style='text-align:right; color:gray; padding-top:10px;'>Executive Mode Active</p>", unsafe_allow_html=True)

st.divider()

# --- 5. DASHBOARD ---
if st.session_state.page == "Dashboard":
    st.markdown("<br><h1 style='text-align: center; font-size: 3rem;'>Discover Your Ideal Career Path with AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; font-size: 1.2rem;'>The world's most advanced AI-driven career suite for the 2026 job market.</p>", unsafe_allow_html=True)
    
    _, col_btn, _ = st.columns([2,1,2])
    with col_btn:
        if st.button("🚀 START YOUR ANALYSIS", use_container_width=True):
            st.session_state.page = "Analyzer"
            st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="premium-card"><h1>📈</h1><h3>Market Intelligence</h3><p>Analysis of 2026 hiring patterns.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="premium-card"><h1>🧠</h1><h3>NLP Alignment</h3><p>Semantic matching for potential.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="premium-card"><h1>🎯</h1><h3>Strategic Roadmaps</h3><p>Project paths to bridge your gaps.</p></div>', unsafe_allow_html=True)
# --- 6. ANALYZER PAGE (FIXED) ---
elif st.session_state.page == "Analyzer": 
    add_home_link()

    # --- Upload Button CSS ---
    # Custom CSS for the "Add Resume File" button style within the uploader
    st.markdown("""
        <style>
           /* Default uploader button (before upload) */
            [data-testid="stFileUploader"] button {
            width: 100% !important;
            height: 50px !important;
            background: #F9FAFB !important;
            color: transparent !important;
            border: 2px dashed #6366F1 !important;
            border-radius: 15px !important;
            font-weight: 700 !important;
            position: relative;
           }

           /* Custom label */
           [data-testid="stFileUploader"] button::after {
               content: "➕ ADD RESUME FILE";
               position: absolute;
               top: 50%;
               left: 50%;
               transform: translate(-50%, -50%);
               font-size: 10px;
               color: #6366F1;
           }
           
           /* 🔥 KEY FIX: Hide extra button AFTER file is uploaded */
           [data-testid="stFileUploader"] section button {
               display: none !important;
           }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center;'>Resume Architect Pro</h2>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("##### 🎯 1. Target Role")
        st.session_state.target_job = st.text_input(
            "target_role_input",
            value=st.session_state.target_job,
            label_visibility="collapsed",
            placeholder="e.g. Machine Learning Engineer"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("##### 📂 2. Select Document")
        st.markdown(
    "<p style='color: gray; font-size: 15px; margin-bottom: 6px;'>Upload your resume (PDF only)</p>",
    unsafe_allow_html=True
)
        uploaded_file = st.file_uploader(
        "",
        type=["pdf"],
        key="pdf_uploader"
        )

        if uploaded_file is not None:
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                extracted = "".join([page.extract_text() or "" for page in pdf_reader.pages])
                if extracted.strip():
                    st.session_state.resume_text = extracted
                    st.success("✅ File Linked Successfully")
            except Exception:
                st.error("Error processing PDF.")

    with col_right:
        st.markdown("##### ✍️ 3. Direct Text Entry")
        st.session_state.resume_text = st.text_area(
            "Paste resume text",
            value=st.session_state.resume_text,
            height=250,
            placeholder="Paste your resume content here...",
            label_visibility="collapsed"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- EXECUTE BUTTON ---
    if st.button("🚀 EXECUTE DEEP ANALYSIS", use_container_width=True, type="primary"):
        if st.session_state.target_job.strip() and st.session_state.resume_text.strip():
            with st.spinner("Analyzing..."):
                coach = CareerAnalyzer()

                target_role = st.session_state.target_job.strip()

                if len(target_role.split()) < 3:
                   target_role += " with skills in Cloud, APIs, Python, and problem solving"

                   analysis = coach.analyze_resume(
                          st.session_state.resume_text,
                         target_role
                  )

                scores = coach.get_skill_scores(
                    st.session_state.resume_text,
                    st.session_state.target_job
                )

                st.session_state.analysis_results = {
                    "analysis": analysis,
                    "scores": scores
                }

                st.session_state.analysis_done = True
                st.rerun()

    # --- RESULTS (FIXED INSIDE ANALYZER) ---
    if st.session_state.analysis_done:
        st.markdown("### 🧠 Analysis Results")

        analysis_text = st.session_state.analysis_results.get("analysis", "")
        raw_scores = st.session_state.analysis_results.get("scores", {})

        st.write(analysis_text)

        # Normalize keys
        scores_data = {
            "Technical": raw_scores.get("Technical", 0),
            "Communication": raw_scores.get("Communication", 0),
            "Leadership": raw_scores.get("Leadership", 0),
            "Problem Solving": raw_scores.get("Problem Solving", raw_scores.get("Problem-Solving", 0)),
            "Creativity": raw_scores.get("Creativity", 0)
        }

        st.markdown("### 📊 Skill Scores")
        st.json(scores_data)

        # --- RADAR CHART ---
        categories = list(scores_data.keys())
        values = list(scores_data.values())

        categories += [categories[0]]
        values += [values[0]]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)

        st.markdown("### 🕸️ Skill Radar Analysis")
        st.plotly_chart(fig, use_container_width=True)

        # --- PDF GENERATION ---
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        import io        

        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer)
        styles = getSampleStyleSheet()        

        content = []        

        content.append(Paragraph("PATHFINDER AI PRO - CAREER ANALYSIS REPORT", styles['Title']))
        content.append(Spacer(1, 12))        

        content.append(Paragraph(f"<b>Target Role:</b> {st.session_state.target_job}", styles['Normal']))
        content.append(Spacer(1, 12))        

        content.append(Paragraph("<b>Analysis:</b>", styles['Heading2']))
        content.append(Paragraph(analysis_text, styles['Normal']))
        content.append(Spacer(1, 12))        

        content.append(Paragraph("<b>Skill Scores:</b>", styles['Heading2']))
        for k, v in scores_data.items():
            content.append(Paragraph(f"{k}: {v}", styles['Normal']))        

        content.append(Spacer(1, 20))
        content.append(Paragraph("<b>Skill Radar:</b> Available in web view", styles['Normal']))        

        doc.build(content)
        pdf_buffer.seek(0)        

        st.download_button(
             label="📥 DOWNLOAD PDF REPORT",
             data=pdf_buffer,
             file_name="career_analysis_report.pdf",
             mime="application/pdf",
             use_container_width=True
        )
             

    if st.button("✨ Try Sample Resume"):
        with st.spinner("Analyzing sample resume..."):
          result = analyze_sample_resume()

        if "error" in result:
            st.error(result["error"])
        else:
            st.subheader("📄 Sample Resume Analysis")
    
            st.write("💡 **Suggested Skills to Improve:**")
            st.write(", ".join(result['missing']))
    
            st.subheader("🧠 AI Career Coach Feedback")
            st.write(result["analysis"])

# --- 7. FIXED PREDICTIONS PAGE ---
elif st.session_state.page == "Predictions":
    add_home_link()
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>🔮 2026 Global Career Predictions</h1>", unsafe_allow_html=True)
    
    # 1. DATA OPTIONS
    skill_options = ['Python', 'Java', 'React', 'Web', 'AWS', 'Docker', 'ML', 'Cybersec', 'Data Science', 'DevOps', 'Blockchain']
    
    st.subheader("📊 Profile Parameters")
    
    # Form used to prevent mid-selection flickering
    with st.form("prediction_engine"):
        col1, col2 = st.columns(2)
        
        with col1:
            years_exp = st.slider("Experience (Years)", 0, 10, st.session_state.pred_inputs['years_exp'])
            gpa = st.slider("GPA/10", 6.0, 10.0, float(st.session_state.pred_inputs['gpa']), 0.1)
            # New Communication Slider
            comm_skills = st.slider("Communication Skills", 1, 10, 7, help="Critical for Leadership & Management roles")
        
        with col2:
            projects = st.slider("Significant Projects", 0, 15, st.session_state.pred_inputs['projects'])
            skills_list = st.multiselect("Technical Skills", skill_options, default=['Python', 'ML'])
            location = st.selectbox("Market Focus", ['US (Remote)', 'EU (Berlin)', 'UK (London)', 'India (Bangalore/Pune)'])
        
        run_pred = st.form_submit_button("🚀 EXECUTE AI PREDICTION", use_container_width=True)

    # 2. THE LOGIC ENGINE
    if run_pred:
        # Configuration for diverse 2026 roles
        potential_roles = {
            "AI Solution Architect": {"req": ["ML", "Python"], "comm_weight": 1.3, "min_exp": 3},
            "Senior Full Stack Engineer": {"req": ["React", "Web", "Java"], "comm_weight": 0.8, "min_exp": 2},
            "DevOps Lead": {"req": ["AWS", "Docker", "DevOps"], "comm_weight": 1.1, "min_exp": 4},
            "Cybersecurity Consultant": {"req": ["Cybersec"], "comm_weight": 1.4, "min_exp": 1},
            "Data Science Manager": {"req": ["Data Science", "Python"], "comm_weight": 1.5, "min_exp": 5},
            "Blockchain Engineer": {"req": ["Blockchain"], "comm_weight": 0.7, "min_exp": 0},
            "UI/UX Technical Lead": {"req": ["Web", "React"], "comm_weight": 1.4, "min_exp": 3}
        }

        results = {}
        for role, criteria in potential_roles.items():
            # --- Technical Matching ---
            tech_match = len([s for s in skills_list if s in criteria["req"]])
            base_score = 45 + (tech_match * 16)
            
            # --- Experience & Communication Synergy ---
            comm_boost = (comm_skills * criteria["comm_weight"]) * 1.8
            exp_boost = (years_exp * 3.5)
            
            # Penalty for being under-qualified by experience
            if years_exp < criteria["min_exp"]:
                base_score -= 22
                
            final_fit = min(98.5, base_score + comm_boost + exp_boost + (gpa * 1.2))
            
            # --- REALISTIC SALARY ENGINE (USD $) ---
            # Step A: Define Market Base by Experience Tier
            if years_exp < 2:
                market_base = 48000   # Entry
            elif years_exp < 5:
                market_base = 90000  # Mid
            elif years_exp < 8:
                market_base = 145000  # Senior
            else:
                market_base = 190000  # Lead/Principal

            # Step B: Location Adjustments
            loc_mult = {
                'US (Remote)': 1.2, 
                'EU (Berlin)': 0.9, 
                'UK (London)': 0.95, 
                'India (Bangalore/Pune)': 0.45 
            }[location]

            # Step C: Performance Multiplier (based on Fit and Communication)
            performance_mult = 0.85 + (final_fit / 250) + (comm_skills / 60)
            
            salary_val = market_base * loc_mult * performance_mult
            
            # Step D: ANTI-FAKE CAP
            # Ensures 3rd year students (0-1 yrs exp) don't see $300k+ salaries
            if years_exp < 3:
                salary_val = min(salary_val, 62000)
            elif years_exp < 6:
                salary_val = min(salary_val, 190000)

            if final_fit > 52: 
                results[role] = {
                    'fit': round(final_fit, 1),
                    'salary': f"${int(salary_val/1000):,}k"
                }

        st.session_state.model_results = dict(sorted(results.items(), key=lambda x: x[1]['fit'], reverse=True))
        st.session_state.predictions_run = True

    # 3. RESULT DISPLAY
    # 3. PREMIUM RESULT DISPLAY
    if st.session_state.predictions_run:
        st.divider()
        st.markdown(f"### 🎯 Top Career Matches | {location}")
        
        # Display top 3 as "Premium Cards"
        top_matches = list(st.session_state.model_results.items())[:3]
        cols = st.columns(len(top_matches))
        
        for idx, (role, data) in enumerate(top_matches):
            with cols[idx]:
                st.markdown(f"""
                <div class="premium-card" style="min-height: 220px; border-top: 4px solid #A855F7;">
                    <p style="color: #6366F1; font-weight: 800; font-size: 0.8rem; margin: 0;">MATCH RANK #{idx+1}</p>
                    <h3 style="margin: 10px 0; min-height: 50px;">{role}</h3>
                    <h2 style="margin: 5px 0;">{data['fit']}%</h2>
                    <p style="color: #666; font-size: 0.9rem; margin-bottom: 0;">Est. 2026 TC:</p>
                    <h4 style="color: #A855F7; margin-top: 0;">{data['salary']} /yr</h4>
                </div>
                """, unsafe_allow_html=True)
                st.progress(data['fit']/100)

        # --- NEW: DIRECT ALTERNATIVE PATHS (No Dropdown) ---
        if len(st.session_state.model_results) > 3:
            st.markdown("<br><h5>🔍 Additional Career Horizons</h5>", unsafe_allow_html=True)
            
            # Loop through the remaining results directly on the page
            for role, data in list(st.session_state.model_results.items())[3:]:
                # Using a container for a clean row-like feel
                with st.container():
                    c1, c2, c3 = st.columns([2, 1, 1])
                    with c1:
                        st.markdown(f"**{role}**")
                    with c2:
                        # Color coding based on fit %
                        color = "green" if data['fit'] > 75 else "orange"
                        st.markdown(f"<span style='color:{color}; font-weight:bold;'>{data['fit']}% Match</span>", unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"**{data['salary']}**")
                    st.divider() # Simple line between entries
        
        # Reset Button at the bottom
        if st.button("🔄 Clear and Recalculate", use_container_width=True):
            st.session_state.predictions_run = False
            st.rerun()
# --- 8. CHAT ADVISOR ---
# Updated Chat Advisor Logic
elif st.session_state.page == "Chat Advisor":
    add_home_link()
    st.markdown("<h1 style='text-align: center;'>💬 AI Career Coach</h1>", unsafe_allow_html=True)
    
    # Display chat history
    for msg in st.session_state.deep_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about career strategy..."):
        # Add user message to state
        st.session_state.deep_chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                coach = CareerAnalyzer()
                # Providing more context from the profile
                profile = st.session_state.user_profile
                context = f"Student: {profile['name']}, Goal: {profile['goals']}. Question: {prompt}"
                response = coach._call_cohere(context, "Senior career coach")
                st.markdown(response)
        
        # Add assistant message to state
        st.session_state.deep_chat.append({"role": "assistant", "content": response})
        # No st.rerun() needed here; Streamlit will refresh the chat history on the next interaction.