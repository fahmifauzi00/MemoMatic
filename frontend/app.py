import streamlit as st
import requests
import os
import json
from utils.style_utils import load_css

# get the absolute path to the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMP_DIR = os.path.join(PROJECT_ROOT, "temp")

# create a temp directory if it does not exist
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

API_BASE_URL = "http://localhost:8000/v1"

# set page config
st.set_page_config(page_title="MemoMatic", page_icon=":memo:", layout="centered")

# load styles
load_css()

st.title("Memomatic")
st.write("A streamlined meeting minutes generator that transcribes audio files and generates formatted meeting minutes using AI.")

# initialize session state for storing transcript
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
    
    
# file upload
audio_file = st.file_uploader(
    "Upload your meeting recording (Supported formats: MP3, WAV)",
    type=["mp3", "wav"],
    help="Maximum file size: 200MB"
)

if audio_file:
    try:
        # save file
        file_path = os.path.join(TEMP_DIR, audio_file.name)
        with open(file_path, "wb") as f:
            f.write(audio_file.getbuffer())
        st.success("File uploaded successfully!")
            
        # transcribe audio
        if st.button("🎙️ Transcribe Audio"):
            with st.spinner("Transcribing audio... This may take a few minutes."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/transcribe/{audio_file.name}"
                    )
                    response.raise_for_status() # raise exception for bad status codes
                    st.session_state.transcript = response.json()["transcript"]
                    st.success("Transcription completed!")
                    
                except requests.exceptions.RequestException as e:
                    st.error(f"Error during transcription: {str(e)}")
                    st.stop()
                    
        if st.session_state.transcript: # show transcription with expander
            with st.expander("View Transcription"):
                st.write(st.session_state.transcript)
                        
                
            # generate minutes
            if st.button("📝 Generate Minutes"):
                with st.spinner("Generating Minutes... Please wait."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/generate_minutes/",
                            json={"transcript": st.session_state.transcript}
                        )
                        response.raise_for_status()
                        minutes_content = response.json()["minutes"]
                        
                        try:
                            # parse the minutes content
                            minutes_data = json.loads(minutes_content)
                            
                            # display formatted minutes
                            st.markdown("---")
                            st.markdown(f"<h1 class='minutes-title'>{minutes_data['title']}</h1>",
                                        unsafe_allow_html=True)
                            
                            # summary
                            st.markdown("<h2 class='section-title'>Summary</h2>", 
                                          unsafe_allow_html=True)
                            st.markdown(f"<div class='summary-section'>{minutes_data['summary']}</div>", 
                                          unsafe_allow_html=True)
                                
                            # Key Points
                            if minutes_data.get('key_points'):
                                st.markdown("<h2 class='section-title'>Key Points</h2>", 
                                            unsafe_allow_html=True)
                                st.markdown("<div class='key-points-section'>", unsafe_allow_html=True)
                                for point in minutes_data['key_points']:
                                    st.markdown(f"<div class='key-points-item'>• {point}</div>", 
                                                unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                            # action Items
                            if minutes_data.get('action_items'):
                                st.markdown("<h2 class='section-title'>Action Items</h2>", 
                                            unsafe_allow_html=True)
                                st.markdown("<div class='action-items-section'>", unsafe_allow_html=True)
                                for item in minutes_data['action_items']:
                                    st.markdown(f"<div class='action-items-item'>• {item}</div>",
                                                unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                            # decisions
                            if minutes_data.get('decisions'):
                                st.markdown("<h2 class='section-title'>Decisions</h2>", 
                                            unsafe_allow_html=True)
                                st.markdown("<div class='decisions-section'>", unsafe_allow_html=True)
                                for decision in minutes_data['decisions']:
                                    st.markdown(f"<div class='decisions-item'>• {decision}</div>",
                                                unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)
                                    
                        except json.JSONDecodeError:
                            # if not JSON, display raw content
                            st.write(minutes_content)
                        
                        # download button
                        docx_path = os.path.join(TEMP_DIR, "minutes.docx")
                        if os.path.exists(docx_path):
                            with open(docx_path, "rb") as docx_file:
                                st.download_button(
                                    data=docx_file,
                                    file_name="meeting_minutes.docx",
                                    label="📄 Download Minutes",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key="download_button"
                                )
                        else:
                            st.error(f"Error: Generated document not found.")
                            
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error generating minutes: {str(e)}")
                        
    except Exception as e:
        st.error(f"An error occured: {str(e)}")
        
        
# sidebar
with st.sidebar:
    st.header("About MemoMatic")
    st.write("""
    MemoMatic automatically generates meeting minutes from audio recordings. The system will:
    1. Transcribe the audio
    2. Generate a structured minutes with standard format
    """)
    
    st.subheader("Tools & Frameworks")
    st.write("""
    - **Streamlit**: Python library for building web applications
    - **MaLLaM (Malaysian Large Language Model)**: AI models by Mesolitica for transcribing and generating meeting minutes.
    - **FastAPI**: Python framework for building APIs
    """)
    
    
    st.write("""
    ps. This is a prototype and not for production use. If you want to try MaLLaM and Mesolitica's API, check out [here](https://mesolitica.com/).
    """)
    
    
# footer
st.markdown("---")
st.markdown("Made with ❤️ using MaLLaM API and Streamlit.")