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

# initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'active_session' not in st.session_state:
    st.session_state.active_session = None
if 'file_upload' not in st.session_state:
    st.session_state.file_uploaded = False
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
    
def check_rate_limit_status():
    """Check current rate limit status"""
    try:
        response = requests.get(f"{API_BASE_URL}/rate-limit-status")
        return response.json()
    except requests.exceptions.RequestException:
        return None

def format_time_remaining(seconds):
    """Format remaining time in a human-readable format"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{int(hours)}h {int(minutes)}m"

def display_rate_limit_info():
    """Display rate limit information in the sidebar"""
    rate_info = check_rate_limit_status()
    
    if rate_info:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Usage Limits")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            st.metric(
                "Cycles Remaining",
                f"{rate_info['cycles_remaining']}/{rate_info['total_daily_limit']}"
            )
        
        with col2:
            time_remaining = format_time_remaining(rate_info['time_remaining_seconds'])
            st.metric("Time Until Reset", time_remaining)
            
        if rate_info['cycles_remaining'] == 0:
            st.sidebar.warning("⚠️ You've reached your daily limit. Please try again tomorrow.")
        elif rate_info['cycles_remaining'] <= 1:
            st.sidebar.warning("⚠️ You're almost at your daily limit!")
            
        if rate_info['active_cycle']:
            st.sidebar.info("🔄 You have an active transcription cycle.")

def start_new_cycle():
    """Start a new transcription cycle"""
    try:
        response = requests.post(f"{API_BASE_URL}/start-cycle")
        if response.status_code == 429:
            error_data = response.json()
            rate_info = error_data['detail']['rate_limit_info']
            time_remaining = format_time_remaining(rate_info['time_remaining_seconds'])
            st.error(f"""
            🚫 Daily limit exceeded!
            Please try again in {time_remaining}.
            Daily limit: {rate_info['total_daily_limit']} cycles per day.
            """)
            return None
            
        response.raise_for_status()
        session_data = response.json()
        st.session_state.active_session = session_data['session_id']
        return session_data
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error starting new cycle: {str(e)}")
        return None
    
def handle_file_upload(audio_file):
    """Handle file upload only if necessary"""
    if not st.session_state.file_uploaded or st.session_state.current_file != audio_file.name:
        try:
            # Save file
            file_path = os.path.join(TEMP_DIR, audio_file.name)
            with open(file_path, "wb") as f:
                f.write(audio_file.getbuffer())
                
            # Upload file
            response = requests.post(
                f"{API_BASE_URL}/upload_audio/",
                files={"file": audio_file}
            )
            response.raise_for_status()
            
            # Update session state
            st.session_state.file_uploaded = True
            st.session_state.current_file = audio_file.name
            return True
            
        except Exception as e:
            st.error(f"Error uploading file: {str(e)}")
            return False
    return True

# main app    
st.title("Memomatic")
st.write("A streamlined meeting minutes generator that transcribes audio files and generates formatted meeting minutes using AI.")

# display rate limit info
display_rate_limit_info()

# file upload
audio_file = st.file_uploader(
    "Upload your meeting recording (Supported formats: MP3, WAV)",
    type=["mp3", "wav"],
    help="Maximum file size: 200MB"
)

if audio_file:
    # Handle file upload only when necessary
    if handle_file_upload(audio_file):
        # Transcribe button
        if st.button("🎙️ Transcribe Audio"):
            cycle_data = start_new_cycle()
            
            if cycle_data:
                with st.spinner("Transcribing audio... This may take a few minutes."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/transcribe/{audio_file.name}",
                            params={"session_id": st.session_state.active_session}
                        )
                        response.raise_for_status()
                        st.session_state.transcript = response.json()["transcript"]
                        st.success("Transcription completed!")
                        
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error during transcription: {str(e)}")
                        st.session_state.active_session = None
        
        # Show transcription and generate minutes if available
        if st.session_state.transcript:
            with st.expander("View Transcription"):
                st.write(st.session_state.transcript)
            
            # Generate minutes button
            if st.button("📝 Generate Minutes", key="generate_minutes"):
                with st.spinner("Generating Minutes... Please wait."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/generate_minutes",
                            json={
                                "transcript": st.session_state.transcript,
                                "session_id": st.session_state.active_session
                            }
                        )
                        response.raise_for_status()
                        minutes_content = response.json()["minutes"]
                        
                        try:
                            # Parse and display minutes
                            minutes_data = json.loads(minutes_content)
                            
                            # Display formatted minutes
                            st.markdown("---")
                            st.markdown(f"<h1 class='minutes-title'>{minutes_data['title']}</h1>",
                                        unsafe_allow_html=True)
                            
                            # Summary
                            st.markdown("<h2 class='section-title'>Summary</h2>", 
                                        unsafe_allow_html=True)
                            st.markdown(f"<div class='summary-section'>{minutes_data['summary']}</div>", 
                                        unsafe_allow_html=True)
                            
                            # Key Points
                            if minutes_data.get('key_points'):
                                st.markdown("<h2 class='section-title'>Key Points</h2>", 
                                            unsafe_allow_html=True)
                                for point in minutes_data['key_points']:
                                    st.markdown(f"<div class='key-point-item'>• {point}</div>", 
                                                unsafe_allow_html=True)
                            
                            # Action Items
                            if minutes_data.get('action_items'):
                                st.markdown("<h2 class='section-title'>Action Items</h2>", 
                                            unsafe_allow_html=True)
                                for item in minutes_data['action_items']:
                                    st.markdown(f"<div class='action-item'>• {item}</div>",
                                                unsafe_allow_html=True)
                            
                            # Decisions
                            if minutes_data.get('decisions'):
                                st.markdown("<h2 class='section-title'>Decisions</h2>", 
                                            unsafe_allow_html=True)
                                for decision in minutes_data['decisions']:
                                    st.markdown(f"<div class='decision-item'>• {decision}</div>",
                                                unsafe_allow_html=True)
                            
                            # Download button
                            docx_path = os.path.join(TEMP_DIR, "minutes.docx")
                            if os.path.exists(docx_path):
                                with open(docx_path, "rb") as docx_file:
                                    st.download_button(
                                        label="📄 Download Minutes",
                                        data=docx_file,
                                        file_name="meeting_minutes.docx",
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                        key="download_minutes"
                                    )
                            else:
                                st.error("Error: Generated document not found.")
                                
                        except json.JSONDecodeError:
                            st.write(minutes_content)
                            
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error generating minutes: {str(e)}")
        
        
# sidebar
with st.sidebar:
    st.header("About MemoMatic")
    st.write("""
    MemoMatic automatically generates meeting minutes from audio recordings using AI.
    """)
    
    st.subheader("How it works")
    st.write("""
    1. Upload your audio file
    2. Click "Transcribe Audio" to start a new cycle
    3. Review the transcript
    4. Generate formatted minutes
    5. Download your minutes
    """)
    
    st.subheader("Usage Limits")
    st.write("""
    - 3 usage per day
    - Each usage includes: transcription, generation and download
    - Usage reset every 24 hours
    """)
    
    st.subheader("Tools & Frameworks")
    st.write("""
    - **Streamlit**: Python library for building web applications
    - **MaLLaM (Malaysian Large Language Model)**: AI models by Mesolitica for transcribing and generating meeting minutes.
    - **FastAPI**: Python framework for building APIs
    """)
    
    st.markdown("---")
    st.write("""
    ps. This is a prototype and not for production use. If you want to try MaLLaM and Mesolitica's API, check out [their website](https://mesolitica.com/).
    """)
    
    
# footer
st.markdown("---")
st.markdown("Made with ❤️ using MaLLaM API and Streamlit.")