import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from db import Base, TodoDB, UserDB
from main import app, get_db, get_current_user
from schemas import User
import os

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
@pytest.fixture(scope="function")
def test_db():
    engine=create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

    Base.metadata.create_all(bind=engine)
    TestingSessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
    db=TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("./test_test.db"):
            os.remove("./test_test.db")

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    app.dependency_overrides[get_db]=override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(test_db):
    from main import get_password_hash
    user=UserDB(email="test@gmail.com",
    hashed_password=get_password_hash("test_password"))  
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user  

@pytest.fixture(scope="function")
def auth_client(client, test_user):
    """Create an authenticated test client"""
    response = client.post(
        "/auth/login",
        json={"email": "test@gmail.com", "password": "test_password"}
    )
    token = response.json()["access_token"]
    
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture(scope="function")
def sample_todo(test_db, test_user):
    """Create a sample todo for testing"""
    from datetime import datetime, timedelta
    
    todo = TodoDB(
        title="test todo",
        ddl=datetime.now() + timedelta(days=1),
        done=False,
        owner_id=test_user.id
    )
    test_db.add(todo)
    test_db.commit()
    test_db.refresh(todo)
    return todo