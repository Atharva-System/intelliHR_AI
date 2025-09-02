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

def test_AI_titleSuggestion():
    payload = {
        "title": "DevOps Engineer",
        "experienceRange": "4-6 years",
        "department": "Engineering",
        "subDepartment": "Cloud/DevOps",
        "keyResponsibilities": [
            "Design, implement, and maintain CI/CD pipelines",
            "Manage AWS infrastructure using IaC (Terraform, CloudFormation)",
            "Monitor system performance and ensure high availability",
            "Collaborate with development teams to optimize deployment processes"
        ],
        "softSkills": [
            "Problem-solving",
            "Communication",
            "Teamwork",
            "Adaptability"
        ],
        "technicalSkills": [
            "AWS (EC2, S3, Lambda, RDS, CloudWatch)",
            "Docker & Kubernetes",
            "Terraform / CloudFormation",
            "CI/CD tools (Jenkins, GitHub Actions, GitLab CI)",
            "Linux Administration",
            "Python / Bash scripting"
        ],
        "education": [
            "Bachelor's degree in Computer Science, IT, or related field"
        ],
        "certifications": [
            "AWS Certified DevOps Engineer",
            "AWS Solutions Architect Associate",
            "Certified Kubernetes Administrator (CKA)"
        ],
        "niceToHave": [
            "Experience with monitoring tools like Prometheus/Grafana",
            "Familiarity with serverless architecture",
            "Experience with hybrid cloud environments"
        ]
        }

    response = client.post("/generate-AI-titleSuggestion", json=payload)
    
    assert response.status_code == 200
    
def test_refine_job_field_regenerate():
    payload = {
        "title": "Software Engineer",
        "experienceRange": "3-5 years",
        "department": "Engineering",
        "subDepartment": "Backend",
        "keyResponsibilities": [
            "Develop and maintain backend services",
            "Collaborate with frontend developers",
            "Write clean, scalable code"
        ]
    }

    response = client.post("/regenerate-job-field", json=payload)
    
    assert response.status_code == 200
    
    data = response.json()
    assert "keyResponsibilities" in data
    assert isinstance(data["keyResponsibilities"], list)


def test_refine_job_field_enhance():
    payload = {
        "title": "Data Scientist",
        "experienceRange": "2-4 years",
        "department": "Engineering",
        "subDepartment": "AI/ML",
        "technicalSkills": [
            "Python", 
            "Machine Learning", 
            "Data Analysis"
        ]
    }

    response = client.post("/enhance-job-field", json=payload)
    
    assert response.status_code == 200
    
    data = response.json()
    assert "technicalSkills" in data
    assert isinstance(data["technicalSkills"], list)
