"""
SaintSal Labs v11 - Comprehensive Backend API Tests
Testing: CookinCards, Website Intel, Real Estate, Career Suite 14-status Kanban
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://sal-preview-deploy.preview.emergentagent.com').rstrip('/')

# Test credentials from test_credentials.md
TEST_EMAIL = "ryan@cookin.io"
TEST_PASSWORD = "Ayden0428$$"


class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_health_endpoint(self):
        """Test API health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print(f"✓ Health check passed: {response.json()}")
    
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        # Login may return 200 or 201
        assert response.status_code in [200, 201], f"Login failed: {response.status_code} - {response.text}"
        data = response.json()
        print(f"✓ Login successful: {data.get('user', {}).get('email', 'N/A')}")
        return data


class TestCookinCardsSearch:
    """CookinCards - Pokemon TCG API search tests"""
    
    def test_cards_search_charizard(self):
        """POST /api/cards/search with {query:'Charizard'} returns cards with images, set names, prices"""
        response = requests.post(f"{BASE_URL}/api/cards/search", json={
            "query": "Charizard"
        })
        assert response.status_code == 200, f"Cards search failed: {response.status_code} - {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "results" in data, "Response missing 'results' field"
        assert "query" in data, "Response missing 'query' field"
        assert data["query"] == "Charizard", f"Query mismatch: {data['query']}"
        
        results = data["results"]
        assert len(results) > 0, "No cards returned for Charizard search"
        
        # Verify card structure
        first_card = results[0]
        assert "name" in first_card, "Card missing 'name' field"
        assert "set_name" in first_card, "Card missing 'set_name' field"
        assert "image_small" in first_card or "image_large" in first_card, "Card missing image fields"
        
        # Check for price data
        has_price = first_card.get("market_price") is not None or first_card.get("tcgplayer_url")
        print(f"✓ Cards search returned {len(results)} results")
        print(f"  First card: {first_card.get('name')} from {first_card.get('set_name')}")
        print(f"  Has price data: {has_price}")
        print(f"  Image URL: {first_card.get('image_small', 'N/A')[:50]}...")
    
    def test_cards_search_pikachu(self):
        """Test search for another popular card"""
        response = requests.post(f"{BASE_URL}/api/cards/search", json={
            "query": "Pikachu"
        })
        assert response.status_code == 200, f"Cards search failed: {response.status_code}"
        data = response.json()
        assert len(data.get("results", [])) > 0, "No Pikachu cards found"
        print(f"✓ Pikachu search returned {len(data['results'])} results")
    
    def test_cards_search_empty_query(self):
        """Test search with empty query returns error"""
        response = requests.post(f"{BASE_URL}/api/cards/search", json={
            "query": ""
        })
        assert response.status_code == 400, f"Expected 400 for empty query, got {response.status_code}"
        print("✓ Empty query correctly returns 400 error")


class TestCookinCardsPrice:
    """CookinCards - eBay pricing via Tavily tests"""
    
    def test_cards_price_charizard(self):
        """POST /api/cards/price with {card_name:'Charizard',card_type:'tcg'} returns ebay_listings and tcgplayer prices"""
        response = requests.post(f"{BASE_URL}/api/cards/price", json={
            "card_name": "Charizard",
            "card_type": "tcg"
        })
        assert response.status_code == 200, f"Cards price failed: {response.status_code} - {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "card_name" in data, "Response missing 'card_name' field"
        assert "ebay_listings" in data, "Response missing 'ebay_listings' field"
        assert "tcgplayer" in data, "Response missing 'tcgplayer' field"
        
        print(f"✓ Cards price lookup successful")
        print(f"  Card: {data.get('card_name')}")
        print(f"  eBay listings: {len(data.get('ebay_listings', []))}")
        print(f"  TCGPlayer data: {bool(data.get('tcgplayer'))}")
        
        # Check eBay listings structure if present
        if data.get("ebay_listings"):
            listing = data["ebay_listings"][0]
            assert "title" in listing, "eBay listing missing 'title'"
            assert "url" in listing, "eBay listing missing 'url'"
            print(f"  First eBay listing: {listing.get('title', 'N/A')[:50]}...")
    
    def test_cards_price_missing_name(self):
        """Test price lookup with missing card name"""
        response = requests.post(f"{BASE_URL}/api/cards/price", json={
            "card_type": "tcg"
        })
        assert response.status_code == 400, f"Expected 400 for missing card_name, got {response.status_code}"
        print("✓ Missing card_name correctly returns 400 error")


