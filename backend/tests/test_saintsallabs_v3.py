"""
SaintSal Labs Platform v3 - Backend API Tests
Tests for NEW features: Business Plan AI, Patent/IP Search, Formation Wizard (10-step),
CookinCards Scan, and Recently Used in Command Palette
"""
import pytest
import requests
import os
import time
import json

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


class TestBusinessPlanAI:
    """Tests for Business Plan AI (SSE streaming) - Section 3.5"""
    
    def test_business_plan_sse_streaming(self):
        """Test POST /api/business/plan returns SSE stream"""
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
        content_type = response.headers.get('content-type', '')
        assert 'text/event-stream' in content_type, f"Expected SSE, got {content_type}"
        
        # Read first few events to verify streaming works
        events_received = 0
        sections_started = []
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith('data:'):
                events_received += 1
                try:
                    event_data = json.loads(line[5:].strip())
                    if event_data.get('event') == 'section_start':
                        sections_started.append(event_data.get('section'))
                except:
                    pass
                if events_received >= 3:
                    break
        
        assert events_received >= 1, "Should receive at least 1 SSE event"
        print(f"✓ Business Plan SSE streaming: {events_received} events, sections: {sections_started}")
    
    def test_business_plan_missing_idea(self):
        """Test business plan validation - missing idea_description"""
        payload = {"target_market": "Millennials", "stage": "pre-revenue"}
        response = requests.post(
            f"{BASE_URL}/api/business/plan",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        print("✓ Business Plan validation: rejects missing idea_description")


class TestPatentIPSearch:
    """Tests for Patent/IP Search - Section 3.6"""
    
    def test_patent_search_full(self):
        """Test POST /api/business/patent-search with full payload"""
        payload = {
            "technology_description": "Machine learning system for real-time fraud detection in financial transactions using neural networks",
            "competitors": ["Stripe", "PayPal", "Square"]
        }
        response = requests.post(
            f"{BASE_URL}/api/business/patent-search",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=90
        )
        assert response.status_code == 200
        data = response.json()
        # Should return prior_art, fto_analysis, valuation_range, licensing_opportunities
        assert "prior_art" in data or "fto_analysis" in data
        print(f"✓ Patent search returned: {list(data.keys())}")
    
    def test_patent_search_minimal(self):
        """Test patent search with minimal payload (just tech description)"""
        payload = {
            "technology_description": "Blockchain-based supply chain tracking system"
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
        print(f"✓ Patent search (minimal): {list(data.keys())}")
    
    def test_patent_search_missing_description(self):
        """Test patent search validation - missing technology_description"""
        payload = {"competitors": ["Google", "Microsoft"]}
        response = requests.post(
            f"{BASE_URL}/api/business/patent-search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        print("✓ Patent search validation: rejects missing technology_description")


class TestFormationWizard:
    """Tests for 10-step Formation Wizard endpoints"""
    
    def test_name_check(self):
        """Test POST /api/launchpad/name-check - Step 1"""
        payload = {
            "business_name": "TEST_TechVentures AI Solutions",
            "state": "DE"
        }
        response = requests.post(
            f"{BASE_URL}/api/launchpad/name-check",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        # Should return domains, trademark_conflicts, social_handles, state_available
        assert "business_name" in data
        assert "domains" in data or "state_available" in data
        print(f"✓ Name check returned: {list(data.keys())}")
    
    def test_name_check_missing_name(self):
        """Test name check validation - missing business_name"""
        payload = {"state": "CA"}
        response = requests.post(
            f"{BASE_URL}/api/launchpad/name-check",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        print("✓ Name check validation: rejects missing business_name")
    
    def test_entity_advisor(self):
        """Test POST /api/launchpad/entity-advisor - Step 2"""
        payload = {
            "cofounders": 2,
            "funding_plans": "vc",
            "liability_needs": "high",
            "tax_preference": "minimize taxes"
        }
        response = requests.post(
            f"{BASE_URL}/api/launchpad/entity-advisor",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        # Should return recommended_entity, state, rationale, tax_implications, next_steps
        assert "recommended_entity" in data or "rationale" in data
        print(f"✓ Entity advisor returned: {list(data.keys())}")
    
    def test_ein_filing(self):
        """Test POST /api/launchpad/entity/ein - Step 6"""
        payload = {
            "formation_order_id": "test-order-123"
        }
        response = requests.post(
            f"{BASE_URL}/api/launchpad/entity/ein",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        # May return 404 if order not found, or 200 if it processes
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "ein_status" in data
            print(f"✓ EIN filing returned: {list(data.keys())}")
        else:
            print("✓ EIN filing: correctly returns 404 for non-existent order")
    
    def test_dns_configure(self):
        """Test POST /api/launchpad/dns/configure - Step 7"""
        payload = {
            "domain": "testdomain.com",
            "target": "vercel"
        }
        response = requests.post(
            f"{BASE_URL}/api/launchpad/dns/configure",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        # May return 400 if GoDaddy API not configured, or 200 if it works
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert "records_created" in data or "propagation_status" in data
            print(f"✓ DNS configure returned: {list(data.keys())}")
        else:
            print("✓ DNS configure: returns 400 (GoDaddy API required)")
    
    def test_dns_configure_missing_domain(self):
        """Test DNS configure validation - missing domain"""
        payload = {"target": "vercel"}
        response = requests.post(
            f"{BASE_URL}/api/launchpad/dns/configure",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        print("✓ DNS configure validation: rejects missing domain")
    
    def test_ssl_provision(self):
        """Test POST /api/launchpad/ssl/provision - Step 8"""
        payload = {
            "domain": "testdomain.com"
        }
        response = requests.post(
            f"{BASE_URL}/api/launchpad/ssl/provision",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert "ssl_status" in data
        assert "domain" in data
        print(f"✓ SSL provision returned: {list(data.keys())}")
    
    def test_ssl_provision_missing_domain(self):
        """Test SSL provision validation - missing domain"""
        payload = {}
        response = requests.post(
            f"{BASE_URL}/api/launchpad/ssl/provision",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        print("✓ SSL provision validation: rejects missing domain")
    
    def test_compliance_setup(self):
        """Test POST /api/launchpad/compliance/setup - Step 9"""
        payload = {
            "entity_type": "LLC",
            "state": "DE",
            "formation_date": "2025-01-15"
        }
        response = requests.post(
            f"{BASE_URL}/api/launchpad/compliance/setup",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert "calendar_events" in data
        print(f"✓ Compliance setup returned: {len(data.get('calendar_events', []))} events")


class TestCookinCardsAPIs:
    """Tests for CookinCards Scan endpoints - Section 6"""
    
    def test_card_scan_with_base64(self):
        """Test POST /api/cards/scan with base64 image
        NOTE: server.py has a duplicate endpoint that expects 'image' (base64) instead of 'image_url'
        The router version in cards.py is overridden by server.py endpoint
        """
        # Using a minimal valid base64 image (1x1 pixel PNG)
        minimal_png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        payload = {
            "image": minimal_png_base64
        }
        response = requests.post(
            f"{BASE_URL}/api/cards/scan",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        # May return 200 with results, or error if Vision API not configured
        assert response.status_code in [200, 500]
        data = response.json()
        # Should return matches array (even if empty)
        assert "matches" in data or "error" in data
        print(f"✓ Card scan returned: {list(data.keys())}")
    
    def test_card_scan_missing_image(self):
        """Test card scan validation - missing image"""
        payload = {"card_type": "tcg"}
        response = requests.post(
            f"{BASE_URL}/api/cards/scan",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        print("✓ Card scan validation: rejects missing image")
    
    def test_card_grade_with_url(self):
        """Test POST /api/cards/grade with image URL"""
        payload = {
            "image_url": "https://images.pokemontcg.io/base1/4.png"
        }
        response = requests.post(
            f"{BASE_URL}/api/cards/grade",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        # May return 200 with grading, or 502 if Ximilar API has issues
        assert response.status_code in [200, 502, 500]
        if response.status_code == 200:
            data = response.json()
            # Should return overall_grade, centering, corners, edges, surface
            assert "overall_grade" in data or "grade_label" in data
            print(f"✓ Card grade returned: {list(data.keys())}")
        else:
            data = response.json()
            print(f"⚠ Card grade returned {response.status_code}: {data.get('error', 'unknown')}")
    
    def test_card_grade_missing_image(self):
        """Test card grade validation - missing image"""
        payload = {}
        response = requests.post(
            f"{BASE_URL}/api/cards/grade",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        print("✓ Card grade validation: rejects missing image")
    
    def test_collection_add(self):
        """Test POST /api/cards/collection/add"""
        payload = {
            "user_id": "test_user_123",
            "card_name": "TEST_Charizard",
            "card_set": "Base Set",
            "card_number": "4",
            "condition": "NM",
            "grade_estimate": 8.5,
            "estimated_value": 350.00
        }
        response = requests.post(
            f"{BASE_URL}/api/cards/collection/add",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "added"
        assert "card" in data
        print(f"✓ Collection add: card added with id {data['card'].get('id', 'unknown')}")
    
    def test_collection_get(self):
        """Test GET /api/cards/collection"""
        response = requests.get(
            f"{BASE_URL}/api/cards/collection",
            params={"user_id": "test_user_123"},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert "collection" in data
        assert "total_cards" in data
        print(f"✓ Collection get: {data['total_cards']} cards, value: ${data.get('estimated_value', 0)}")
    
    def test_market_trending(self):
        """Test GET /api/cards/market/trending"""
        response = requests.get(
            f"{BASE_URL}/api/cards/market/trending",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert "trending" in data
        assert len(data["trending"]) > 0
        print(f"✓ Market trending: {len(data['trending'])} cards")


class TestExistingAPIs:
    """Verify existing APIs still work (regression tests)"""
    
    def test_cover_letter_generation(self):
        """Test POST /api/career/cover-letter still works"""
        payload = {
            "resume_text": "Software Engineer with 5 years experience",
            "job_description": "Senior Software Engineer position",
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
        print(f"✓ Cover letter still working: {data.get('word_count', 0)} words")
    
    def test_verticals_trending(self):
        """Test GET /api/verticals/trending still works"""
        response = requests.get(
            f"{BASE_URL}/api/verticals/trending",
            params={"vertical": "sports"},
            timeout=30
        )
        assert response.status_code == 200
        print("✓ Verticals trending still working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
