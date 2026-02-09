"""
Pre-commit hooks for automated DTA provenance validation.

Provides entry points for pre-commit framework to validate metadata
files and check commit messages for DTA trailers.
"""

import sys
import json
from pathlib import Path
from typing import List, Sequence

from .verify import ProvenanceVerifier


def validate_metadata_hook(argv: Sequence[str] = None) -> int:
    """
    Pre-commit hook to validate DTA provenance JSON files.

    This hook validates that JSON files with provenance metadata
    comply with DTA v1.0.0 standards. Non-provenance JSON files
    are silently passed through.

    Args:
        argv: List of file paths to validate (from pre-commit)

    Returns:
        0 if all files are valid, 1 otherwise
    """
    if argv is None:
        argv = sys.argv[1:]

    verifier = ProvenanceVerifier()
    failed_files = []

    for file_path_str in argv:
        file_path = Path(file_path_str)

        # Skip non-JSON files
        if file_path.suffix != '.json':
            continue

        try:
            with open(file_path) as f:
                data = json.load(f)

            # Check if this looks like a DTA provenance file
            # (has source, provenance, and use sections)
            if not all(key in data for key in ['source', 'provenance', 'use']):
                # Not a provenance file, skip validation
                continue

            # Validate against DTA standards
            report = verifier.validate_dta_compliance(data)

            if not report.is_valid:
                failed_files.append((file_path, report))
                print(f"\n❌ Validation failed: {file_path}", file=sys.stderr)
                print(str(report), file=sys.stderr)

        except json.JSONDecodeError as e:
            print(f"\n❌ Invalid JSON in {file_path}: {e}", file=sys.stderr)
            failed_files.append((file_path, None))
        except Exception as e:
            print(f"\n❌ Error validating {file_path}: {e}", file=sys.stderr)
            failed_files.append((file_path, None))

    if failed_files:
        print(f"\n❌ {len(failed_files)} file(s) failed validation", file=sys.stderr)
        return 1

    return 0


def check_trailers_hook(argv: Sequence[str] = None) -> int:
    """
    Pre-commit hook to check commit messages for DTA trailers.

    Verifies that commits with provenance metadata include the required
    DTA trailers (DTA-Provenance-Version, DTA-Provenance-Hash, etc.).

    This hook is designed to work with commit-msg hook stage.

    Args:
        argv: List containing path to commit message file

    Returns:
        0 if commit message is valid, 1 otherwise
    """
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) < 1:
        print("❌ Usage: check-trailers <commit-msg-file>", file=sys.stderr)
        return 1

    commit_msg_file = Path(argv[0])

    try:
        with open(commit_msg_file) as f:
            commit_message = f.read()
    except FileNotFoundError:
        print(f"❌ Commit message file not found: {commit_msg_file}", file=sys.stderr)
        return 1

    # Check if this commit includes provenance metadata
    has_metadata = 'DTA-Provenance-Metadata:' in commit_message

    if not has_metadata:
        # No provenance metadata, nothing to check
        return 0

    # If metadata is present, verify required trailers
    required_trailers = [
        'DTA-Provenance-Version:',
        'DTA-Provenance-Hash:',
        'DTA-Dataset-Name:',
        'DTA-Provenance-Metadata:'
    ]

    missing_trailers = []
    for trailer in required_trailers:
        if trailer not in commit_message:
            missing_trailers.append(trailer.rstrip(':'))

    if missing_trailers:
        print("\n❌ Commit message has provenance metadata but missing required trailers:",
              file=sys.stderr)
        for trailer in missing_trailers:
            print(f"  - {trailer}", file=sys.stderr)
        print("\nUse 'dta-provenance commit' to create properly formatted commits.",
              file=sys.stderr)
        return 1

    # Validate that the metadata JSON is well-formed
    for line in commit_message.split('\n'):
        if line.startswith('DTA-Provenance-Metadata:'):
            metadata_json = line.split(':', 1)[1].strip()
            try:
                metadata = json.loads(metadata_json)

                # Quick sanity check
                if not all(key in metadata for key in ['source', 'provenance', 'use']):
                    print("\n❌ DTA-Provenance-Metadata is malformed (missing required sections)",
                          file=sys.stderr)
                    return 1

            except json.JSONDecodeError as e:
                print(f"\n❌ DTA-Provenance-Metadata contains invalid JSON: {e}",
                      file=sys.stderr)
                return 1

    return 0


if __name__ == '__main__':
    # Allow direct invocation for testing
    if len(sys.argv) > 1 and sys.argv[1] == 'validate':
        sys.exit(validate_metadata_hook(sys.argv[2:]))
    elif len(sys.argv) > 1 and sys.argv[1] == 'check-trailers':
        sys.exit(check_trailers_hook(sys.argv[2:]))
    else:
        print("Usage: python -m src.hooks [validate|check-trailers] <files...>")
        sys.exit(1)
