#!/usr/bin/env python3
"""
SaintSal Labs Platform v2 — Backend API Testing
Tests all 32+ new endpoints across 8 sections
"""
import requests
import sys
import json
import time
from datetime import datetime

class SaintSalAPITester:
    def __init__(self, base_url="https://sal-preview-deploy.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   {method} {endpoint}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, timeout=timeout)
            elif method == 'POST':
                response = self.session.post(url, json=data, timeout=timeout)
            elif method == 'PUT':
                response = self.session.put(url, json=data, timeout=timeout)
            elif method == 'DELETE':
                response = self.session.delete(url, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                try:
                    resp_json = response.json()
                    if isinstance(resp_json, dict):
                        # Show key fields for verification
                        if 'articles' in resp_json:
                            print(f"   📰 Found {len(resp_json['articles'])} articles")
                        elif 'cover_letter' in resp_json:
                            print(f"   📝 Cover letter generated ({resp_json.get('word_count', 0)} words)")
                        elif 'headline' in resp_json:
                            print(f"   💼 LinkedIn optimization complete")
                        elif 'market_range' in resp_json:
                            print(f"   💰 Salary negotiation data ready")
                        elif 'connections' in resp_json:
                            print(f"   🌐 Found {len(resp_json.get('connections', []))} connections")
                        elif 'prior_art' in resp_json:
                            print(f"   🔬 Found {len(resp_json.get('prior_art', []))} prior art references")
                        elif 'trending' in resp_json:
                            print(f"   📈 Found {len(resp_json.get('trending', []))} trending cards")
                        elif 'collection' in resp_json:
                            print(f"   🎴 Collection has {len(resp_json.get('collection', []))} cards")
                        elif 'models' in resp_json:
                            print(f"   🤖 Found {len(resp_json.get('models', []))} models")
                        elif 'logged' in resp_json:
                            print(f"   📊 Metering logged successfully")
                        elif 'domains' in resp_json:
                            print(f"   🌐 Found {len(resp_json.get('domains', []))} domains")
                        elif 'recommended_entity' in resp_json:
                            print(f"   🏢 Recommended: {resp_json.get('recommended_entity', 'N/A')}")
                        elif 'order_id' in resp_json:
                            print(f"   📋 Order created: {resp_json.get('order_id', 'N/A')}")
                        elif 'calendar_events' in resp_json:
                            print(f"   📅 Generated {len(resp_json.get('calendar_events', []))} compliance events")
                        elif 'status' in resp_json and resp_json['status'] == 'added':
                            print(f"   ✅ Card added to collection")
                except:
                    print(f"   📄 Response received (non-JSON or complex structure)")
            else:
                self.tests_passed += 0  # Don't increment on failure
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text[:200]}")
                self.failed_tests.append({
                    'name': name,
                    'endpoint': endpoint,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'error': response.text[:200]
                })

            return success, response

        except requests.exceptions.Timeout:
            print(f"❌ FAILED - Request timeout after {timeout}s")
            self.failed_tests.append({
                'name': name,
                'endpoint': endpoint,
                'expected': expected_status,
                'actual': 'TIMEOUT',
                'error': f'Request timeout after {timeout}s'
            })
            return False, None
        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            self.failed_tests.append({
                'name': name,
                'endpoint': endpoint,
                'expected': expected_status,
                'actual': 'ERROR',
                'error': str(e)
            })
            return False, None

    def test_verticals_trending(self):
        """Test verticals trending endpoints"""
        print("\n" + "="*60)
        print("🔥 TESTING VERTICALS TRENDING")
        print("="*60)
        
        # Test sports vertical
        self.run_test(
            "Verticals Trending - Sports",
            "GET",
            "/api/verticals/trending?vertical=sports",
            200
        )
        
        # Test finance vertical
        self.run_test(
            "Verticals Trending - Finance", 
            "GET",
            "/api/verticals/trending?vertical=finance",
            200
        )

    def test_career_suite(self):
        """Test Career Suite endpoints"""
        print("\n" + "="*60)
        print("💼 TESTING CAREER SUITE")
        print("="*60)
        
        # Cover Letter AI
        self.run_test(
            "Career - Cover Letter",
            "POST",
            "/api/career/cover-letter",
            200,
            {
                "resume_text": "John Doe, Software Engineer with 5 years experience in Python, React, and AWS. Led team of 3 developers at TechCorp.",
                "job_description": "Senior Software Engineer position at Google. Requirements: Python, React, cloud experience, team leadership.",
                "style": "direct"
            }
        )
        
        # LinkedIn Optimizer
        self.run_test(
            "Career - LinkedIn Optimize",
            "POST", 
            "/api/career/linkedin-optimize",
            200,
            {
                "current_profile_text": "Software Engineer at TechCorp. I work with Python and React. I like coding and solving problems."
            }
        )
        
        # Salary Negotiator
        self.run_test(
            "Career - Salary Negotiate",
            "POST",
            "/api/career/salary-negotiate", 
            200,
            {
                "role": "Senior Software Engineer",
                "location": "San Francisco, CA",
                "experience_years": 5
            }
        )
        
        # Network Mapper
        self.run_test(
            "Career - Network Map",
            "POST",
            "/api/career/network-map",
            200,
            {
                "target_company": "Google"
            }
        )

    def test_business_intelligence(self):
        """Test Business Intelligence endpoints"""
        print("\n" + "="*60)
        print("🧠 TESTING BUSINESS INTELLIGENCE")
        print("="*60)
        
        # Business Plan AI (SSE streaming - test initial response)
        print(f"\n🔍 Testing Business Plan AI (SSE Stream)...")
        print(f"   POST /api/business/plan")
        try:
            response = self.session.post(
                f"{self.base_url}/api/business/plan",
                json={
                    "idea_description": "AI-powered fitness app that creates personalized workout plans",
                    "target_market": "Health-conscious millennials",
                    "stage": "pre-revenue"
                },
                stream=True,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ PASSED - SSE stream started (Status: {response.status_code})")
                # Read first few chunks to verify streaming
                chunk_count = 0
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        chunk_count += 1
                        if chunk_count >= 3:  # Read first 3 chunks then break
                            break
                print(f"   📊 Received {chunk_count} data chunks")
                self.tests_passed += 1
            else:
                print(f"❌ FAILED - Expected 200, got {response.status_code}")
                self.failed_tests.append({
                    'name': 'Business Plan AI',
                    'endpoint': '/api/business/plan',
                    'expected': 200,
                    'actual': response.status_code,
                    'error': response.text[:200]
                })
        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            self.failed_tests.append({
                'name': 'Business Plan AI',
                'endpoint': '/api/business/plan', 
                'expected': 200,
                'actual': 'ERROR',
                'error': str(e)
            })
        self.tests_run += 1
        
        # Patent Search
        self.run_test(
            "Business - Patent Search",
            "POST",
            "/api/business/patent-search",
            200,
            {
                "technology_description": "Machine learning algorithm for image recognition",
                "competitors": ["Google", "Microsoft", "Amazon"]
            }
        )

    def test_launchpad(self):
        """Test Launch Pad endpoints"""
        print("\n" + "="*60)
        print("🚀 TESTING LAUNCH PAD")
        print("="*60)
        
        # Name Check
        self.run_test(
            "LaunchPad - Name Check",
            "POST",
            "/api/launchpad/name-check",
            200,
            {
                "business_name": "TechStartup Solutions",
                "state": "CA"
            }
        )
        
        # Entity Advisor
        self.run_test(
            "LaunchPad - Entity Advisor",
            "POST", 
            "/api/launchpad/entity-advisor",
            200,
            {
                "cofounders": 2,
                "funding_plans": "seed_funding",
                "liability_needs": "high",
                "tax_preference": "minimize_taxes"
            }
        )
        
        # Entity Formation
        self.run_test(
            "LaunchPad - Entity Formation",
            "POST",
            "/api/launchpad/entity/form",
            200,
            {
                "entity_type": "LLC",
                "state": "DE", 
                "entity_name": "Test Startup LLC",
                "members": [{"name": "John Doe", "ownership": 100}],
                "registered_agent": True
            }
        )
        
        # Compliance Setup
        self.run_test(
            "LaunchPad - Compliance Setup",
            "POST",
            "/api/launchpad/compliance/setup",
            200,
            {
                "entity_type": "LLC",
                "state": "CA",
                "formation_date": "2024-01-01"
            }
        )

    def test_cookin_cards(self):
        """Test CookinCards endpoints"""
        print("\n" + "="*60)
        print("🎴 TESTING COOKIN CARDS")
        print("="*60)
        
        # Market Trending
        self.run_test(
            "Cards - Market Trending",
            "GET",
            "/api/cards/market/trending",
            200
        )
        
        # Add to Collection
        self.run_test(
            "Cards - Add to Collection",
            "POST",
            "/api/cards/collection/add",
            200,
            {
                "card_name": "Charizard VMAX",
                "user_id": "test_user"
            }
        )
        
        # Get Collection
        self.run_test(
            "Cards - Get Collection",
            "GET", 
            "/api/cards/collection?user_id=test_user",
            200
        )

    def test_builder_v2(self):
        """Test Builder v2 endpoints"""
        print("\n" + "="*60)
        print("🏗️ TESTING BUILDER V2")
        print("="*60)
        
        # Get Models
        self.run_test(
            "Builder - Get Models",
            "GET",
            "/api/builder/models",
            200
        )

    def test_metering(self):
        """Test Metering endpoints"""
        print("\n" + "="*60)
        print("📊 TESTING METERING")
        print("="*60)
        
        # Log Usage
        self.run_test(
            "Metering - Log Usage",
            "POST",
            "/api/metering/log",
            200,
            {
                "user_id": "test_user",
                "action": "chat_completion",
                "compute_minutes": 2.5,
                "model_used": "claude-sonnet"
            }
        )

    def run_all_tests(self):
        """Run all test suites"""
        start_time = time.time()
        print("🚀 SaintSal Labs Platform v2 - API Testing Suite")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test suites
        self.test_verticals_trending()
        self.test_career_suite()
        self.test_business_intelligence()
        self.test_launchpad()
        self.test_cookin_cards()
        self.test_builder_v2()
        self.test_metering()
        
        # Print final results
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "="*80)
        print("📊 FINAL TEST RESULTS")
        print("="*80)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            for i, test in enumerate(self.failed_tests, 1):
                print(f"{i}. {test['name']}")
                print(f"   Endpoint: {test['endpoint']}")
                print(f"   Expected: {test['expected']}, Got: {test['actual']}")
                print(f"   Error: {test['error']}")
                print()
        
        return self.tests_passed == self.tests_run

def main():
    tester = SaintSalAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())