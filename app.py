import streamlit as str
import PyPDF2
import matplotlib.pyplot as plt
import numpy as np

# Page configuration
str.set_page_config(page_title="AI Resume Analyzer", layout="centered")
str.title("📊 AI Resume Analyzer & Matcher")
str.write("Upload your resume and enter the Job Description to check the compatibility match.")

# 1. Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text.lower()

# 2. Sidebar for User Input
str.sidebar.header("User Panel")
uploaded_file = str.sidebar.file_uploader("Upload Resume (PDF only)", type=["pdf"])
job_description = str.sidebar.text_area("Paste Job Description (JD) Here", height=200)

if uploaded_file and job_description:
    # Extract text from resume
    resume_text = extract_text_from_pdf(uploaded_file)
    jd_text = job_description.lower()
    
    # Clean and split job description into unique keywords
    jd_words = set([word.strip(".,;:!?()") for word in jd_text.split() if len(word) > 3])
    
    stop_words = {'with', 'this', 'that', 'from', 'have', 'good', 'will', 'your', 'their', 'about'}
    keywords_to_check = [word for word in jd_words if word not in stop_words]
    
    # 3. Analyze Matching Keywords
    matched_keywords = []
    missing_keywords = []
    
    for word in keywords_to_check:
        if word in resume_text:
            matched_keywords.append(word)
        else:
            missing_keywords.append(word)
            
    # Calculate Score
    total_keywords = len(keywords_to_check)
    if total_keywords > 0:
        match_percentage = (len(matched_keywords) / total_keywords) * 100
    else:
        match_percentage = 0
        
    # 4. Display Results
    str.subheader("🎯 Analysis Overview")
    col1, col2 = str.columns(2)
    col1.metric(label="Match Score", value=f"{match_percentage:.2f}%")
    col2.metric(label="Total Keywords Checked", value=total_keywords)
    
    # 5. Visualizing Data using Matplotlib & NumPy
    str.subheader("📈 Visual Breakdown")
    
    fig, ax = plt.subplots(figsize=(6, 4))
    categories = ['Matched Skills', 'Missing Skills']
    counts = np.array([len(matched_keywords), len(missing_keywords)])
    colors = ['#2ecc71', '#e74c3c']
    
    ax.bar(categories, counts, color=colors, width=0.5)
    ax.set_ylabel('Number of Keywords')
    ax.set_title('Resume vs Job Description Match')
    
    str.pyplot(fig)
    
    # 6. Detailed Recommendations
    str.subheader("💡 Recommendations to Improve Your Resume")
    
    if len(missing_keywords) > 0:
        str.warning("⚠️ Critical: Your resume is missing important terms from the Job Description.")
        
        with str.expander("🔍 Missing Skills to Add (Top 10)"):
            str.write("Integrate these exact terms naturally into your 'Skills' or 'Projects' section:")
            for word in missing_keywords[:10]:
                str.write(f"- **{word.upper()}**")
                
        with str.expander("🛠️ How to fix this? (Action Plan)"):
            str.write("1. **Tailor Your Resume:** Don't use the same resume everywhere. Modify it for every job application using the keywords above.")
            str.write("2. **Add Context:** Don't just list words. Write lines like *'Developed a project using [Missing Skill] to solve X problem'*.")
            str.write("3. **Highlight Core Subjects:** Since you are a fresher, ensure fundamental subjects like OOPs, DBMS, and OS are visible if mentioned in JD.")
    else:
        str.success("🏆 Excellent! Your resume covers almost all major keywords from the job description.")

    # Always show global best practices for freshers
    with str.expander("📋 Golden Rules for a Fresher IT Resume"):
        str.write("Make sure your resume follows these industry standards to pass ATS tracking:")
        str.markdown("""
        - **Keep it to 1 Page:** As a fresher, your resume must strictly fit on a single page.
        - **Quantify Your Projects:** Instead of saying *'Worked on Python project'*, write *'Built an AI Analyzer handling **PDF extraction** with **100% text accuracy**'*.
        - **Add Clickable Links:** Always include active links to your **GitHub profile**, **LinkedIn**, and live project links.
        - **Remove Hobby Cliches:** Avoid outdated hobbies like *'Listening to music'*. Instead, mention *'Problem Solving on LeetCode'* or *'Open Source Contribution'*.
        - **Use ATS-Friendly Fonts:** Stick to clean, modern fonts like Arial, Calibri, or Helvetica. Avoid graphics or complex tables.
        """)
        
else:
    str.info("Please upload a PDF resume and paste the job description from the sidebar to begin analysis.")