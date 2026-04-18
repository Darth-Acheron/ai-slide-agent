import pytest
import os
import re
from unittest.mock import patch, MagicMock
from web.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_get_index_exists(client):
    resp = client.get('/')
    assert resp.status_code == 200

def test_api_prompt_does_not_exist(client):
    resp = client.post('/api/prompt', json={"prompt": "test"})
    assert resp.status_code == 404

def test_generate_slides_endpoint_exists(client):
    with patch('web.app.requests.post') as mock_post:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"choices": [{"message": {"content": "# Test"}}]}
        )
        resp = client.post('/api/generate_slides', json={"prompt": "test"})
        assert resp.status_code == 200
