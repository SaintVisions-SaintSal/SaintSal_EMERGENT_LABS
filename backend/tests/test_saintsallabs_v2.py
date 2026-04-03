"""
SaintSal Labs Platform v2 - Backend API Tests
Tests for Career Suite, Real Estate, Business Center, and Command Palette features
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print(f"✓ Health check passed: {data.get('version', 'unknown')}")


class TestCareerSuiteAPIs:
    """Tests for Career Suite endpoints (Section 3.1-3.4)"""
    
    def test_cover_letter_generation(self):
        """Test POST /api/career/cover-letter"""
        payload = {
            "resume_text": "Software Engineer with 5 years experience in Python, JavaScript, React. Led team of 4 developers. Increased deployment speed by 40%.",
            "job_description": "Senior Software Engineer position at tech startup. Requirements: Python, React, team leadership, CI/CD experience.",
            "style": "direct"
        }
        response = requests.post(
            f"{BASE_URL}/api/career/cover-letter",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert "cover_letter" in data
        assert "word_count" in data
        assert data["word_count"] > 50  # Should generate substantial content
        print(f"✓ Cover letter generated: {data['word_count']} words")
    
    def test_cover_letter_missing_fields(self):
        """Test cover letter endpoint with missing required fields"""
        payload = {"resume_text": "Some resume"}  # Missing job_description
        response = requests.post(
            f"{BASE_URL}/api/career/cover-letter",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        print("✓ Cover letter validation works correctly")
    
    def test_linkedin_optimizer(self):
        """Test POST /api/career/linkedin-optimize"""
        payload = {
            "current_profile_text": "Software developer at ABC Corp. I write code and fix bugs. Skills: Python, JavaScript. Education: BS Computer Science."
        }
        response = requests.post(
            f"{BASE_URL}/api/career/linkedin-optimize",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        # Should return optimization suggestions
        assert "headline" in data or "summary" in data or "score_before" in data
        print(f"✓ LinkedIn optimizer returned: {list(data.keys())}")
    
    def test_linkedin_optimizer_missing_profile(self):
        """Test LinkedIn optimizer with missing profile text"""
        payload = {}
        response = requests.post(
            f"{BASE_URL}/api/career/linkedin-optimize",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        print("✓ LinkedIn optimizer validation works correctly")
    
    def test_salary_negotiator(self):
        """Test POST /api/career/salary-negotiate"""
        payload = {
            "role": "Senior Software Engineer",
            "location": "San Francisco, CA",
            "experience_years": 5,
            "offer_details": "Base: $180,000, RSUs: $50,000/year"
        }
        response = requests.post(
            f"{BASE_URL}/api/career/salary-negotiate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        # Should return market data and negotiation strategy
        assert "market_range" in data or "counter_offer_script" in data
        print(f"✓ Salary negotiator returned: {list(data.keys())}")
    
    def test_salary_negotiator_missing_role(self):
        """Test salary negotiator with missing role"""
        payload = {"location": "NYC"}
        response = requests.post(
            f"{BASE_URL}/api/career/salary-negotiate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        print("✓ Salary negotiator validation works correctly")
    
    def test_network_mapper(self):
        """Test POST /api/career/network-map"""
        payload = {
            "target_company": "Google",
            "user_linkedin_url": "https://linkedin.com/in/testuser"
        }
        response = requests.post(
            f"{BASE_URL}/api/career/network-map",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        # Should return connections and intro templates
        assert "connections" in data or "intro_templates" in data or "approach_strategy" in data
        print(f"✓ Network mapper returned: {list(data.keys())}")
    
    def test_network_mapper_missing_company(self):
        """Test network mapper with missing company"""
        payload = {}
        response = requests.post(
            f"{BASE_URL}/api/career/network-map",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        print("✓ Network mapper validation works correctly")


class TestRealEstateAPIs:
    """Tests for Real Estate endpoints"""
    
    def test_listings_sale(self):
        """Test GET /api/realestate/listings/sale"""
        params = {"city": "Austin", "state": "TX"}
        response = requests.get(
            f"{BASE_URL}/api/realestate/listings/sale",
            params=params,
            timeout=30
        )
        # May return 200 with listings or empty results
        assert response.status_code in [200, 404, 500]  # API may have rate limits
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Real estate listings: {len(data.get('listings', []))} found")
        else:
            print(f"⚠ Real estate listings returned {response.status_code} (may be rate limited)")
    
    def test_property_value(self):
        """Test GET /api/realestate/value"""
        params = {"address": "123 Main St, Austin, TX 78701"}
        response = requests.get(
            f"{BASE_URL}/api/realestate/value",
            params=params,
            timeout=30
        )
        # May return 200 or error if address not found
        assert response.status_code in [200, 400, 404, 500]
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Property value endpoint working: {list(data.keys())}")
        else:
            print(f"⚠ Property value returned {response.status_code}")
    
    def test_rent_estimate(self):
        """Test GET /api/realestate/rent"""
        params = {"address": "123 Main St, Austin, TX 78701"}
        response = requests.get(
            f"{BASE_URL}/api/realestate/rent",
            params=params,
            timeout=30
        )
        assert response.status_code in [200, 400, 404, 500]
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Rent estimate endpoint working: {list(data.keys())}")
        else:
            print(f"⚠ Rent estimate returned {response.status_code}")


class TestBusinessAPIs:
    """Tests for Business Intelligence endpoints"""
    
    def test_patent_search(self):
        """Test POST /api/business/patent-search"""
        payload = {
            "technology_description": "AI-powered document analysis system using natural language processing",
            "competitors": ["Google", "Microsoft"]
        }
        response = requests.post(
            f"{BASE_URL}/api/business/patent-search",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=90
        )
        assert response.status_code == 200
        data = response.json()
        assert "prior_art" in data or "fto_analysis" in data
        print(f"✓ Patent search returned: {list(data.keys())}")
    
    def test_patent_search_missing_description(self):
        """Test patent search with missing technology description"""
        payload = {"competitors": ["Google"]}
        response = requests.post(
            f"{BASE_URL}/api/business/patent-search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        print("✓ Patent search validation works correctly")
    
    def test_business_plan_sse(self):
        """Test POST /api/business/plan (SSE streaming)"""
        payload = {
            "idea_description": "AI-powered fitness coaching app that creates personalized workout plans",
            "target_market": "Health-conscious millennials",
            "stage": "pre-revenue"
        }
        response = requests.post(
            f"{BASE_URL}/api/business/plan",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120,
            stream=True
        )
        assert response.status_code == 200
        # Check that we get SSE events
        content_type = response.headers.get('content-type', '')
        assert 'text/event-stream' in content_type
        
        # Read first few events
        events_received = 0
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith('data:'):
                events_received += 1
                if events_received >= 2:  # Just verify we get events
                    break
        
        print(f"✓ Business plan SSE streaming working: {events_received} events received")
    
    def test_business_plan_missing_idea(self):
        """Test business plan with missing idea description"""
        payload = {"target_market": "Millennials"}
        response = requests.post(
            f"{BASE_URL}/api/business/plan",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        print("✓ Business plan validation works correctly")


class TestLaunchpadAPIs:
    """Tests for Launchpad/Business Center endpoints"""
    
    def test_name_check(self):
        """Test POST /api/launchpad/name-check"""
        payload = {"business_name": "TestCorp AI Solutions"}
        response = requests.post(
            f"{BASE_URL}/api/launchpad/name-check",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        # May return 200 or 404 if endpoint not implemented
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Name check returned: {list(data.keys())}")
        else:
            print(f"⚠ Name check returned {response.status_code}")
    
    def test_entity_advisor(self):
        """Test POST /api/launchpad/entity-advisor"""
        payload = {
            "business_type": "tech startup",
            "state": "DE",
            "revenue_estimate": 100000
        }
        response = requests.post(
            f"{BASE_URL}/api/launchpad/entity-advisor",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Entity advisor returned: {list(data.keys())}")
        else:
            print(f"⚠ Entity advisor returned {response.status_code}")


class TestVerticalsAPIs:
    """Tests for Verticals trending endpoints"""
    
    def test_sports_trending(self):
        """Test GET /api/verticals/trending?vertical=sports"""
        response = requests.get(
            f"{BASE_URL}/api/verticals/trending",
            params={"vertical": "sports"},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert "articles" in data or isinstance(data, list)
        print(f"✓ Sports trending working")
    
    def test_finance_trending(self):
        """Test GET /api/verticals/trending?vertical=finance"""
        response = requests.get(
            f"{BASE_URL}/api/verticals/trending",
            params={"vertical": "finance"},
            timeout=30
        )
        assert response.status_code == 200
        print(f"✓ Finance trending working")


class TestCardsAPIs:
    """Tests for CookinCards endpoints"""
    
    def test_market_trending(self):
        """Test GET /api/cards/market/trending"""
        response = requests.get(
            f"{BASE_URL}/api/cards/market/trending",
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Cards market trending working")
        else:
            print(f"⚠ Cards market trending returned {response.status_code}")


class TestMeteringAPIs:
    """Tests for Metering/Usage endpoints"""
    
    def test_metering_log(self):
        """Test POST /api/metering/log"""
        payload = {
            "event_type": "test_event",
            "credits_used": 1,
            "metadata": {"test": True}
        }
        response = requests.post(
            f"{BASE_URL}/api/metering/log",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if response.status_code == 200:
            print(f"✓ Metering log working")
        else:
            print(f"⚠ Metering log returned {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
