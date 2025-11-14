#!/usr/bin/env python3
"""
Initialize CSV database files with proper headers
"""
import os
import csv
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
CSV_DIR = BASE_DIR / "data" / "csv_files"
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
GENERATED_DIR = BASE_DIR / "data" / "generated"


def create_directories():
    """Create necessary directories"""
    directories = [
        CSV_DIR,
        UPLOAD_DIR / "audio",
        GENERATED_DIR / "audio",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def initialize_csv_files():
    """Initialize CSV files with headers"""
    csv_files = {
        "chat_messages.csv": [
            "id",
            "session_id",
            "user_message",
            "bot_response",
            "transcription",
            "audio_url",
            "timestamp",
            "language_code",
        ],
        "users.csv": [
            "id",
            "email",
            "username",
            "password_hash",
            "role",
            "created_at",
            "updated_at",
            "is_active",
            "last_login",
        ],
        "doctors.csv": [
            "user_id",
            "license_number",
            "specialization",
            "hospital",
            "years_experience",
            "verification_status",
        ],
        "patients.csv": [
            "user_id",
            "date_of_birth",
            "blood_group",
            "medical_history_summary",
            "emergency_contact",
        ],
        "reports.csv": [
            "id",
            "patient_id",
            "uploaded_by_id",
            "report_type",
            "file_path",
            "upload_date",
            "processed_status",
            "analysis_result",
            "created_at",
        ],
        "visualizations.csv": [
            "id",
            "report_id",
            "fibo_params_id",
            "image_path",
            "generation_date",
            "complexity_level",
            "approved_by",
            "corrections_count",
            "quality_score",
        ],
    }

    for filename, headers in csv_files.items():
        filepath = CSV_DIR / filename

        # Only create if doesn't exist
        if not filepath.exists():
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            print(f"✓ Initialized: {filename}")
        else:
            print(f"⊘ Already exists: {filename}")


def main():
    """Main initialization function"""
    print("\n" + "=" * 60)
    print("FIBOMed - CSV Database Initialization")
    print("=" * 60 + "\n")

    print("Creating directories...")
    create_directories()

    print("\nInitializing CSV files...")
    initialize_csv_files()

    print("\n" + "=" * 60)
    print("✓ Initialization complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
