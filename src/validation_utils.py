import json
import sys
import os
sys.path.insert(0, os.path.abspath("schema/six"))
sys.path.insert(0, os.path.abspath("schema/"))
import jsonschema
from typing import Dict, List


class ValidationUtils:
    @staticmethod
    def validate_preset_config(preset: Dict, preset_name: str) -> bool:
        """
        Validates that a preset has either preset_id or config, but not both.

        Args:
            preset: The preset configuration
            preset_name: Name of the preset for error messages

        Returns:
            bool: True if preset is valid
        """
        has_preset = "preset_id" in preset
        has_config = "config" in preset

        if has_preset and has_config:
            print(
                f'Error in preset "{preset_name}": Cannot specify both "preset_id" and "config".'
            )
            print('Please use either "preset_id" OR "config", but not both.')
            return False
        elif not has_preset and not has_config:
            print(
                f'Error in preset "{preset_name}": Must specify either "preset_id" or "config".'
            )
            return False
        return True

    @staticmethod
    def validate_json_with_api_schema(
        preset_config: Dict, schema_file: str, silent: bool = False
    ) -> bool:
        """
        Validate a preset configuration against the JSON schema.

        Args:
            preset_config: The configuration to validate
            schema_file: Path to the JSON schema file
            silent: If True, suppress validation messages

        Returns:
            bool: True if configuration is valid
        """
        try:
            with open(schema_file) as f:
                schema = json.load(f)
        except:
            if not silent:
                print(
                    f'Error: Unable to validate configuration against schema: schema couldn\'t be read from file "{schema_file}".'
                )
            return False

        try:
            jsonschema.validate(preset_config, schema)
            if not silent:
                print("Preset configuration passed validation.")
            return True
        except Exception as e:
            if not silent:
                print(
                    "Error: Preset configuration is not valid - see JSON validation report on how to fix this:"
                )
                print("*" * 80)
                print(e)
                print("*" * 80)
        return False

    @staticmethod
    def validate_input_file(file_path: str) -> bool:
        """
        Validate that the input file exists and is accessible.

        Args:
            file_path: Path to the input file

        Returns:
            bool: True if file is valid and accessible
        """
        if not os.path.exists(file_path):
            print(f'Error: Input file "{file_path}" does not exist.')
            return False

        if not os.path.isfile(file_path):
            print(f'Error: Path "{file_path}" is not a file.')
            return False

        try:
            with open(file_path, "rb"):
                pass
            return True
        except IOError as e:
            print(f'Error: Cannot access input file "{file_path}": {str(e)}')
            return False

    @staticmethod
    def validate_output_directory(output_prefix: str) -> bool:
        """
        Validate that the output directory exists or can be created.

        Args:
            output_prefix: Output file prefix including directory path

        Returns:
            bool: True if directory is valid or was created successfully
        """
        directory = os.path.dirname(output_prefix)
        if directory:
            try:
                os.makedirs(directory, exist_ok=True)
                return True
            except OSError as e:
                print(f'Error: Cannot create output directory "{directory}": {str(e)}')
                return False
        return True

    @staticmethod
    def validate_settings(settings: Dict) -> bool:
        """
        Validate the settings configuration.

        Args:
            settings: Settings dictionary

        Returns:
            bool: True if settings are valid
        """
        required_fields = ["schemaPath"]

        for field in required_fields:
            if field not in settings:
                print(f'Error: Required field "{field}" missing in settings file.')
                return False

        if not os.path.exists(settings["schemaPath"]):
            print(f'Error: Schema file "{settings["schemaPath"]}" does not exist.')
            return False

        return True

    @staticmethod
    def validate_credentials(credentials: Dict) -> bool:
        """
        Validate the credentials configuration.

        Args:
            credentials: Credentials dictionary

        Returns:
            bool: True if credentials are valid
        """
        # Validate that credentials is valid JSON
        try:
            json.dumps(credentials)
        except (TypeError, ValueError):
            print('Error: Credentials must be valid JSON.')
            return False

        if "token" not in credentials:
            print('Error: Required field "token" missing in credentials file.')
            return False

        if not isinstance(credentials["token"], str):
            print('Error: Field "token" must be a string in credentials file.')
            return False

        if not credentials["token"]:
            print('Error: Field "token" cannot be empty in credentials file.')
            return False

        return True

    def validate_presets(self, presets: dict, schema_path: str) -> bool:
        """Validate all presets in the configuration."""
        print("\nValidating preset configurations...")
        all_presets_invalid = True

        for preset_name in presets["presets"]:
            preset = presets["presets"][preset_name]

            # First check preset/config structure
            if not self.validate_preset_config(preset, preset_name):
                continue

            # Then validate config if present
            if "config" in preset:
                print(f'Validating configuration for preset "{preset_name}".')
                if self.validate_json_with_api_schema(preset["config"], schema_path, False):
                    all_presets_invalid = False
            else:  # preset_id case
                print(f'Preset "{preset_name}" uses preset_id: {preset["preset_id"]}')
                all_presets_invalid = False

        if all_presets_invalid:
            print("No valid preset configuration found. Terminating.")
            return False
        
        return True
