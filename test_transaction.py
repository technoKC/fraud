import requests
import json

# Test the transaction action functionality
def test_transaction_action():
    base_url = "http://localhost:8000"
    
    # Step 1: Login to get access token
    print("🔐 Logging in...")
    login_data = {
        "username": "centralbank",
        "password": "admin123",
        "dashboard_type": "centralbank"
    }
    
    response = requests.post(f"{base_url}/admin/login/", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return
    
    login_response = response.json()
    access_token = login_response.get('access_token')
    print(f"✅ Login successful! Token: {access_token[:20]}...")
    
    # Step 2: Get admin data to see available transactions
    print("\n📊 Getting admin data...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{base_url}/admin/data/", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get admin data: {response.status_code}")
        print(response.text)
        return
    
    admin_data = response.json()
    fraud_transactions = admin_data.get('fraud_transactions', [])
    print(f"✅ Found {len(fraud_transactions)} fraud transactions")
    
    if not fraud_transactions:
        print("❌ No fraud transactions found to test with")
        return
    
    # Step 3: Test transaction action
    test_transaction = fraud_transactions[0]
    transaction_id = test_transaction.get('transaction_id')
    
    print(f"\n🔧 Testing transaction action for: {transaction_id}")
    
    # Test blocking a transaction
    action_data = {
        "transaction_id": transaction_id,
        "action": "blocked"
    }
    
    response = requests.post(f"{base_url}/admin/transaction-action/", 
                           json=action_data, 
                           headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Transaction action successful!")
        print(f"   Transaction ID: {result['transaction_id']}")
        print(f"   Action: {result['action']}")
        print(f"   Updated by: {result['updated_by']}")
    else:
        print(f"❌ Transaction action failed: {response.status_code}")
        print(response.text)
    
    # Step 4: Verify the change by getting admin data again
    print("\n🔄 Verifying the change...")
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

if __name__ == "__main__":
    test_transaction_action() 