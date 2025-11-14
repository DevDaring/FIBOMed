# FIBOMed - Voice-Enabled Medical Chat Application

A multilingual voice chat application powered by Google Cloud Speech APIs and Gemini Flash AI. This application enables users to have natural voice conversations with an AI assistant that can help understand medical information.

## Features

- **Voice Input**: Record your voice and convert speech to text using Google Speech-to-Text API
- **AI-Powered Responses**: Get intelligent responses from Google Gemini Flash AI
- **Text-to-Speech**: Hear responses spoken back to you with Google Text-to-Speech API
- **Multilingual Support**: Supports multiple languages including English, Hindi, Spanish, French, German, Japanese, and Chinese
- **Speaker Toggle**: Enable or disable audio playback of responses
- **Chat History**: All conversations are stored in CSV database for future reference
- **Responsive UI**: Modern, clean interface that works on desktop and mobile

## Architecture

### Backend (Python FastAPI)
- FastAPI web framework for high-performance API endpoints
- Google Cloud Speech-to-Text for voice recognition
- Google Cloud Text-to-Speech for audio generation
- Google Gemini Flash for AI-powered responses
- CSV-based database for data persistence

### Frontend (React + TypeScript + Vite)
- React 18 with TypeScript for type safety
- Vite for fast development and building
- Modern CSS with responsive design
- Web Audio API for voice recording

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn
- Google Cloud Platform account
- Google AI Studio account (for Gemini API)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd FIBOMed
```

### 2. Get API Keys

#### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the API key

#### Google Cloud Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Cloud Speech-to-Text API
   - Cloud Text-to-Speech API
4. Go to "Credentials" > "Create Credentials" > "Service Account"
5. Create a service account and download the JSON key file
6. Save the JSON file securely (do NOT commit to git)

### 3. Quick Setup (Automated)

Run the setup script:

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This will:
- Create Python virtual environment
- Install Python dependencies
- Install Node dependencies
- Initialize CSV database
- Create .env file from template

### 4. Manual Setup (Alternative)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

cd ..
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

cd ..
```

#### Initialize Database

```bash
python3 scripts/init_csv.py
```

### 5. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```env
   # Gemini API Key
   GEMINI_API_KEY=your_actual_gemini_api_key

   # Path to Google Cloud credentials JSON file
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/google-credentials.json

   # Generate random secret keys (you can use: python -c "import secrets; print(secrets.token_urlsafe(32))")
   SECRET_KEY=your_random_secret_key
   JWT_SECRET=your_random_jwt_secret
   ```

## Running the Application

### Start Backend Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

The backend will start on `http://localhost:8000`

### Start Frontend Development Server

In a new terminal:

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173`

### Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

## Usage

### Text Chat
1. Type your message in the text input area
2. Click "Send" or press Enter
3. The AI will respond with text
4. If speaker is enabled, you'll hear the response

### Voice Chat
1. Click "Start Recording" button
2. Speak your message (microphone permission required)
3. Click "Stop Recording" when done
4. Your speech will be transcribed and sent to the AI
5. You'll see the transcription and AI response
6. If speaker is enabled, you'll hear the response

### Controls
- **Speaker Toggle**: Enable/disable audio playback of responses
- **Language Selector**: Choose your preferred language
- **Clear Button**: Clear the current chat session

## Project Structure

```
FIBOMed/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/v1/            # API endpoints
│   │   ├── core/              # Security, exceptions
│   │   ├── database/          # CSV database manager
│   │   ├── integrations/      # External API clients
│   │   │   └── google_gemini/ # Gemini integration
│   │   ├── services/          # Business logic
│   │   │   ├── voice_service.py    # STT/TTS
│   │   │   └── chat_service.py     # Chat processing
│   │   ├── schemas/           # Pydantic models
│   │   └── config.py          # Configuration
│   ├── main.py                # Application entry point
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React + TypeScript frontend
│   ├── src/
│   │   ├── api/               # API integration
│   │   ├── components/        # React components
│   │   │   └── chat/          # Chat components
│   │   ├── types/             # TypeScript types
│   │   ├── App.tsx            # Main app component
│   │   └── main.tsx           # Entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
│
├── data/                       # Data storage
│   ├── csv_files/             # CSV database files
│   ├── uploads/audio/         # Uploaded audio files
│   └── generated/audio/       # Generated audio responses
│
├── scripts/                    # Utility scripts
│   ├── init_csv.py            # Initialize database
│   └── setup.sh               # Setup script
│
├── .env.example               # Environment variables template
├── .gitignore
└── README.md
```

## API Endpoints

### Chat Endpoints

#### POST `/api/v1/chat/text`
Send a text message and receive AI response

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "session_id": "optional-session-id",
  "enable_tts": true,
  "language_code": "en-US"
}
```

**Response:**
```json
{
  "response": "AI generated response",
  "audio_url": "/generated/audio/xxx.mp3",
  "session_id": "session-id",
  "timestamp": "2024-01-01T00:00:00"
}
```

#### POST `/api/v1/chat/voice`
Send a voice message and receive AI response

**Request:** Multipart form data
- `audio`: Audio file (WebM, OGG, WAV)
- `session_id`: Optional session ID
- `enable_tts`: Enable audio response (default: true)
- `language_code`: Language code for STT

**Response:**
```json
{
  "transcription": "Transcribed user speech",
  "response": "AI generated response",
  "audio_url": "/generated/audio/xxx.mp3",
  "session_id": "session-id",
  "timestamp": "2024-01-01T00:00:00"
}
```

#### POST `/api/v1/chat/session/clear`
Clear a chat session

#### GET `/api/v1/chat/session/{session_id}/history`
Get chat history for a session

### Health Check

#### GET `/api/v1/health`
Check API health status

## Supported Languages

- English (en-US)
- Hindi (hi-IN)
- Spanish (es-ES)
- French (fr-FR)
- German (de-DE)
- Japanese (ja-JP)
- Chinese Simplified (zh-CN)

The application automatically detects the language of AI responses and uses appropriate TTS voices.

## Troubleshooting

### Microphone Not Working
- Ensure you've granted microphone permissions to your browser
- Check browser console for errors
- Try using HTTPS (some browsers require secure context)

### API Errors
- Verify your API keys are correct in `.env`
- Check that Google Cloud APIs are enabled
- Ensure service account has necessary permissions
- Check backend logs for detailed error messages

### Audio Playback Issues
- Ensure speaker is enabled (toggle in UI)
- Check browser audio permissions
- Verify audio files are being generated in `data/generated/audio/`

### CSV Database Issues
- Run `python3 scripts/init_csv.py` to reinitialize database
- Check file permissions on `data/csv_files/` directory

## Security Considerations

1. **Never commit `.env` file or Google Cloud credentials to git**
2. **Use environment-specific secret keys in production**
3. **Enable HTTPS in production**
4. **Implement rate limiting for API endpoints**
5. **Add authentication for production use**

## Development

### Running Tests

```bash
cd backend
pytest
```

### Building for Production

#### Backend
```bash
cd backend
pip install -r requirements.txt
# Use gunicorn or similar WSGI server
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

#### Frontend
```bash
cd frontend
npm run build
# Serve the dist/ folder with any static file server
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open an issue on the GitHub repository.

## Acknowledgments

- Google Cloud for Speech-to-Text and Text-to-Speech APIs
- Google for Gemini Flash AI
- FastAPI framework
- React and Vite communities
