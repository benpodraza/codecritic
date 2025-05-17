from __future__ import annotations

from app.abstract_classes.tool_provider_base import ToolProviderBase


class SonarCloudToolProvider(ToolProviderBase):
    def _run(self, project_key: str, organization: str, token: str):
        self.logger.info(
            "SonarCloud stub executed for project '%s' in organization '%s'.",
            project_key,
            organization,
        )
        return {
            "status": "success",
            "project_key": project_key,
            "organization": organization,
            "analysis_url": "https://sonarcloud.io/dashboard?id=" + project_key,
        }
