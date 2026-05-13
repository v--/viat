import pathlib

from viat import ViatFileTracker
from viat._vault.config import ViatVaultStaticConfig
from viat._vault.resolver import ViatPathResolver
from viat.exceptions import ViatUntrackedFileWarning, emit_warning


class TrackerBaseMixin(ViatFileTracker):
    static_config: ViatVaultStaticConfig
    resolver: ViatPathResolver | None

    def _resolve_path(self, path: pathlib.Path | str) -> pathlib.Path:
        return self.resolver.relativize(path) if self.resolver else pathlib.Path(path)

    def validate_tracked(self, path: pathlib.Path | str) -> None:
        if self.static_config.skip_validation:
            return

        rel_path = self._resolve_path(path)

        if not self.is_tracked(rel_path):
            emit_warning(ViatUntrackedFileWarning(rel_path), stacklevel=2)
