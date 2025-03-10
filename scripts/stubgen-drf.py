import shutil
from argparse import ArgumentParser

from mypy.stubgen import generate_stubs, parse_options

from scripts.git_helpers import checkout_target_tag
from scripts.paths import DRF_SOURCE_DIRECTORY, STUBGEN_TARGET_DIRECTORY

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--drf_version", required=False)
    args = parser.parse_args()
    if DRF_SOURCE_DIRECTORY.exists():
        shutil.rmtree(DRF_SOURCE_DIRECTORY)
    checkout_target_tag(args.drf_version)
    drf_root = DRF_SOURCE_DIRECTORY / "rest_framework"
    stubgen_options = parse_options([f"{drf_root}", f"-o={STUBGEN_TARGET_DIRECTORY}"])
    generate_stubs(stubgen_options)
