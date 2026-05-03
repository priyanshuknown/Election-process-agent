import os
import tempfile
import pytest
from app import app, init_db, get_db

@pytest.fixture
def client():
    # Set up a temporary database
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

def test_index_page(client):
    """Test that the index page loads correctly."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'VoteMate' in rv.data

def test_timeline_page(client):
    """Test timeline page."""
    rv = client.get('/timeline')
    assert rv.status_code == 200

def test_booth_page(client):
    """Test booth page."""
    rv = client.get('/booth')
    assert rv.status_code == 200

def test_documents_page(client):
    """Test documents page."""
    rv = client.get('/documents')
    assert rv.status_code == 200

def test_quiz_page(client):
    """Test quiz page."""
    rv = client.get('/quiz')
    assert rv.status_code == 200

def test_chat_api_missing_message(client):
    """Test the chat API missing message edge case."""
    rv = client.post('/api/chat', json={})
    assert rv.status_code == 400
    assert b'No message provided' in rv.data

def test_booth_api(client):
    """Test the polling booth API."""
    rv = client.get('/api/booth?pincode=110001')
    assert rv.status_code == 200
    # Just check it returns valid JSON and has a booth name
    json_data = rv.get_json()
    assert 'booth' in json_data
