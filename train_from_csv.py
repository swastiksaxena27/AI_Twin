"""
Enroll a user (train + save model + write ModelMetadata row) from a CSV of feature rows.

Usage:
    python train_from_csv.py demo_user_alice.csv --username alice
    python train_from_csv.py demo_user_alice.csv --username alice --create-if-missing

CSV must have these exact columns (order doesn't matter, names must match):
    ks_dwell_mean, ks_dwell_std, ks_flight_mean, ks_flight_std, ks_wpm,
    ks_error_rate, ms_speed_mean, ms_speed_std, ms_click_rate, ms_idle_ratio,
    ap_unique_count, ap_unknown_flag

This goes through the real ml.enrollment.enroll_user() path, so it also creates a
ModelMetadata row in the DB (training_samples, is_active, timestamps) - not just
the .pkl/.json files on disk.
"""

import argparse
import csv

from behavioral_guardian.config.settings import FROZEN_FEATURE_NAMES
from behavioral_guardian.database.connection import init_db, session_scope
from behavioral_guardian.database.models import User
from behavioral_guardian.ml.enrollment import enroll_user


def load_feature_rows(csv_path: str) -> list[dict]:
    rows = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        missing = set(FROZEN_FEATURE_NAMES) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing required columns: {missing}")

        for raw_row in reader:
            rows.append({name: float(raw_row[name]) for name in FROZEN_FEATURE_NAMES})
    return rows


def main():
    parser = argparse.ArgumentParser(description="Enroll a user's model from a CSV of feature rows.")
    parser.add_argument("csv_path", help="Path to the feature CSV (e.g. demo_user_alice.csv)")
    parser.add_argument("--username", required=True, help="username to enroll (must exist in the user table)")
    parser.add_argument(
        "--create-if-missing",
        action="store_true",
        help="If the username doesn't exist yet, create a bare-minimum User row for it first.",
    )
    args = parser.parse_args()

    feature_rows = load_feature_rows(args.csv_path)
    print(f"Loaded {len(feature_rows)} feature rows from {args.csv_path}")

    if len(feature_rows) < 10:
        print(f"Warning: only {len(feature_rows)} rows - enrollment normally expects 7-10 days of data.")

    init_db()  # no-op if tables already exist

    with session_scope() as db:
        user = db.query(User).filter(User.username == args.username).first()

        if user is None:
            if not args.create_if_missing:
                raise SystemExit(
                    f"No user found with username='{args.username}'. "
                    f"Pass --create-if-missing to auto-create one, or enroll an existing user."
                )
            user = User(username=args.username, full_name=args.username.title())
            db.add(user)
            db.flush()  # populates user.id before we use it below
            print(f"Created new user '{args.username}' with id={user.id}")

        metadata = enroll_user(db, user.id, feature_rows)
        # pull out plain values now, before the session closes and objects expire
        user_id = user.id
        model_version = metadata.model_version
        training_samples = metadata.training_samples
        is_active = metadata.is_active

    print(f"Done. Enrolled user_id={user_id} (username='{args.username}')")
    print(f"  - model_version: {model_version}")
    print(f"  - training_samples: {training_samples}")
    print(f"  - is_active: {is_active}")
    print(f"  - artifacts: behavioral_guardian/data/models/{user_id}/")


if __name__ == "__main__":
    main()
