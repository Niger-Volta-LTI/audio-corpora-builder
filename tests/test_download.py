"""
Tests for download_youtube module.
"""

import os
import pytest

from download_youtube import validate_url, build_yt_dlp_command


class TestValidateUrl:
    """Tests for validate_url function."""

    def test_validate_url_valid_playlist(self):
        """Valid playlist URL should pass validation."""
        url = "https://www.youtube.com/watch?v=ABC123&list=PLxyz"
        is_valid, result = validate_url(url, "playlists")
        assert is_valid is True
        assert "ABC123" in result

    def test_validate_url_valid_user(self):
        """Valid user URL should pass validation."""
        url = "https://www.youtube.com/user/OrisunTv"
        is_valid, result = validate_url(url, "users")
        assert is_valid is True

    def test_validate_url_empty(self):
        """Empty URL should fail validation."""
        is_valid, result = validate_url("", "playlists")
        assert is_valid is False
        assert "Empty URL" in result

    def test_validate_url_none(self):
        """None URL should fail validation."""
        is_valid, result = validate_url(None, "users")
        assert is_valid is False

    def test_validate_url_missing_https(self):
        """URL without https should fail validation."""
        url = "http://youtube.com/watch?v=ABC"
        is_valid, result = validate_url(url, "playlists")
        assert is_valid is False
        assert "must start with" in result

    def test_validate_url_with_whitespace(self):
        """URL with whitespace should be trimmed."""
        url = "  https://youtube.com/watch?v=ABC  "
        is_valid, result = validate_url(url, "playlists")
        assert is_valid is True
        assert result == "https://youtube.com/watch?v=ABC"


class TestBuildYtDlpCommand:
    """Tests for build_yt_dlp_command function."""

    def test_build_playlist_command(self):
        """Playlist command should include archive and no-post-overwrites."""
        cmd = build_yt_dlp_command(
            source="https://youtube.com/playlist?list=ABC",
            source_type="playlists",
            output_path="/tmp/output",
            max_downloads=100,
        )

        assert "yt-dlp" in cmd[0]
        assert "--download-archive" in cmd
        assert "--no-post-overwrites" in cmd
        assert "--max-downloads" in cmd
        assert "100" in cmd

    def test_build_users_command(self):
        """Users command should have max 10 downloads."""
        cmd = build_yt_dlp_command(
            source="https://youtube.com/user/Test",
            source_type="users",
            output_path="/tmp/output",
            max_downloads=100,
        )

        assert "--max-downloads" in cmd
        max_idx = cmd.index("--max-downloads")
        assert cmd[max_idx + 1] == "10"

    def test_build_command_output_path(self):
        """Command should use correct output path."""
        cmd = build_yt_dlp_command(
            source="https://youtube.com/watch?v=ABC",
            source_type="playlists",
            output_path="/custom/path",
            max_downloads=50,
        )

        assert "/custom/path/%(track)s-%(id)s.%(ext)s" in cmd

    def test_build_command_audio_format(self):
        """Command should respect audio format."""
        cmd = build_yt_dlp_command(
            source="https://youtube.com/watch?v=ABC",
            source_type="playlists",
            output_path="/tmp",
            max_downloads=50,
            audio_format="mp3",
        )

        assert "--audio-format" in cmd
        format_idx = cmd.index("--audio-format")
        assert cmd[format_idx + 1] == "mp3"

    def test_build_command_invalid_source_type(self):
        """Invalid source type should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown source type"):
            build_yt_dlp_command(
                source="https://youtube.com/watch?v=ABC",
                source_type="invalid",
                output_path="/tmp",
                max_downloads=50,
            )
