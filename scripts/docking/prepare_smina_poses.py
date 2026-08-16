from __future__ import annotations

import csv
import re
from pathlib import Path


SOURCE_FILE = Path("input/smina_poses_original.sdf")
OUTPUT_DIRECTORY = Path("input/poses")
MANIFEST_FILE = Path("input/pose_manifest.csv")


def split_sdf(text: str) -> list[str]:
    records = []
    current = []

    for line in text.splitlines(keepends=True):
        if line.strip() == "$$$$":
            record = "".join(current).rstrip()

            if record:
                records.append(record)

            current = []
        else:
            current.append(line)

    if "".join(current).strip():
        raise RuntimeError(
            "SDF末尾に$$$$がないレコードがあります"
        )

    return records


def extract_property(
    record: str,
    candidate_names: list[str],
) -> str | None:
    wanted = {
        name.lower()
        for name in candidate_names
    }

    lines = record.splitlines()

    for index, line in enumerate(lines):
        match = re.match(
            r"^>\s*<([^>]+)>",
            line.strip(),
        )

        if match is None:
            continue

        property_name = match.group(1).strip()

        if property_name.lower() not in wanted:
            continue

        values = []
        cursor = index + 1

        while cursor < len(lines):
            value = lines[cursor].strip()

            if value == "":
                break

            values.append(value)
            cursor += 1

        if values:
            return " ".join(values)

    return None


def main() -> None:
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(SOURCE_FILE)

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    for old_file in OUTPUT_DIRECTORY.glob("pose_*.sdf"):
        old_file.unlink()

    records = split_sdf(
        SOURCE_FILE.read_text(
            encoding="utf-8",
            errors="replace",
        )
    )

    rows = []

    affinity_names = [
        "minimizedAffinity",
        "Affinity",
        "affinity",
        "vina_affinity",
    ]

    for pose_number, record in enumerate(
        records,
        start=1,
    ):
        affinity = extract_property(
            record,
            affinity_names,
        )

        output_file = (
            OUTPUT_DIRECTORY
            / f"pose_{pose_number:02d}.sdf"
        )

        additions = [
            "",
            ">  <OriginalPose>",
            str(pose_number),
            "",
            ">  <SMINA_Affinity_Original>",
            affinity if affinity is not None else "NA",
            "",
        ]

        output_file.write_text(
            record.rstrip()
            + "\n"
            + "\n".join(additions)
            + "\n$$$$\n",
            encoding="utf-8",
        )

        rows.append(
            {
                "original_pose": pose_number,
                "smina_affinity": (
                    affinity
                    if affinity is not None
                    else ""
                ),
                "file": str(output_file),
            }
        )

    with MANIFEST_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0].keys()),
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"分割ポーズ数: {len(records)}")
    print(f"保存先: {OUTPUT_DIRECTORY}")
    print(f"Manifest: {MANIFEST_FILE}")


if __name__ == "__main__":
    main()
