"""Generate the bounded repository index from self-contained package files."""

import hashlib
import json
from pathlib import Path


root = Path(__file__).resolve().parent
packages = []
for path in sorted((root / "packages").glob("*.json")):
    data = path.read_bytes()
    package = json.loads(data)
    packages.append(
        {
            "id": package["id"],
            "version": package["version"],
            "title": package["title"],
            "url": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(data).hexdigest(),
            "androidPackages": package.get("androidPackages", []),
        }
    )

assert len({package["id"] for package in packages}) == len(packages), "Duplicate package ID"
(root / "index.json").write_text(
    json.dumps({"formatVersion": 1, "packages": packages}, indent=2) + "\n"
)
