# Docker Swarm Deployment Helper

A Python utility for deploying Docker stack configurations to remote Docker Swarm clusters. This tool is designed to be used as part of a CI/CD pipeline, particularly with GitHub Actions.

## Features

- Template-based configuration management using YAML files
- Environment variable substitution in configuration files
- Secure remote deployment using SSH and rsync
- Basic versioning support for deployed configurations
- Support for multiple deployment stages (dev, qa, prod)
- Docker Swarm stack deployment with registry authentication

## Prerequisites

- Python 3.x
- SSH access to the remote Docker Swarm cluster
- Docker Swarm cluster running on the remote server
- SSH key for authentication

## Installation

1. Clone the repository
2. Ensure you have the required Python packages installed:
   ```bash
   pip install pyyaml
   ```

## Usage

### Command Line Interface

```bash
python main.py --app_name <app_name> \
              --placeholder_file_path <path_to_yml> \
              --remote_address <remote_host> \
              --stage <deployment_stage>
```

### Parameters

- `--app_name`: Name of the application being deployed
- `--placeholder_file_path`: Path to the YAML template file
- `--remote_address`: IP address or hostname of the remote server
- `--stage`: Deployment stage (e.g., dev, qa, prod)

### Optional Parameters

- `--ssh_key_path`: Path to SSH key (default: "ssh_key")
- `--remote_user`: Remote user for SSH (default: "root")
- `--ssh_port`: SSH port (default: "61111")

## Configuration

### Template File Format

The tool expects a YAML file with environment variable placeholders. Example:

```yaml
version: "3.9"
services:
  app:
    image: ${IMAGE_NAME}:${IMAGE_TAG}
    environment:
      - DB_HOST=${DB_HOST}
```

### GitHub Actions Integration

Example workflow configuration:

```yaml
name: Deploy to Swarm
on:
  workflow_dispatch:
    inputs:
      stage:
        description: "Deployment environment"
        required: true
        default: "dev"
        type: choice
        options: ["dev", "qa", "prod"]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy stack
        env:
          SSH_KEY: ${{ secrets.SSH_KEY }}
        run: |
          python helper/main.py \
            --app_name "myapp" \
            --placeholder_file_path "deployment/${{ inputs.stage }}.yml" \
            --remote_address "your-server" \
            --stage "${{ inputs.stage }}"
```

## Security

- SSH keys should be stored securely and never committed to version control
- Use environment variables or secrets management for sensitive values
- The tool supports custom SSH ports and users for enhanced security

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

