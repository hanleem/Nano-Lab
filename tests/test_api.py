from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    res = client.get('/health')
    assert res.status_code == 200
    assert res.json()['status'] == 'ok'


def test_project_requirement_and_dashboard_flow() -> None:
    create = client.post('/projects', json={'name': 'MVP Project', 'description': 'demo'})
    assert create.status_code == 200
    project_id = create.json()['id']

    activate = client.patch(f'/projects/{project_id}/activate')
    assert activate.status_code == 200
    assert activate.json()['status'] == 'active'

    req = client.post(
        f'/projects/{project_id}/requirements',
        json={'title': 'Need OCR pipeline', 'detail': 'support korean docs', 'priority': 'high'},
    )
    assert req.status_code == 200

    task = client.post(f'/projects/{project_id}/tasks', json={'title': 'set up workers'})
    assert task.status_code == 200

    export = client.get(f'/projects/{project_id}/requirements/export.csv')
    assert export.status_code == 200
    assert 'Need OCR pipeline' in export.text

    dashboard = client.get(f'/projects/{project_id}/dashboard')
    assert dashboard.status_code == 200
    body = dashboard.json()['summary']
    assert body['requirements'] >= 1
    assert body['tasks_total'] >= 1


def test_compare_endpoint() -> None:
    payload = {'left_text': 'alpha beta gamma', 'right_text': 'beta delta'}
    res = client.post('/analysis/compare', json=payload)
    assert res.status_code == 200
    data = res.json()
    assert 0 <= data['overlap_score'] <= 1
    assert 'alpha' in data['left_only']
