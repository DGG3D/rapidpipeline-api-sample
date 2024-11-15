# RapidPipeline API Sample

This python script serves as an example and starting point for your own API-based integration of the [RapidPipeline REST API](https://docs.rapidpipeline.com/docs/category/rapidpipeline-api) uploading, optimizing and downloading 3D models.

[Explore the Docs](https://docs.rapidpipeline.com/) · [Signup to RapidPipeline](https://app.rapidpipeline.com/signup)

## Table of Contents

- [Usage Examples](#usage-examples)
  - [Process Single File](#process-single-file)
  - [Process Directory](#process-directory)
  - [Process Existing Rawmodel](#process-existing-rawmodel)
- [Prerequisites & Setup](#prerequisites-&-setup)
- [Preset Configuration](#preset-configuration)
  - [Using Preset IDs](#using-preset-ids)
  - [Using Full Configurations](#using-full-configurations)
- [Project File Structure](#project-file-structure)
- [API Capabilities](#api-capabilities)
  - [Core Concepts](#core-concepts)
  - [Webhooks](#webhooks)
  - [DCC to PBR Conversion](#dcc-to-pbr-conversion)
  - [Automated 3D QA](#automated-qu)

## Usage Examples

You can upload a single file, files inside a directory or an existing rawmodel/base asset and optimize them using the specified presets inside `presets.json` and finally download them to the `output` directory. Make sure to setup the `credentials.json` file first.

#### Process single file:

```bash
python main.py input/teapot.glb
```

- file named `teapot.glb` in a folder named `input`

#### Process directory:

```bash
python main.py input
```

- folder named `input`

#### Process existing rawmodel/base asset:

```bash
python main.py 1234567890.id
```

- Format: {RawmodelID/BaseAssetID}.id

##### For all available options:

```bash
python main.py --help
```

- like using a preset, a label, cleanup after processing, exit on error, etc.

## Prerequisites & Setup

1. **Requirements**

   - [Python 3.8](https://www.python.org/) or higher installed
   - API token from [RapidPipeline](https://app.rapidpipeline.com/api_tokens)
     - Requires an active subscription to the Team, Studio or Enterprise plans
     - [Tutorial](https://docs.rapidpipeline.com/docs/rapidpipeline-cloud-tutorials/api-token-setup) on how to get an API token

2. **API Token Configuration**
   - Get your API token from [RapidPipeline](https://app.rapidpipeline.com/api_tokens) under the API Tokens settings
   - Copy `credentials.example.json` to `credentials.json` and add your token:

```json
{
  "token": "your-api-token"
}
```

### Preset Configuration

The `presets.json` file allows you to specify one or multiple optimization presets. You can use either preset IDs or full preset configurations.

##### Example Structure of `presets.json` file:

```json
{
  "presets": {
    // Preset using a preset ID
    "example_with_preset_id": {
      "preset_id": 7008
    },
    // Preset using full configuration
    "example_with_full_configuration": {
      "config": {
        "export": [
          {
            "preserveTextureFilenames": false,
            "reencodeTextures": "auto"
            // ... other configuration options
          }
        ]
      }
    }
  }
}
```

#### Optimize with Preset IDs

How to obtain preset IDs:

**Via UI**:

- Navigate to the Presets page in RapidPipeline
- Select your preset
- The preset ID will be visible in the preset details
- Set the preset ID in the presets.json file

Example for presets.json:

```json
{
  "presets": {
    "example_preset": {
      "preset_id": <SET_PRESET_ID_HERE AS NUMBER>
    }
  }
}
```

#### Optimize with Full Configurations Preset

How to obtain full configuration preset:

**Via UI**:

- Navigate to the Presets page
- Select your preset
- Click on three dots under the Actions column and select "Download"

The downloaded configuration is zipped and inside the API folder is a preset.json which contents you need to copy inside of the presets

Example for presets.json:

```json
{
  "presets": {
    "example_preset": {
      "config": <COPY HERE THE CONTENTS OF downloaded preset JSON file>
    }
  }
}
```

## Project File Structure

```
├── main.py                 # Main script entry point
├── credentials.json        # API credentials configuration
├── settings.json          # General settings configuration
├── presets.json          # Optimization preset configurations
├── src/
│   ├── client.py           # RapidPipeline API client
│   ├── model_processor.py  # Model processing logic
│   ├── request_utils.py    # HTTP request utilities
│   └── validation_utils.py # Configuration validation utilities
│   └── file_utils.py       # File handling utilities
├── schema/               # JSON schema files for validation
│   ├── six/             # Schema dependencies
│   └── 3d_processor_schema_v1_0.json
├── input/               # Directory for input models
└── output/              # Directory for processed models (will be created if it doesn't exist)
```

## API Capabilities

RapidPipeline's REST API provides comprehensive functionality for managing your 3D asset pipeline:

### Concepts 

- **Uploading Base Assets**: Source/raw models uploaded by users that serve as the foundation for all processing
- **Optimize to Rapid Models and Download**: Optimized models created by processing base assets through the 3D Processor
- **Presets**: Saved 3D processor settings for consistent asset optimization
- **Embeds**: Embeddable 3D viewers created from Rapid Models
- **Tags**: User-defined or system-generated tags for asset filtering and organization

### Webhooks

RapidPipeline uses webhooks to notify your application when events occur in your account, eliminating the need to poll the API for status updates. Events include model upload completion, optimization status, and processing errors.

[Webhook API Documentation](https://docs.rapidpipeline.com/docs/api/rapidpipeline_v2/webhooks)
[Webhook API Example](https://github.com/DGG3D/webhook-api-example)

### DCC to PBR Conversion

Convert your DCC scenes directly to web-ready formats with automatic material conversion:

- Support for 3ds Max scenes with V-Ray materials
- Automatic conversion to PBR materials
- Export to industry-standard formats (.FBX, .GLB, .USDZ)
- Simply upload your .max files as a ZIP archive and process them like any other asset

[DCC to PBR Conversion API Documentation](https://docs.rapidpipeline.com/docs/api/rapidpipeline_v2/get-imported-dcc-files)

### Automated 3D QA

Built-in QA tools to ensure consistency across your optimized assets:

- Automated comparison between original and processed models
- Quality metrics validation
- Ensure optimizations meet your quality standards
- Integrate QA checks into your automated pipeline

[Automated Quality Assurance API Documentation for Base Assets](https://docs.rapidpipeline.com/docs/api/rapidpipeline_v2/returns-hash-signed-links-for-the-quality-control-images-generated-after-importing-the-rawmodel)

[Automated Quality Assurance API Documentation for Rapid Models](https://docs.rapidpipeline.com/docs/api/rapidpipeline_v2/returns-hash-signed-links-for-the-quality-control-images-generated-after-optimization)

## Get Started with RapidPipeline

Transform your 3D asset pipeline with RapidPipeline - trusted by brands and platforms in 20+ countries worldwide.

### Why Choose RapidPipeline?

- ⭐ Award-winning technology
- 🚀 More than 4,500,000 3D models optimized
- ⚡ Up to 100x faster turnaround times
- 💰 Up to 95% cost savings
- 🛠️ Best-in-Class 3D Optimizer + Material Baker
- 🔄 3D Format Conversion + DCC Import
- ⚙️ QC Tools & Delivery Presets
- 🔌 REST API & On-Prem Options

### Key Features

- **Powerful Optimization**: Best-in-class automation toolchain with full control over mesh decimation, remeshing, texture baking, and more
- **Format Conversion**: Convert between proprietary formats and open standards like glTF or USD(Z)
- **Quality Control**: Automated QC process with factory presets or custom pipeline creation
- **Flexible Deployment**: Web UI, REST API, private cloud, on-premise Docker container, or CLI

### Ready to Transform Your 3D Pipeline?

[Sign up for free](https://app.rapidpipeline.com/signup) (no credit card needed) or [explore the docs](https://docs.rapidpipeline.com/)

---

Made with ❤️ by Darmstadt Graphics Group GmbH (DGG)
