"""Package operations and resolving dependencies."""

import tomllib
from pathlib import Path

from packaging import version
from pydantic import BaseModel

from mini_linux.config import CONFIG

from .fetch import check_sha256sum, download_source


class Package(BaseModel):
    """A package with version, source files, and checksums."""

    name: str
    version: str
    sources: list[str]
    checksums: list[str]
    fetched_sources: list[Path] | None = None

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


p = Package.from_file(CONFIG.pkgs_dir / "acpi.toml")
p.fetch()
p.unpack()
