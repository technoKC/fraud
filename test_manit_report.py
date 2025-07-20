import requests
import json

def test_manit_report_generation():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing MANIT Report Generation")
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
    
    # Test 2: Generate MANIT Report
    print("\n2️⃣ Testing MANIT report generation...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{base_url}/manit/generate-report/", headers=headers)
        if response.status_code == 200:
            print("✅ MANIT report generated successfully!")
            print("   Report should now have proper spacing between logo and heading")
            print("   Check the generated PDF file in the reports directory")
            
            # Check if we can get the filename from headers
            content_disposition = response.headers.get('content-disposition', '')
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')
                print(f"   Filename: {filename}")
        else:
            print(f"❌ Report generation failed: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Report generation error: {e}")
        return
    
    print("\n🎉 MANIT report testing completed!")
    print("📄 Check the generated PDF to verify logo and heading spacing is fixed")

if __name__ == "__main__":
    test_manit_report_generation() 