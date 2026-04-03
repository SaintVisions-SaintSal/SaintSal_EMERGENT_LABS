"""
SaintSal Labs — Metering v3 Production Spec Tests
Tests for: 5 tiers ($0/$27/$97/$297/$497), 4 compute levels, 65+ integrations, hard/soft cap logic
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ═══════════════════════════════════════════════════════════════════════════════
# TIER INFO TESTS — Verify 5 tiers with correct prices and Stripe IDs
# ═══════════════════════════════════════════════════════════════════════════════

class TestTierInfo:
    """Test GET /api/metering/tier-info endpoint with production pricing"""
    
    def test_tier_info_returns_5_tiers(self):
        """Should return all 5 tiers: free, starter, pro, teams, enterprise"""
        response = requests.get(f"{BASE_URL}/api/metering/tier-info")
        assert response.status_code == 200
        
        data = response.json()
        assert "tiers" in data
        
        expected_tiers = ["free", "starter", "pro", "teams", "enterprise"]
        for tier in expected_tiers:
            assert tier in data["tiers"], f"Missing tier: {tier}"
        
        print(f"✓ All 5 tiers present: {list(data['tiers'].keys())}")
    
    def test_tier_prices_match_production_spec(self):
        """Verify prices: $0, $27, $97, $297, $497"""
        response = requests.get(f"{BASE_URL}/api/metering/tier-info")
        data = response.json()
        tiers = data["tiers"]
        
        expected_prices = {
            "free": 0,
            "starter": 27,
            "pro": 97,
            "teams": 297,
            "enterprise": 497
        }
        
        for tier_name, expected_price in expected_prices.items():
            actual_price = tiers[tier_name]["price_monthly"]
            assert actual_price == expected_price, f"{tier_name} price mismatch: expected ${expected_price}, got ${actual_price}"
            print(f"✓ {tier_name}: ${actual_price}/mo")
    
    def test_tier_compute_limits(self):
        """Verify compute limits: 100/500/2000/10000/unlimited"""
        response = requests.get(f"{BASE_URL}/api/metering/tier-info")
        data = response.json()
        tiers = data["tiers"]
        
        expected_limits = {
            "free": 100,
            "starter": 500,
            "pro": 2000,
            "teams": 10000,
            "enterprise": -1  # Unlimited
        }
        
        for tier_name, expected_limit in expected_limits.items():
            actual_limit = tiers[tier_name]["compute_minutes"]
            assert actual_limit == expected_limit, f"{tier_name} limit mismatch: expected {expected_limit}, got {actual_limit}"
            print(f"✓ {tier_name}: {actual_limit} compute minutes")
    
    def test_tier_stripe_ids_present(self):
        """Verify each tier has Stripe product_id and price_id"""
        response = requests.get(f"{BASE_URL}/api/metering/tier-info")
        data = response.json()
        tiers = data["tiers"]
        
        for tier_name, tier_config in tiers.items():
            assert "stripe" in tier_config, f"{tier_name} missing stripe config"
            stripe = tier_config["stripe"]
            assert "product_id" in stripe, f"{tier_name} missing stripe product_id"
            assert "monthly_price_id" in stripe, f"{tier_name} missing stripe monthly_price_id"
            print(f"✓ {tier_name}: product={stripe['product_id'][:15]}...")
    
    def test_tier_cap_types(self):
        """Verify cap types: free/starter=hard, pro/teams/enterprise=soft/none"""
        response = requests.get(f"{BASE_URL}/api/metering/tier-info")
        data = response.json()
        tiers = data["tiers"]
        
        expected_caps = {
            "free": "hard",
            "starter": "hard",
            "pro": "soft",
            "teams": "soft",
            "enterprise": "none"
        }
        
        for tier_name, expected_cap in expected_caps.items():
            actual_cap = tiers[tier_name]["cap_type"]
            assert actual_cap == expected_cap, f"{tier_name} cap mismatch: expected {expected_cap}, got {actual_cap}"
            print(f"✓ {tier_name}: cap_type={actual_cap}")


# ═══════════════════════════════════════════════════════════════════════════════
# COMPUTE LEVELS TESTS — 4 levels with correct rates
# ═══════════════════════════════════════════════════════════════════════════════

class TestComputeLevels:
    """Test GET /api/metering/compute-levels endpoint"""
    
    def test_compute_levels_returns_4_levels(self):
        """Should return 4 compute levels: mini, pro, max, max_fast"""
        response = requests.get(f"{BASE_URL}/api/metering/compute-levels")
        assert response.status_code == 200
        
        data = response.json()
        assert "levels" in data
        
        expected_levels = ["mini", "pro", "max", "max_fast"]
        for level in expected_levels:
            assert level in data["levels"], f"Missing compute level: {level}"
        
        print(f"✓ All 4 compute levels present: {list(data['levels'].keys())}")
    
    def test_compute_level_rates(self):
        """Verify rates: Mini $0.05, Pro $0.25, Max $0.75, Max Fast $1.00"""
        response = requests.get(f"{BASE_URL}/api/metering/compute-levels")
        data = response.json()
        levels = data["levels"]
        
        expected_rates = {
            "mini": 0.05,
            "pro": 0.25,
            "max": 0.75,
            "max_fast": 1.00
        }
        
        for level_name, expected_rate in expected_rates.items():
            actual_rate = levels[level_name]["rate_per_min"]
            assert actual_rate == expected_rate, f"{level_name} rate mismatch: expected ${expected_rate}, got ${actual_rate}"
            print(f"✓ {level_name}: ${actual_rate}/min")
    
    def test_compute_level_min_tier_requirements(self):
        """Verify min tier requirements for each compute level"""
        response = requests.get(f"{BASE_URL}/api/metering/compute-levels")
        data = response.json()
        levels = data["levels"]
        
        expected_min_tiers = {
            "mini": "free",
            "pro": "starter",
            "max": "pro",
            "max_fast": "teams"
        }
        
        for level_name, expected_min_tier in expected_min_tiers.items():
            actual_min_tier = levels[level_name]["min_tier"]
            assert actual_min_tier == expected_min_tier, f"{level_name} min_tier mismatch: expected {expected_min_tier}, got {actual_min_tier}"
            print(f"✓ {level_name}: requires {actual_min_tier} tier")


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATIONS TESTS — 65+ integrations across 16 categories
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntegrations:
    """Test GET /api/metering/integrations endpoint"""
    
    def test_integrations_returns_65_plus(self):
        """Should return 65+ integrations"""
        response = requests.get(f"{BASE_URL}/api/metering/integrations")
        assert response.status_code == 200
        
        data = response.json()
        assert "integrations" in data
        assert "total" in data
        
        total = data["total"]
        assert total >= 65, f"Expected 65+ integrations, got {total}"
        print(f"✓ Total integrations: {total}")
    
    def test_integrations_have_categories(self):
        """Should have multiple categories"""
        response = requests.get(f"{BASE_URL}/api/metering/integrations")
        data = response.json()
        
        assert "categories" in data
        categories = data["categories"]
        
        # Should have at least 10 categories
        assert len(categories) >= 10, f"Expected 10+ categories, got {len(categories)}"
        print(f"✓ Categories ({len(categories)}): {categories}")
    
    def test_integrations_filter_by_category(self):
        """Should filter integrations by category"""
        response = requests.get(f"{BASE_URL}/api/metering/integrations?category=LLM")
        assert response.status_code == 200
        
        data = response.json()
        integrations = data["integrations"]
        
        # All returned integrations should be LLM category
        for integration in integrations:
            assert integration["category"] == "LLM", f"Expected LLM category, got {integration['category']}"
        
        print(f"✓ LLM integrations: {len(integrations)}")


# ═══════════════════════════════════════════════════════════════════════════════
# CHECK-ACCESS TESTS — Feature gating with stripe_price_id in 403 response
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckAccess:
    """Test POST /api/metering/check-access endpoint"""
    
    def test_free_user_blocked_from_business_bizplan(self):
        """Free user should be blocked from 'business_bizplan' with 403"""
        # Set user to free tier
        requests.post(
            f"{BASE_URL}/api/metering/set-tier",
            json={"user_id": "test_free_gate", "tier": "free"}
        )
        
        # Check access
        response = requests.post(
            f"{BASE_URL}/api/metering/check-access",
            json={"user_id": "test_free_gate", "feature": "business_bizplan"}
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        
        data = response.json()
        assert data["allowed"] == False
        print(f"✓ Free user blocked from business_bizplan (403)")
    
    def test_403_response_includes_stripe_price_id(self):
        """403 response should include stripe_price_id and required_price"""
        # Set user to free tier
        requests.post(
            f"{BASE_URL}/api/metering/set-tier",
            json={"user_id": "test_stripe_id", "tier": "free"}
        )
        
        # Check access
        response = requests.post(
            f"{BASE_URL}/api/metering/check-access",
            json={"user_id": "test_stripe_id", "feature": "business_bizplan"}
        )
        
        assert response.status_code == 403
        data = response.json()
        
        assert "stripe_price_id" in data, "Missing stripe_price_id in 403 response"
        assert "required_price" in data, "Missing required_price in 403 response"
        
        print(f"✓ 403 includes stripe_price_id: {data['stripe_price_id'][:20]}...")
        print(f"✓ 403 includes required_price: ${data['required_price']}")
    
    def test_pro_user_allowed_business_bizplan(self):
        """Pro user should be allowed to access 'business_bizplan'"""
        # Set user to pro tier
        requests.post(
            f"{BASE_URL}/api/metering/set-tier",
            json={"user_id": "test_pro_access", "tier": "pro"}
        )
        
        # Check access
        response = requests.post(
            f"{BASE_URL}/api/metering/check-access",
            json={"user_id": "test_pro_access", "feature": "business_bizplan"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["allowed"] == True
        print(f"✓ Pro user allowed for business_bizplan")


# ═══════════════════════════════════════════════════════════════════════════════
# LOG USAGE TESTS — Tracks usage with compute_level and cost_usd calculation
# ═══════════════════════════════════════════════════════════════════════════════

class TestLogUsage:
    """Test POST /api/metering/log endpoint"""
    
    def test_log_with_compute_level_calculates_cost(self):
        """POST /log with compute_level='max' should show cost_usd = minutes * 0.75"""
        response = requests.post(
            f"{BASE_URL}/api/metering/log",
            json={
                "user_id": "test_cost_calc",
                "action": "chat_max",
                "compute_minutes": 10,
                "compute_level": "max"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "cost_usd" in data, "Missing cost_usd in response"
        expected_cost = 10 * 0.75  # 10 minutes * $0.75/min
        assert data["cost_usd"] == expected_cost, f"Expected cost ${expected_cost}, got ${data['cost_usd']}"
        
        print(f"✓ 10 min @ max level = ${data['cost_usd']}")
    
    def test_log_with_mini_compute_level(self):
        """POST /log with compute_level='mini' should show cost_usd = minutes * 0.05"""
        response = requests.post(
            f"{BASE_URL}/api/metering/log",
            json={
                "user_id": "test_mini_cost",
                "action": "chat_mini",
                "compute_minutes": 20,
                "compute_level": "mini"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        expected_cost = 20 * 0.05  # 20 minutes * $0.05/min
        assert data["cost_usd"] == expected_cost, f"Expected cost ${expected_cost}, got ${data['cost_usd']}"
        
        print(f"✓ 20 min @ mini level = ${data['cost_usd']}")
    
    def test_log_returns_compute_level(self):
        """Log response should include compute_level"""
        response = requests.post(
            f"{BASE_URL}/api/metering/log",
            json={
                "user_id": "test_level_return",
                "action": "chat",
                "compute_minutes": 5,
                "compute_level": "pro"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "compute_level" in data, "Missing compute_level in response"
        assert data["compute_level"] == "pro"
        
        print(f"✓ Log returns compute_level: {data['compute_level']}")


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD TESTS — Full dashboard with cost, overage, action breakdown
# ═══════════════════════════════════════════════════════════════════════════════

class TestDashboard:
    """Test GET /api/metering/dashboard endpoint"""
    
    def test_dashboard_returns_full_data(self):
        """Dashboard should return cost, overage, action breakdown"""
        response = requests.get(f"{BASE_URL}/api/metering/dashboard?user_id=test_dashboard")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify all required fields
        required_fields = ["user_id", "tier", "tier_name", "tier_color", "compute", "cost", "overage", "rate_limit", "action_breakdown"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Verify compute structure
        assert "used" in data["compute"]
        assert "limit" in data["compute"]
        assert "remaining" in data["compute"]
        assert "cap_type" in data["compute"]
        
        # Verify overage structure
        assert "minutes" in data["overage"]
        assert "cost" in data["overage"]
        assert "allowed" in data["overage"]
        
        print(f"✓ Dashboard returns all required fields")
    
    def test_dashboard_shows_price_monthly(self):
        """Dashboard should include price_monthly for the tier"""
        response = requests.get(f"{BASE_URL}/api/metering/dashboard?user_id=anonymous")
        data = response.json()
        
        assert "price_monthly" in data, "Missing price_monthly in dashboard"
        print(f"✓ Dashboard shows price_monthly: ${data['price_monthly']}")


# ═══════════════════════════════════════════════════════════════════════════════
# HARD/SOFT CAP LOGIC TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCapLogic:
    """Test hard cap (Free/Starter) vs soft cap (Pro/Teams) logic"""
    
    def test_hard_cap_returns_429_when_exhausted(self):
        """Free/Starter should return 429 when compute exhausted"""
        user_id = "test_hard_cap"
        
        # Set to free tier (100 min limit, hard cap)
        requests.post(
            f"{BASE_URL}/api/metering/set-tier",
            json={"user_id": user_id, "tier": "free"}
        )
        
        # Log 110 minutes to exceed limit
        for i in range(11):
            requests.post(
                f"{BASE_URL}/api/metering/log",
                json={"user_id": user_id, "action": "chat", "compute_minutes": 10}
            )
        
        # Check access - should be blocked with 429
        response = requests.post(
            f"{BASE_URL}/api/metering/check-access",
            json={"user_id": user_id, "feature": "search_basic"}
        )
        
        # Hard cap should block with 429
        assert response.status_code == 429, f"Expected 429 for hard cap, got {response.status_code}"
        
        data = response.json()
        assert data["allowed"] == False
        assert "compute_budget" in data.get("reason", "")
        
        print(f"✓ Hard cap returns 429 when exhausted")
    
    def test_soft_cap_allows_overage(self):
        """Pro/Teams should allow overage (returns overage: true in check)"""
        user_id = "test_soft_cap"
        
        # Set to pro tier (2000 min limit, soft cap)
        requests.post(
            f"{BASE_URL}/api/metering/set-tier",
            json={"user_id": user_id, "tier": "pro"}
        )
        
        # Log 2100 minutes to exceed limit
        for i in range(21):
            requests.post(
                f"{BASE_URL}/api/metering/log",
                json={"user_id": user_id, "action": "chat", "compute_minutes": 100}
            )
        
        # Check access - should still be allowed with overage flag
        response = requests.post(
            f"{BASE_URL}/api/metering/check-access",
            json={"user_id": user_id, "feature": "search_basic"}
        )
        
        # Soft cap should allow with overage flag
        assert response.status_code == 200, f"Expected 200 for soft cap, got {response.status_code}"
        
        data = response.json()
        assert data["allowed"] == True
        assert data.get("overage", False) == True, "Expected overage: true for soft cap"
        
        print(f"✓ Soft cap allows overage (overage: true)")


# ═══════════════════════════════════════════════════════════════════════════════
# FORMATION PRODUCTS TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestFormationProducts:
    """Test formation products in tier-info response"""
    
    def test_tier_info_includes_formation_products(self):
        """tier-info should include formation_products with Stripe IDs"""
        response = requests.get(f"{BASE_URL}/api/metering/tier-info")
        data = response.json()
        
        assert "formation_products" in data, "Missing formation_products in tier-info"
        
        formation = data["formation_products"]
        expected_products = ["basic_llc", "deluxe_llc", "complete_llc", "basic_corp", "deluxe_corp", "complete_corp", "registered_agent", "annual_report"]
        
        for product in expected_products:
            assert product in formation, f"Missing formation product: {product}"
            assert "price_id" in formation[product], f"Missing price_id for {product}"
            assert "price" in formation[product], f"Missing price for {product}"
        
        print(f"✓ Formation products present: {list(formation.keys())}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
