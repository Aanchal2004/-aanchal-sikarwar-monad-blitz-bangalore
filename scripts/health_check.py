"""Quick health check script."""

import httpx

BASE = "http://localhost:8000"


def main():
    endpoints = ["/health", "/"]
    for path in endpoints:
        try:
            r = httpx.get(f"{BASE}{path}", timeout=5)
            print(f"✓ {path} → {r.status_code}")
        except Exception as e:
            print(f"✗ {path} → {e}")


if __name__ == "__main__":
    main()
