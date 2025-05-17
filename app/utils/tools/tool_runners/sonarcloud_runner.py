"""
SonarCloud client for conceptbuilder.

Assumes SONAR_TOKEN and SONAR_PROJECT_KEY are in env, or uses local fallback JSON.
"""

import os
import requests


def run_sonarcloud(code: str) -> str:
    token = os.getenv("SONAR_TOKEN")
    project = os.getenv("SONAR_PROJECT_KEY")

    if not token or not project:
        return "{}"

    try:
        params = {
            "component": project,
            "metricKeys": "complexity,code_smells,comment_lines_density,duplicated_lines_density"
        }
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get("https://sonarcloud.io/api/measures/component", params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        parsed = {
            m["metric"]: float(m["value"]) for m in data.get("component", {}).get("measures", [])
        }

        return str(parsed or {})  # Return actual metrics or empty

    except Exception as e:
        return f"{{'error': '{str(e)}'}}"

