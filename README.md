# Azure Key Vault for KEK and DEK

This project is a Flask application that securely handles customer feedback using Azure Key Vault for encryption. It allows users to submit feedback, which is then encrypted before being stored in a database. The application provides endpoints for submitting and retrieving feedback, ensuring that sensitive information such as email addresses and contact numbers are protected through encryption.

## Features
- Securely encrypts customer feedback using Azure Key Vault.
- Provides RESTful API endpoints for submitting and retrieving feedback.
- Implements authentication for accessing feedback records.
- Uses SQLAlchemy for database interactions.

## Installation Requirements
- Flask
- Azure Identity
- Azure Key Vault Secrets
- SQLAlchemy

## Setup
1. Install the required dependencies.
   ```bash
   pip install Flask Flask-SQLAlchemy Flask-Session Flask-CORS azure-identity azure-keyvault-keys pycryptodome
   ```
2. Set up the Azure Key Vault and configure the necessary environment variables.
3. Run the application.