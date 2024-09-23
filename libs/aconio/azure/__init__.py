"""Utilities for interacting with Azure file shares."""

import os

from azure.storage.fileshare import (
    ShareDirectoryClient,
    ShareFileClient,
)


class Auth:
    account_url: str
    share_name: str
    credential: str

    def __init__(
        self, account_url: str, share_name: str, credential: str
    ) -> None:
        self.account_url = account_url
        self.share_name = share_name
        self.credential = credential


def download_storage_dir(
    storage_dir_path: str,
    output_path: str,
    auth: Auth,
    raise_on_empty: bool = False,
) -> None:
    """Download directory from Azure file share.

    Args:
        storage_dir_path:
            Path to the directory in the Azure file share.
        output_path:
            Path to the output directory.
        auth:
            Authentication object.
        raise_on_empty:
            If `True`, the function will raise an error if the directory
            specified with `storage_dir_path` is empty. Defaults to `False`.

    Raises:
        FileNotFoundError:
            If the directory does not exist.
        RuntimeError:
            If the directory is empty and `raise_on_empty` is `True`.
    """
    client = ShareDirectoryClient(
        account_url=auth.account_url,
        share_name=auth.share_name,
        credential=auth.credential,
        directory_path=storage_dir_path,
    )

    if not client.exists(timeout=5):
        raise FileNotFoundError(
            f"Directory '{storage_dir_path}' does not exist."
        )

    items = list(client.list_directories_and_files())
    if len(items) == 0 and raise_on_empty:
        raise RuntimeError(f"Directory '{storage_dir_path}' is empty.")

    for item in items:
        item_name = item.get("name")

        if item.get("is_directory") is True:
            sub_storage_dir_path = os.path.join(storage_dir_path, item_name)
            sub_output_path = os.path.join(output_path, item_name)

            os.makedirs(sub_output_path, exist_ok=True)

            download_storage_dir(
                storage_dir_path=sub_storage_dir_path,
                output_path=sub_output_path,
                auth=auth,
            )
        else:
            download_file(storage_dir_path, item_name, output_path, auth)


def download_file(
    storage_dir_path: str, file_name: str, output_path: str, auth: Auth
) -> None:
    """Download file from Azure file share.

    Args:
        storage_dir_path:
            Path to the directory in the Azure file share.
        file_name:
            File name of the object to download.
        output_path:
            Path to the output directory.
        auth:
            Authentication object.
    """
    client = ShareFileClient(
        account_url=auth.account_url,
        share_name=auth.share_name,
        credential=auth.credential,
        file_path=os.path.join(storage_dir_path, file_name),
    )

    with open(os.path.join(output_path, file_name), "wb") as data:
        stream = client.download_file()
        data.write(stream.readall())
