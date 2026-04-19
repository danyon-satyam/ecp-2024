"""
Locust load test file for the Student Sentiment Analysis API.

Locust simulates real users hitting your API concurrently.
Each Locust user follows the behaviour defined in the task methods.

How it works:
  - You define a User class with task methods
  - Each @task represents an action a real user might take
  - The weight= parameter controls how often each task runs
    (weight=3 means this task runs 3x more often than weight=1)
  - Locust spawns N virtual users and each runs tasks continuously

Running the load test:
  1. Start your API server first:
     python scripts/start_server.py --workers 4

  2. In a SEPARATE terminal, run Locust:
     locust -f tests/load/locustfile.py --host=http://127.0.0.1:8000

  3. Open http://localhost:8089 in your browser
     - Set number of users (start with 50, then 100, then 200)
     - Set spawn rate (users added per second, use 10)
     - Click Start

  4. Watch the dashboard:
     - RPS (requests per second) — how many requests per second
     - Response time — average, median, 95th percentile
     - Failure rate — % of requests that failed
     - Number of users — current concurrent user count

Target metrics for Pramit's demo:
  - 100 concurrent users
  - Average response time < 200ms
  - Failure rate < 1%
  - RPS > 50
"""
import random
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner


# Sample data for realistic load test requests
GENDERS = ["Male", "Female", "Other"]
ACADEMIC_OPTIONS = ["Excellent", "Good", "Satisfactory", "Bad"]
EMOTIONAL_OPTIONS = ["Happy", "Glad", "Neutral", "Sad", "Angry"]
DEPARTMENTS = ["CS", "EC", "ME", "CE", "IT", "EE"]


def generate_feedback_payload() -> dict:
    """
    Generate a realistic student feedback payload for load testing.

    Returns a random but valid feedback record that passes all
    Pydantic validation rules — simulating real student submissions.
    """
    dept = random.choice(DEPARTMENTS)
    year = random.randint(2020, 2024)
    num = random.randint(1, 120)

    return {
        "roll_number": f"{dept}{year}{num:03d}",
        "gender": random.choice(GENDERS),
        "age": random.randint(18, 25),
        "study_hours_per_day": random.randint(2, 10),
        "attendance_percentage": random.randint(50, 100),
        "active_backlogs": random.choices([0, 1, 2, 3], weights=[60, 20, 12, 8])[0],
        "academic_feedback": random.choice(ACADEMIC_OPTIONS),
        "emotional_feedback": random.choice(EMOTIONAL_OPTIONS),
    }


