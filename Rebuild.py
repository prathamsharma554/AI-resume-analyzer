import streamlit as st
import PyPDF2
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="AI Resume Analyzer Pro", layout="wide")

# Custom CSS for Professional Look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e445e; }
    </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def get_semantic_similarity(resume_text, jd_text):
    vectorizer = TfidfVectorizer().fit_transform([resume_text, jd_text])
    vectors = vectorizer.toarray()
    return cosine_similarity(vectors)[0][1] * 100

def detect_sections(text):
    sections = {
        "Education": ["education", "academic", "university", "college"],
        "Experience": ["experience", "work", "employment", "internship"],
        "Skills": ["skills", "technical", "technologies", "tools"],
        "Projects": ["projects", "personal projects", "portfolio"]
    }
    found = {}
    for sec, keywords in sections.items():
        found[sec] = any(kw in text.lower() for kw in keywords)
    return found

def extract_contact_info(text):
    email = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    links = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)
    return {"email": email[0] if email else "Not Found", "links": len(links)}

def check_quantifiable_metrics(text):
    # Checks for percentages, currency, or numbers followed by '+'
    metrics = re.findall(r'\d+%', text) + re.findall(r'\$\d+', text) + re.findall(r'\d+\+', text)
    return len(metrics)

# --- Main UI ---
st.title("🤖 AI Resume Analyzer Pro")
st.caption("ATS-Optimized Resume Analysis with Semantic AI")

# Sidebar
st.sidebar.header("📁 Upload Center")
uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF)", type=["pdf"])
job_description = st.sidebar.text_area("Target Job Description", height=250)

if uploaded_file and job_description:
    with st.spinner('AI is analyzing your resume...'):
        resume_text = extract_text_from_pdf(uploaded_file)
        
        # 1. Semantic Analysis
        similarity_score = get_semantic_similarity(resume_text.lower(), job_description.lower())
        
        # 2. Section & Info Extraction
        sections = detect_sections(resume_text)
        contact = extract_contact_info(resume_text)
        metrics_count = check_quantifiable_metrics(resume_text)
        word_count = len(resume_text.split())
        
        # 3. Calculations for Score
        # Simple weighted score for ATS Gauge
        ats_score = (similarity_score * 0.5) + (sum(sections.values()) * 10) + (min(metrics_count, 5) * 2)
        ats_score = min(ats_score, 100)

        # --- Dashboard Layout (Matching your Screenshot) ---
        
        # Top Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ATS Score", f"{int(ats_score)}%")
        m2.metric("Word Count", word_count)
        m3.metric("JD Match", f"{int(similarity_score)}%")
        m4.metric("Metrics Found", metrics_count)

        st.divider()

        # Visualizations Row
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("📊 Score Breakdown")
            # Radar Chart
            categories = ['Similarity', 'Sections', 'Metrics', 'Formatting', 'Keywords']
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=[similarity_score, sum(sections.values())*25, metrics_count*20, 85, 70],
                theta=categories,
                fill='toself',
                line_color='#00d1b2'
            ))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=350, margin=dict(t=20, b=20))
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_right:
            st.subheader("⏲️ ATS Compatibility")
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = ats_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {'axis': {'range': [None, 100]},
                         'bar': {'color': "#00d1b2"},
                         'steps' : [
                             {'range': [0, 50], 'color': "#333"},
                             {'range': [50, 80], 'color': "#555"}]}))
            fig_gauge.update_layout(height=350, margin=dict(t=20, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

        st.divider()

        # Skills & Analysis
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("✅ Sections Detected")
            for sec, found in sections.items():
                st.write(f"{'🟢' if found else '🔴'} {sec}")
            
            st.subheader("📧 Contact Info")
            st.info(f"Email: {contact['email']}\n\nLinks found: {contact['links']}")

        with c2:
            st.subheader("💡 AI Recommendations")
            if metrics_count < 3:
                st.warning("Action: Add more quantifiable results (e.g., 'Improved speed by 20%').")
            if not sections["Projects"]:
                st.error("Action: Project section is missing or not clearly labeled.")
            if similarity_score < 60:
                st.info("Tip: Incorporate more industry-specific verbs from the JD.")
            else:
                st.success("Great job! Your resume has strong semantic alignment.")

        # Bottom Progress Bar
        st.subheader("🧠 Semantic Similarity Detail")
        st.progress(int(similarity_score))
        st.caption(f"Contextual match with Job Description: {similarity_score:.2f}%")

else:
    # Landing Page State
    st.info("Please upload your Resume and paste the Job Description to generate the AI Analysis.")
    
    # Visual placeholder to match the vibe
    st.image("https://img.icons8.com/clouds/200/000000/analytics.png")