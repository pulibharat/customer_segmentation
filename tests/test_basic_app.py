from fastapi.testclient import TestClient

from main import app


def test_root_health():
    client = TestClient(app)
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'


def test_support_ticket_endpoint():
    client = TestClient(app)
    payload = {
        'customer_id': 'cust_001',
        'message': 'My API times out again',
        'channel': 'chat',
    }
    response = client.post('/api/support/ticket', json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body['ticket_id']
    assert 'response' in body


def test_analytics_tracks_memory_growth():
    client = TestClient(app)
    for i in range(3):
        response = client.post('/api/support/ticket', json={
            'customer_id': f'cust_{i + 10}',
            'message': 'API timeout in production after deployment',
            'channel': 'chat',
        })
        assert response.status_code == 200

    metrics = client.get('/api/analytics/metrics')
    assert metrics.status_code == 200
    data = metrics.json()
    assert data['total_tickets'] >= 3
    assert data['service_status'] == 'healthy'
