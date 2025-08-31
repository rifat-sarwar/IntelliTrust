# IntelliTrust - AI-Driven Blockchain Document Lifecycle Management

## Overview

IntelliTrust is a comprehensive platform for secure, dynamic digital document lifecycle management powered by AI and blockchain technology. The platform provides:

- **AI Gatekeeper**: Advanced document authenticity verification
- **Blockchain Anchor**: Immutable record of verified document hashes
- **Oracle Layer**: Secure integration of AI results with blockchain actions
- **Multi-tenant Architecture**: Support for academic, healthcare, finance, and real estate sectors

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Blockchain    │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│ (Hyperledger)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   AI Engine     │◄─────────────┘
                        │  (Document      │
                        │   Analysis)     │
                        └─────────────────┘
```

## Key Features

### 🎓 Academic Credentials (Primary Focus)
- Degree verification and validation
- Transcript analysis and authenticity checks
- Academic institution integration
- Student credential management

### 🏥 Healthcare (Future)
- Medical record verification
- Prescription validation
- Healthcare provider credentials

### 💰 Finance (Future)
- Financial document verification
- KYC/AML compliance
- Transaction record validation

### 🏠 Real Estate (Future)
- Property document verification
- Title deed validation
- Contract authenticity checks

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Shadcn/ui
- **Backend**: FastAPI, Python 3.11+, SQLAlchemy, Pydantic
- **Database**: PostgreSQL
- **Blockchain**: Hyperledger Fabric
- **AI/ML**: scikit-learn, OpenCV, TensorFlow
- **Authentication**: DID-based, JWT
- **File Storage**: AWS S3
- **Message Queue**: Redis
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL
- Redis

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd IntelliTrust
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start the development environment**
```bash
docker-compose up -d
```

4. **Install frontend dependencies**
```bash
cd frontend
npm install
npm run dev
```

5. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Project Structure

```
IntelliTrust/
├── frontend/                 # Next.js frontend application
├── backend/                  # FastAPI backend application
├── blockchain/               # Hyperledger Fabric configuration
├── ai-engine/               # AI/ML document analysis engine
├── docs/                    # Documentation
├── docker-compose.yml       # Development environment
└── README.md               # This file
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