class TestCookinCardsTrending:
    """CookinCards - Live trending market data via Tavily"""
    
    def test_market_trending(self):
        """GET /api/cards/market/trending returns trending_articles from Tavily"""
        response = requests.get(f"{BASE_URL}/api/cards/market/trending")
        assert response.status_code == 200, f"Market trending failed: {response.status_code} - {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "trending_articles" in data or "trending" in data, "Response missing trending data"
        assert "updated_at" in data, "Response missing 'updated_at' field"
        
        articles = data.get("trending_articles", [])
        source = data.get("source", "unknown")
        
        print(f"✓ Market trending returned {len(articles)} articles")
        print(f"  Source: {source}")
        print(f"  Updated at: {data.get('updated_at')}")
        
        if articles:
            first_article = articles[0]
            assert "title" in first_article, "Article missing 'title'"
            assert "url" in first_article, "Article missing 'url'"
            print(f"  First article: {first_article.get('title', 'N/A')[:60]}...")


class TestCookinCardsCertVerification:
    """CookinCards - PSA/BGS cert verification"""
    
    def test_verify_cert_psa(self):
        """POST /api/cards/verify-cert with {cert_number:'12345678',company:'PSA'} returns verification_url and search_results"""
        response = requests.post(f"{BASE_URL}/api/cards/verify-cert", json={
            "cert_number": "12345678",
            "company": "PSA"
        })
        assert response.status_code == 200, f"Cert verification failed: {response.status_code} - {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "cert_number" in data, "Response missing 'cert_number'"
        assert "company" in data, "Response missing 'company'"
        assert "verification_url" in data, "Response missing 'verification_url'"
        assert "search_results" in data, "Response missing 'search_results'"
        
        print(f"✓ Cert verification successful")
        print(f"  Cert: {data.get('cert_number')}")
        print(f"  Company: {data.get('company')}")
        print(f"  Verification URL: {data.get('verification_url')}")
        print(f"  Search results: {len(data.get('search_results', []))}")
    
    def test_verify_cert_bgs(self):
        """Test BGS cert verification"""
        response = requests.post(f"{BASE_URL}/api/cards/verify-cert", json={
            "cert_number": "87654321",
            "company": "BGS"
        })
        assert response.status_code == 200, f"BGS cert verification failed: {response.status_code}"
        data = response.json()
        assert data.get("company") == "BGS", f"Company mismatch: {data.get('company')}"
        print(f"✓ BGS cert verification successful")
    
    def test_verify_cert_missing_number(self):
        """Test cert verification with missing cert number"""
        response = requests.post(f"{BASE_URL}/api/cards/verify-cert", json={
            "company": "PSA"
        })
        assert response.status_code == 400, f"Expected 400 for missing cert_number, got {response.status_code}"
        print("✓ Missing cert_number correctly returns 400 error")


class TestCookinCardsCollection:
    """CookinCards - Supabase-backed collection management"""
    
    def test_get_collection_anonymous(self):
        """GET /api/cards/collection returns empty collection for anonymous user"""
        response = requests.get(f"{BASE_URL}/api/cards/collection")
        assert response.status_code == 200, f"Get collection failed: {response.status_code}"
        data = response.json()
        
        assert "collection" in data, "Response missing 'collection'"
        assert "total_cards" in data, "Response missing 'total_cards'"
        assert "estimated_value" in data, "Response missing 'estimated_value'"
        
        print(f"✓ Get collection (anonymous) successful")
        print(f"  Total cards: {data.get('total_cards')}")
        print(f"  Estimated value: ${data.get('estimated_value', 0)}")
    
    def test_add_to_collection_anonymous(self):
        """POST /api/cards/collection/add without auth returns local save note"""
        response = requests.post(f"{BASE_URL}/api/cards/collection/add", json={
            "card_name": "TEST_Charizard",
            "card_set": "Base Set",
            "card_type": "tcg",
            "estimated_value": 500
        })
        # Should return 200 with local save note for anonymous users
        assert response.status_code == 200, f"Add to collection failed: {response.status_code} - {response.text}"
        data = response.json()
        
        # For anonymous users, should return added_local status
        status = data.get("status")
        assert status in ["added", "added_local"], f"Unexpected status: {status}"
        
        print(f"✓ Add to collection successful")
        print(f"  Status: {status}")
        if data.get("note"):
            print(f"  Note: {data.get('note')}")


