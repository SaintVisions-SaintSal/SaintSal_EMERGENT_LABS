"""
Career Suite P0 Features - Backend API Tests
Tests: Resume CRUD + Export, Cover Letter CRUD + Export, File Uploads, Job Tracker, Job Search
All endpoints use Supabase for persistence. No auth required (anonymous user_id).
"""
import pytest
import requests
import os
import io
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthCheck:
    """Verify backend is running and Supabase is connected"""
    
    def test_health_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        # Verify Supabase is connected
        supabase = data.get("integrations", {}).get("supabase", {})
        assert supabase.get("public") == True or supabase.get("admin") == True


class TestResumeBuilder:
    """Resume CRUD and Export tests - POST /api/career/v2/resumes, GET export/pdf, export/docx"""
    
    @pytest.fixture
    def test_resume_data(self):
        return {
            "full_name": f"TEST_User_{uuid.uuid4().hex[:6]}",
            "email": "test@example.com",
            "phone": "+1-555-123-4567",
            "location": "San Francisco, CA",
            "linkedin_url": "linkedin.com/in/testuser",
            "website": "testuser.dev",
            "name": "Test Resume",
            "summary": "Experienced software engineer with 10+ years in full-stack development.",
            "skills": ["Python", "React", "AWS", "Docker"],
            "work_experience": [
                {
                    "company": "Acme Corp",
                    "title": "Senior Engineer",
                    "start_date": "2020-01",
                    "end_date": None,
                    "is_current": True,
                    "description": "Led team of 8 engineers",
                    "achievements": ["Increased revenue by 40%", "Reduced latency by 60%"]
                }
            ],
            "education": [
                {"school": "Stanford University", "degree": "B.S. Computer Science", "year": "2014"}
            ]
        }
    
    def test_create_resume_returns_resume_id(self, test_resume_data):
        """POST /api/career/v2/resumes should save to Supabase and return resume_id"""
        response = requests.post(
            f"{BASE_URL}/api/career/v2/resumes",
            json=test_resume_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        assert "resume_id" in data, f"Expected resume_id in response, got {data}"
        assert len(data["resume_id"]) > 10, "resume_id should be a UUID"
        # Store for subsequent tests
        pytest.resume_id = data["resume_id"]
        print(f"Created resume with ID: {pytest.resume_id}")
    
    def test_export_resume_pdf(self, test_resume_data):
        """GET /api/career/v2/resumes/{id}/export/pdf should return valid PDF"""
        # First create a resume
        create_resp = requests.post(
            f"{BASE_URL}/api/career/v2/resumes",
            json=test_resume_data,
            headers={"Content-Type": "application/json"}
        )
        assert create_resp.status_code == 200
        resume_id = create_resp.json().get("resume_id")
        assert resume_id
        
        # Export as PDF
        response = requests.get(f"{BASE_URL}/api/career/v2/resumes/{resume_id}/export/pdf")
        assert response.status_code == 200, f"PDF export failed: {response.status_code} - {response.text[:200]}"
        assert response.headers.get("content-type") == "application/pdf"
        # Check PDF magic bytes
        assert response.content[:4] == b'%PDF', "Response is not a valid PDF"
        print(f"PDF export successful, size: {len(response.content)} bytes")
    
    def test_export_resume_docx(self, test_resume_data):
        """GET /api/career/v2/resumes/{id}/export/docx should return valid DOCX"""
        # First create a resume
        create_resp = requests.post(
            f"{BASE_URL}/api/career/v2/resumes",
            json=test_resume_data,
            headers={"Content-Type": "application/json"}
        )
        assert create_resp.status_code == 200
        resume_id = create_resp.json().get("resume_id")
        assert resume_id
        
        # Export as DOCX
        response = requests.get(f"{BASE_URL}/api/career/v2/resumes/{resume_id}/export/docx")
        assert response.status_code == 200, f"DOCX export failed: {response.status_code} - {response.text[:200]}"
        assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers.get("content-type", "")
        # Check DOCX magic bytes (PK zip header)
        assert response.content[:2] == b'PK', "Response is not a valid DOCX (ZIP) file"
        print(f"DOCX export successful, size: {len(response.content)} bytes")
    
    def test_list_resumes(self):
        """GET /api/career/v2/resumes should return list of resumes"""
        response = requests.get(f"{BASE_URL}/api/career/v2/resumes")
        assert response.status_code == 200
        data = response.json()
        assert "resumes" in data
        assert "total" in data
        print(f"Found {data['total']} resumes")


class TestCoverLetter:
    """Cover Letter CRUD and Export tests"""
    
    @pytest.fixture
    def test_cover_letter_data(self):
        return {
            "name": f"TEST_CoverLetter_{uuid.uuid4().hex[:6]}",
            "content": "Dear Hiring Manager,\n\nI am writing to express my interest in the Software Engineer position at your company. With over 10 years of experience in full-stack development, I believe I would be a valuable addition to your team.\n\nBest regards,\nTest User",
            "target_company": "Acme Corp",
            "target_role": "Senior Software Engineer",
            "style": "professional"  # Will be mapped to 'professional' tone
        }
    
    def test_save_cover_letter_returns_id(self, test_cover_letter_data):
        """POST /api/career/v2/cover-letters should save and return cover_letter_id"""
        response = requests.post(
            f"{BASE_URL}/api/career/v2/cover-letters",
            json=test_cover_letter_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        assert "cover_letter_id" in data, f"Expected cover_letter_id in response, got {data}"
        assert len(data["cover_letter_id"]) > 10, "cover_letter_id should be a UUID"
        pytest.cover_letter_id = data["cover_letter_id"]
        print(f"Created cover letter with ID: {pytest.cover_letter_id}")
    
    def test_export_cover_letter_pdf(self, test_cover_letter_data):
        """GET /api/career/v2/cover-letters/{id}/export/pdf should return valid PDF"""
        # First create a cover letter
        create_resp = requests.post(
            f"{BASE_URL}/api/career/v2/cover-letters",
            json=test_cover_letter_data,
            headers={"Content-Type": "application/json"}
        )
        assert create_resp.status_code == 200
        cl_id = create_resp.json().get("cover_letter_id")
        assert cl_id
        
        # Export as PDF
        response = requests.get(f"{BASE_URL}/api/career/v2/cover-letters/{cl_id}/export/pdf")
        assert response.status_code == 200, f"PDF export failed: {response.status_code} - {response.text[:200]}"
        assert response.headers.get("content-type") == "application/pdf"
        assert response.content[:4] == b'%PDF', "Response is not a valid PDF"
        print(f"Cover letter PDF export successful, size: {len(response.content)} bytes")
    
    def test_export_cover_letter_docx(self, test_cover_letter_data):
        """GET /api/career/v2/cover-letters/{id}/export/docx should return valid DOCX"""
        # First create a cover letter
        create_resp = requests.post(
            f"{BASE_URL}/api/career/v2/cover-letters",
            json=test_cover_letter_data,
            headers={"Content-Type": "application/json"}
        )
        assert create_resp.status_code == 200
        cl_id = create_resp.json().get("cover_letter_id")
        assert cl_id
        
        # Export as DOCX
        response = requests.get(f"{BASE_URL}/api/career/v2/cover-letters/{cl_id}/export/docx")
        assert response.status_code == 200, f"DOCX export failed: {response.status_code} - {response.text[:200]}"
        assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers.get("content-type", "")
        assert response.content[:2] == b'PK', "Response is not a valid DOCX (ZIP) file"
        print(f"Cover letter DOCX export successful, size: {len(response.content)} bytes")
    
    def test_list_cover_letters(self):
        """GET /api/career/v2/cover-letters should return list"""
        response = requests.get(f"{BASE_URL}/api/career/v2/cover-letters")
        assert response.status_code == 200
        data = response.json()
        assert "cover_letters" in data
        assert "total" in data
        print(f"Found {data['total']} cover letters")


class TestFileUpload:
    """File upload tests for headshot and background images"""
    
    def _create_test_image(self):
        """Create a minimal valid PNG image for testing"""
        # Minimal 1x1 red PNG
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
            0x00, 0x00, 0x03, 0x00, 0x01, 0x00, 0x18, 0xDD,
            0x8D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45,  # IEND chunk
            0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        return png_data
    
    def test_upload_headshot_returns_url(self):
        """POST /api/career/v2/upload/headshot should accept image and return URL"""
        png_data = self._create_test_image()
        files = {'file': ('test_headshot.png', io.BytesIO(png_data), 'image/png')}
        
        response = requests.post(f"{BASE_URL}/api/career/v2/upload/headshot", files=files)
        assert response.status_code == 200, f"Upload failed: {response.status_code} - {response.text}"
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        assert "url" in data, f"Expected url in response, got {data}"
        assert "file_id" in data, f"Expected file_id in response, got {data}"
        assert data["url"].startswith("/api/career/v2/uploads/"), f"URL should start with /api/career/v2/uploads/, got {data['url']}"
        pytest.headshot_file_id = data["file_id"]
        pytest.headshot_url = data["url"]
        print(f"Headshot uploaded: {data['url']}")
    
    def test_upload_background_returns_url(self):
        """POST /api/career/v2/upload/background should accept image and return URL"""
        png_data = self._create_test_image()
        files = {'file': ('test_background.png', io.BytesIO(png_data), 'image/png')}
        
        response = requests.post(f"{BASE_URL}/api/career/v2/upload/background", files=files)
        assert response.status_code == 200, f"Upload failed: {response.status_code} - {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "url" in data
        assert "file_id" in data
        pytest.background_file_id = data["file_id"]
        pytest.background_url = data["url"]
        print(f"Background uploaded: {data['url']}")
    
    def test_serve_uploaded_file(self):
        """GET /api/career/v2/uploads/{file_id} should serve the uploaded image"""
        # First upload a file
        png_data = self._create_test_image()
        files = {'file': ('test_serve.png', io.BytesIO(png_data), 'image/png')}
        upload_resp = requests.post(f"{BASE_URL}/api/career/v2/upload/headshot", files=files)
        assert upload_resp.status_code == 200
        file_id = upload_resp.json().get("file_id")
        assert file_id
        
        # Serve the file
        response = requests.get(f"{BASE_URL}/api/career/v2/uploads/{file_id}")
        assert response.status_code == 200, f"Serve failed: {response.status_code}"
        assert "image/" in response.headers.get("content-type", ""), f"Expected image content-type, got {response.headers.get('content-type')}"
        print(f"File served successfully, content-type: {response.headers.get('content-type')}")
    
    def test_upload_rejects_invalid_extension(self):
        """POST /api/career/v2/upload/headshot should reject non-image files"""
        files = {'file': ('test.txt', io.BytesIO(b'not an image'), 'text/plain')}
        response = requests.post(f"{BASE_URL}/api/career/v2/upload/headshot", files=files)
        assert response.status_code == 400, f"Expected 400 for invalid file, got {response.status_code}"


class TestJobTracker:
    """Job Tracker Kanban tests - GET/POST /api/career/v2/tracker"""
    
    @pytest.fixture
    def test_job_data(self):
        return {
            "job_title": f"TEST_SoftwareEngineer_{uuid.uuid4().hex[:6]}",
            "company_name": "Test Company Inc",
            "job_url": "https://example.com/jobs/123",
            "location": "Remote",
            "status": "saved",  # Valid Supabase statuses: saved, applied, phone_screen, rejected
            "notes": "Great opportunity",
            "job_source": "manual"
        }
    
    def test_get_tracker_returns_kanban(self):
        """GET /api/career/v2/tracker should return kanban data from Supabase"""
        response = requests.get(f"{BASE_URL}/api/career/v2/tracker")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "kanban" in data, f"Expected kanban in response, got {data.keys()}"
        assert "total" in data
        # Verify kanban has expected columns (valid Supabase statuses)
        kanban = data["kanban"]
        expected_columns = ["saved", "applied", "phone_screen", "rejected"]
        for col in expected_columns:
            assert col in kanban, f"Expected column '{col}' in kanban"
        print(f"Tracker has {data['total']} jobs across {len(kanban)} columns")
    
    def test_add_job_to_tracker(self, test_job_data):
        """POST /api/career/v2/tracker should add job to Supabase"""
        response = requests.post(
            f"{BASE_URL}/api/career/v2/tracker",
            json=test_job_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        assert "job_id" in data, f"Expected job_id in response, got {data}"
        pytest.tracker_job_id = data["job_id"]
        print(f"Added job to tracker with ID: {pytest.tracker_job_id}")
    
    def test_update_job_status(self, test_job_data):
        """PUT /api/career/v2/tracker/{job_id} should update job status"""
        # First add a job
        create_resp = requests.post(
            f"{BASE_URL}/api/career/v2/tracker",
            json=test_job_data,
            headers={"Content-Type": "application/json"}
        )
        assert create_resp.status_code == 200
        job_id = create_resp.json().get("job_id")
        assert job_id
        
        # Update status to 'applied'
        update_resp = requests.put(
            f"{BASE_URL}/api/career/v2/tracker/{job_id}",
            json={"status": "applied"},
            headers={"Content-Type": "application/json"}
        )
        assert update_resp.status_code == 200, f"Update failed: {update_resp.status_code} - {update_resp.text}"
        assert update_resp.json().get("success") == True
        print(f"Updated job {job_id} status to 'applied'")
    
    def test_delete_job_from_tracker(self, test_job_data):
        """DELETE /api/career/v2/tracker/{job_id} should remove job"""
        # First add a job
        create_resp = requests.post(
            f"{BASE_URL}/api/career/v2/tracker",
            json=test_job_data,
            headers={"Content-Type": "application/json"}
        )
        assert create_resp.status_code == 200
        job_id = create_resp.json().get("job_id")
        assert job_id
        
        # Delete the job
        delete_resp = requests.delete(f"{BASE_URL}/api/career/v2/tracker/{job_id}")
        assert delete_resp.status_code == 200, f"Delete failed: {delete_resp.status_code}"
        assert delete_resp.json().get("success") == True
        print(f"Deleted job {job_id} from tracker")


class TestJobSearch:
    """Job Search tests - GET /api/career/jobs/search"""
    
    def test_job_search_returns_results(self):
        """GET /api/career/jobs/search?query=software+engineer should return job results"""
        response = requests.get(
            f"{BASE_URL}/api/career/jobs/search",
            params={"query": "software engineer", "location": "San Francisco"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "jobs" in data, f"Expected jobs in response, got {data.keys()}"
        assert "total" in data
        assert "query" in data
        # Jobs may be empty if search providers are unavailable, but structure should be correct
        if data["total"] > 0:
            job = data["jobs"][0]
            assert "title" in job
            assert "company" in job
            assert "url" in job or "snippet" in job
            print(f"Job search returned {data['total']} results via {data.get('provider', 'unknown')}")
        else:
            print(f"Job search returned 0 results (search providers may be unavailable)")
    
    def test_job_search_with_remote_filter(self):
        """GET /api/career/jobs/search with remote=true should work"""
        response = requests.get(
            f"{BASE_URL}/api/career/jobs/search",
            params={"query": "python developer", "remote": "true"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        print(f"Remote job search returned {data['total']} results")


class TestCareerProfile:
    """Career Profile tests - GET/POST /api/career/v2/profile"""
    
    def test_get_profile(self):
        """GET /api/career/v2/profile should return profile or create default"""
        response = requests.get(f"{BASE_URL}/api/career/v2/profile")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        print(f"Profile user_id: {data['user_id']}")
    
    def test_save_profile(self):
        """POST /api/career/v2/profile should save profile data"""
        profile_data = {
            "full_name": "Test User",
            "email": "test@example.com",
            "headline": "Senior Software Engineer",
            "summary": "10+ years experience in full-stack development"
        }
        response = requests.post(
            f"{BASE_URL}/api/career/v2/profile",
            json=profile_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print("Profile saved successfully")


class TestEmailSignatures:
    """Email Signature tests - GET/POST /api/career/v2/signatures"""
    
    def test_save_signature(self):
        """POST /api/career/v2/signatures should save signature"""
        sig_data = {
            "signature_name": f"TEST_Signature_{uuid.uuid4().hex[:6]}",
            "full_name": "Test User",
            "title": "CEO",
            "company": "Test Corp",
            "email": "test@testcorp.com",
            "phone": "+1-555-123-4567",
            "template_style": "executive"
        }
        response = requests.post(
            f"{BASE_URL}/api/career/v2/signatures",
            json=sig_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "sig_id" in data
        print(f"Signature saved with ID: {data['sig_id']}")
    
    def test_list_signatures(self):
        """GET /api/career/v2/signatures should return list"""
        response = requests.get(f"{BASE_URL}/api/career/v2/signatures")
        assert response.status_code == 200
        data = response.json()
        assert "signatures" in data
        assert "total" in data
        print(f"Found {data['total']} signatures")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
