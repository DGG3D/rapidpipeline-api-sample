import os
from typing import List, Dict
from src.client import RapidPipelineClient


class ModelProcessor:
    def __init__(self, client: RapidPipelineClient):
        self.client = client
        self.failed_optimizations = 0

    def process_models(
        self,
        model_path: str,
        presets: Dict,
        cleanup: bool = True,
        exit_on_error: bool = False,
        model_label: str = "",
    ) -> int:
        """
        Process one or more 3D models with the given presets.

        Args:
            model_path: Path to model file or directory
            presets: Dictionary of presets to apply
            cleanup: Whether to cleanup after processing
            exit_on_error: Whether to exit on optimization error
            model_label: Optional label for the model

        Returns:
            int: Number of failed optimizations
        """
        # Reset failed optimizations counter
        self.failed_optimizations = 0

        # Get list of files to process
        files_to_process = self._get_files_to_process(model_path)

        # Process each file
        for model_file in files_to_process:
            self._process_single_file(
                model_file=model_file,
                presets=presets,
                cleanup=cleanup,
                exit_on_error=exit_on_error,
                model_label=model_label,
            )

        return self.failed_optimizations

    def _get_files_to_process(self, model_path: str) -> List[str]:
        """Get list of files to process based on input path."""
        # First check if it's a base asset ID
        if model_path.endswith(".id"):
            print("\nRunning in base asset ID mode.")
            return [model_path]

        # Original directory/file logic
        if os.path.isdir(model_path):
            print("\nRunning in directory mode.")
            return [os.path.join(model_path, f) for f in os.listdir(model_path)]
        else:
            print("\nRunning in single-file mode.")
            return [model_path]

    def _process_single_file(
        self,
        model_file: str,
        presets: Dict,
        cleanup: bool,
        exit_on_error: bool,
        model_label: str,
    ) -> None:
        """Process a single model file with all presets."""
        rapid_model_ids = []
        is_base_asset_id = model_file.endswith(".id")

        # Get model_id either from base asset ID or by uploading new file
        if is_base_asset_id:
            try:
                model_id = int(
                    model_file.rsplit(".", 1)[0]
                )  # Extract number from "123.id"
                model_name = str(model_id)
                print(f"\nProcessing base asset ID: {model_id}")
            except ValueError:
                print(f"Invalid base asset ID format: {model_file}")
                self.failed_optimizations += 1
                return
        else:
            # Handle regular file upload
            model_name = os.path.splitext(os.path.basename(model_file))[0]
            file_ext = os.path.splitext(model_file)[1]
            print(f"\nProcessing model: {model_name}")

            upload_urls = self.client.get_upload_urls(
                file_ext=file_ext, model_label=model_label or model_name
            )
            if not upload_urls:
                print("Couldn't obtain signed upload URLs from server.")
                self.failed_optimizations += 1
                return

            if not self.client.upload_model(model_file, file_ext, upload_urls):
                print("Couldn't upload base asset.")
                self.failed_optimizations += 1
                return

            model_id = upload_urls["id"]

        # Process presets (common for both paths)
        for preset_name, preset in presets["presets"].items():
            rapid_model_id = self._process_preset(
                model_id=model_id,
                model_name=model_label or model_name,
                preset_name=preset_name,
                preset=preset,
                exit_on_error=exit_on_error,
            )
            if rapid_model_id != -1:
                rapid_model_ids.append(rapid_model_id)

        # Cleanup if requested (but don't delete base asset if it's a base asset ID)
        if cleanup:
            self._cleanup_assets(
                model_id, rapid_model_ids, delete_base_asset=not is_base_asset_id
            )

    def _process_preset(
        self,
        model_id: int,
        model_name: str,
        preset_name: str,
        preset: Dict,
        exit_on_error: bool,
    ) -> int:
        """Process a single preset for a model."""
        print(f'\nStarting Optimization for preset "{preset_name}"')

        output_prefix = f"output/{model_name}_{preset_name}"

        rapid_model_id = self.client.optimize_model(
            model_id=model_id, output_prefix=output_prefix, preset=preset
        )

        if rapid_model_id == -1:
            self.failed_optimizations += 1
            if exit_on_error:
                import sys

                sys.exit(2)

        return rapid_model_id

    def _cleanup_assets(
        self, model_id: int, rapid_model_ids: List[int], delete_base_asset: bool = True
    ) -> None:
        """Clean up uploaded assets and optimized results."""
        print("\nCleaning up: deleting optimized results...")
        if delete_base_asset:
            self.client.delete_base_asset(model_id)
        else:
            print(
                f"Skipping deletion of base asset (ID: {model_id}) as it was processed using base asset ID mode"
            )

        for rapid_model_id in rapid_model_ids:
            self.client.delete_rapid_model(rapid_model_id)