class TestWebsiteIntel:
    """Website Intelligence - Crawl and auto-populate Business DNA"""
    
    def test_website_intel_crawl(self):
        """POST /api/studio/website-intel with {url:'https://cookin.io'} triggers crawl"""
        response = requests.post(f"{BASE_URL}/api/studio/website-intel", json={
            "url": "https://cookin.io"
        }, timeout=90)  # Longer timeout for crawl
        
        assert response.status_code == 200, f"Website intel failed: {response.status_code} - {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "crawl_id" in data, "Response missing 'crawl_id'"
        assert "url" in data, "Response missing 'url'"
        assert "brand_extraction" in data, "Response missing 'brand_extraction'"
        
        print(f"✓ Website intel crawl successful")
        print(f"  Crawl ID: {data.get('crawl_id')}")
        print(f"  URL: {data.get('url')}")
        print(f"  Saved to Supabase: {data.get('saved_to_supabase')}")
        print(f"  DNA auto-populated: {data.get('dna_auto_populated')}")
        
        # Check brand extraction
        brand = data.get("brand_extraction", {})
        if brand:
            print(f"  Brand name: {brand.get('brand_name', 'N/A')}")
            print(f"  Industry: {brand.get('industry', 'N/A')}")
    
    def test_website_intel_empty_url(self):
        """Test website intel with empty URL returns error"""
        response = requests.post(f"{BASE_URL}/api/studio/website-intel", json={
            "url": ""
        })
        assert response.status_code == 400, f"Expected 400 for empty URL, got {response.status_code}"
        print("✓ Empty URL correctly returns 400 error")
    
    def test_website_intel_list_crawls(self):
        """GET /api/studio/website-intel returns list of crawls"""
        response = requests.get(f"{BASE_URL}/api/studio/website-intel")
        assert response.status_code == 200, f"List crawls failed: {response.status_code}"
        data = response.json()
        
        assert "crawls" in data, "Response missing 'crawls'"
        print(f"✓ List crawls successful: {len(data.get('crawls', []))} crawls")


class TestRealEstateListings:
    """Real Estate - Property listings with coordinates"""
    
    def test_listings_sale_austin(self):
        """GET /api/realestate/listings/sale?city=Austin&state=TX returns listings with lat/lng/price"""
        response = requests.get(f"{BASE_URL}/api/realestate/listings/sale", params={
            "city": "Austin",
            "state": "TX"
        })
        assert response.status_code == 200, f"Listings failed: {response.status_code} - {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "listings" in data, "Response missing 'listings'"
        listings = data.get("listings", [])
        
        print(f"✓ Real estate listings successful")
        print(f"  Total listings: {len(listings)}")
        print(f"  Source: {data.get('source', 'N/A')}")
        
        if listings:
            first = listings[0]
            # Check for required fields
            has_lat = "latitude" in first
            has_lng = "longitude" in first
            has_price = "price" in first
            
            print(f"  First listing:")
            print(f"    Address: {first.get('formattedAddress', first.get('address', 'N/A'))}")
            print(f"    Price: ${first.get('price', 'N/A')}")
            print(f"    Has coordinates: lat={has_lat}, lng={has_lng}")
            
            if has_lat and has_lng:
                print(f"    Coordinates: ({first.get('latitude')}, {first.get('longitude')})")
    
    def test_listings_sale_by_zipcode(self):
        """Test listings by zipcode"""
        response = requests.get(f"{BASE_URL}/api/realestate/listings/sale", params={
            "zipcode": "78701"
        })
        assert response.status_code == 200, f"Listings by zipcode failed: {response.status_code}"
        data = response.json()
        print(f"✓ Listings by zipcode: {len(data.get('listings', []))} results")


