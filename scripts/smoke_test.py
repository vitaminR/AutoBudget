import requests
import sys

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000"
ENDPOINTS_TO_TEST = [
    "/",
    "/bills",
    "/debts/snowball",
    "/payperiods/17/summary",
    "/gamification/status",
    "/gamification/tasks",
]
# Simulate a request from the frontend to test CORS
HEADERS = {
    "Origin": "http://localhost:3000"
}

def run_smoke_tests():
    """
    Runs a series of requests to the backend to ensure it's connected and responsive.
    """
    print("--- Running Backend Smoke Tests ---")
    failures = 0
    
    for endpoint in ENDPOINTS_TO_TEST:
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url, headers=HEADERS, timeout=5)
            if response.status_code == 200:
                print(f"[PASS] {url} -> Status: {response.status_code}")
            else:
                print(f"[FAIL] {url} -> Status: {response.status_code}")
                failures += 1
        except requests.exceptions.RequestException as e:
            print(f"[FAIL] {url} -> Error: {e}")
            failures += 1
            
    print("--- Smoke Tests Complete ---")
    if failures > 0:
        print(f"\nResult: {failures} test(s) failed. The backend is not connected or responding correctly.")
        sys.exit(1)
    else:
        print("\nResult: All tests passed. Backend is connected and responding correctly.")
        sys.exit(0)

if __name__ == "__main__":
    run_smoke_tests()
