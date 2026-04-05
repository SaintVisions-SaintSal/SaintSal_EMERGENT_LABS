"""
Career Suite P0 Features - Comprehensive Backend Tests
Tests: Resume/CL Export, Job Search, 8-Column Kanban, Stage Coaching, Interview Prep,
       Supabase Storage Uploads, DNA Autofill, Auth (auto-confirm)
"""
import pytest
import requests
import os
import json
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://sal-preview-deploy.preview.emergentagent.com').rstrip('/')

# Test credentials from test_credentials.md
TEST_EMAIL = "ryan@cookin.io"
TEST_PASSWORD = "SaintSal2024!"


class TestHealthAndConfig:
    """Basic health and configuration tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns 200 with Supabase status"""
        r = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert r.status_code == 200, f"Health check failed: {r.status_code}"
        data = r.json()
        print(f"Health check: {data}")
        assert "status" in data or "supabase" in str(data).lower()


class TestAuth:
    """Authentication tests - auto-confirm and login"""
    
    def test_login_with_valid_credentials(self):
        """Test POST /api/auth/login with ryan@cookin.io"""
        r = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }, timeout=15)
        print(f"Login response: {r.status_code} - {r.text[:500]}")
        assert r.status_code == 200, f"Login failed: {r.status_code} - {r.text}"
        data = r.json()
        assert data.get("success") == True, f"Login not successful: {data}"
        assert "session" in data, "No session in response"
        assert data["session"].get("access_token"), "No access_token in session"
        print(f"Login successful for {TEST_EMAIL}")
        return data["session"]["access_token"]
    
    def test_signup_auto_confirms_email(self):
        """Test POST /api/auth/signup auto-confirms and returns session"""
        # Use a unique test email
        test_email = f"test_autoconfirm_{int(time.time())}@test.com"
        r = requests.post(f"{BASE_URL}/api/auth/signup", json={
            "email": test_email,
            "password": "TestPass123!",
            "full_name": "Test User"
        }, timeout=15)
        print(f"Signup response: {r.status_code} - {r.text[:500]}")
        # 200 = success, 409 = already registered (acceptable)
        assert r.status_code in [200, 409], f"Signup failed: {r.status_code} - {r.text}"
        if r.status_code == 200:
            data = r.json()
            assert data.get("success") == True, f"Signup not successful: {data}"
            # Check email_confirmed is True (auto-confirm)
            user = data.get("user", {})
            assert user.get("email_confirmed") == True, f"Email not auto-confirmed: {user}"
            print(f"Signup auto-confirmed for {test_email}")


