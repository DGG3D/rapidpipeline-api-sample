import argparse
import json
import sys
from src.client import RapidPipelineClient
from src.validation_utils import ValidationUtils
from src.model_processor import ModelProcessor

def parse_arguments():
    parser = argparse.ArgumentParser()
    
    # Required argument
    parser.add_argument(
        "model",
        help="input directory or 3D model (must be a self-contained file e.g. .glb OR .zip file OR base asset ID in the form <number>.id)",
    )

    # Optional arguments
    parser.add_argument(
        "-b",
        "--base-url",
        dest="baseUrl",
        default="https://api.rapidpipeline.com/api/v2/",
        help="api base url with trailing slash at the end",
    )
    parser.add_argument(
        "-c",
        "--credentials-file",
        dest="credentialsFile",
        default="credentials.json",
        help="credentials JSON file",
    )
    parser.add_argument(
        "-p",
        "--presets-file",
        dest="presetsFile",
        default="presets.json",
        help="preset definitions JSON file",
    )
    parser.add_argument(
        "-s",
        "--settings-file",
        dest="settingsFile",
        default="settings.json",
        help="settings JSON file",
    )
    parser.add_argument(
        "-l",
        "--label",
        dest="modelLabel",
        default="",
        help="label for the model"
    )
    parser.add_argument(
        "--cleanup",
        dest="cleanup",
        action="store_true",
        help="cleanup after processing (default)",
    )
    parser.add_argument(
        "--no-cleanup",
        dest="cleanup",
        action="store_false",
        help="don't cleanup after processing",
    )
    parser.add_argument(
        "-e",
        "--exit",
        dest="exitOnError",
        default=False,
        help="exit script on optimize error. Set False or True",
    )

    parser.set_defaults(cleanup=True)
    
    return parser.parse_args()

def main():
    # Parse arguments
    args = parse_arguments()
    validator = ValidationUtils()

    # Load and validate credentials
    try:
        with open(args.credentialsFile) as f:
            credentials = json.load(f)
            if not validator.validate_credentials(credentials):
                sys.exit(1)
    except:
        print(f'Unable to load and parse credentials JSON file "{args.credentialsFile}". Make sure the file exists and is valid JSON.')
        sys.exit(1)

    # Load and validate settings
    try:
        with open(args.settingsFile) as f:
            settings = json.load(f)
            if not validator.validate_settings(settings):
                sys.exit(1)
    except:
        print(f'Unable to load and parse settings JSON file "{args.settingsFile}". Make sure the file exists and is valid JSON.')
        sys.exit(1)

    # Load and validate presets
    try:
        with open(args.presetsFile) as f:
            presets = json.load(f)
            if not validator.validate_presets(presets, settings["schemaPath"]):
                sys.exit(1)
    except:
        print(f'Unable to load and parse preset definitions JSON file "{args.presetsFile}". Make sure the file exists and is valid JSON.')
        sys.exit(1)

    # Initialize client and processor
    client = RapidPipelineClient(
        access_token=credentials["token"],
        base_url=args.baseUrl
    )
    processor = ModelProcessor(client)

    # Process models
    failed_optimizations = processor.process_models(
        model_path=args.model,
        presets=presets,
        cleanup=args.cleanup,
        exit_on_error=args.exitOnError,
        model_label=args.modelLabel
    )

    # Exit with error if any optimizations failed
    sys.exit(0 if failed_optimizations == 0 else 1)

if __name__ == "__main__":
    main()
