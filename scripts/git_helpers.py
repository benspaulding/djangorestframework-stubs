import shutil
from typing import Optional, Union

from git.remote import RemoteProgress
from git.repo import Repo

from scripts.paths import DRF_SOURCE_DIRECTORY


class ProgressPrinter(RemoteProgress):
    def line_dropped(self, line: str) -> None:
        print(line)

    def update(
        self, op_code: int, cur_count: Union[str, float], max_count: Union[str, float, None] = None, message: str = ""
    ) -> None:
        print(self._cur_line)


def checkout_target_tag(drf_version: Optional[str]) -> None:
    if DRF_SOURCE_DIRECTORY.exists():
        shutil.rmtree(DRF_SOURCE_DIRECTORY)
    DRF_SOURCE_DIRECTORY.mkdir(exist_ok=True, parents=False)
    Repo.clone_from(
        "https://github.com/encode/django-rest-framework.git",
        DRF_SOURCE_DIRECTORY,
        progress=ProgressPrinter(),  # type: ignore
        branch=drf_version or "master",
        depth=100,
    )
