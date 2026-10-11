import os
import random

from locust import HttpUser, between, task


FILE_ID = os.getenv("TEST_FILE_ID")


class GeospatialAPIUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(5)
    def check_health(self):
        response = self.client.get(
            "/health",
            name="GET /health",
        )

        if response.status_code != 200:
            response.failure(
                f"Health check failed: {response.status_code}"
            )

    @task(3)
    def get_file_details(self):
        if not FILE_ID:
            return

        response = self.client.get(
            f"/api/files/{FILE_ID}/",
            name="GET /api/files/{id}",
        )

        if response.status_code != 200:
            response.failure(
                f"File details failed: {response.status_code}"
            )

    @task(2)
    def get_measurements(self):
        if not FILE_ID:
            return

        response = self.client.get(
            f"/api/files/{FILE_ID}/measurements/",
            name="GET /api/files/{id}/measurements",
        )

        if response.status_code != 200:
            response.failure(
                f"Measurements failed: {response.status_code}"
            )