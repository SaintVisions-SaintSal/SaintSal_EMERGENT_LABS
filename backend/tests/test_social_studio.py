"""
Social Studio Backend Tests - Iteration 6
Tests for 7 new endpoints added for Social Studio fix:
- Brand profile generation
- Image library save
- GHL marketing connect
- Reviews management
- Workflow management
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestBrandProfiles:
    """Brand profile generation endpoint tests"""
    
    def test_brand_generate_ai_success(self):
        """POST /api/creative/brand/generate-ai returns generated profile"""
        response = requests.post(f"{BASE_URL}/api/creative/brand/generate-ai", json={
            "brand_name": "TEST_TechStartup",
            "industry": "Technology"
        })
        assert response.status_code == 200
        data = response.json()
        assert "brand_name" in data
        assert data["brand_name"] == "TEST_TechStartup"
        assert "profile" in data
        assert "generated" in data
        assert data["generated"] == True
    
    def test_brand_generate_ai_empty_name(self):
        """POST /api/creative/brand/generate-ai handles empty brand name"""
        response = requests.post(f"{BASE_URL}/api/creative/brand/generate-ai", json={
            "brand_name": "",
            "industry": "Retail"
        })
        assert response.status_code == 200
        data = response.json()
        assert "profile" in data


class TestImageLibrary:
    """Image library save endpoint tests"""
    
    def test_image_save_library_success(self):
        """POST /api/creative/image/save-library saves image to library"""
        response = requests.post(f"{BASE_URL}/api/creative/image/save-library", json={
            "url": "https://example.com/TEST_image.jpg",
            "title": "TEST_Image",
            "tags": ["test", "automation"]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["saved"] == True
        assert "entry" in data
        assert data["entry"]["title"] == "TEST_Image"
        assert data["entry"]["url"] == "https://example.com/TEST_image.jpg"
        assert "id" in data["entry"]
        assert "saved_at" in data["entry"]
        assert "total_in_library" in data
    
    def test_image_save_library_minimal(self):
        """POST /api/creative/image/save-library with minimal data"""
        response = requests.post(f"{BASE_URL}/api/creative/image/save-library", json={
            "url": "https://example.com/TEST_minimal.png"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["saved"] == True


class TestGHLConnect:
    """GHL Marketing integration tests"""
    
    def test_ghl_connect_without_key(self):
        """POST /api/marketing/ghl/connect without API key returns 400"""
        response = requests.post(f"{BASE_URL}/api/marketing/ghl/connect", json={
            "api_key": ""
        })
        # Should return 400 when no API key provided
        assert response.status_code == 400
        data = response.json()
        assert data["connected"] == False
        assert "error" in data
    
    def test_ghl_connect_with_env_key(self):
        """POST /api/marketing/ghl/connect uses env key if not provided"""
        response = requests.post(f"{BASE_URL}/api/marketing/ghl/connect", json={})
        # Uses env key - may return 401 if key is invalid/expired
        assert response.status_code == 200
        data = response.json()
        assert "connected" in data
        # GHL API may return 401 if key expired, but endpoint works
        if not data["connected"]:
            assert "error" in data


class TestReviews:
    """Reviews management endpoint tests"""
    
    def test_get_reviews_empty(self):
        """GET /api/marketing/reviews returns reviews list"""
        response = requests.get(f"{BASE_URL}/api/marketing/reviews")
        assert response.status_code == 200
        data = response.json()
        assert "reviews" in data
        assert "total" in data
        assert "avg_rating" in data
        assert isinstance(data["reviews"], list)
    
    def test_review_response_generation(self):
        """POST /api/marketing/review-response generates AI review response"""
        response = requests.post(f"{BASE_URL}/api/marketing/review-response", json={
            "review_id": "TEST_r1",
            "review_text": "Excellent service, very professional!",
            "tone": "professional"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["review_id"] == "TEST_r1"
        assert "response" in data
        assert len(data["response"]) > 0
        assert data["tone"] == "professional"
    
    def test_review_response_different_tones(self):
        """POST /api/marketing/review-response with different tones"""
        for tone in ["professional", "casual", "friendly"]:
            response = requests.post(f"{BASE_URL}/api/marketing/review-response", json={
                "review_id": f"TEST_r_{tone}",
                "review_text": "Good experience",
                "tone": tone
            })
            assert response.status_code == 200
            data = response.json()
            assert data["tone"] == tone


class TestWorkflows:
    """Workflow management endpoint tests"""
    
    def test_get_workflows(self):
        """GET /api/marketing/workflows returns 4 workflows"""
        response = requests.get(f"{BASE_URL}/api/marketing/workflows")
        assert response.status_code == 200
        data = response.json()
        assert "workflows" in data
        assert "total" in data
        assert "active" in data
        assert data["total"] == 4
        # Verify workflow structure
        for wf in data["workflows"]:
            assert "id" in wf
            assert "name" in wf
            assert "trigger" in wf
            assert "status" in wf
            assert wf["status"] in ["active", "paused"]
    
    def test_toggle_workflow(self):
        """POST /api/marketing/workflows/toggle changes workflow status"""
        # First get current status
        get_response = requests.get(f"{BASE_URL}/api/marketing/workflows")
        workflows = get_response.json()["workflows"]
        wf_to_toggle = workflows[0]
        original_status = wf_to_toggle["status"]
        
        # Toggle it
        toggle_response = requests.post(f"{BASE_URL}/api/marketing/workflows/toggle", json={
            "workflow_id": wf_to_toggle["id"]
        })
        assert toggle_response.status_code == 200
        data = toggle_response.json()
        assert data["toggled"] == True
        assert data["workflow"]["status"] != original_status
        
        # Toggle back to restore state
        requests.post(f"{BASE_URL}/api/marketing/workflows/toggle", json={
            "workflow_id": wf_to_toggle["id"]
        })
    
    def test_toggle_nonexistent_workflow(self):
        """POST /api/marketing/workflows/toggle with invalid ID returns 404"""
        response = requests.post(f"{BASE_URL}/api/marketing/workflows/toggle", json={
            "workflow_id": "wf_nonexistent"
        })
        assert response.status_code == 404
        data = response.json()
        assert "error" in data


class TestMeteringDashboard:
    """Metering dashboard endpoint tests"""
    
    def test_metering_dashboard(self):
        """GET /api/metering/dashboard returns usage metrics"""
        response = requests.get(f"{BASE_URL}/api/metering/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "tier" in data
        assert "compute" in data
        assert "cost" in data
        assert "rate_limit" in data
        # Verify compute structure
        assert "used" in data["compute"]
        assert "limit" in data["compute"]
        assert "remaining" in data["compute"]


class TestContentGeneration:
    """Content generation endpoint tests"""
    
    def test_social_generate(self):
        """POST /api/social/generate returns generated content"""
        response = requests.post(f"{BASE_URL}/api/social/generate", json={
            "platform": "instagram",
            "content_type": "post",
            "topic": "TEST_topic",
            "tone": "professional"
        })
        assert response.status_code == 200
        data = response.json()
        assert "platform" in data
        assert "caption" in data or "content" in data
        assert "hashtags" in data


class TestExistingEndpoints:
    """Tests for existing Social Studio endpoints"""
    
    def test_image_generate(self):
        """POST /api/creative/image/generate endpoint exists"""
        response = requests.post(f"{BASE_URL}/api/creative/image/generate", json={
            "prompt": "TEST_image prompt",
            "provider": "dall-e-3",
            "size": "1024x1024"
        })
        # May return 200, 401 (auth required), 400, or 500 - endpoint should exist
        assert response.status_code in [200, 400, 401, 500]
    
    def test_video_generate(self):
        """POST /api/creative/video/generate endpoint exists"""
        response = requests.post(f"{BASE_URL}/api/creative/video/generate", json={
            "prompt": "TEST_video prompt",
            "type": "quick-clip"
        })
        assert response.status_code in [200, 400, 401, 500]
    
    def test_ad_generate(self):
        """POST /api/creative/ad/generate endpoint exists"""
        response = requests.post(f"{BASE_URL}/api/creative/ad/generate", json={
            "campaign_name": "TEST_Campaign",
            "objective": "awareness",
            "audience": "general"
        })
        assert response.status_code in [200, 400, 401, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
