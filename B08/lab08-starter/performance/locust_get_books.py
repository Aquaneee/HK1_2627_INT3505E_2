from locust import HttpUser, task, between

class PrimaryBooksEndpointUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task
    def get_all_books(self):
        with self.client.get("/books", name="GET /books", catch_response=True) as res:
            if res.status_code != 200:
                res.failure(f"Unexpected status code: {res.status_code}")