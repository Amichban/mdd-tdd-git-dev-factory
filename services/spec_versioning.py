"""
Spec versioning and migration service.

Manages spec versions and applies migrations between versions.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Callable


class SpecVersion:
    """Represents a spec file version."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self._data = None
        self._hash = None

    @property
    def data(self) -> dict:
        if self._data is None:
            with open(self.filepath) as f:
                self._data = json.load(f)
        return self._data

    @property
    def version(self) -> str:
        return self.data.get("version", "0.0.0")

    @property
    def hash(self) -> str:
        if self._hash is None:
            content = json.dumps(self.data, sort_keys=True)
            self._hash = hashlib.sha256(content.encode()).hexdigest()[:12]
        return self._hash

    def save(self, new_data: dict = None):
        """Save data to file."""
        data = new_data if new_data else self._data
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)
        self._data = data
        self._hash = None


class SpecMigration:
    """A migration between spec versions."""

    def __init__(
        self,
        from_version: str,
        to_version: str,
        migrate_fn: Callable[[dict], dict],
        description: str = ""
    ):
        self.from_version = from_version
        self.to_version = to_version
        self.migrate_fn = migrate_fn
        self.description = description

    def apply(self, data: dict) -> dict:
        """Apply this migration to data."""
        return self.migrate_fn(data)


class SpecVersionManager:
    """Manages spec versions and migrations."""

    def __init__(self, specs_dir: Path = None):
        if specs_dir is None:
            specs_dir = Path(__file__).parent.parent / "specs"
        self.specs_dir = specs_dir
        self.versions_dir = specs_dir / ".versions"
        self.migrations: dict[str, list[SpecMigration]] = {}
        self._register_default_migrations()

    def _register_default_migrations(self):
        """Register built-in migrations."""
        # Entity migrations
        self.register_migration(
            "entities",
            SpecMigration(
                "1.0.0", "1.1.0",
                self._migrate_entities_1_0_to_1_1,
                "Add layer field to entities"
            )
        )

    def register_migration(self, spec_type: str, migration: SpecMigration):
        """Register a migration for a spec type."""
        if spec_type not in self.migrations:
            self.migrations[spec_type] = []
        self.migrations[spec_type].append(migration)

    def get_version(self, spec_type: str) -> SpecVersion:
        """Get current version of a spec type."""
        filepath = self.specs_dir / f"{spec_type}.json"
        if not filepath.exists():
            raise FileNotFoundError(f"Spec not found: {filepath}")
        return SpecVersion(filepath)

    def create_snapshot(self, spec_type: str, label: str = None) -> Path:
        """Create a versioned snapshot of a spec."""
        self.versions_dir.mkdir(parents=True, exist_ok=True)

        spec = self.get_version(spec_type)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        label_part = f"_{label}" if label else ""

        snapshot_name = f"{spec_type}_v{spec.version}_{timestamp}{label_part}.json"
        snapshot_path = self.versions_dir / snapshot_name

        with open(snapshot_path, "w") as f:
            json.dump(spec.data, f, indent=2)

        return snapshot_path

    def list_snapshots(self, spec_type: str = None) -> list[Path]:
        """List all snapshots, optionally filtered by type."""
        if not self.versions_dir.exists():
            return []

        pattern = f"{spec_type}_*.json" if spec_type else "*.json"
        return sorted(self.versions_dir.glob(pattern))

    def migrate(self, spec_type: str, target_version: str = None) -> bool:
        """Migrate a spec to target version (or latest)."""
        spec = self.get_version(spec_type)
        current = spec.version
        migrations = self.migrations.get(spec_type, [])

        if not migrations:
            return False

        # Find applicable migrations
        applicable = [
            m for m in migrations
            if self._version_compare(m.from_version, current) >= 0
        ]

        if target_version:
            applicable = [
                m for m in applicable
                if self._version_compare(m.to_version, target_version) <= 0
            ]

        if not applicable:
            return False

        # Sort by version
        applicable.sort(key=lambda m: self._version_tuple(m.from_version))

        # Create backup
        self.create_snapshot(spec_type, f"pre_migrate_{current}")

        # Apply migrations
        data = spec.data.copy()
        for migration in applicable:
            if data.get("version") == migration.from_version:
                data = migration.apply(data)
                data["version"] = migration.to_version
                print(f"  Applied: {migration.from_version} -> {migration.to_version}")

        # Save migrated data
        spec.save(data)
        return True

    def check_migrations(self, spec_type: str) -> list[SpecMigration]:
        """Check what migrations are pending for a spec."""
        spec = self.get_version(spec_type)
        current = spec.version
        migrations = self.migrations.get(spec_type, [])

        pending = [
            m for m in migrations
            if self._version_compare(m.from_version, current) >= 0
        ]

        return sorted(pending, key=lambda m: self._version_tuple(m.from_version))

    def bump_version(self, spec_type: str, part: str = "patch") -> str:
        """Bump the version of a spec."""
        spec = self.get_version(spec_type)
        major, minor, patch = self._version_tuple(spec.version)

        if part == "major":
            major += 1
            minor = 0
            patch = 0
        elif part == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        new_version = f"{major}.{minor}.{patch}"

        # Update and save
        data = spec.data.copy()
        data["version"] = new_version
        spec.save(data)

        return new_version

    @staticmethod
    def _version_tuple(version: str) -> tuple[int, int, int]:
        """Convert version string to tuple."""
        parts = version.split(".")
        return (
            int(parts[0]) if len(parts) > 0 else 0,
            int(parts[1]) if len(parts) > 1 else 0,
            int(parts[2]) if len(parts) > 2 else 0
        )

    @staticmethod
    def _version_compare(v1: str, v2: str) -> int:
        """Compare two versions. Returns -1, 0, or 1."""
        t1 = SpecVersionManager._version_tuple(v1)
        t2 = SpecVersionManager._version_tuple(v2)

        if t1 < t2:
            return -1
        elif t1 > t2:
            return 1
        return 0

    # Built-in migration functions
    @staticmethod
    def _migrate_entities_1_0_to_1_1(data: dict) -> dict:
        """Add layer field to entities without it."""
        for entity in data.get("entities", []):
            if "layer" not in entity:
                entity["layer"] = "domain"
        return data


# Global manager instance
_manager = None


def get_version_manager() -> SpecVersionManager:
    """Get the global version manager instance."""
    global _manager
    if _manager is None:
        _manager = SpecVersionManager()
    return _manager


def create_snapshot(spec_type: str, label: str = None) -> Path:
    """Create a snapshot of a spec."""
    return get_version_manager().create_snapshot(spec_type, label)


def migrate_spec(spec_type: str, target_version: str = None) -> bool:
    """Migrate a spec to target version."""
    return get_version_manager().migrate(spec_type, target_version)


def bump_version(spec_type: str, part: str = "patch") -> str:
    """Bump the version of a spec."""
    return get_version_manager().bump_version(spec_type, part)
