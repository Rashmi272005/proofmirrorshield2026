
# ProofMirror Shield

### AI-Assisted Digital Content Risk Analysis Prototype

ProofMirror Shield is a web-based prototype that identifies potential warning signs in suspicious messages and URLs.

## Features

- Message risk analysis
- URL structure analysis
- Rule-based risk scoring
- Evidence and warning explanations
- Risk classification
- Report generation and JSON download
- Community report history
- Dashboard statistics
- Intelligence dashboard

## Technology Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python Flask
- Database: SQLite
- Testing: Pytest

## Risk Classification

| Score | Classification |
|---|---|
| 0–24 | Lower Risk |
| 25–59 | Needs Review |
| 60–100 | High Risk |

## Installation

1. Install Python 3.
2. Open the project folder in VS Code.
3. Create a virtual environment:

   python -m venv venv

4. Activate it on Windows:

   venv\Scripts\activate

5. Install dependencies:

   pip install -r requirements.txt

## Run the Application

python app.py

Open:

http://127.0.0.1:5000

## Run Tests

pytest -v

## Important Limitations

- Uses transparent rule-based checks.
- Does not independently verify facts.
- Does not visit submitted URLs.
- Does not use a live threat-intelligence database.
- Risk scores are indicators, not proof of authenticity.

Always verify important information using official sources.
