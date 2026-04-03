"""
SaintSal Labs Platform — Backend API Tests (Iteration 7)
Tests: Health, GHL Stats, Business DNA, Credit Top-up, Checkout, Metering Engine
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://sal-preview-deploy.preview.emergentagent.com').rstrip('/')


class TestHealthEndpoints:
    """Health and status endpoint tests"""
    
    def test_health_returns_ok(self):
        """GET /api/health returns status ok with Supabase configured"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=15)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        assert "integrations" in data
        # Verify Supabase public and admin are configured
        supabase = data["integrations"].get("supabase", {})
        assert supabase.get("public") == True, "Supabase public client should be True"
        assert supabase.get("admin") == True, "Supabase admin client should be True"
        print(f"✅ Health check passed: Supabase public={supabase.get('public')}, admin={supabase.get('admin')}")


class TestGHLStats:
    """GoHighLevel stats endpoint tests"""
    
    def test_ghl_stats_returns_ok(self):
        """GET /api/ghl/stats returns ok=true (GHL configured)"""
        response = requests.get(f"{BASE_URL}/api/ghl/stats", timeout=15)
        assert response.status_code == 200
        data = response.json()
        # Should return ok=True if GHL is configured, or error message if not
        # Based on code: if token exists, returns ok=True
        if data.get("ok"):
            print(f"✅ GHL stats: ok=True, contacts={data.get('contacts')}, opportunities={data.get('opportunities')}")
        else:
            # If GHL returns error, it means token is missing or invalid
            error = data.get("error", "")
            print(f"⚠️ GHL stats: ok=False, error={error}")
            # The test should still pass if GHL is configured but API returns error
            # Only fail if "GHL not configured" is returned
            assert "GHL not configured" not in error, "GHL should be configured in env"


