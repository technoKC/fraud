import requests
import json

def test_api_endpoints():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing FraudShield API Endpoints")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    print("\n1️⃣ Testing basic connectivity...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Backend is accessible")
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    # Test 2: Login
    print("\n2️⃣ Testing login...")
    login_data = {
        "username": "centralbank",
        "password": "admin123",
        "dashboard_type": "centralbank"
    }
    
    try:
        response = requests.post(f"{base_url}/admin/login/", json=login_data)
        if response.status_code == 200:
            login_response = response.json()
            access_token = login_response.get('access_token')
            print("✅ Login successful")
            print(f"   Token: {access_token[:20]}...")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test 3: Get admin data
    print("\n3️⃣ Testing admin data endpoint...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{base_url}/admin/data/", headers=headers)
        if response.status_code == 200:
            admin_data = response.json()
            fraud_transactions = admin_data.get('fraud_transactions', [])
            print(f"✅ Admin data loaded successfully")
            print(f"   Found {len(fraud_transactions)} fraud transactions")
            
            if fraud_transactions:
                test_transaction = fraud_transactions[0]
                transaction_id = test_transaction.get('transaction_id')
                print(f"   Test transaction ID: {transaction_id}")
            else:
                print("   ⚠️ No fraud transactions found to test with")
                return
        else:
            print(f"❌ Failed to get admin data: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Admin data error: {e}")
        return
    
    # Test 4: Transaction action
    print("\n4️⃣ Testing transaction action...")
    action_data = {
        "transaction_id": transaction_id,
        "action": "blocked"
    }
    
    try:
        response = requests.post(f"{base_url}/admin/transaction-action/", 
                               json=action_data, 
                               headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ Transaction action successful!")
            print(f"   Transaction ID: {result['transaction_id']}")
            print(f"   Action: {result['action']}")
            print(f"   Updated by: {result['updated_by']}")
        else:
            print(f"❌ Transaction action failed: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Transaction action error: {e}")
        return
    
    # Test 5: Verify the change
    print("\n5️⃣ Verifying the change...")
    try:
        response = requests.get(f"{base_url}/admin/data/", headers=headers)
        if response.status_code == 200:
            admin_data = response.json()
            fraud_transactions = admin_data.get('fraud_transactions', [])
            
            for txn in fraud_transactions:
                if txn.get('transaction_id') == transaction_id:
                    status = txn.get('status', 'unknown')
                    print(f"✅ Transaction {transaction_id} status: {status}")
                    break
        else:
            print(f"❌ Failed to verify: {response.status_code}")
    except Exception as e:
        print(f"❌ Verification error: {e}")
    
    # Test 6: MANIT login
    print("\n6️⃣ Testing MANIT login...")
    manit_login_data = {
        "username": "manit",
        "password": "bhopal123",
        "dashboard_type": "manit"
    }
    
    try:
        response = requests.post(f"{base_url}/admin/login/", json=manit_login_data)
        if response.status_code == 200:
            manit_response = response.json()
            manit_token = manit_response.get('access_token')
            print("✅ MANIT login successful")
        else:
            print(f"❌ MANIT login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ MANIT login error: {e}")
        return
    
    # Test 7: MANIT data
    print("\n7️⃣ Testing MANIT data endpoint...")
    manit_headers = {"Authorization": f"Bearer {manit_token}"}
    
    try:
        response = requests.get(f"{base_url}/manit/data/", headers=manit_headers)
        if response.status_code == 200:
            manit_data = response.json()
            print("✅ MANIT data loaded successfully")
            print(f"   Data keys: {list(manit_data.keys())}")
        else:
            print(f"❌ Failed to get MANIT data: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ MANIT data error: {e}")
    
    print("\n🎉 API testing completed!")

if __name__ == "__main__":
    test_api_endpoints() 