import streamlit as st
import json
import os
from st_on_hover_tabs import on_hover_tabs
from streamlit_lottie import st_lottie
from menu.mcqgen import main as mcq
from menu.Ask_to_PDF import main as ask_to_pdf_page
from menu.NotesMaker import main as notes
from menu.ATS import main as ats_page
from menu.resources import main as resource_library, init_db
from menu.firebase import firebase_collaborative_study

# Page config
st.set_page_config(page_title="ScholarAI", page_icon="📚", layout="wide")

if "current_theme" not in st.session_state:
    st.session_state.current_theme = "light"

st.markdown('<style>' + open('./src/style.css').read() + '</style>', unsafe_allow_html=True)

# Initialize database
init_db()

def home():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<h1 style='margin-top: 50px;'>ScholarAI</h1>", unsafe_allow_html=True)
        st.markdown("<h3>Your Intelligent Academic Assistant</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='margin-top: 30px;'>
            <p>Transform your learning experience with our comprehensive AI-powered tools:</p>
            <ul>
                <li><strong>Generate MCQs</strong> from any study material</li>
                <li><strong>Query PDF documents</strong> for quick answers</li>
                <li><strong>Create study notes</strong> automatically</li>
                <li><strong>ATS optimization</strong> for your academic resume</li>
                <li><strong>Organize resources</strong> in one place</li>
            </ul>
            <p style='margin-top: 30px;'>Get started by selecting a tool from the sidebar!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        try:
            with open('src/Home_student.json', encoding='utf-8') as anim_source:
                animation_data = json.load(anim_source)
                st_lottie(animation_data, 1, True, True, "high", 350, -100)
        except Exception as e:
            st.error(f"Animation error: {e}")

def main():
    st.markdown("""
        <style>
            .css-1y0tads, .block-container, .css-1lcbmhc {
                padding-top: 0px !important;
                padding-bottom: 0px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.image('src/Logo College.png', width=70)
        
        tabs = on_hover_tabs(
            tabName=['Home', 'MCQ Generator', 'Ask To PDF', 'Notes Maker', 'ATS', 'Resource Library' , 'Study Room'],
            iconName=['home', 'center_focus_weak', 'search', 'edit', 'work', 'library_books' , 'group'],
            default_choice=0
        )
    
    menu = {
        'Home': home,
        'MCQ Generator': mcq,
        'Ask To PDF': ask_to_pdf_page,
        'Notes Maker': notes,
        'ATS': ats_page,
        'Resource Library': resource_library,
        'Study Room': firebase_collaborative_study,
    }
    
    menu[tabs]()

if __name__ == "__main__":
    main()