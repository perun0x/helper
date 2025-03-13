import os
import yaml
import subprocess
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class StackFile:
    def __init__(
        self,
        app_name,
        placeholder_file_path,
        remote_address,
        stage,
        ssh_key_path="ssh_key",
        remote_user="root",
        ssh_port="61111",
    ):
        self.app_name = app_name
        self.placeholder_file_path = placeholder_file_path
        self.remote_address = remote_address
        self.stage = stage
        self.ssh_key_path = ssh_key_path
        self.remote_user = remote_user
        self.ssh_port = ssh_port

    @property
    def remote_path(self) -> str:
        return f"~/stacks/${self.app_name}/{self.stage}/"

    @property
    def stack_name(self) -> str:
        return f"${self.app_name}-{self.stage}"

    def run_command(self, command: list, capture_output: bool = False) -> Optional[str]:
        """Run a shell command and handle errors.
        NOTE: Other commands depend on this one"""
        try:
            result = subprocess.run(
                command, check=True, capture_output=capture_output, text=True
            )
            if capture_output:
                return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed: {command}\nError: {e}")
            raise RuntimeError(f"Error executing command: {e}")

    def replace_placeholders(self) -> None:
        """Replace placeholders with environment variables in the YAML file."""
        try:
            with open(self.placeholder_file_path, "r") as placeholder_file:
                content = placeholder_file.read()

            content = os.path.expandvars(content)
            config = yaml.safe_load(content)

            with open(self.placeholder_file_path, "w") as file:
                yaml.dump(config, file, sort_keys=False)

            logging.info("Placeholders replaced successfully.")
        except Exception as e:
            logging.error(f"Failed to replace placeholders: {e}")
            raise

    def rsync_to_remote(self) -> None:
        """Rsync stack file to a remote host."""
        command = [
            "rsync",
            "-avz",
            "-e",
            f"ssh -i {self.ssh_key_path} -o StrictHostKeyChecking=no -p {self.ssh_port}",
            self.placeholder_file_path,
            f"{self.remote_user}@{self.remote_address}:{self.remote_path}",
        ]
        self.run_command(command)
        logging.info(f"File synced to {self.remote_address}:{self.remote_path}")

    def deploy_on_remote(self) -> None:
        """Deploy stack file to a remote host."""
        command = [
            "ssh",
            "-i",
            self.ssh_key_path,
            f"-p {self.ssh_port}",
            "-o",
            "StrictHostKeyChecking=no",
            f"{self.remote_user}@{self.remote_address}",
            f"docker stack deploy --with-registry-auth --resolve-image always "
            f"--compose-file {self.remote_path}{os.path.basename(self.placeholder_file_path)} {self.stack_name}",
        ]
        self.run_command(command)
        logging.info(
            f"Successfully deployed {self.stack_name} on {self.remote_address}"
        )

    def count_files_in_dir(self) -> int:
        """Count files in the remote directory."""
        command = [
            "ssh",
            "-i",
            self.ssh_key_path,
            f"-p {self.ssh_port}",
            "-o",
            "StrictHostKeyChecking=no",
            f"{self.remote_user}@{self.remote_address}",
            f"ls -1 {self.remote_path} 2>/dev/null | wc -l",
        ]
        count = self.run_command(command, capture_output=True)
        logging.info(f"File count in {self.remote_path}: {count}")
        return int(count) if count.isdigit() else 0

    def copy_stack_file(self, version: int) -> None:
        """Copy stack file to a new path."""
        new_file = f"{self.remote_path}{self.stage}-v{version}.yml"
        command = [
            "ssh",
            "-i",
            self.ssh_key_path,
            f"-p {self.ssh_port}",
            "-o",
            "StrictHostKeyChecking=no",
            f"{self.remote_user}@{self.remote_address}",
            f"cp {self.remote_path}{os.path.basename(self.placeholder_file_path)} {new_file}",
        ]
        self.run_command(command)
        logging.info(f"Successfully copied file to {new_file}")

    def create_stage_dir_if_not_exist(self) -> None:
        """Create a stage directory if it doesn't exist."""
        command = [
            "ssh",
            "-i",
            self.ssh_key_path,
            f"-p {self.ssh_port}",
            "-o",
            "StrictHostKeyChecking=no",
            f"{self.remote_user}@{self.remote_address}",
            f"mkdir -p {self.remote_path}",
        ]
        self.run_command(command)
        logging.info(f"Directory ensured: {self.remote_path}")
