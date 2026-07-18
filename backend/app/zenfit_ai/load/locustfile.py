"""Realistic API traffic; expensive scans are intentionally a separate low-rate task."""
import os
from locust import HttpUser,between,task

class ZenFitDailyUser(HttpUser):
    wait_time=between(15,60)
    def on_start(self):
        response=self.client.post("/auth/login",json={"email":os.environ["LOAD_EMAIL"],"password":os.environ["LOAD_PASSWORD"]})
        token=response.json().get("access_token")
        if token:self.client.headers.update({"Authorization":f"Bearer {token}"})
    @task(5)
    def dashboard(self):self.client.get("/dashboard")
    @task(2)
    def nutrition(self):self.client.get("/nutrition/today")
    @task(2)
    def recommendations(self):self.client.get("/recommendations")
    @task(1)
    def ai_health(self):self.client.get("/ai/health")
