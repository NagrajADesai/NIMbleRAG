import urllib.request
import time

url = "http://localhost:8000/health"
max_retries = 30
for i in range(max_retries):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("✅ API is UP AND RUNNING! Response:", response.read().decode())
                break
    except Exception as e:
        print(f"Waiting for API to load NLP models... ({i+1}/{max_retries})")
        time.sleep(2)
else:
    print("❌ API failed to start in time or crashed.")
