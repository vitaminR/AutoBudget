from fastapi.testclient import TestClient
from autobudget_backend.app import app

if __name__ == "__main__":
    c = TestClient(app)
    urls = ["/", "/payperiods/17/summary", "/debts/snowball", "/unlocks"]
    for u in urls:
        r = c.get(u)
        print(u, r.status_code, len(r.content))
    r = c.post("/reconcile", json={"transactions": [{"memo":"rent"},{"memo":"coffee"}]})
    print("/reconcile", r.status_code, r.json())
    print("/api/pay-periods", c.get("/api/pay-periods").status_code)
