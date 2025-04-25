# RAG (Retrieval-Augmented Generation) Project

## Project Overview

This is a Retrieval-Augmented Generation (RAG) demo project built with FastAPI and various machine learning libraries.

## Prerequisites

- Python 3.12
- pip or pip3

## Installation

### Create a Virtual Environment

```bash
python -m venv ~/venv
```

### Install Dependencies

Frontend: build and copy to backend

```bash
cd frontend
npm install
npm run build
```

or run develop

```bash
npm start
```

Backend:

```bash
cd backend
source ~/venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt  # Install project dependencies
```

## Development Setup

### Running the Application

```bash
source ~/venv/bin/activate
uvicorn --host 0.0.0.0 --port 8000 app.main:app --reload
```

## Project Structure

```
backend/
│
├── app/                # Main application code
│   ├── api/            # api
│   ├── core/           # config app, ...
│   ├── models/         # Database models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   └── main.py         # Application entry point
│
├── uploads/            # Directory for uploaded files
├── www/                # Web-related resources
├── requirements.txt    # Project configuration
└── README.md           # This file
```

## Key Dependencies

- FastAPI
- SQLAlchemy
- Pydantic
- LangChain
- OpenAI
- scikit-learn
- pandas

## Configuration

Use `.env` file for environment-specific configurations.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Specify your license]
