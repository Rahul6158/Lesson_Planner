import streamlit as st
import requests
from fpdf import FPDF
from docx import Document
import io
from htmldocx import HtmlToDocx
import markdown
import html

# Configure page
st.set_page_config(
    page_title="Pedagogic Planner Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional typography
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Open+Sans:wght@300;400;600&display=swap');
    
    html, body, .stApp {
        font-family: 'Open Sans', sans-serif;
        line-height: 1.6;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Merriweather', serif;
        font-weight: 700;
        color: #2c3e50;
    }
    
    h1 {
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.3em;
    }
    
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
    
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 8px 16px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #2980b9;
    }
    
    .section-card {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        padding: 1.5rem;
        margin-bottom: 2rem;
        border-left: 4px solid #3498db;
    }
    
    .problem-card {
        background-color: #f8f9fa;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }
    
    .solution {
        background-color: #e8f4fc;
        border-left: 3px solid #3498db;
        padding: 0.8rem;
        margin-top: 0.5rem;
        border-radius: 0 4px 4px 0;
    }
    
    .copy-btn {
        float: right;
        background-color: #f1f1f1;
        border: none;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 0.8rem;
        cursor: pointer;
    }
    
    .copy-btn:hover {
        background-color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'lesson_content' not in st.session_state:
    st.session_state.lesson_content = None

# Sidebar inputs
with st.sidebar:
    st.markdown("<h1 style='font-size: 1.5rem; border-bottom: none;'>Lesson Parameters</h1>", unsafe_allow_html=True)
    
    subject = st.text_input("Subject", placeholder="Mathematics, Physics, History...")
    topic = st.text_input("Topic", placeholder="Quadratic Equations, World War II...")
    grade_level = st.selectbox("Grade Level", 
                             ["Elementary", "Middle School", "High School", "College"])
    teaching_style = st.selectbox("Teaching Style",
                                ["Direct Instruction", "Inquiry-Based", "Collaborative", "Flipped Classroom"])
    
    if st.button("Generate Lesson Plan"):
        if subject and topic:
            st.session_state.generate = True
        else:
            st.warning("Please enter both Subject and Topic")

# Main content area
st.markdown("<h1>Pedagogic Planner Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.1rem; color: #555;'>Create structured, research-based lesson plans with clear learning objectives and assessment strategies.</p>", 
            unsafe_allow_html=True)

if st.session_state.get('generate'):
    with st.spinner("Generating your professional lesson plan..."):
        # Prepare the prompt
        prompt = f"""Create a comprehensive lesson plan for {grade_level} {subject} on "{topic}" using {teaching_style} approach.

        Structure the output exactly as follows:

        ### Learning Objectives
        - List 3-5 clear, measurable objectives that students should achieve
        - Each objective should begin with "Students will be able to..."

        ### Teaching Strategies
        For each learning objective:
        1. Provide 5 unique, engaging teaching methods
        2. Include specific activities or techniques
        3. Align with {teaching_style} approach

        ### Homework Assignments
        Provide 2 meaningful problems/exercises:
        - Each problem should be clearly stated
        - Followed by a detailed solution showing all steps
        - Highlight any key formulas or concepts used
        - Format as:
            **Problem 1:** [problem statement]
            **Solution:** [step-by-step solution]

        ### Additional Practice Problems
        Create 3 problems for each difficulty level:
        - **Easy:** Basic comprehension
        - **Medium:** Application of concepts
        - **Hard:** Critical thinking/analysis
        - Include complete solutions for each
        """

        # Call Together API
        try:
            response = requests.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={
                    "Authorization": "Bearer 488d9538dd3cfbf08816cca9ae559157f252c3daf6356eb4e10dd965ff589ddb",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-ai/DeepSeek-V3",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert curriculum designer. Create meticulously structured lesson plans with clear sections. Use Markdown formatting with ### for section headings and ** for bold text."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 3500,
                    "temperature": 0.6
                },
                timeout=60
            )

            if response.status_code == 200:
                lesson_content = response.json()["choices"][0]["message"]["content"]
                st.session_state.lesson_content = lesson_content
                st.session_state.generate = False
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                st.stop()
        except Exception as e:
            st.error(f"Failed to connect to API: {str(e)}")
            st.stop()

if st.session_state.lesson_content:
    # Parse and display the content
    sections = {
        "objectives": "",
        "strategies": "",
        "homework": "",
        "practice": ""
    }
    
    current_section = None
    for line in st.session_state.lesson_content.split('\n'):
        if line.startswith('### Learning Objectives'):
            current_section = "objectives"
            sections[current_section] += line + "\n"
        elif line.startswith('### Teaching Strategies'):
            current_section = "strategies"
            sections[current_section] += line + "\n"
        elif line.startswith('### Homework Assignments'):
            current_section = "homework"
            sections[current_section] += line + "\n"
        elif line.startswith('### Additional Practice Problems'):
            current_section = "practice"
            sections[current_section] += line + "\n"
        elif current_section:
            sections[current_section] += line + "\n"
    
    # Display each section with copy button
    for section_name, section_content in sections.items():
        if section_content:
            with st.container():
                st.markdown(f"<div class='section-card'>{section_content}</div>", unsafe_allow_html=True)
                
                # Copy button for section
                copy_button = st.button(f"Copy {section_name.replace('_', ' ').title()}", 
                                      key=f"copy_{section_name}")
                if copy_button:
                    st.session_state[f"copied_{section_name}"] = True
                    st.code(section_content, language="markdown")
                    st.success(f"{section_name.replace('_', ' ').title()} copied to clipboard!")
    
    # Download buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # PDF Download
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Add title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"{subject} Lesson Plan: {topic}", ln=1)
        pdf.set_font("Arial", size=12)
        
        # Add content
        for line in st.session_state.lesson_content.split('\n'):
            if line.startswith('### '):
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, line[4:], ln=1)
                pdf.set_font("Arial", size=12)
            else:
                pdf.multi_cell(0, 10, line)
        
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=f"{subject}_{topic}_LessonPlan.pdf",
            mime="application/pdf"
        )
    
    with col2:
        # DOCX Download
        doc = Document()
        
        # Add title
        doc.add_heading(f"{subject} Lesson Plan: {topic}", level=1)
        
        # Convert markdown to HTML then to DOCX
        html_content = markdown.markdown(st.session_state.lesson_content)
        parser = HtmlToDocx()
        parser.add_html_to_document(html_content, doc)
        
        docx_bytes = io.BytesIO()
        doc.save(docx_bytes)
        st.download_button(
            label="Download DOCX",
            data=docx_bytes.getvalue(),
            file_name=f"{subject}_{topic}_LessonPlan.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
