import pathlib
import shutil
import tempfile
from collections.abc import Iterable

import pytest


@pytest.fixture
def temp_directory() -> Iterable[pathlib.Path]:
    tmpdir = pathlib.Path(tempfile.mkdtemp(prefix='viat_test_'))

    try:
        yield tmpdir
    finally:
         # Make sure the directory can be deleted in case the tests messed the permissions up
        tmpdir.chmod(0o755)

        for path, dir_names, file_names in tmpdir.walk():
            path.chmod(0o755)

            for dir_name in dir_names:
                (path / dir_name).chmod(0o755)

            for file_name in file_names:
                (path / file_name).chmod(0o755)

        shutil.rmtree(tmpdir)
