from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_job_description():
    payload = {
        "title": "Software Engineer",
        "experienceRange": "3-5 years",
        "department": "Engineering",
        "subDepartment": "Backend"
    }

    response = client.post("/generate-job-description", json=payload)
    
    assert response.status_code == 200
    
    data = response.json()
    
    expected_fields = [
        "keyResponsibilities",
        "softSkills",
        "technicalSkills",
        "education",
        "certifications",
        "niceToHave"
    ]
    for field in expected_fields:
        assert field in data
        assert isinstance(data[field], list)
