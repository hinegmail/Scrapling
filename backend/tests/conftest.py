"""Pytest configuration and fixtures"""

import pytest
import os
import sys

# Patch bcrypt before any imports that use it
try:
    # Disable bcrypt's wrap bug detection which causes issues
    import passlib.handlers.bcrypt as bcrypt_module
    bcrypt_module.detect_wrap_bug = lambda ident: False
    
    # Also patch the _finalize_backend_mixin to skip the detection
    original_finalize = bcrypt_module._BcryptBackend._finalize_backend_mixin
    
    @classmethod
    def patched_finalize(cls, name, dryrun=False):
        # Skip the wrap bug detection
        return True
    
    bcrypt_module._BcryptBackend._finalize_backend_mixin = patched_finalize
except Exception as e:
    print(f"Warning: Could not patch bcrypt: {e}")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.db.database import get_db
from app.main import app


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine"""
    # Use SQLite for testing
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create test database session"""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(test_db_session):
    """Create test client"""
    def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    
    from fastapi.testclient import TestClient
    return TestClient(app)
