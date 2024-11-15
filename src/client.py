from typing import Dict, Optional, Tuple
from src.request_utils import RequestUtils
from src.file_utils import FileUtils
import time


class RapidPipelineClient:
    """Client for interacting with the RapidPipeline API."""

    def __init__(
        self, access_token: str, base_url: str = "https://api.rapidpipeline.com/api/v2/"
    ):
        self.access_token = access_token
        self.base_url = base_url
        self.request_utils = RequestUtils()
        self.file_utils = FileUtils()

    def get_upload_urls(self, file_ext: str, model_label: str) -> Optional[Dict]:
        """Get presigned URLs for uploading model files."""
        headers = self._get_auth_headers()
        payload = {"filenames": [f"rapid{file_ext}"], "model_name": model_label}

        print(f"Starting Upload for model: {model_label} ...")
        response = self.request_utils.post_json(
            f"{self.base_url}rawmodel/api-upload/start",
            headers=headers,
            payload=payload,
        )
        return response

    def upload_model(self, model_file: str, file_ext: str, upload_urls: Dict) -> bool:
        """Upload a model file and finalize the upload."""
        try:
            with open(model_file, "rb") as data_model:
                url_model = upload_urls["links"]["s3_upload_urls"]["rapid" + file_ext]
                model_id = upload_urls["id"]

                print("Uploading model file ...")
                if not self.request_utils.put_binary(url_model, data_model.read()):
                    return False

                return self._finalize_upload(model_id)
        except IOError:
            print(f'Error: cannot open model file "{model_file}"')
            return False

    def optimize_model(self, model_id: int, output_prefix: str, preset: Dict) -> int:
        """Submit and monitor an optimization job."""
        headers = self._get_auth_headers()

        # Submit optimization job
        response = self.request_utils.post_json(
            f"{self.base_url}rawmodel/optimize/{model_id}",
            headers=headers,
            payload=preset,
        )

        if not response:
            return -1

        rapid_model_id = response["id"]
        return self._wait_for_optimization(rapid_model_id, output_prefix)

    def delete_base_asset(self, asset_id: int) -> bool:
        """Delete a base asset from cloud storage."""
        print("Deleting base asset from cloud storage ...")
        return self.request_utils.delete(
            f"{self.base_url}rawmodel/{asset_id}", headers=self._get_auth_headers()
        )

    def delete_rapid_model(self, model_id: int) -> bool:
        """Delete an optimized model from cloud storage."""
        print("Deleting optimized model from cloud storage ...")
        return self.request_utils.delete(
            f"{self.base_url}rapidmodel/{model_id}", headers=self._get_auth_headers()
        )

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get headers with authentication token."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _finalize_upload(self, model_id: str) -> bool:
        """Finalize the model upload and wait for processing."""
        print("Finalizing Upload ...")
        response = self.request_utils.get_json(
            f"{self.base_url}rawmodel/{model_id}/api-upload/complete",
            headers=self._get_auth_headers(),
        )

        if not response:
            return False

        print("Waiting for model to finish analysing ...")
        return self._wait_for_processing(model_id)

    def _wait_for_processing(self, model_id: str) -> bool:
        """Wait for initial model processing to complete."""
        start_time = time.time()
        while True:
            response = self.request_utils.get_json(
                f"{self.base_url}rawmodel/{model_id}", headers=self._get_auth_headers()
            )

            if not response:
                return False

            status = response["data"]["upload_status"]
            if status == "complete":
                return True
            elif status not in ["waiting", "unzipping", "analysing"]:
                print(f"Unexpected status: {status}")
                return False

            elapsed_time = int(time.time() - start_time)
            if elapsed_time % 5 == 0:  # Print every 5 seconds
                minutes = elapsed_time // 60
                seconds = elapsed_time % 60
                time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
                print(f"Waiting for processing... ({time_str}) Status: {status}")

            time.sleep(1)

    def _wait_for_optimization(self, rapid_model_id: int, output_prefix: str) -> int:
        """Wait for optimization to complete and download results."""
        print(f"Waiting for optimization to complete for rapidmodel {rapid_model_id}")

        while True:
            response = self.request_utils.get_json(
                f"{self.base_url}rapidmodel/{rapid_model_id}",
                headers=self._get_auth_headers(),
            )

            if not response:
                return -1

            status = response["data"]["optimization_status"]
            if status == "done":
                self._handle_optimization_complete(response, output_prefix)
                return rapid_model_id
            elif status != "sent_to_queue":
                print(
                    f"Error: Unexpected status code from optimization run ({status})."
                )
                return -1

            self._update_optimization_progress(response["data"])

    def _handle_optimization_complete(self, response: Dict, output_prefix: str) -> None:
        """Handle successful optimization completion."""
        download_urls = response["data"]["downloads"]["all"]
        for file_type, url in download_urls.items():
            output_path = self.file_utils.get_output_path(url, output_prefix)
            self.file_utils.download_file(url, output_path)

    def _update_optimization_progress(self, data: Dict) -> None:
        """Update optimization progress display."""
        if "progress" in data:
            progress = data["progress"]
            step = data.get("processing_step", "")
            self.file_utils.display_progress(progress, step)
