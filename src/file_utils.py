import os
import urllib.request
from typing import Dict, Optional
from pathlib import Path
import sys


class FileUtils:
    """Utility class for handling file operations and progress tracking."""

    def download_file(self, url: str, output_path: str) -> bool:
        """
        Download a file from a URL to a specified path.

        Args:
            url: The URL to download from
            output_path: The path to save the file to

        Returns:
            bool: True if download was successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            print(f"Downloading to: {output_path}")
            with urllib.request.urlopen(url) as response:
                with open(output_path, "wb") as out_file:
                    out_file.write(response.read())
            return True

        except Exception as e:
            print(f"ERROR: Failed to download file: {str(e)}")
            return False

    def get_output_path(self, url: str, output_prefix: str) -> str:
        """
        Generate the output path for a downloaded file.

        Args:
            url: The download URL
            output_prefix: The prefix for the output path

        Returns:
            str: The complete output path

        Self contained formats like .glb .usdz are in numbered folders.
        Non self-contained formats like .obj are not in numbered folders and zipped e.g. .obj.zip

        a) Example URL with numbered folder pattern

        Input URL
        https://example.com/models/1_usdz/model.usdz

        Output: output/model_1.usdz

        b) Example URL without numbered folder pattern

        Input URL
        https://example.com/models/model.usdz

        Output: output/model_0.usdz

        - default "0" is used if no numbered folder pattern is found

        b.1) Zipped Output

        Input URL
        https://example.com/models/model.obj.zip

        Output: output/model_0.obj.zip

        """
        # Get the file path part before the query parameters
        url_path = url.split("?")[0]

        # Get just the filename part
        filename = url_path.split("/")[-1]

        # Initialize folder_number as "0" by default
        folder_number = "0"

        # Check if there's a numbered folder pattern (e.g., "1_usdz")
        folder_part = url_path.split("/")[-2]
        if "_" in folder_part:
            folder_number = folder_part.split("_")[0]

        # Get the full extension by repeatedly using splitext
        extension = ""
        while True:
            filename, ext = os.path.splitext(filename)
            if not ext:
                break
            extension = ext + extension

        # Construct the final filename
        final_filename = f"_{folder_number}{extension}"

        return output_prefix + final_filename

    def display_progress(self, progress: int, step: str = "") -> None:
        """
        Display a progress bar with optional processing step.

        Args:
            progress: Progress percentage (0-100)
            step: Current processing step description
        """
        bar = self._make_progress_bar(progress)
        step_info = f"  |  {step}" if step else ""
        if step_info:
            step_info = step_info + " " * (45 - len(step_info))

        sys.stdout.write(f"\rProgress: {bar} {progress}%{step_info}")
        sys.stdout.flush()

        if progress == 100:
            print()  # New line when complete

    def _make_progress_bar(self, progress: int, width: int = 20) -> str:
        """
        Create a text-based progress bar.

        Args:
            progress: Progress percentage (0-100)
            width: Width of the progress bar in characters

        Returns:
            str: The progress bar string
        """
        filled = int(width * progress / 100)
        bar = "[" + "#" * filled + "_" * (width - filled) + "]"
        return bar
