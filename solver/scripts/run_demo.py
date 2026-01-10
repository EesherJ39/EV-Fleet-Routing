import json
import httpx
from evsolver.scenario import demo_request


def main():
    req = demo_request()
    with httpx.Client(timeout=30) as client:
        r = client.post("http://localhost:8000/solve", json=req.model_dump())

        # Print helpful output even on errors
        try:
            data = r.json()
        except Exception:
            print("Non-JSON response:")
            print(r.text)
            r.raise_for_status()
            return

        print(json.dumps(data, indent=2))
        r.raise_for_status()


if __name__ == "__main__":
    main()