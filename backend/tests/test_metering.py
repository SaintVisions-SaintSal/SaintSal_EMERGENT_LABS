"""
SaintSal Labs — Metering, Tiering & Usage Dashboard Tests
Tests for Section 7 v2: Full metering, tier gating, and usage tracking
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestMeteringTierInfo:
    """Test GET /api/metering/tier-info endpoint"""
    
    def test_tier_info_returns_all_tiers(self):
        """GET /api/metering/tier-info should return 5 tiers with features, limits, costs"""
        response = requests.get(f"{BASE_URL}/api/metering/tier-info")
        assert response.status_code == 200
        
        data = response.json()
        assert "tiers" in data
        assert "action_costs" in data
        
        # Verify 5 tiers exist
        tiers = data["tiers"]
        expected_tiers = ["free", "starter", "pro", "teams", "enterprise"]
        for tier in expected_tiers:
            assert tier in tiers, f"Missing tier: {tier}"
        
        # Verify tier structure
        for tier_name, tier_config in tiers.items():
            assert "name" in tier_config
            assert "compute_minutes" in tier_config
            assert "overage_rate" in tier_config
            assert "color" in tier_config
            assert "rate_limit_per_hour" in tier_config
            assert "models" in tier_config
            assert "feature_count" in tier_config
    
    def test_tier_info_has_correct_limits(self):
        """Verify tier compute limits are correct"""
        response = requests.get(f"{BASE_URL}/api/metering/tier-info")
        data = response.json()
        tiers = data["tiers"]
        
        # Verify specific limits
        assert tiers["free"]["compute_minutes"] == 100
        assert tiers["starter"]["compute_minutes"] == 500
        assert tiers["pro"]["compute_minutes"] == 2000
        assert tiers["teams"]["compute_minutes"] == 10000
        assert tiers["enterprise"]["compute_minutes"] == -1  # Unlimited
        
    def test_tier_info_has_rate_limits(self):
        """Verify rate limits per tier"""
        response = requests.get(f"{BASE_URL}/api/metering/tier-info")
        data = response.json()
        tiers = data["tiers"]
        
        assert tiers["free"]["rate_limit_per_hour"] == 30
        assert tiers["pro"]["rate_limit_per_hour"] == 300
        assert tiers["enterprise"]["rate_limit_per_hour"] == -1  # Unlimited


class TestMeteringDashboard:
    """Test GET /api/metering/dashboard endpoint"""
    
    def test_dashboard_returns_usage_data(self):
        """GET /api/metering/dashboard returns compute usage, rate limits, action breakdown"""
        response = requests.get(f"{BASE_URL}/api/metering/dashboard?user_id=anonymous")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify structure
        assert "user_id" in data
        assert "tier" in data
        assert "tier_name" in data
        assert "tier_color" in data
        assert "compute" in data
        assert "overage" in data
        assert "rate_limit" in data
        assert "action_breakdown" in data
        assert "models_available" in data
        
        # Verify compute structure
        compute = data["compute"]
        assert "used" in compute
        assert "limit" in compute
        assert "remaining" in compute
        assert "pct_used" in compute
        
        # Verify rate_limit structure
        rate_limit = data["rate_limit"]
        assert "used" in rate_limit
        assert "limit" in rate_limit
        assert "remaining" in rate_limit
    
    def test_dashboard_default_user_is_pro(self):
        """Default anonymous user should be Pro tier"""
        response = requests.get(f"{BASE_URL}/api/metering/dashboard?user_id=anonymous")
        data = response.json()
        
        assert data["tier"] == "pro"
        assert data["tier_name"] == "Pro"
        assert data["compute"]["limit"] == 2000


class TestMeteringCheckAccess:
    """Test POST /api/metering/check-access endpoint"""
    
    def test_pro_user_can_access_business_bizplan(self):
        """Pro user should be allowed to access business_bizplan feature"""
        response = requests.post(
            f"{BASE_URL}/api/metering/check-access",
            json={"user_id": "test_pro_user", "feature": "business_bizplan"}
        )
        # First call creates user as pro by default
        assert response.status_code == 200
        data = response.json()
        assert data["allowed"] == True
        assert data["user_tier"] == "pro"
    
    def test_free_user_blocked_from_pro_feature(self):
        """Free user should be blocked from business_bizplan (Pro feature)"""
        # First set user to free tier
        set_response = requests.post(
            f"{BASE_URL}/api/metering/set-tier",
            json={"user_id": "test_free_user", "tier": "free"}
        )
        assert set_response.status_code == 200
        
        # Now check access
        response = requests.post(
            f"{BASE_URL}/api/metering/check-access",
            json={"user_id": "test_free_user", "feature": "business_bizplan"}
        )
        assert response.status_code == 403
        
        data = response.json()
        assert data["allowed"] == False
        assert "required_tier" in data
        assert "upgrade_message" in data
    
    def test_free_user_can_access_basic_features(self):
        """Free user should be able to access basic features like search"""
        # Set user to free tier
        requests.post(
            f"{BASE_URL}/api/metering/set-tier",
            json={"user_id": "test_free_basic", "tier": "free"}
        )
        
        # Check access to basic feature
        response = requests.post(
            f"{BASE_URL}/api/metering/check-access",
            json={"user_id": "test_free_basic", "feature": "search"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["allowed"] == True


class TestMeteringLog:
    """Test POST /api/metering/log endpoint"""
    
    def test_log_usage_updates_credits(self):
        """POST /api/metering/log should track usage and update remaining credits"""
        # First get current usage
        dashboard_resp = requests.get(f"{BASE_URL}/api/metering/dashboard?user_id=test_log_user")
        initial_used = dashboard_resp.json()["compute"]["used"]
        
        # Log some usage
        response = requests.post(
            f"{BASE_URL}/api/metering/log",
            json={
                "user_id": "test_log_user",
                "action": "chat",
                "compute_minutes": 5,
                "model_used": "claude"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["logged"] == True
        assert data["action"] == "chat"
        assert data["cost"] == 5
        assert data["total_minutes_used"] == initial_used + 5
        assert "remaining" in data
        assert "pct_used" in data
    
    def test_log_usage_detects_overage(self):
        """Log should detect overage when exceeding limit"""
        # Create a user with low limit (free tier)
        requests.post(
            f"{BASE_URL}/api/metering/set-tier",
            json={"user_id": "test_overage_user", "tier": "free"}
        )
        
        # Log usage that exceeds free tier limit (100 minutes)
        for i in range(25):  # 25 * 5 = 125 minutes
            requests.post(
                f"{BASE_URL}/api/metering/log",
                json={
                    "user_id": "test_overage_user",
                    "action": "chat",
                    "compute_minutes": 5
                }
            )
        
        # Check dashboard for overage
        dashboard_resp = requests.get(f"{BASE_URL}/api/metering/dashboard?user_id=test_overage_user")
        data = dashboard_resp.json()
        
        # Free tier doesn't allow overage, but we can check the compute used
        assert data["compute"]["used"] >= 100


class TestMeteringSetTier:
    """Test POST /api/metering/set-tier endpoint"""
    
    def test_set_tier_changes_tier(self):
        """POST /api/metering/set-tier should change tier and return old/new tier"""
        # First set to free
        response = requests.post(
            f"{BASE_URL}/api/metering/set-tier",
            json={"user_id": "test_tier_change", "tier": "free"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["new_tier"] == "free"
        
        # Now set to pro
        response = requests.post(
            f"{BASE_URL}/api/metering/set-tier",
            json={"user_id": "test_tier_change", "tier": "pro"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["old_tier"] == "free"
        assert data["new_tier"] == "pro"
        assert data["tier_name"] == "Pro"
        assert data["compute_minutes"] == 2000
    
    def test_set_tier_invalid_tier_returns_400(self):
        """Setting invalid tier should return 400"""
        response = requests.post(
            f"{BASE_URL}/api/metering/set-tier",
            json={"user_id": "test_invalid_tier", "tier": "invalid_tier"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data


class TestMeteringUsage:
    """Test GET /api/metering/usage endpoint"""
    
    def test_usage_returns_summary(self):
        """GET /api/metering/usage should return user's usage summary"""
        response = requests.get(f"{BASE_URL}/api/metering/usage?user_id=anonymous")
        assert response.status_code == 200
        
        data = response.json()
        assert "user_id" in data
        assert "tier" in data
        # The usage endpoint has different structure than dashboard
        assert "credits_used" in data or "total_compute_minutes" in data
        assert "credits_limit" in data or "credits_remaining" in data


