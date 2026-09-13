"""Handle execution environment specific properties."""

import os

import robocorp.vault

import aconio.botdata


def get_env() -> str:
    """Get the execution environment identifier.

    The execution environment is set via the environment variable
    `ENVIRONMENT`. Can be one of the following: ["dev", "test", "prod"].
    """
    valid_identifiers = ["dev", "test", "prod"]
    env = os.environ.get("ENVIRONMENT").lower()

    if env is None:
        raise ValueError(
            "Failed to load env identifier! "
            "Environment variable 'ENVIRONMENT' not set! "
            f"Please use one of: {valid_identifiers}."
        )

    if env not in valid_identifiers:
        raise ValueError(
            "Failed to load env identifier! "
            "Environment variable 'ENVIRONMENT' has "
            f"invalid value '{env}'. Please use "
            f"one of: {valid_identifiers}."
        )

    return env.lower()


def get_yaml_config_path() -> str:
    """Get path to the YAML config file for current execution environment.

    In case of `test` or `prod` environment, the config file is downloaded
    from Azure Files. The environment variable `AZURE_CONFIG_DIR` must be
    set to the directory of the Azure Files folder to be downloaded.

    Also, in `test` or `prod` environments, a Robocorp vault secret named
    `azure_fileshare` must be set up with the following keys:
    - `account_url`
    - `share_name`
    - `access_key`
    """

    match env := get_env():
        case "dev":
            return f"devdata/{env}.config.yaml"

        case "prod" | "test":

            azure_files_dir = os.environ.get("AZURE_CONFIG_DIR")
            if azure_files_dir is None:
                raise ValueError(
                    "Failed to load Azure config dir! "
                    "Environment variable 'AZURE_CONFIG_DIR' not set!"
                )

            azure_creds = robocorp.vault.get_secret("azure_fileshare")

            aconio.botdata.load_process_config_from_azure(
                storage_dir_path=azure_files_dir,
                account_url=azure_creds["account_url"],
                share_name=azure_creds["share_name"],
                access_key=azure_creds["access_key"],
            )

            return os.path.join(
                aconio.botdata.config_dir(),
                f"{env}.config.yaml",
            )


def get_j2_template_dirs() -> list[str]:
    """Get list of Jinja2 template directories.

    Note that Jinja2 template directories are searched and applied
    in order, so if multiple template directories are returned, the
    first matching template overwrites any following ones.

    Assumes that in case of "prod" or "test" execution environment,
    Azure templates have been downloaded to the `aconio.botdata` config
    dir.
    """

    dirs = []

    if get_env() in ["prod", "test"]:
        dirs.append(os.path.join(aconio.botdata.config_dir(), "templates"))

    # Default jinja templates, overwritten with Azure templates if present
    dirs.append(os.path.join(os.environ.get("ROBOT_ROOT"), "templates"))

    return dirs
