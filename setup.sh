#!/bin/bash

# IntelliTrust Platform Setup Script
# This script sets up the complete IntelliTrust platform with all components

set -e

echo "🚀 IntelliTrust Platform Setup"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check prerequisites
print_status "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    print_status "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    print_status "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    print_status "Visit: https://nodejs.org/"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.11+ first."
    print_status "Visit: https://www.python.org/downloads/"
    exit 1
fi

print_success "All prerequisites are satisfied!"

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating environment file..."
    cp env.example .env
    print_success "Environment file created from template"
    print_warning "Please review and update .env file with your configuration"
else
    print_status "Environment file already exists"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/minio
mkdir -p data/blockchain
print_success "Directories created"

# Setup backend
print_status "Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Python dependencies installed"

# Run database migrations
print_status "Running database migrations..."
python migrate.py
print_success "Database migrations completed"

# Create admin user
print_status "Creating admin user..."
python create_admin.py
print_success "Admin user created"

cd ..

# Setup frontend
print_status "Setting up frontend..."
cd frontend

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install
print_success "Node.js dependencies installed"

cd ..

# Setup AI Engine
print_status "Setting up AI Engine..."
cd ai-engine

# Install AI Engine dependencies
print_status "Installing AI Engine dependencies..."
pip install -r requirements.txt
print_success "AI Engine dependencies installed"

cd ..

# Setup blockchain (optional)
print_status "Setting up blockchain configuration..."
if [ ! -d "blockchain/crypto" ]; then
    mkdir -p blockchain/crypto
    print_success "Blockchain directories created"
    print_warning "Blockchain setup requires additional configuration. See blockchain/README.md"
else
    print_status "Blockchain directories already exist"
fi

# Build Docker images
print_status "Building Docker images..."
docker-compose build
print_success "Docker images built"

# Start services
print_status "Starting services..."
docker-compose up -d
print_success "Services started"

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend is running"
else
    print_warning "Backend health check failed"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend is running"
else
    print_warning "Frontend health check failed"
fi

# Check AI Engine
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    print_success "AI Engine is running"
else
    print_warning "AI Engine health check failed"
fi

# Check MinIO
if curl -f http://localhost:9000/minio/health/live > /dev/null 2>&1; then
    print_success "MinIO is running"
else
    print_warning "MinIO health check failed"
fi

echo ""
echo "🎉 IntelliTrust Platform Setup Complete!"
echo "========================================"
echo ""
echo "Services are now running:"
echo "  • Frontend: http://localhost:3000"
echo "  • Backend API: http://localhost:8000"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • AI Engine: http://localhost:8001"
echo "  • MinIO Console: http://localhost:9001"
echo ""
echo "Default credentials:"
echo "  • Admin: admin@intellitrust.com / admin123"
echo "  • MinIO: minioadmin / minioadmin123"
echo ""
echo "Next steps:"
echo "  1. Visit http://localhost:3000 to access the platform"
echo "  2. Log in with admin credentials"
echo "  3. Configure your organization and users"
echo "  4. Upload and verify your first document"
echo ""
echo "For more information:"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • README: README.md"
echo "  • Issues: Check the GitHub repository"
echo ""
print_warning "Remember to change default passwords in production!"
echo ""
