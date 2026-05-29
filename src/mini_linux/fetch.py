"""Downloading from URLs to a local `sources` directory."""

import hashlib
from pathlib import Path

import requests

from .config import CONFIG


class HashFailedError(Exception):
    """Raised if SHA256 hash of downloaded file does not match expected hash."""


def download_source(url: str, timeout: int = 10) -> Path:
    """Download a source file to `CONFIG.sources_dir`.

    Returns
    -------
    output_path : Path
        Path object of downloaded source file.

    Raises
    ------
    ConnectionError
        If response to GET is not 200.

    """
    filename = url.rsplit("/", maxsplit=1)[-1]

    output_path = CONFIG.sources_dir / filename
    if output_path.exists():
        return output_path

    response = requests.get(url, stream=True, timeout=timeout)

    if response.status_code != 200:  # noqa: PLR2004
        raise ConnectionError

    with output_path.open("wb") as f:
        for chunk in response.iter_content():
            f.write(chunk)

    return output_path


def check_sha256sum(fp: Path, expected: str) -> None:
    """Check that the SHA256 sum of a downloaded file matches the package spec.

    Raises
    ------
    HashFailedError
        Raised if hashes do not match.

    """
    with fp.open("rb") as f:
        digest = hashlib.file_digest(f, "sha256")

    hex_digest = digest.hexdigest()

    if hex_digest != expected:
        msg = f"Hash failed for {fp}"
        raise HashFailedError(msg)
