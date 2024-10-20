import argparse
import logging
from datetime import datetime as dt

from groundblock import GroundBlock


def rclone_google_drive_hanif(dt_current: dt) -> str:
    return (
        f"rclone copy "  #
        f"google_drive_hanif: "  #
        f"/usr/share/zfs_pool/remote/google_drive_hanif/ "  #
        f"-vv "  #
    )


def rclone_google_drive_asadun(dt_current: dt) -> str:
    return (
        f"rclone copy "  #
        f"google_drive_asadun: "  #
        f"/usr/share/zfs_pool/remote/google_drive_asadun/ "  #
        f"-vv "  #
    )


def rclone_google_photos_hanif(dt_current: dt) -> str:
    return (
        f"rclone copy "  #
        f"google_photos_hanif: "  #
        f"/usr/share/zfs_pool/remote/google_photos_hanif/ "  #
        f"-vv "  #
    )


def rclone_google_photos_asadun(dt_current: dt) -> str:
    return (
        f"rclone copy "  #
        f"google_photos_asadun: "  #
        f"/usr/share/zfs_pool/remote/google_photos_asadun/ "  #
        f"-vv "  #
    )


def rclone_commit(dt_current: dt) -> str:
    return (
        f"cd /usr/share/zfs_pool/remote && "  #
        f"git status && "  #
        f"git add . && "  #
        f'git commit -s -m "commit {dt_current.isoformat()}"'  #
    )


def run(db_path: str, dry_run: bool):
    ground_block = GroundBlock(db_path, dry_run)
    ground_block.add(
        "Cloud Storage Rclone",
        "0 0 * * *",
        [
            rclone_google_drive_hanif,  #
            rclone_google_drive_asadun,  #
            rclone_google_photos_hanif,  #
            rclone_google_photos_asadun,  #
            rclone_commit,  #
        ],
    )
    ground_block.run()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", type=str, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(args.db_path, args.dry_run)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(funcName)15s | %(message)s", level=logging.INFO)
    main()
