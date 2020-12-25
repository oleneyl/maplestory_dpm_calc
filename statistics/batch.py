import argparse
import subprocess

from .preset import get_preset_list


def get_args():
    parser = argparse.ArgumentParser("Batch argument")
    parser.add_argument("--script", type=str)

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    presets = get_preset_list()
    for preset in presets:
        subprocess.Popen(
            ["python3", "-m", f"statistics.{args.script}", "--id", preset.id],
            stdout=subprocess.PIPE,
        )
