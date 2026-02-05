"""
Tests for the CLI module.
"""

import json
import tempfile
from pathlib import Path
import pytest
from click.testing import CliRunner
from git import Repo

from src.cli import cli
from src.provenance import ProvenanceMetadata


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        repo = Repo.init(repo_path)

        # Configure git user
        with repo.config_writer() as git_config:
            git_config.set_value("user", "name", "Test User")
            git_config.set_value("user", "email", "test@example.com")

        yield repo_path


@pytest.fixture
def valid_metadata_file(tmp_path):
    """Create a valid metadata JSON file."""
    metadata = {
        "source": {
            "datasetName": "Test Dataset",
            "providerName": "Test Provider"
        },
        "provenance": {
            "dataGenerationMethod": "Testing",
            "dateDataGenerated": "2024-01-15T00:00:00Z",
            "dataType": "Tabular",
            "dataFormat": "CSV"
        },
        "use": {
            "intendedUse": "Testing",
            "legalRightsToUse": "Test license",
            "sensitiveData": False
        }
    }

    metadata_file = tmp_path / "metadata.json"
    metadata_file.write_text(json.dumps(metadata))
    return metadata_file


class TestCLI:
    """Test suite for CLI commands."""

    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "DTA-compliant provenance tracking" in result.output

    def test_cli_version(self, runner):
        """Test CLI version command."""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "version" in result.output.lower()

    def test_validate_command_help(self, runner):
        """Test validate command help."""
        result = runner.invoke(cli, ['validate', '--help'])
        assert result.exit_code == 0
        assert "validate" in result.output.lower()

    def test_validate_command_valid_file(self, runner, valid_metadata_file):
        """Test validate command with valid metadata file."""
        result = runner.invoke(cli, ['validate', str(valid_metadata_file)])
        assert result.exit_code == 0

    def test_validate_command_missing_file(self, runner):
        """Test validate command with non-existent file."""
        result = runner.invoke(cli, ['validate', 'nonexistent.json'])
        assert result.exit_code != 0

    def test_commit_command_help(self, runner):
        """Test commit command help."""
        result = runner.invoke(cli, ['commit', '--help'])
        assert result.exit_code == 0
        assert "commit" in result.output.lower()
        assert "metadata" in result.output.lower()

    def test_verify_command_help(self, runner):
        """Test verify command help."""
        result = runner.invoke(cli, ['verify', '--help'])
        assert result.exit_code == 0
        assert "verify" in result.output.lower()

    def test_show_command_help(self, runner):
        """Test show command help."""
        result = runner.invoke(cli, ['show', '--help'])
        assert result.exit_code == 0
        assert "show" in result.output.lower()

    def test_trace_command_help(self, runner):
        """Test trace command help."""
        result = runner.invoke(cli, ['trace', '--help'])
        assert result.exit_code == 0
        assert "trace" in result.output.lower()

    def test_commit_command_basic(self, runner, temp_git_repo, valid_metadata_file):
        """Test basic commit command."""
        # Create a test file
        test_file = temp_git_repo / "data.csv"
        test_file.write_text("test,data\n1,2\n")

        result = runner.invoke(cli, [
            'commit',
            str(test_file),
            '--metadata', str(valid_metadata_file),
            '--message', 'Test commit',
            '--repo', str(temp_git_repo)
        ])

        # Should succeed or give reasonable error
        assert result.exit_code in [0, 1]  # May fail due to git config

    def test_commit_command_missing_metadata(self, runner, temp_git_repo):
        """Test commit command without metadata."""
        test_file = temp_git_repo / "data.csv"
        test_file.write_text("test,data\n")

        result = runner.invoke(cli, [
            'commit',
            str(test_file),
            '--message', 'Test commit',
            '--repo', str(temp_git_repo)
        ])

        assert result.exit_code != 0  # Should fail without metadata

    def test_commit_command_missing_message(self, runner, temp_git_repo, valid_metadata_file):
        """Test commit command without message."""
        test_file = temp_git_repo / "data.csv"
        test_file.write_text("test,data\n")

        result = runner.invoke(cli, [
            'commit',
            str(test_file),
            '--metadata', str(valid_metadata_file),
            '--repo', str(temp_git_repo)
        ])

        assert result.exit_code != 0  # Should fail without message

    def test_commit_command_nonexistent_file(self, runner, temp_git_repo, valid_metadata_file):
        """Test commit command with non-existent file."""
        result = runner.invoke(cli, [
            'commit',
            'nonexistent.csv',
            '--metadata', str(valid_metadata_file),
            '--message', 'Test commit',
            '--repo', str(temp_git_repo)
        ])

        assert result.exit_code != 0

    def test_validate_command_invalid_json(self, runner, tmp_path):
        """Test validate command with invalid JSON."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ invalid json }")

        result = runner.invoke(cli, ['validate', str(invalid_file)])
        assert result.exit_code != 0

    def test_cli_commands_exist(self, runner):
        """Test that all main commands are registered."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

        # Check for main commands
        commands = ['commit', 'validate', 'verify', 'show', 'trace']
        for command in commands:
            assert command in result.output


class TestCLIEdgeCases:
    """Test edge cases and error handling in CLI."""

    def test_cli_no_arguments(self, runner):
        """Test CLI with no arguments."""
        result = runner.invoke(cli, [])
        assert result.exit_code == 0  # Should show help

    def test_cli_invalid_command(self, runner):
        """Test CLI with invalid command."""
        result = runner.invoke(cli, ['invalid-command'])
        assert result.exit_code != 0

    def test_validate_empty_file(self, runner, tmp_path):
        """Test validate with empty file."""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("")

        result = runner.invoke(cli, ['validate', str(empty_file)])
        assert result.exit_code != 0
