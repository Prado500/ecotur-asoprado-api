"""Suite-wide test configuration, loaded by pytest before tests/conftest.py imports the app.

The app reads its settings once (app/core/config.py, ADR-0013). Every setting is fixed here, before
anything imports the app, so the suite never depends on a developer's .env file or on CI variables:
process environment variables take priority over the .env file.
"""

import os

TEST_ENVIRONMENT = {
    "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
    "JWT_SECRET_KEY": "test-only-jwt-secret-key-not-for-production",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "VERIFICATION_TOKEN_EXPIRE_MINUTES": "15",
    "MAIL_USERNAME": "smtp-account@test.com",
    "MAIL_PASSWORD": "test-mail-password",
    "MAIL_FROM": "sender@test.com",
    "MAIL_PORT": "465",
    "MAIL_SERVER": "smtp.test.com",
    "AZURE_STORAGE_CONNECTION_STRING": "UseDevelopmentStorage=true",
    "AZURE_CONTAINER_NAME": "ecotur-images",
    "AZURE_TEMPORAL_CONTAINER_NAME": "temp-ecotur-images",
    "FRONTEND_URL": "http://localhost:3000",
    "CORS_ORIGINS": "http://localhost:3000",
}

os.environ.update(TEST_ENVIRONMENT)
