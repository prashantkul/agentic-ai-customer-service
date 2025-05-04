#!/usr/bin/env python3
"""
Simple test for the database implementation.
Run this file directly to test database functionality.
"""

import logging
import sys
import json
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def test_database_initialization():
    """Test database initialization."""
    from database.init_db import init_db
    try:
        init_db()
        logger.info("✅ Database initialization successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

def test_customer_retrieval():
    """Test customer retrieval."""
    from database.operations import get_customer
    try:
        customer = get_customer("123")
        if not customer:
            logger.error("❌ Customer not found")
            return False
        
        logger.info(f"✅ Customer retrieved: {customer['customer_first_name']} {customer['customer_last_name']}")
        logger.info(f"   Email: {customer['email']}")
        logger.info(f"   Loyalty points: {customer['loyalty_points']}")
        
        # Test sports profile
        if 'sports_profile' in customer:
            sports = json.loads(customer['sports_profile']['preferred_sports']) if isinstance(customer['sports_profile']['preferred_sports'], str) else customer['sports_profile']['preferred_sports']
            logger.info(f"   Preferred sports: {', '.join(sports)}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Customer retrieval failed: {e}")
        return False

def test_cart_operations():
    """Test cart operations."""
    from database.operations import access_cart_information, modify_cart
    try:
        # Get initial cart
        cart = access_cart_information("123")
        if not cart or "cart" not in cart:
            logger.error("❌ Cart not found")
            return False
        
        initial_items = len(cart["cart"])
        logger.info(f"✅ Cart retrieved with {initial_items} items")
        logger.info(f"   Subtotal: ${cart['subtotal']:.2f}")
        
        # Add an item
        result = modify_cart(
            "123", 
            [{"product_id": "TNB-003", "quantity": 2}],  # Add tennis balls
            []
        )
        
        if not result or result.get("status") != "success":
            logger.error(f"❌ Cart modification failed: {result}")
            return False
        
        logger.info("✅ Added item to cart")
        
        # Get updated cart
        updated_cart = access_cart_information("123")
        updated_items = len(updated_cart["cart"])
        
        if "TNB-003" in [item["product_id"] for item in updated_cart["cart"]]:
            logger.info("✅ Tennis balls successfully added to cart")
        else:
            logger.info("✅ Cart updated but tennis balls not found")
        
        logger.info(f"   Updated cart has {updated_items} items")
        logger.info(f"   Updated subtotal: ${updated_cart['subtotal']:.2f}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Cart operations failed: {e}")
        return False

def test_product_recommendations():
    """Test product recommendations."""
    from database.operations import get_product_recommendations
    try:
        # Get tennis recommendations
        tennis_recs = get_product_recommendations("Tennis", "123")
        if not tennis_recs or "recommendations" not in tennis_recs:
            logger.error("❌ Tennis recommendations not found")
            return False
        
        logger.info(f"✅ Found {len(tennis_recs['recommendations'])} tennis recommendations")
        for i, rec in enumerate(tennis_recs['recommendations'][:3], 1):  # Show top 3
            logger.info(f"   {i}. {rec['name']} - ${rec['price']:.2f}")
        
        # Get basketball recommendations
        basketball_recs = get_product_recommendations("Basketball", "123")
        if basketball_recs and "recommendations" in basketball_recs:
            logger.info(f"✅ Found {len(basketball_recs['recommendations'])} basketball recommendations")
        
        return True
    except Exception as e:
        logger.error(f"❌ Product recommendations failed: {e}")
        return False

def main():
    """Run all database tests."""
    logger.info("🔍 Testing database implementation...\n")
    
    tests = [
        ("Database Initialization", test_database_initialization),
        ("Customer Retrieval", test_customer_retrieval),
        ("Cart Operations", test_cart_operations),
        ("Product Recommendations", test_product_recommendations)
    ]
    
    results = []
    for name, test_func in tests:
        logger.info(f"🧪 Running {name} test...")
        success = test_func()
        results.append((name, success))
        logger.info("")  # Empty line between tests
    
    # Summary
    logger.info("📊 Test Summary:")
    passed = sum(1 for _, success in results if success)
    logger.info(f"Passed: {passed}/{len(tests)} tests")
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status}: {name}")
    
    if passed == len(tests):
        logger.info("\n🎉 All tests passed! The database implementation is working correctly.")
    else:
        logger.info("\n⚠️ Some tests failed. See the logs above for details.")

if __name__ == "__main__":
    main()