class StudentAPIUser(HttpUser):
    """
    Simulates a user of the Student Sentiment API.

    wait_time = between(0.5, 2.0) means each virtual user waits
    0.5 to 2 seconds between tasks — simulating realistic human
    interaction patterns rather than hammering the API instantly.

    In a real university scenario:
      - Most traffic is READ (viewing dashboards, getting reports)
      - Some traffic is WRITE (submitting new feedback)
      - Occasional traffic is analytics (generating charts)
    The task weights below reflect this pattern.
    """

    wait_time = between(0.5, 2.0)

    def on_start(self) -> None:
        """
        Called when a virtual user starts.

        Uses a small random delay before the initial POST to avoid
        thundering herd — all 100 users trying to write simultaneously
        at spawn time overwhelms even a healthy connection pool.
        """
        import time
        import random
        # Stagger startup writes — spread over 3 seconds
        time.sleep(random.uniform(0, 3.0))

        payload = generate_feedback_payload()
        response = self.client.post(
            "/api/v1/feedback",
            json=payload,
            name="/api/v1/feedback [POST - setup]",
        )
        if response.status_code == 201:
            data = response.json()
            self.created_id = data.get("id", 1)
        else:
            # Fallback — use ID 1 which seed data guarantees exists
            self.created_id = 1

    @task(3)
    def get_all_feedback(self) -> None:
        """
        GET all feedback records — simulates dashboard loading.

        weight=3: this is the most common operation (3x more frequent
        than submitting feedback). University admins check the dashboard
        far more often than students submit new feedback.
        """
        self.client.get(
            "/api/v1/feedback?limit=50",
            name="/api/v1/feedback [GET all]",
        )

    @task(2)
    def submit_feedback(self) -> None:
        """
        POST new student feedback — simulates student submission.

        weight=2: second most common. Students submit feedback
        periodically, not continuously.
        """
        payload = generate_feedback_payload()
        with self.client.post(
            "/api/v1/feedback",
            json=payload,
            name="/api/v1/feedback [POST]",
            catch_response=True,
        ) as response:
            if response.status_code == 201:
                response.success()
                data = response.json()
                # Store the new ID for subsequent GET requests
                self.created_id = data.get("id", self.created_id)
            else:
                response.failure(
                    f"Expected 201, got {response.status_code}: {response.text}"
                )

    @task(2)
    def get_feedback_by_id(self) -> None:
        """
        GET a specific feedback record by ID.

        weight=2: University staff often look up specific students.
        """
        self.client.get(
            f"/api/v1/feedback/{self.created_id}",
            name="/api/v1/feedback/{id} [GET one]",
        )

    @task(2)
    def get_analytics_summary(self) -> None:
        """
        GET analytics summary — simulates dashboard widget loading.

        weight=2: Analytics are checked frequently by administrators.
        """
        self.client.get(
            "/api/v1/analytics/summary",
            name="/api/v1/analytics/summary [GET]",
        )

    @task(1)
    def get_at_risk_students(self) -> None:
        """
        GET at-risk students — simulates counsellor checking their list.

        weight=1: Less frequent — counsellors check this daily, not per minute.
        """
        self.client.get(
            "/api/v1/analytics/at-risk",
            name="/api/v1/analytics/at-risk [GET]",
        )

    @task(1)
    def get_sentiment_chart(self) -> None:
        """
        GET sentiment bar chart — simulates dashboard chart loading.

        weight=1: Charts load when the dashboard opens — less frequent
        than data requests.
        """
        self.client.get(
            "/api/v1/visualisations/sentiment-bar",
            name="/api/v1/visualisations/sentiment-bar [GET]",
        )

    @task(1)
    def health_check(self) -> None:
        """
        GET health endpoint — simulates monitoring system pings.

        weight=1: Monitoring tools check health every few seconds.
        """
        self.client.get(
            "/health",
            name="/health [GET]",
        )


class AdminUser(HttpUser):
    """
    Simulates an administrator doing bulk operations and analytics.

    Admins do heavier operations less frequently than regular users.
    wait_time is longer — admins spend time reading reports between actions.
    """

    wait_time = between(2.0, 5.0)
    weight = 1  # 1 admin for every 9 regular users

    def on_start(self) -> None:
        """
        Submit initial record for admin user.

        Staggered delay prevents thundering herd at spawn time.
        """
        import time
        import random
        time.sleep(random.uniform(0, 3.0))

        payload = generate_feedback_payload()
        self.client.post("/api/v1/feedback", json=payload)

    @task(3)
    def get_trends_analytics(self) -> None:
        """Admin frequently checks trend analytics."""
        self.client.get(
            "/api/v1/analytics/trends",
            name="/api/v1/analytics/trends [GET]",
        )

    @task(2)
    def filter_by_sentiment(self) -> None:
        """Admin filters by different sentiment categories."""
        sentiment = random.choice(["Positive", "Neutral", "Negative"])
        self.client.get(
            f"/api/v1/analytics/by-sentiment?sentiment={sentiment}",
            name="/api/v1/analytics/by-sentiment [GET]",
        )

    @task(1)
    def view_multiple_charts(self) -> None:
        """Admin views multiple charts when generating reports."""
        charts = [
            "/api/v1/visualisations/sentiment-pie",
            "/api/v1/visualisations/attendance-vs-sentiment",
            "/api/v1/visualisations/gender-sentiment",
        ]
        for chart in charts:
            self.client.get(chart, name=f"{chart} [GET]")