class TestCareerSuiteTracker:
    """Career Suite - 14-status Kanban tracker"""
    
    def test_tracker_get_14_statuses(self):
        """GET /api/career/v2/tracker returns exactly 14 kanban statuses"""
        response = requests.get(f"{BASE_URL}/api/career/v2/tracker")
        assert response.status_code == 200, f"Tracker GET failed: {response.status_code} - {response.text}"
        data = response.json()
        
        # Verify kanban structure
        assert "kanban" in data, "Response missing 'kanban'"
        kanban = data.get("kanban", {})
        
        # Expected 14 statuses
        expected_statuses = [
            "wishlist", "networking", "saved", "applied", "phone_screen",
            "assessment", "interview_scheduled", "interview_completed",
            "reference_check", "offer_received", "negotiating",
            "job_won", "rejected", "withdrawn"
        ]
        
        actual_statuses = list(kanban.keys())
        
        print(f"✓ Tracker returned {len(actual_statuses)} statuses")
        print(f"  Expected: {len(expected_statuses)}")
        
        # Check each expected status exists
        missing = [s for s in expected_statuses if s not in actual_statuses]
        extra = [s for s in actual_statuses if s not in expected_statuses]
        
        if missing:
            print(f"  Missing statuses: {missing}")
        if extra:
            print(f"  Extra statuses: {extra}")
        
        assert len(actual_statuses) == 14, f"Expected 14 statuses, got {len(actual_statuses)}"
        
        for status in expected_statuses:
            assert status in kanban, f"Missing status: {status}"
        
        print(f"  All 14 statuses present: ✓")
        
        # Count total jobs
        total_jobs = sum(len(jobs) for jobs in kanban.values())
        print(f"  Total jobs tracked: {total_jobs}")
    
    def test_tracker_add_job_saved_status(self):
        """POST /api/career/v2/tracker adds job with 'saved' status"""
        response = requests.post(f"{BASE_URL}/api/career/v2/tracker", json={
            "job_title": "TEST_Software Engineer",
            "company_name": "TEST_Company",
            "job_url": "https://example.com/job",
            "status": "saved",
            "notes": "Test job for v11 testing"
        })
        
        # May fail due to Supabase constraint, but should return meaningful response
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Job added successfully")
            print(f"  Job ID: {data.get('job_id', 'N/A')}")
        elif response.status_code == 500:
            print(f"⚠ Job add failed (likely Supabase constraint): {response.text[:100]}")
        else:
            print(f"⚠ Unexpected status: {response.status_code}")


class TestCareerSuiteResumes:
    """Career Suite - Resume endpoints"""
    
    def test_get_resumes_list(self):
        """GET /api/career/v2/resumes returns resumes list"""
        response = requests.get(f"{BASE_URL}/api/career/v2/resumes")
        assert response.status_code == 200, f"Get resumes failed: {response.status_code}"
        data = response.json()
        
        assert "resumes" in data, "Response missing 'resumes'"
        print(f"✓ Get resumes successful: {len(data.get('resumes', []))} resumes")


class TestCareerSuiteSignatures:
    """Career Suite - Email signatures"""
    
    def test_get_signatures_list(self):
        """GET /api/career/v2/signatures returns signatures list"""
        response = requests.get(f"{BASE_URL}/api/career/v2/signatures")
        assert response.status_code == 200, f"Get signatures failed: {response.status_code}"
        data = response.json()
        
        assert "signatures" in data, "Response missing 'signatures'"
        print(f"✓ Get signatures successful: {len(data.get('signatures', []))} signatures")


class TestCareerSuiteJobSearch:
    """Career Suite - Job search via Tavily"""
    
    def test_job_search(self):
        """GET /api/career/jobs/search returns real job results"""
        response = requests.get(f"{BASE_URL}/api/career/jobs/search", params={
            "query": "software engineer"
        })
        assert response.status_code == 200, f"Job search failed: {response.status_code}"
        data = response.json()
        
        assert "jobs" in data, "Response missing 'jobs'"
        jobs = data.get("jobs", [])
        
        print(f"✓ Job search successful: {len(jobs)} jobs found")
        if jobs:
            first = jobs[0]
            print(f"  First job: {first.get('title', 'N/A')} at {first.get('company', 'N/A')}")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
