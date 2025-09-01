# intelliHR-AI

## Project Overview
intelliHR-AI is an AI-powered platform designed to enhance HR processes through automation, analytics, and intelligent decision-making. The project is structured for scalability and maintainability, following best practices in Python application development.

## Project Structure
```
intelliHR-AI/
├── agents/         # AI agents and related logic
├── app/            # Main application code
│   ├── main.py     # Application entry point
│   ├── models/     # Data models
│   ├── routes/     # API routes
│   ├── services/   # Business logic/services
│   └── utils/      # Utility functions
├── config/         # Configuration files
├── tests/          # Unit and integration tests
├── requirements.txt# Python dependencies
├── env_example     # Example environment variables
├── README.md       # Project documentation
```


## Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd intelliHR-AI
   ```
2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv

   # On Windows PowerShell
   .\venv\Scripts\Activate.ps1

   # On Windows CMD
   .\venv\Scripts\activate.bat

   # On Unix or MacOS
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment variables:**
   - Copy `env_example` to `.env` and update values as needed.


### Running the Application (FastAPI)

The server uses [FastAPI](https://fastapi.tiangolo.com/) for the backend. To run the development server, use [uvicorn](https://www.uvicorn.org/):


```bash
# Run on default port 8000
uvicorn app.main:app --reload
# Run on a custom port (e.g., 8080)
uvicorn app.main:app --reload --port 8080
```

This will start the FastAPI server with auto-reload enabled for development. By default, the server will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000) or your chosen port (e.g., [http://127.0.0.1:8080](http://127.0.0.1:8080)).

#### API Documentation
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Running Tests
```bash
pytest -v
```
## Notes
- Ensure Python 3.8+ is installed.
- For any missing dependencies, add them to `requirements.txt` and re-run the install step.
- For development, use the `--reload` flag with Uvicorn for auto-reload.

## Contributing
1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a pull request

## License
This project is licensed under the MIT License.
