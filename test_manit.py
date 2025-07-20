import requests
import json

def test_manit_functionality():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing MANIT Transaction Status Updates")
    print("=" * 50)
    
    # Test 1: MANIT Login
    print("\n1️⃣ Testing MANIT login...")
    login_data = {
        "username": "manit",
        "password": "bhopal123",
        "dashboard_type": "manit"
    }
    
    try:
        response = requests.post(f"{base_url}/admin/login/", json=login_data)
        if response.status_code == 200:
            login_response = response.json()
            access_token = login_response.get('access_token')
            print("✅ MANIT login successful")
            print(f"   Token: {access_token[:20]}...")
        else:
            print(f"❌ MANIT login failed: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ MANIT login error: {e}")
        return
    
    # Test 2: Get MANIT data
    print("\n2️⃣ Testing MANIT data endpoint...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{base_url}/manit/data/", headers=headers)
        if response.status_code == 200:
            manit_data = response.json()
            transactions = manit_data.get('transactions', [])
            print(f"✅ MANIT data loaded successfully")
            print(f"   Found {len(transactions)} transactions")
            
            if transactions:
                test_transaction = transactions[0]
                transaction_id = test_transaction.get('transaction_id')
                current_status = test_transaction.get('status', 'unknown')
                print(f"   Test transaction ID: {transaction_id}")
                print(f"   Current status: {current_status}")
            else:
                print("   ⚠️ No transactions found to test with")
                return
        else:
            print(f"❌ Failed to get MANIT data: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ MANIT data error: {e}")
        return
    
    # Test 3: Update transaction status to "received"
    print("\n3️⃣ Testing status update to 'received'...")
    status_data = {
        "transaction_id": transaction_id,
        "status": "received"
    }
    
    try:
        response = requests.post(f"{base_url}/manit/update-status/", 
                               json=status_data, 
                               headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ Status update to 'received' successful!")
            print(f"   Transaction ID: {result['transaction_id']}")
            print(f"   New Status: {result['new_status']}")
            print(f"   Updated by: {result['updated_by']}")
        else:
            print(f"❌ Status update failed: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Status update error: {e}")
        return
    
    # Test 4: Update transaction status to "verified"
    print("\n4️⃣ Testing status update to 'verified'...")
    status_data = {
        "transaction_id": transaction_id,
        "status": "verified"
    }
    
    try:
        response = requests.post(f"{base_url}/manit/update-status/", 
                               json=status_data, 
                               headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ Status update to 'verified' successful!")
            print(f"   Transaction ID: {result['transaction_id']}")
            print(f"   New Status: {result['new_status']}")
            print(f"   Updated by: {result['updated_by']}")
        else:
            print(f"❌ Status update failed: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Status update error: {e}")
        return
    
    # Test 5: Verify the changes by getting data again
    print("\n5️⃣ Verifying the changes...")
    try:
        response = requests.get(f"{base_url}/manit/data/", headers=headers)
        if response.status_code == 200:
            manit_data = response.json()
            transactions = manit_data.get('transactions', [])
            
            for txn in transactions:
                if txn.get('transaction_id') == transaction_id:
                    status = txn.get('status', 'unknown')
                    print(f"✅ Transaction {transaction_id} final status: {status}")
                    break
        else:
            print(f"❌ Failed to verify: {response.status_code}")
    except Exception as e:
        print(f"❌ Verification error: {e}")
    
    print("\n🎉 MANIT testing completed!")

if __name__ == "__main__":
    test_manit_functionality() 