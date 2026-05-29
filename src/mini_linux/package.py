"""Package operations and resolving dependencies."""

import tarfile
import tomllib
from pathlib import Path

from packaging import version
from pydantic import BaseModel

from mini_linux.config import CONFIG

from .fetch import check_sha256sum, download_source


def find_top_level_source_dir(tf: tarfile.TarFile) -> str:
    """Find the top-level directory in a .tar file.

    (i.e. the unpacked source directory to traverse into to build.)

    Returns
    -------
    str
        The name of the unpacked directory.

    """
    top_level_dirs: set[str] = set()

    for m in tf.getmembers():
        parts = m.name.lstrip("/").split("/")
        if len(parts) > 1 or m.isdir():
            top_level_dirs.add(parts[0])

    if len(top_level_dirs) > 1:
        msg = "Multiple top-level dirs in tar file is not supported."
        raise NotImplementedError(msg)

    return next(iter(top_level_dirs))


class Package(BaseModel):
    """A package with version, source files, and checksums."""

    name: str
    version: str
    sources: list[str]
    checksums: list[str]
    fetched_sources: list[Path] | None = None
    build_dir: str | None = None

    @classmethod
    def from_file(cls, fp: str | Path) -> "Package":
        """Create a Package object from a package .toml file.

        Returns
        -------
        Package
            The package.

        """
        if isinstance(fp, str):
            fp = Path(fp)

        with fp.open("rb") as f:
            data = tomllib.load(f)

        return cls(**data["package"])

    @property
    def packaging_version(self) -> version.Version:
        """Parsed version from `packaging` allowing easier comparison of versions."""
        return version.parse(self.version)

    @property
    def versioned_sources(self) -> list[str]:
        """List of source URLs with package name and version in-filled."""
        return [s.format(name=self.name, version=self.version) for s in self.sources]

    def fetch(self) -> None:
        """Retrieve needed source files and create `self.fetched_sources`."""
        fetched_sources: list[Path] = []

        for url, expected_hash in zip(self.versioned_sources, self.checksums, strict=True):
            path = download_source(url)
            check_sha256sum(path, expected_hash)

            fetched_sources.append(path)

        self.fetched_sources = fetched_sources

    def unpack(self) -> None:
        """Unpack the fetched source files to build directory.

        Raises
        ------
        TypeError
            If fetched sources could not be found.

        NotImplementedError
            If there is more than one source file.

        """
        # TODO: What if we need extra operations e.g. after unpack?
        if self.fetched_sources is None:
            msg = f"Sources for `{self.name}` could not be found locally."
            raise TypeError(msg)

        if len(self.fetched_sources) > 1:
            raise NotImplementedError

        # TODO: What if a source file is not a tar file?
        if not any("tar" in suffix for suffix in self.fetched_sources[0].suffixes):
            msg = "non-tar files are not yet implemented"
            raise NotImplementedError(msg)

        with tarfile.open(self.fetched_sources[0]) as tf:
            top_level = find_top_level_source_dir(tf)
            tf.extractall(CONFIG.build_dir, filter="data")

        self.build_dir = top_level


p = Package.from_file(CONFIG.pkgs_dir / "acpi.toml")
p.fetch()
p.unpack()
print(p.build_dir)
