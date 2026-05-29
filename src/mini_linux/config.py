"""Configuration for mini-linux."""

import tomllib
from pathlib import Path
from typing import Self

from pydantic import BaseModel, model_validator


class Config(BaseModel):
    """Configuration variables from `config.toml`."""

    output_dir: Path
    build_dir: Path
    sources_dir: Path
    pkgs_dirs: list[Path]

    @model_validator(mode="after")
    def check_output_dir(self) -> Self:
        """Check that `output_dir` exists.

        Returns
        -------
        Config
            The valid Config object

        Raises
        ------
        FileNotFoundError
            If output_dir does not exist.

        """
        if not self.output_dir.exists():
            msg = f"{self.output_dir.resolve()} does not exist. Please create it first."
            raise FileNotFoundError(msg)

        return self

    @model_validator(mode="after")
    def check_build_dir(self) -> Self:
        """Check that `build_dir` exists.

        Returns
        -------
        Config
            The valid Config object

        Raises
        ------
        FileNotFoundError
            If build_dir does not exist.

        """
        if not self.build_dir.exists():
            msg = f"{self.build_dir.resolve()} does not exist. Please create it first."
            raise FileNotFoundError(msg)

        return self

    @model_validator(mode="after")
    def check_sources_dir(self) -> Self:
        """Check that `sources_dir` exists.

        Returns
        -------
        Config
            The valid Config object

        Raises
        ------
        FileNotFoundError
            If sources_dir does not exist.

        """
        if not self.sources_dir.exists():
            msg = f"{self.sources_dir.resolve()} does not exist. Please create it first."
            raise FileNotFoundError(msg)

        return self

    @model_validator(mode="after")
    def check_pkgs_dir(self) -> Self:
        """Check that `pkgs_dir` exists.

        Returns
        -------
        Config
            The valid Config object

        Raises
        ------
        FileNotFoundError
            If pkgs_dir does not exist.

        """
        for pkgs_dir in self.pkgs_dirs:
            if not pkgs_dir.exists():
                msg = f"{pkgs_dir.resolve()} does not exist. Please create it first."
                raise FileNotFoundError(msg)

        return self


config_file = Path("./config.toml")
if not config_file.exists():
    msg = "`./config.toml` does not exist."
    raise FileNotFoundError(msg)

with config_file.open("rb") as f:
    config_data = tomllib.load(f)

CONFIG = Config(**config_data)
