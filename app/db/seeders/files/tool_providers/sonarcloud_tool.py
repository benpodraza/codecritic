import os
import subprocess
import time
import uuid
import json
import tempfile
from pathlib import Path
from typing import Dict
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema

class SonarCloudToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> ToolOutputSchema:
        target_path = Path(input.get("target"))
        if not target_path.exists():
            raise FileNotFoundError(f"{target_path} does not exist")

        github_token, sonar_token, sonar_project, sonar_org, github_user = self._load_env()

        metrics = {}
        stdout_msg = ""

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_url = f"https://github.com/{github_user}/codecritic_scoring"
            subprocess.run(["gh", "repo", "clone", repo_url, tmpdir], check=True)

            filename = f"test_{uuid.uuid4()}.py"
            src_dir = Path(tmpdir) / "src"
            src_dir.mkdir(parents=True, exist_ok=True)
            target_dest = src_dir / filename
            target_dest.write_text(target_path.read_text(encoding="utf-8"))

            self._git_push(filename, cwd=src_dir)
            self._wait_for_scan_completion(sonar_token, sonar_project)
            metrics = self._poll_sonarcloud_metrics(sonar_token, sonar_project)
            stdout_msg = f"Scan complete for {filename}"

            if metrics:
                self._git_cleanup(filename, cwd=src_dir)

        return ToolOutputSchema(
            return_code=0,
            stdout=stdout_msg,
            metrics=metrics,
            summary="SonarCloud scan completed successfully"
        )


    def _load_env(self) -> tuple[str, str, str, str, str]:
        github_token = os.getenv("GITHUB_TOKEN")
        sonar_token = os.getenv("SONAR_TOKEN")
        sonar_project = os.getenv("SONAR_PROJECT_KEY")
        sonar_org = os.getenv("SONAR_ORGANIZATION_KEY")
        github_user = os.getenv("GITHUB_USERNAME")
        if not all([github_token, sonar_token, sonar_project, sonar_org, github_user]):
            raise EnvironmentError("Missing one or more required environment variables")
        return github_token, sonar_token, sonar_project, sonar_org, github_user

    def _git_push(self, filename: str, cwd: Path) -> None:
        subprocess.run(["git", "checkout", "main"], cwd=cwd.parent, check=True)
        subprocess.run(["git", "pull"], cwd=cwd.parent, check=True)
        subprocess.run(["git", "add", f"src/{filename}"], cwd=cwd.parent, check=True)
        subprocess.run(["git", "commit", "-m", f"Add test file src/{filename}"], cwd=cwd.parent, check=True)
        subprocess.run(["git", "push"], cwd=cwd.parent, check=True)

    def _git_cleanup(self, filename: str, cwd: Path) -> None:
        subprocess.run(["git", "rm", f"src/{filename}"], cwd=cwd.parent, check=True)
        subprocess.run(["git", "commit", "-m", f"Remove test file src/{filename}"], cwd=cwd.parent, check=True)
        subprocess.run(["git", "push"], cwd=cwd.parent, check=True)

    def _wait_for_scan_completion(self, sonar_token: str, sonar_project: str) -> None:
        url = f"https://sonarcloud.io/api/ce/component?component={sonar_project}"
        for attempt in range(20):
            time.sleep(10)
            result = subprocess.run(
                ["curl", "-s", "-u", f"{sonar_token}:", url],
                capture_output=True,
                text=True
            )
            try:
                parsed = json.loads(result.stdout)
                status = parsed.get("current", {}).get("status")
                if status == "SUCCESS":
                    return
            except Exception as e:
                print(f"⚠️ Error reading scan status: {e}")

    def _poll_sonarcloud_metrics(self, sonar_token: str, sonar_project: str) -> Dict[str, int]:
        metric_keys = ",".join([
            "bugs", "vulnerabilities", "security_hotspots", "code_smells",
            "coverage", "line_coverage", "lines_to_cover", "tests",
            "test_errors", "test_failures", "skipped_tests",
            "lines", "ncloc", "functions", "classes", "statements",
            "complexity", "cognitive_complexity",
            "duplicated_lines", "duplicated_blocks", "duplicated_files", "duplicated_lines_density"
        ])

        api_url = (
            f"https://sonarcloud.io/api/measures/component"
            f"?component={sonar_project}&metricKeys={metric_keys}"
        )

        for attempt in range(10):
            time.sleep(5)
            result = subprocess.run(
                ["curl", "-s", "-u", f"{sonar_token}:", api_url],
                capture_output=True,
                text=True
            )
            try:
                parsed = json.loads(result.stdout)
                measures = parsed.get("component", {}).get("measures", [])
                return {m["metric"]: float(m["value"]) for m in measures}
            except Exception as e:
                print(f"⚠️ Error parsing metrics: {e}")
        return {}

