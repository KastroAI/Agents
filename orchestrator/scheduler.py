"""GCP Cloud Scheduler job management."""

from __future__ import annotations

from google.cloud import scheduler_v1

from config.settings import settings
from shared.logger import get_logger

logger = get_logger(__name__)


class Scheduler:
    """Creates and manages Cloud Scheduler jobs for recurring tasks."""

    def __init__(self) -> None:
        """Initialise the Cloud Scheduler client."""
        self._client = scheduler_v1.CloudSchedulerClient()
        self._project_id = settings.GCP_PROJECT_ID
        self._location = "europe-west2"  # London
        self._parent = self._client.common_location_path(self._project_id, self._location)
        self._topic = settings.GCP_PUBSUB_TOPIC

    def _topic_path(self) -> str:
        """Return the fully-qualified Pub/Sub topic path.

        Returns:
            The full resource path for the configured Pub/Sub topic.
        """
        return f"projects/{self._project_id}/topics/{self._topic}"

    def create_weekly_report_job(self) -> scheduler_v1.Job:
        """Create a Cloud Scheduler job that triggers every Monday at 08:00 London time.

        The job publishes a ``weekly_report`` task to the Pub/Sub topic.

        Returns:
            The created :class:`scheduler_v1.Job`.
        """
        job = scheduler_v1.Job(
            name=f"{self._parent}/jobs/weekly-report",
            schedule="0 8 * * 1",
            time_zone="Europe/London",
            pubsub_target=scheduler_v1.PubsubTarget(
                topic_name=self._topic_path(),
                data=b'{"task_type": "weekly_report", "payload": {}}',
            ),
        )

        logger.info("Creating weekly report scheduler job")
        created = self._client.create_job(
            request=scheduler_v1.CreateJobRequest(parent=self._parent, job=job)
        )
        logger.info("Weekly report job created", extra={"job_name": created.name})
        return created

    def create_daily_sync_job(self) -> scheduler_v1.Job:
        """Create a Cloud Scheduler job that triggers daily at 03:00 for Shopify sync.

        The job publishes a ``product_sync`` task to the Pub/Sub topic.

        Returns:
            The created :class:`scheduler_v1.Job`.
        """
        job = scheduler_v1.Job(
            name=f"{self._parent}/jobs/daily-product-sync",
            schedule="0 3 * * *",
            time_zone="Europe/London",
            pubsub_target=scheduler_v1.PubsubTarget(
                topic_name=self._topic_path(),
                data=b'{"task_type": "product_sync", "payload": {}}',
            ),
        )

        logger.info("Creating daily sync scheduler job")
        created = self._client.create_job(
            request=scheduler_v1.CreateJobRequest(parent=self._parent, job=job)
        )
        logger.info("Daily sync job created", extra={"job_name": created.name})
        return created