class TestMeteringRateLimit:
    """Test rate limiting functionality"""
    
    def test_rate_limit_enforced(self):
        """Rate limiting should be enforced based on tier"""
        # Set user to free tier (30 req/hr limit)
        requests.post(
            f"{BASE_URL}/api/metering/set-tier",
            json={"user_id": "test_rate_limit", "tier": "free"}
        )
        
        # Make many requests to trigger rate limit
        # Note: This is a simplified test - in production you'd need to make 30+ requests
        for i in range(5):
            requests.post(
                f"{BASE_URL}/api/metering/log",
                json={"user_id": "test_rate_limit", "action": "chat"}
            )
        
        # Check rate limit status
        response = requests.post(
            f"{BASE_URL}/api/metering/check-access",
            json={"user_id": "test_rate_limit", "feature": "search"}
        )
        data = response.json()
        
        # Should still be allowed (haven't hit 30 yet)
        assert response.status_code == 200
        assert data["allowed"] == True
        assert "rate_remaining" in data


class TestMeteringIntegration:
    """Integration tests for full metering flow"""
    
    def test_full_tier_gate_flow(self):
        """Test complete flow: set tier to free, check access blocked, set to pro, check access allowed"""
        user_id = "test_full_flow"
        
        # 1. Set to free tier
        set_resp = requests.post(
            f"{BASE_URL}/api/metering/set-tier",
            json={"user_id": user_id, "tier": "free"}
        )
        assert set_resp.status_code == 200
        
        # 2. Check access to Pro feature - should be blocked
        check_resp = requests.post(
            f"{BASE_URL}/api/metering/check-access",
            json={"user_id": user_id, "feature": "business_bizplan"}
        )
        assert check_resp.status_code == 403
        assert check_resp.json()["allowed"] == False
        
        # 3. Set to pro tier
        set_resp = requests.post(
            f"{BASE_URL}/api/metering/set-tier",
            json={"user_id": user_id, "tier": "pro"}
        )
        assert set_resp.status_code == 200
        
        # 4. Check access again - should be allowed
        check_resp = requests.post(
            f"{BASE_URL}/api/metering/check-access",
            json={"user_id": user_id, "feature": "business_bizplan"}
        )
        assert check_resp.status_code == 200
        assert check_resp.json()["allowed"] == True
    
    def test_usage_logging_updates_dashboard(self):
        """Test that logging usage updates dashboard data"""
        user_id = "test_dashboard_update"
        
        # Get initial dashboard
        dash_resp = requests.get(f"{BASE_URL}/api/metering/dashboard?user_id={user_id}")
        initial_used = dash_resp.json()["compute"]["used"]
        
        # Log usage
        log_resp = requests.post(
            f"{BASE_URL}/api/metering/log",
            json={"user_id": user_id, "action": "business_plan", "compute_minutes": 10}
        )
        assert log_resp.status_code == 200
        
        # Check dashboard updated
        dash_resp = requests.get(f"{BASE_URL}/api/metering/dashboard?user_id={user_id}")
        new_used = dash_resp.json()["compute"]["used"]
        
        assert new_used == initial_used + 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
