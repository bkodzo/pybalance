"""
Simple test script to verify load balancer is working.
"""

import requests
import time
from collections import Counter


def test_load_balancer(url="http://localhost:8080", num_requests=30):
    """Test the load balancer by making multiple requests."""
    print(f"Testing load balancer at {url}")
    print(f"Making {num_requests} requests...\n")
    
    responses = []
    start_time = time.time()
    
    for i in range(num_requests):
        try:
            response = requests.get(url, timeout=5)
            # I extract which backend handled the request based on response format
            responses.append(response.status_code)
            if i % 5 == 0:
                print(f"Request {i+1}: Status {response.status_code}")
        except Exception as e:
            print(f"Request {i+1} failed: {e}")
            responses.append("ERROR")
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*50}")
    print(f"Test completed in {elapsed:.2f} seconds")
    print(f"Total requests: {num_requests}")
    print(f"Status code distribution:")
    status_counts = Counter(responses)
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    print(f"{'='*50}")


if __name__ == "__main__":
    test_load_balancer()

