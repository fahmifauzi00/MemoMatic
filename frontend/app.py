import streamlit as st
import requests
import os

# get the absolute path to the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMP_DIR = os.path.join(PROJECT_ROOT, "temp")

# create a temp directory if it does not exist
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

API_BASE_URL = "http://localhost:8000/v1"

st.title("Memomatic")
st.write("Upload your meeting recording and let AI generate professional minutes for you.")

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
        if st.button("Transcribe Audio"):
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
                        minutes = response.json()["minutes"]
                        
                        # display minutes
                        st.markdown("## Generated Minutes")
                        st.write(minutes)
                        
                        # download button
                        docx_path = os.path.join(TEMP_DIR, "minutes.docx")
                        if os.path.exists(docx_path):
                            with open(docx_path, "rb") as docx_file:
                                st.download_button(
                                    data=docx_file,
                                    file_name="meeting_minutes.docx",
                                    label="Download Minutes",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )
                        else:
                            st.error(f"Error: Generated document not found.")
                            
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error generating minutes: {str(e)}")
                        
    except Exception as e:
        st.error(f"An error occured: {str(e)}")
        
        
# footer
st.markdown("---")
st.markdown("Made with ❤️ using MaLLaM and Streamlit.")