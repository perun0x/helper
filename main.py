import argparse
from helper import StackFile


def main():
    parser = argparse.ArgumentParser(
        description="Generate and deploy a stack file to remote server",
    )

    parser.add_argument("--app_name", required=True)
    parser.add_argument("--placeholder_file_path", required=True)
    parser.add_argument("--remote_address", required=True)
    parser.add_argument("--stage", required=True)
    args = parser.parse_args()

    stack_file = StackFile(
        app_name=args.app_name,
        placeholder_file_path=args.placeholder_file_path,
        remote_address=args.remote_address,
        stage=args.stage,
    )

    stack_file.create_stage_dir_if_not_exist()
    stack_file.replace_placeholders()
    stack_file.rsync_to_remote()
    stack_file.deploy_on_remote()
    version = stack_file.count_files_in_dir()
    stack_file.copy_stack_file(version)


if __name__ == "__main__":
    main()