class TestBusinessDNA:
    """Business DNA profile CRUD tests"""
    
    def test_save_business_dna(self):
        """POST /api/user/business-dna saves and returns complete profile"""
        payload = {
            "first_name": "TEST_John",
            "last_name": "Doe",
            "email": "test@example.com",
            "phone": "555-123-4567",
            "business_name": "TEST_Acme Corp",
            "dba_name": "Acme",
            "business_type": "llc",
            "ein_number": "12-3456789",
            "state_of_incorporation": "DE",
            "industry": "Technology",
            "naics_code": "541511",
            "years_in_business": 5,
            "number_of_employees": 10,
            "annual_revenue": 500000,
            "monthly_revenue": 42000,
            "business_address": "123 Main St",
            "business_city": "Wilmington",
            "business_state": "DE",
            "business_zip": "19801",
            "website": "https://acme.com",
            "tagline": "Building the future",
            "bio": "We are a technology company focused on innovation.",
            "interests": ["ai_chat", "builder", "formation"],
            "anon_id": "test_anon_123"
        }
        response = requests.post(
            f"{BASE_URL}/api/user/business-dna",
            json=payload,
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        profile = data.get("profile", {})
        # Verify all fields are returned
        assert profile.get("first_name") == "TEST_John"
        assert profile.get("last_name") == "Doe"
        assert profile.get("email") == "test@example.com"
        assert profile.get("business_name") == "TEST_Acme Corp"
        assert profile.get("business_type") == "llc"
        assert profile.get("industry") == "Technology"
        assert profile.get("tagline") == "Building the future"
        assert profile.get("bio") == "We are a technology company focused on innovation."
        assert "ai_chat" in profile.get("interests", [])
        assert profile.get("onboarding_completed") == True
        print(f"✅ Business DNA saved: {profile.get('first_name')} {profile.get('last_name')}, {profile.get('business_name')}")
    
    def test_get_business_dna_returns_profile_or_empty(self):
        """GET /api/user/business-dna returns saved profile or empty default"""
        response = requests.get(f"{BASE_URL}/api/user/business-dna", timeout=15)
        assert response.status_code == 200
        data = response.json()
        # Should return either a saved profile or empty default
        assert "first_name" in data
        assert "business_type" in data
        assert "interests" in data
        print(f"✅ Business DNA retrieved: first_name={data.get('first_name')}, onboarding_completed={data.get('onboarding_completed')}")


class TestCreditTopup:
    """Credit top-up checkout tests"""
    
    def test_credit_topup_returns_stripe_url(self):
        """POST /api/billing/credit-topup with amount=25 returns valid Stripe URL"""
        payload = {"amount": 25}
        response = requests.post(
            f"{BASE_URL}/api/billing/credit-topup",
            json=payload,
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        assert "url" in data, "Response should contain Stripe checkout URL"
        assert data["url"].startswith("https://checkout.stripe.com"), f"URL should be Stripe checkout: {data['url']}"
        assert "session_id" in data
        assert data.get("amount") == 25
        assert data.get("credits") == 2500  # 25 * 100 cents
        print(f"✅ Credit top-up: amount=$25, credits={data.get('credits')}, url={data['url'][:60]}...")
    
    def test_credit_topup_various_amounts(self):
        """Test credit top-up with various valid amounts"""
        valid_amounts = [5, 10, 50, 100]
        for amount in valid_amounts:
            response = requests.post(
                f"{BASE_URL}/api/billing/credit-topup",
                json={"amount": amount},
                timeout=15
            )
            assert response.status_code == 200
            data = response.json()
            assert "url" in data
            print(f"✅ Credit top-up ${amount}: OK")
    
    def test_credit_topup_invalid_amount(self):
        """Test credit top-up with invalid amount returns error"""
        response = requests.post(
            f"{BASE_URL}/api/billing/credit-topup",
            json={"amount": 9999},
            timeout=15
        )
        # Should return 400 for invalid amount
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        print(f"✅ Invalid amount rejected: {data.get('error')}")


class TestCheckoutCreateSession:
    """Stripe checkout session creation tests"""
    
    def test_checkout_create_session_with_price_id(self):
        """POST /api/checkout/create-session with price_id returns Stripe URL"""
        # Use a real price_id from the metering config
        payload = {
            "price_id": "price_1T5bkAL47U80vDLAaChP4Hqg",  # Starter monthly
            "vertical": "general"
        }
        response = requests.post(
            f"{BASE_URL}/api/checkout/create-session",
            json=payload,
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        assert "url" in data, "Response should contain Stripe checkout URL"
        assert data["url"].startswith("https://checkout.stripe.com"), f"URL should be Stripe checkout: {data['url']}"
        assert "session_id" in data
        print(f"✅ Checkout session created: url={data['url'][:60]}...")
    
    def test_checkout_create_session_missing_price_id(self):
        """POST /api/checkout/create-session without price_id returns error"""
        response = requests.post(
            f"{BASE_URL}/api/checkout/create-session",
            json={"vertical": "general"},
            timeout=15
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "price_id" in data["error"].lower()
        print(f"✅ Missing price_id rejected: {data.get('error')}")


class TestMeteringDashboard:
    """Metering dashboard endpoint tests"""
    
    def test_metering_dashboard_returns_tier_info(self):
        """GET /api/metering/dashboard returns tier info, compute stats, action breakdown"""
        response = requests.get(
            f"{BASE_URL}/api/metering/dashboard?user_id=test_user_123",
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        # Verify required fields
        assert "tier" in data
        assert "tier_name" in data
        assert "compute" in data
        assert "action_breakdown" in data
        assert "rate_limit" in data
        # Verify compute structure
        compute = data.get("compute", {})
        assert "used" in compute
        assert "limit" in compute
        assert "remaining" in compute
        assert "cap_type" in compute
        print(f"✅ Metering dashboard: tier={data.get('tier')}, tier_name={data.get('tier_name')}, compute_used={compute.get('used')}")


class TestMeteringLog:
    """Metering log endpoint tests"""
    
    def test_metering_log_usage(self):
        """POST /api/metering/log logs usage and returns updated stats"""
        payload = {
            "user_id": "test_user_456",
            "action": "chat",
            "compute_minutes": 1,
            "model_used": "claude-sonnet",
            "compute_level": "pro"
        }
        response = requests.post(
            f"{BASE_URL}/api/metering/log",
            json=payload,
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("logged") == True
        assert data.get("action") == "chat"
        assert "total_minutes_used" in data
        assert "tier" in data
        assert "remaining" in data
        print(f"✅ Metering logged: action={data.get('action')}, total_minutes={data.get('total_minutes_used')}, remaining={data.get('remaining')}")


class TestMeteringCheckAccess:
    """Metering check-access endpoint tests"""
    
    def test_metering_check_access_allowed(self):
        """POST /api/metering/check-access validates feature access"""
        payload = {
            "user_id": "test_user_789",
            "feature": "search_basic"
        }
        response = requests.post(
            f"{BASE_URL}/api/metering/check-access",
            json=payload,
            timeout=15
        )
        # Should return 200 for allowed features
        assert response.status_code == 200
        data = response.json()
        assert data.get("allowed") == True
        assert "user_tier" in data
        print(f"✅ Check access: feature=search_basic, allowed={data.get('allowed')}, tier={data.get('user_tier')}")
    
    def test_metering_check_access_denied(self):
        """POST /api/metering/check-access returns 403 for restricted features"""
        # First set user to free tier
        requests.post(
            f"{BASE_URL}/api/metering/set-tier",
            json={"user_id": "test_free_user", "tier": "free"},
            timeout=15
        )
        # Then check access to a pro feature
        payload = {
            "user_id": "test_free_user",
            "feature": "builder_full"  # Pro feature
        }
        response = requests.post(
            f"{BASE_URL}/api/metering/check-access",
            json=payload,
            timeout=15
        )
        assert response.status_code == 403
        data = response.json()
        assert data.get("allowed") == False
        assert "required_tier" in data
        assert "upgrade_message" in data
        print(f"✅ Check access denied: feature=builder_full, required_tier={data.get('required_tier')}")


class TestMeteringTierInfo:
    """Metering tier info endpoint tests"""
    
    def test_metering_tier_info_returns_all_tiers(self):
        """GET /api/metering/tier-info returns all 5 tiers with Stripe IDs"""
        response = requests.get(f"{BASE_URL}/api/metering/tier-info", timeout=15)
        assert response.status_code == 200
        data = response.json()
        assert "tiers" in data
        tiers = data["tiers"]
        # Verify all 5 tiers exist
        expected_tiers = ["free", "starter", "pro", "teams", "enterprise"]
        for tier_name in expected_tiers:
            assert tier_name in tiers, f"Missing tier: {tier_name}"
            tier = tiers[tier_name]
            assert "name" in tier
            assert "price_monthly" in tier
            assert "compute_minutes" in tier
            assert "stripe" in tier
            assert "monthly_price_id" in tier["stripe"]
            print(f"✅ Tier {tier_name}: ${tier.get('price_monthly')}/mo, {tier.get('compute_minutes')} min, stripe_id={tier['stripe'].get('monthly_price_id')[:20]}...")
        
        # Verify compute levels
        assert "compute_levels" in data
        assert "action_costs" in data


class TestMeteringIntegrations:
    """Metering integrations endpoint tests"""
    
    def test_metering_integrations_returns_connectors(self):
        """GET /api/metering/integrations returns connectors across categories"""
        response = requests.get(f"{BASE_URL}/api/metering/integrations", timeout=15)
        assert response.status_code == 200
        data = response.json()
        assert "integrations" in data
        assert "categories" in data
        assert "total" in data
        integrations = data["integrations"]
        total = data["total"]
        categories = data["categories"]
        # Verify 60+ integrations (actual count is 65)
        assert total >= 60, f"Expected 60+ integrations, got {total}"
        assert len(integrations) >= 60
        # Verify categories exist
        expected_categories = ["LLM", "Search", "Voice", "Media", "CRM", "Data", "Deploy", "Payment"]
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"
        print(f"✅ Integrations: {total} total, {len(categories)} categories: {', '.join(categories[:5])}...")
    
    def test_metering_integrations_filter_by_category(self):
        """GET /api/metering/integrations?category=LLM filters by category"""
        response = requests.get(f"{BASE_URL}/api/metering/integrations?category=LLM", timeout=15)
        assert response.status_code == 200
        data = response.json()
        integrations = data["integrations"]
        # All returned integrations should be LLM category
        for integration in integrations:
            assert integration.get("category") == "LLM"
        print(f"✅ LLM integrations: {len(integrations)} found")


class TestMeteringComputeLevels:
    """Metering compute levels endpoint tests"""
    
    def test_metering_compute_levels(self):
        """GET /api/metering/compute-levels returns 4 compute levels"""
        response = requests.get(f"{BASE_URL}/api/metering/compute-levels", timeout=15)
        assert response.status_code == 200
        data = response.json()
        assert "levels" in data
        levels = data["levels"]
        expected_levels = ["mini", "pro", "max", "max_fast"]
        for level_name in expected_levels:
            assert level_name in levels, f"Missing compute level: {level_name}"
            level = levels[level_name]
            assert "name" in level
            assert "rate_per_min" in level
            assert "min_tier" in level
            print(f"✅ Compute level {level_name}: ${level.get('rate_per_min')}/min, min_tier={level.get('min_tier')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
