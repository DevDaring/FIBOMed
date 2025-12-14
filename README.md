# FIBOMed - Medical Visual Storytelling Platform

> Transform complex medical reports into patient-understandable visual narratives using BRIA FIBO's JSON-native controllable image generation.

![FIBOMed](https://img.shields.io/badge/FIBO-Hackathon-purple)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![React](https://img.shields.io/badge/React-18-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)

## 🎯 Project Vision

FIBOMed bridges the gap between complex medical reports and patient understanding through AI-powered visual storytelling. Using BRIA's FIBO API for controllable image generation and Google's Gemini for intelligent analysis, we transform medical data into clear, educational visualizations.

### Key Features

- **🏥 Multi-Role Support**: Doctor, Patient, and Technician dashboards
- **📄 Intelligent Report Processing**: Upload medical reports and get AI-analyzed summaries
- **🎨 FIBO Visualization**: Generate medical visualizations with JSON-native parameter control
- **🗣️ Voice Chat**: Multilingual voice interaction for accessibility
- **🔄 Expert Refinement**: Doctors can refine visualizations for accuracy
- **📊 Training Data Pipeline**: Collect expert corrections for BRIA AI training

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- BRIA FIBO API Key (Production)
- Google Gemini API Key
- Google Cloud Speech credentials (optional, for voice features)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/DevDaring/FIBOMed.git
cd FIBOMed
```

2. **Set up environment variables**
```bash
# Create secrets folder
mkdir secrets

# Create .env file with your API keys
cat > secrets/.env << EOF
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_API_KEY=your_google_api_key
FIBO_PROD_API_KEY=your_bria_fibo_production_key
GOOGLE_APPLICATION_CREDENTIALS=secrets/speech_key.json
EOF
```

3. **Run the application**

**Windows:**
```batch
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

4. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 👥 Test Credentials

| Role | Email | User ID |
|------|-------|---------|
| Doctor | dr.anita@fibomed.com | DOC001 |
| Doctor | dr.vikram@fibomed.com | DOC002 |
| Patient | rajesh.kumar@email.com | PAT001 |
| Patient | priya.patel@email.com | PAT002 |
| Technician | tech.ravi@fibomed.com | TECH001 |

## 📁 Project Structure

```
FIBOMed/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   │   ├── chat.py     # Chat endpoints
│   │   │   ├── fibo.py     # FIBO visualization endpoints
│   │   │   ├── reports.py  # Medical reports endpoints
│   │   │   └── users.py    # User management endpoints
│   │   ├── integrations/   # External API clients
│   │   │   ├── bria_fibo/  # BRIA FIBO client
│   │   │   └── google_gemini/ # Gemini client
│   │   └── services/       # Business logic
│   └── main.py
├── frontend/               # React frontend
│   └── src/
│       ├── components/     # React components
│       └── api/           # API clients
├── data/                   # Data storage (CSV-based)
│   ├── csv_files/         # Database CSVs
│   ├── uploads/           # Uploaded files
│   │   ├── reports/       # Medical reports
│   │   └── prescriptions/ # Prescriptions
│   ├── generated/         # Generated content
│   │   └── visualizations/
│   └── resources/         # Parameter presets
├── secrets/               # API keys (gitignored)
└── Dockerfile            # GCP Cloud Run deployment
```

## 🔌 API Endpoints

### Users
- `POST /api/v1/users/login` - Authenticate user
- `GET /api/v1/users/dashboard/{user_id}` - Get user dashboard
- `GET /api/v1/users/doctors` - List all doctors
- `GET /api/v1/users/patients` - List all patients

### Reports
- `POST /api/v1/reports/upload` - Upload medical report
- `POST /api/v1/reports/process/{report_id}` - Process with Gemini AI
- `GET /api/v1/reports/list` - List all reports
- `POST /api/v1/reports/generate-visualization` - Generate FIBO visualization

### FIBO Visualization
- `POST /api/v1/fibo/generate` - Generate visualization from prompt
- `POST /api/v1/fibo/refine/{id}` - Refine existing visualization
- `GET /api/v1/fibo/{id}` - Get visualization details

### Chat
- `POST /api/v1/chat/text` - Send text message
- `POST /api/v1/chat/voice` - Send voice message

## 🎨 FIBO Integration

FIBOMed uses BRIA's FIBO API with intelligent parameter generation:

```json
{
  "scene_type": "medical_visualization",
  "primary_subject": {
    "system": "cardiovascular",
    "organ": "heart",
    "view": "anterior"
  },
  "pathology": {
    "type": "coronary_blockage",
    "severity": 7,
    "conditions": ["CAD", "Stenosis"]
  },
  "style": {
    "complexity": "patient_friendly",
    "realism": "semi-realistic"
  },
  "background": {
    "type": "blurred_body_interior"
  }
}
```

### Auto-Enhancement

Medical prompts are automatically enhanced with:
- Blurred body interior backgrounds for anatomical context
- Appropriate lighting and camera angles
- Patient-friendly complexity levels

## 🐳 Docker Deployment

```bash
# Build image
docker build -t fibomed .

# Run container
docker run -p 8000:8000 fibomed
```

### GCP Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/fibomed

# Deploy
gcloud run deploy fibomed \
  --image gcr.io/PROJECT_ID/fibomed \
  --platform managed \
  --allow-unauthenticated
```

## 📊 Sample Medical Reports

The project includes sample medical reports for testing:

1. **Cardiac Report** (`data/uploads/reports/cardiac_report_001.txt`)
   - Patient with coronary artery disease
   - 70% RCA stenosis
   - Includes ECG and angiography findings

2. **Diabetes Report** (`data/uploads/reports/diabetes_report_002.txt`)
   - Type 2 DM with complications
   - Diabetic neuropathy and retinopathy
   - Lab results and treatment plan

3. **Pulmonary Report** (`data/uploads/reports/pulmonary_report_003.txt`)
   - COPD GOLD Stage II
   - Emphysema findings
   - Spirometry and HRCT results

## 🏆 Hackathon Categories

- **Primary**: Best JSON-Native or Agentic Workflow
- **Secondary**: Best Overall & Best Controllability

## 📝 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines.

---

Built with ❤️ for the FIBO Hackathon
