"""Declarative metadata shared by CLI wrapper integrations."""

from __future__ import annotations

from dataclasses import dataclass
from shutil import which
from collections.abc import Callable


@dataclass(frozen=True)
class ToolSpec:
    """Stable integration metadata; command functions only own options."""

    key: str
    label: str
    executables: tuple[str, ...]
    install_hint: str
    missing_name: str | None = None

    def find_binary(self, resolver: Callable[[str], str | None] = which) -> str | None:
        return next((path for name in self.executables if (path := resolver(name))), None)

    def missing_message(self) -> str:
        names = self.missing_name or f"'{'/'.join(self.executables)}'"
        return f"Error: {names} not found in PATH.\nInstall {self.install_hint}"