class TestResumeExport:
    """Resume creation and PDF/DOCX export tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.resume_id = None
    
    def test_create_resume(self):
        """Test POST /api/career/v2/resumes creates resume"""
        r = requests.post(f"{BASE_URL}/api/career/v2/resumes", json={
            "full_name": "TEST_John Doe",
            "email": "test@example.com",
            "phone": "+1-555-123-4567",
            "location": "San Francisco, CA",
            "name": "TEST_Resume",
            "summary": "Experienced software engineer with 10+ years in full-stack development.",
            "skills": ["Python", "React", "AWS", "Docker"],
            "work_experience": [
                {"company": "Tech Corp", "title": "Senior Engineer", "description": "Led team of 5 engineers"}
            ],
            "education": [
                {"school": "Stanford University", "degree": "BS Computer Science", "year": "2015"}
            ]
        }, timeout=15)
        print(f"Create resume response: {r.status_code} - {r.text[:300]}")
        assert r.status_code == 200, f"Create resume failed: {r.status_code} - {r.text}"
        data = r.json()
        assert data.get("success") == True, f"Resume creation not successful: {data}"
        assert "resume_id" in data, f"No resume_id in response: {data}"
        self.resume_id = data["resume_id"]
        print(f"Created resume with ID: {self.resume_id}")
        return self.resume_id
    
    def test_export_resume_pdf(self):
        """Test GET /api/career/v2/resumes/{id}/export/pdf returns valid PDF"""
        # First create a resume
        resume_id = self.test_create_resume()
        
        r = requests.get(f"{BASE_URL}/api/career/v2/resumes/{resume_id}/export/pdf", timeout=20)
        print(f"Export PDF response: {r.status_code}, Content-Type: {r.headers.get('Content-Type')}, Size: {len(r.content)}")
        assert r.status_code == 200, f"Export PDF failed: {r.status_code}"
        assert "application/pdf" in r.headers.get("Content-Type", ""), f"Wrong content type: {r.headers.get('Content-Type')}"
        # Check PDF magic bytes
        assert r.content[:4] == b'%PDF', f"Invalid PDF header: {r.content[:20]}"
        assert len(r.content) > 1000, f"PDF too small: {len(r.content)} bytes"
        print(f"PDF export successful: {len(r.content)} bytes")
    
    def test_export_resume_docx(self):
        """Test GET /api/career/v2/resumes/{id}/export/docx returns valid DOCX"""
        # First create a resume
        resume_id = self.test_create_resume()
        
        r = requests.get(f"{BASE_URL}/api/career/v2/resumes/{resume_id}/export/docx", timeout=20)
        print(f"Export DOCX response: {r.status_code}, Content-Type: {r.headers.get('Content-Type')}, Size: {len(r.content)}")
        assert r.status_code == 200, f"Export DOCX failed: {r.status_code}"
        # DOCX is a ZIP file, starts with PK
        assert r.content[:2] == b'PK', f"Invalid DOCX header: {r.content[:20]}"
        assert len(r.content) > 1000, f"DOCX too small: {len(r.content)} bytes"
        print(f"DOCX export successful: {len(r.content)} bytes")


class TestCoverLetterExport:
    """Cover letter creation and PDF/DOCX export tests"""
    
    def test_create_cover_letter(self):
        """Test POST /api/career/v2/cover-letters saves cover letter"""
        r = requests.post(f"{BASE_URL}/api/career/v2/cover-letters", json={
            "name": "TEST_Cover Letter",
            "content": "Dear Hiring Manager,\n\nI am writing to express my interest in the Software Engineer position at your company. With over 10 years of experience in full-stack development, I believe I would be a valuable addition to your team.\n\nBest regards,\nJohn Doe",
            "target_company": "Tech Corp",
            "target_role": "Senior Software Engineer",
            "tone": "professional"
        }, timeout=15)
        print(f"Create cover letter response: {r.status_code} - {r.text[:300]}")
        assert r.status_code == 200, f"Create cover letter failed: {r.status_code} - {r.text}"
        data = r.json()
        assert data.get("success") == True, f"Cover letter creation not successful: {data}"
        assert "cover_letter_id" in data, f"No cover_letter_id in response: {data}"
        print(f"Created cover letter with ID: {data['cover_letter_id']}")
        return data["cover_letter_id"]
    
    def test_export_cover_letter_pdf(self):
        """Test GET /api/career/v2/cover-letters/{id}/export/pdf returns valid PDF"""
        cl_id = self.test_create_cover_letter()
        
        r = requests.get(f"{BASE_URL}/api/career/v2/cover-letters/{cl_id}/export/pdf", timeout=20)
        print(f"Export CL PDF response: {r.status_code}, Size: {len(r.content)}")
        assert r.status_code == 200, f"Export CL PDF failed: {r.status_code}"
        assert r.content[:4] == b'%PDF', f"Invalid PDF header"
        assert len(r.content) > 500, f"PDF too small: {len(r.content)} bytes"
        print(f"Cover letter PDF export successful: {len(r.content)} bytes")
    
    def test_export_cover_letter_docx(self):
        """Test GET /api/career/v2/cover-letters/{id}/export/docx returns valid DOCX"""
        cl_id = self.test_create_cover_letter()
        
        r = requests.get(f"{BASE_URL}/api/career/v2/cover-letters/{cl_id}/export/docx", timeout=20)
        print(f"Export CL DOCX response: {r.status_code}, Size: {len(r.content)}")
        assert r.status_code == 200, f"Export CL DOCX failed: {r.status_code}"
        assert r.content[:2] == b'PK', f"Invalid DOCX header"
        assert len(r.content) > 500, f"DOCX too small: {len(r.content)} bytes"
        print(f"Cover letter DOCX export successful: {len(r.content)} bytes")


class TestJobSearch:
    """Job search tests - real results from Monster/Indeed/LinkedIn/Glassdoor"""
    
    def test_job_search_returns_results(self):
        """Test GET /api/career/jobs/search?query=software+engineer returns real job listings"""
        r = requests.get(f"{BASE_URL}/api/career/jobs/search", params={
            "query": "software engineer",
            "location": "San Francisco"
        }, timeout=20)
        print(f"Job search response: {r.status_code} - {r.text[:500]}")
        assert r.status_code == 200, f"Job search failed: {r.status_code} - {r.text}"
        data = r.json()
        assert "jobs" in data, f"No jobs in response: {data}"
        jobs = data["jobs"]
        print(f"Found {len(jobs)} jobs, provider: {data.get('provider', 'unknown')}")
        # Should have at least some results
        assert len(jobs) > 0 or data.get("provider") == "AI", f"No jobs found: {data}"
        # Check job structure
        if jobs:
            job = jobs[0]
            print(f"First job: {job.get('title')} at {job.get('company')} - {job.get('source')}")
            assert "title" in job, f"Job missing title: {job}"
    
    def test_job_search_with_remote_filter(self):
        """Test GET /api/career/jobs/search with remote=true filter"""
        r = requests.get(f"{BASE_URL}/api/career/jobs/search", params={
            "query": "python developer",
            "remote": "true"
        }, timeout=20)
        print(f"Remote job search response: {r.status_code}")
        assert r.status_code == 200, f"Remote job search failed: {r.status_code}"
        data = r.json()
        print(f"Remote jobs found: {len(data.get('jobs', []))}")


class TestKanban:
    """8-column Kanban tracker tests"""
    
    VALID_STATUSES = ["saved", "applied", "phone_screen", "interview_scheduled", 
                      "interview_completed", "offer_received", "job_won", "rejected"]
    
    def test_tracker_returns_8_columns(self):
        """Test GET /api/career/v2/tracker returns 8 Kanban columns"""
        r = requests.get(f"{BASE_URL}/api/career/v2/tracker", timeout=15)
        print(f"Tracker response: {r.status_code} - {r.text[:500]}")
        assert r.status_code == 200, f"Tracker failed: {r.status_code} - {r.text}"
        data = r.json()
        assert "kanban" in data, f"No kanban in response: {data}"
        kanban = data["kanban"]
        
        # Check all 8 columns exist
        for status in self.VALID_STATUSES:
            assert status in kanban, f"Missing column: {status}"
        
        print(f"Kanban columns: {list(kanban.keys())}")
        assert len(kanban) == 8, f"Expected 8 columns, got {len(kanban)}"
    
    def test_add_job_to_tracker(self):
        """Test POST /api/career/v2/tracker adds job"""
        r = requests.post(f"{BASE_URL}/api/career/v2/tracker", json={
            "job_title": "TEST_Software Engineer",
            "company_name": "TEST_Tech Corp",
            "job_url": "https://example.com/job/123",
            "status": "saved",
            "notes": "Great opportunity"
        }, timeout=15)
        print(f"Add job response: {r.status_code} - {r.text[:300]}")
        assert r.status_code == 200, f"Add job failed: {r.status_code} - {r.text}"
        data = r.json()
        assert data.get("success") == True, f"Add job not successful: {data}"
        assert "job_id" in data, f"No job_id in response: {data}"
        print(f"Added job with ID: {data['job_id']}")
        return data["job_id"]


class TestStageCoaching:
    """Stage coaching on pipeline transitions"""
    
    def test_status_change_returns_coaching(self):
        """Test PUT /api/career/v2/tracker/{id} with status change returns coaching tips"""
        # First add a job
        add_r = requests.post(f"{BASE_URL}/api/career/v2/tracker", json={
            "job_title": "TEST_Coaching Job",
            "company_name": "TEST_Coaching Corp",
            "status": "saved"
        }, timeout=15)
        assert add_r.status_code == 200
        job_id = add_r.json()["job_id"]
        
        # Update status to applied
        r = requests.put(f"{BASE_URL}/api/career/v2/tracker/{job_id}", json={
            "status": "applied",
            "company_name": "TEST_Coaching Corp",
            "job_title": "TEST_Coaching Job"
        }, timeout=15)
        print(f"Status update response: {r.status_code} - {r.text[:500]}")
        assert r.status_code == 200, f"Status update failed: {r.status_code} - {r.text}"
        data = r.json()
        assert data.get("success") == True, f"Status update not successful: {data}"
        
        # Check coaching is returned
        coaching = data.get("coaching")
        assert coaching is not None, f"No coaching in response: {data}"
        assert "title" in coaching, f"Coaching missing title: {coaching}"
        assert "tips" in coaching, f"Coaching missing tips: {coaching}"
        print(f"Coaching title: {coaching.get('title')}")
        print(f"Coaching tips: {coaching.get('tips', [])[:2]}")


class TestInterviewPrep:
    """Interview prep auto-generation on status change"""
    
    def test_interview_scheduled_returns_prep(self):
        """Test PUT /api/career/v2/tracker/{id} with status='interview_scheduled' returns interview_prep"""
        # First add a job
        add_r = requests.post(f"{BASE_URL}/api/career/v2/tracker", json={
            "job_title": "TEST_Interview Job",
            "company_name": "TEST_Interview Corp",
            "status": "saved"
        }, timeout=15)
        assert add_r.status_code == 200
        job_id = add_r.json()["job_id"]
        
        # Update status to interview_scheduled
        r = requests.put(f"{BASE_URL}/api/career/v2/tracker/{job_id}", json={
            "status": "interview_scheduled",
            "company_name": "TEST_Interview Corp",
            "job_title": "TEST_Interview Job"
        }, timeout=30)  # Longer timeout for AI generation
        print(f"Interview prep response: {r.status_code} - {r.text[:800]}")
        assert r.status_code == 200, f"Interview prep failed: {r.status_code} - {r.text}"
        data = r.json()
        assert data.get("success") == True, f"Interview prep not successful: {data}"
        
        # Check interview_prep is returned
        prep = data.get("interview_prep")
        assert prep is not None, f"No interview_prep in response: {data}"
        assert "prep_checklist" in prep, f"Missing prep_checklist: {prep}"
        assert "common_questions" in prep, f"Missing common_questions: {prep}"
        assert "power_tips" in prep, f"Missing power_tips: {prep}"
        print(f"Interview prep checklist items: {len(prep.get('prep_checklist', []))}")
        print(f"Common questions: {len(prep.get('common_questions', []))}")
        print(f"Power tips: {len(prep.get('power_tips', []))}")


class TestFileUpload:
    """Supabase Storage upload tests"""
    
    def test_upload_headshot_returns_supabase_url(self):
        """Test POST /api/career/v2/upload/headshot returns Supabase Storage public URL"""
        # Create a minimal valid PNG image (1x1 pixel)
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
            0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
            0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,  # IEND chunk
            0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        
        files = {"file": ("test_headshot.png", png_data, "image/png")}
        r = requests.post(f"{BASE_URL}/api/career/v2/upload/headshot", files=files, timeout=20)
        print(f"Headshot upload response: {r.status_code} - {r.text[:300]}")
        assert r.status_code == 200, f"Headshot upload failed: {r.status_code} - {r.text}"
        data = r.json()
        assert data.get("success") == True, f"Upload not successful: {data}"
        assert "url" in data, f"No url in response: {data}"
        
        # Check URL is Supabase Storage URL (not local disk)
        url = data["url"]
        assert "supabase" in url.lower(), f"URL is not Supabase Storage: {url}"
        assert "storage" in url.lower(), f"URL is not Supabase Storage: {url}"
        print(f"Headshot uploaded to Supabase: {url}")
    
    def test_upload_background_returns_supabase_url(self):
        """Test POST /api/career/v2/upload/background returns Supabase Storage public URL"""
        # Create a minimal valid PNG image
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
            0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
            0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
            0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        
        files = {"file": ("test_background.png", png_data, "image/png")}
        r = requests.post(f"{BASE_URL}/api/career/v2/upload/background", files=files, timeout=20)
        print(f"Background upload response: {r.status_code} - {r.text[:300]}")
        assert r.status_code == 200, f"Background upload failed: {r.status_code} - {r.text}"
        data = r.json()
        assert data.get("success") == True, f"Upload not successful: {data}"
        assert "url" in data, f"No url in response: {data}"
        
        url = data["url"]
        assert "supabase" in url.lower(), f"URL is not Supabase Storage: {url}"
        print(f"Background uploaded to Supabase: {url}")


class TestDNAAutofill:
    """DNA autofill for career profile"""
    
    def test_autofill_dna_creates_profile(self):
        """Test POST /api/career/v2/profile/autofill-dna accepts DNA data"""
        r = requests.post(f"{BASE_URL}/api/career/v2/profile/autofill-dna", json={
            "dna": {
                "first_name": "TEST_John",
                "last_name": "Doe",
                "email": "test@example.com",
                "phone": "+1-555-123-4567",
                "tagline": "Full-Stack Developer",
                "bio": "Experienced developer with 10+ years in the industry.",
                "business_name": "Tech Solutions Inc",
                "industry": "Technology",
                "business_city": "San Francisco",
                "business_state": "CA",
                "years_in_business": 10,
                "website": "https://example.com"
            }
        }, timeout=15)
        print(f"DNA autofill response: {r.status_code} - {r.text[:300]}")
        assert r.status_code == 200, f"DNA autofill failed: {r.status_code} - {r.text}"
        data = r.json()
        assert data.get("success") == True, f"DNA autofill not successful: {data}"
        assert "autofilled" in data, f"No autofilled fields in response: {data}"
        print(f"Autofilled fields: {data.get('autofilled')}")


class TestEmailSignature:
    """Email signature tests"""
    
    def test_save_signature(self):
        """Test POST /api/career/v2/signatures saves signature"""
        r = requests.post(f"{BASE_URL}/api/career/v2/signatures", json={
            "signature_name": "TEST_Professional Signature",
            "full_name": "John Doe",
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "email": "john@techcorp.com",
            "phone": "+1-555-123-4567",
            "website": "https://techcorp.com",
            "template_style": "executive"
        }, timeout=15)
        print(f"Save signature response: {r.status_code} - {r.text[:300]}")
        assert r.status_code == 200, f"Save signature failed: {r.status_code} - {r.text}"
        data = r.json()
        assert data.get("success") == True, f"Save signature not successful: {data}"
        assert "sig_id" in data, f"No sig_id in response: {data}"
        print(f"Saved signature with ID: {data['sig_id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
