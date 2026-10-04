"""Tests for subprocess runner and docker container status inspection."""

import subprocess
import unittest
from unittest.mock import patch

from tests.hotspot import hotspot_manager


class RunArgsTests(unittest.TestCase):
    def test_uses_requested_timeout(self):
        completed = subprocess.CompletedProcess(["command"], 0, "ok\n", "")
        with patch.object(subprocess, "run", return_value=completed) as run:
            result = hotspot_manager.run_args(["command"], timeout=75)

        self.assertEqual(result, (True, "ok", ""))
        self.assertEqual(run.call_args.kwargs["timeout"], 75)


class DockerServiceTests(unittest.TestCase):
    def test_check_docker_container_running(self):
        with patch.object(hotspot_manager, "run_args", return_value=(True, "true", "")):
            self.assertTrue(hotspot_manager.check_docker_container("adguardhome"))

    def test_check_docker_container_stopped(self):
        with patch.object(
            hotspot_manager, "run_args", return_value=(True, "false", "")
        ):
            self.assertFalse(hotspot_manager.check_docker_container("adguardhome"))

    def test_check_docker_container_missing(self):
        with patch.object(
            hotspot_manager, "run_args", return_value=(False, "", "no such object")
        ):
            self.assertIsNone(hotspot_manager.check_docker_container("nonexistent"))


if __name__ == "__main__":
    unittest.main()
