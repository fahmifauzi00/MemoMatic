# MemoMatic

MemoMatic is a streamlined meeting minutes generator that automatically transcribes audio recordings and generates formatted meeting minutes using AI. Built with FastAPI and Streamlit, it provides an intuitive interface for converting meeting recordings into professional, structured documents.

<div align="center">
  <img src="https://github.com/user-attachments/assets/3b9de95d-d8ed-4f8f-9eec-7ecbd1531a0c" width="800" alt="MemoMatic Main Interface"/>
</div>


## Features

- 🎙️ **Audio Transcription**: Supports MP3 and WAV file formats
- 📝 **AI-Powered Minutes Generation**: Automatically structures content into clear, professional minutes
- 💾 **Multiple Export Options**: Download as DOCX files
- 🔄 **Rate Limiting**: Built-in usage management (3 cycles per day)
- 🎯 **Structured Output**: Generates organized minutes with:
  - Meeting title
  - Executive summary
  - Key points
  - Action items
  - Decisions
- 🎨 **Clean, Intuitive UI**: User-friendly interface built with Streamlit

<div align="center">
  <img src="https://github.com/user-attachments/assets/b05d1f56-b404-4580-98f9-11b41cf98380" width="600" alt="Generated Minutes Example"/>
</div>


## How It Works

1. **Upload**: User uploads an audio recording of their meeting
2. **Transcription**: Audio is transcribed using Mesolitica's API
3. **Processing**: AI analyzes the transcript and extracts key information
4. **Generation**: Formatted minutes are generated with proper structure
5. **Download**: User can review and download the minutes as a DOCX file

<div align="center">
  <img src="https://github.com/user-attachments/assets/f5c0d91b-7784-49d5-b9da-4eba5d19b8b3" width="600" alt="MemoMatic workflow"/>
</div>


## User Flow

1. User accesses the MemoMatic web interface
2. Uploads meeting recording (MP3/WAV)
3. Clicks "Transcribe Audio" to initiate processing
4. Reviews the generated transcript
5. Clicks "Generate Minutes" to create formatted minutes
6. Downloads the final document in DOCX format

## Technical Architecture

### Backend (FastAPI)
- Rate limiting middleware
- File caching system
- Audio transcription service
- Minutes generation service
- Document formatting service

### Frontend (Streamlit)
- File upload handling
- Progress tracking
- Real-time status updates
- Document preview
- Download management

## Setup Instructions

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)
- Mesolitica API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/memomatic.git
cd memomatic
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
MESOLITICA_API_URL=https://api.mesolitica.com
MESOLITICA_API_KEY=your_api_key_here
```

### Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Start the frontend application (in a new terminal):
```bash
cd frontend
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## API Endpoints

### Rate Limiting
- `GET /v1/rate-limit-status`: Check current rate limit status
- `POST /v1/start-cycle`: Start a new transcription cycle

### File Operations
- `POST /v1/upload_audio`: Upload audio file
- `POST /v1/transcribe/{filename}`: Transcribe uploaded audio
- `POST /v1/generate_minutes`: Generate minutes from transcript

## Usage Limits

- 3 transcription cycles per day
- Each cycle includes:
  - One audio transcription
  - One minutes generation
  - One document download
- Usage resets every 24 hours

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built using [Mesolitica's MaLLaM API](https://mesolitica.com/)
- Frontend powered by [Streamlit](https://streamlit.io/)
- Backend powered by [FastAPI](https://fastapi.tiangolo.com/)

## Note

This is a prototype implementation and not intended for production use. For production deployments, additional security measures, error handling, and scalability considerations would need to be implemented.

MaLLaM is a multi-lingual model developed by Mesolitica which include main Malaysian language Malay, Mandarin, Tamil, English and other dialects. MaLLaM also support 128k context length, chat language model, function call and it is OpenAI compatible. 

---

Made with ❤️ using MaLLaM API and Streamlit
