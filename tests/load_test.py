"""
Load testing script for PyBalance.
Simulates realistic traffic scenarios.
"""

import time
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
import statistics


class LoadTester:
    """Load testing tool for PyBalance."""
    
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.results = []
        self.errors = []
        self.server_distribution = Counter()
        self.response_times = []
    
    def make_request(self):
        """Make a single request and record results."""
        start_time = time.time()
        try:
            response = requests.get(self.base_url, timeout=10)
            elapsed = time.time() - start_time
            
            # Extract which server handled it
            server = "Unknown"
            if "Backend Server 1" in response.text:
                server = "Server 1"
            elif "Backend Server 2" in response.text:
                server = "Server 2"
            elif "Backend Server 3" in response.text:
                server = "Server 3"
            
            self.results.append({
                "status": response.status_code,
                "time": elapsed,
                "server": server
            })
            self.server_distribution[server] += 1
            self.response_times.append(elapsed)
            
            return {"status": "success", "time": elapsed, "server": server}
        except Exception as e:
            elapsed = time.time() - start_time
            self.errors.append({"error": str(e), "time": elapsed})
            return {"status": "error", "error": str(e), "time": elapsed}
    
    def run_concurrent_test(self, num_requests=100, concurrency=10):
        """Run concurrent requests test."""
        print(f"Running concurrent test: {num_requests} requests, {concurrency} concurrent")
        print("=" * 60)
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(self.make_request) for _ in range(num_requests)]
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                if completed % 10 == 0:
                    print(f"  Progress: {completed}/{num_requests} requests completed", end='\r')
        
        total_time = time.time() - start_time
        
        print(f"\n  Completed: {completed}/{num_requests} requests")
        print(f"  Total time: {total_time:.2f} seconds")
        
        return self._print_results(total_time)
    
    def run_sustained_load(self, duration=30, rate=10):
        """Run sustained load test (requests per second for duration)."""
        print(f"Running sustained load: {rate} req/sec for {duration} seconds")
        print("=" * 60)
        
        start_time = time.time()
        request_count = 0
        interval = 1.0 / rate
        
        with ThreadPoolExecutor(max_workers=rate * 2) as executor:
            while time.time() - start_time < duration:
                executor.submit(self.make_request)
                request_count += 1
                time.sleep(interval)
        
        total_time = time.time() - start_time
        print(f"  Total requests: {request_count}")
        print(f"  Actual duration: {total_time:.2f} seconds")
        print(f"  Actual rate: {request_count/total_time:.2f} req/sec")
        
        return self._print_results(total_time)
    
    def run_burst_test(self, burst_size=50):
        """Run burst test - all requests at once."""
        print(f"Running burst test: {burst_size} simultaneous requests")
        print("=" * 60)
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=burst_size) as executor:
            futures = [executor.submit(self.make_request) for _ in range(burst_size)]
            for future in as_completed(futures):
                pass
        
        total_time = time.time() - start_time
        print(f"  Burst completed in: {total_time:.2f} seconds")
        
        return self._print_results(total_time)
    
    def _print_results(self, total_time):
        """Print test results."""
        print("\nResults:")
        print("-" * 60)
        
        # Success rate
        total = len(self.results) + len(self.errors)
        success = len(self.results)
        success_rate = (success / total * 100) if total > 0 else 0
        print(f"Success rate: {success_rate:.1f}% ({success}/{total})")
        
        # Response times
        if self.response_times:
            print(f"\nResponse Times:")
            print(f"  Min: {min(self.response_times)*1000:.2f} ms")
            print(f"  Max: {max(self.response_times)*1000:.2f} ms")
            print(f"  Mean: {statistics.mean(self.response_times)*1000:.2f} ms")
            print(f"  Median: {statistics.median(self.response_times)*1000:.2f} ms")
            if len(self.response_times) > 1:
                print(f"  Std Dev: {statistics.stdev(self.response_times)*1000:.2f} ms")
        
        # Throughput
        if total_time > 0:
            throughput = total / total_time
            print(f"\nThroughput: {throughput:.2f} requests/second")
        
        # Server distribution
        print(f"\nServer Distribution:")
        total_requests = sum(self.server_distribution.values())
        for server, count in self.server_distribution.most_common():
            percentage = (count / total_requests * 100) if total_requests > 0 else 0
            print(f"  {server}: {count} requests ({percentage:.1f}%)")
        
        # Errors
        if self.errors:
            print(f"\nErrors: {len(self.errors)}")
            error_types = Counter([e.get("error", "Unknown") for e in self.errors])
            for error, count in error_types.most_common(5):
                print(f"  {error}: {count}")
        
        print("=" * 60)
        
        return {
            "total": total,
            "success": success,
            "success_rate": success_rate,
            "throughput": total / total_time if total_time > 0 else 0,
            "mean_response_time": statistics.mean(self.response_times) if self.response_times else 0,
            "server_distribution": dict(self.server_distribution)
        }


def main():
    """Run load tests."""
    import sys
    
    tester = LoadTester()
    
    print("PyBalance Load Testing")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == "concurrent":
            num_requests = int(sys.argv[2]) if len(sys.argv) > 2 else 100
            concurrency = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            tester.run_concurrent_test(num_requests, concurrency)
        
        elif test_type == "sustained":
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            rate = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            tester.run_sustained_load(duration, rate)
        
        elif test_type == "burst":
            burst_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            tester.run_burst_test(burst_size)
        
        else:
            print("Unknown test type. Use: concurrent, sustained, or burst")
    else:
        # Run all tests
        print("Running comprehensive load test suite...\n")
        
        print("Test 1: Concurrent Load (100 requests, 10 concurrent)")
        tester.run_concurrent_test(100, 10)
        print("\n")
        
        print("Test 2: Sustained Load (10 req/sec for 10 seconds)")
        tester.run_sustained_load(10, 10)
        print("\n")
        
        print("Test 3: Burst Test (50 simultaneous requests)")
        tester.run_burst_test(50)


if __name__ == "__main__":
    main()

