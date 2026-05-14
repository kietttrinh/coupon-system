import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base
from app.api import deps

# Dùng SQLite in-memory cho môi trường test (nhanh, sạch, tự xóa)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=pool.StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ghi đè (Override) hàm get_db của FastAPI để nó dùng Test DB thay vì MySQL thật
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[deps.get_db] = override_get_db

@pytest.fixture(scope="function")
def test_db():
    # Tạo bảng mới tinh trước mỗi test
    Base.metadata.create_all(bind=engine)
    yield
    # Xóa sạch bảng sau khi test xong
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    with TestClient(app) as c:
        yield c