import logging
import subprocess
import sys
from os import environ, getcwd, getenv
from pathlib import Path

from alpa.config import AlpaRepoConfig, MetadataConfig
from alpa.constants import REQUEST_LABEL
from alpa.gh import GithubAPI
from alpa.repository.branch import AlpaRepoBranch
from copr.v3.proxies.package import PackageProxy
from github.Issue import Issue


if getenv("INPUT_DEBUG") == "true" or getenv("RUNNER_DEBUG") == "1":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
else:
    logging.basicConfig(level=logging.ERROR, stream=sys.stdout)

logger = logging.getLogger(__name__)


NO_CONTRIBUTING_MSG = (
    "Sorry, but this repository does not have "
    "enabled option for other contributors to contribute."
)


class Manager:
    def __init__(self) -> None:
        self.alpa_repo = AlpaRepoBranch(
            (Path(getcwd())), GithubAPI("", environ["INPUT_GH-API-TOKEN"])
        )
        self.gh_repo = self.alpa_repo.gh_repo
        self.alpa_repo_config = AlpaRepoConfig.get_config()
        self.copr_proxy = PackageProxy(
            config={
                "copr_url": "https://copr.fedorainfracloud.org",
                "login": environ["INPUT_COPR-LOGIN"],
                "token": environ["INPUT_COPR-TOKEN"],
                "username": self.alpa_repo_config.copr_owner,
            }
        )

    @staticmethod
    def _refuse_and_close(issue: Issue) -> None:
        issue.create_comment(NO_CONTRIBUTING_MSG)
        issue.edit(state="closed")

    @staticmethod
    def _get_desired_package(issue: Issue) -> str:
        return issue.body.split()[-1]

    def _delete_package(self, issue_request: Issue) -> bool:
        pkg = self._get_desired_package(issue_request)
        self.alpa_repo.git_cmd(["switch", pkg])
        pkg_metadata = MetadataConfig.get_config()
        if issue_request.user.login not in [
            user.nick for user in pkg_metadata.maintainers
        ]:
            issue_request.create_comment("You are not the owner of this package")
            return True

        try:
            self.alpa_repo.git_cmd(["switch", "main"])
            self.alpa_repo.git_cmd(["push", self.alpa_repo.remote_name, "-d", pkg])
            self.copr_proxy.delete(
                self.alpa_repo_config.copr_owner, self.alpa_repo_config.copr_repo, pkg
            )
            return True
        except RuntimeError as exc:
            logger.error(f"Exception appeared when deleting package {exc}")
            return False

    def _request_package(self, issue_request: Issue) -> bool:
        try:
            pkg = self._get_desired_package(issue_request)
            self.alpa_repo.create_package(pkg)
            return True
        except RuntimeError as exc:
            logger.error(f"Exception appeared when requesting package {exc}")
            return False

    def react_to_trigger(self) -> int:
        issue_requests = self.gh_repo.get_issues("open", [REQUEST_LABEL]) or []
        filtered_issue_requests = []
        for issue in issue_requests:
            if issue.title.startswith(
                "[alpa request-new-package]"
            ) or issue.title.startswith("[alpa delete-package]"):
                filtered_issue_requests.append(issue)

        if not filtered_issue_requests:
            logger.info("No issue requests to react to.")
            return 0

        logger.info(f"Issue requests to react to {filtered_issue_requests}")
        if not self.alpa_repo_config.allow_foreign_contributing:
            logger.info("This repo doesn't not support foreign contributing.")
            for issue in filtered_issue_requests:
                self._refuse_and_close(issue)

        status = 0
        for issue in filtered_issue_requests:
            if issue.title.startswith("[alpa request-new-package]"):
                result = self._request_package(issue)
            else:
                result = self._delete_package(issue)

            issue.edit(state="closed")
            if result:
                issue.create_comment("Request was successfully completed")
            else:
                status = 1

        return status


if __name__ == "__main__":
    # TODO: investigate this bug in checkout action
    print(
        subprocess.run(
            [
                "git",
                "config",
                "--global",
                "--add",
                "safe.directory",
                "/github/workspace",
            ]
        )
    )
    sys.exit(Manager().react_to_trigger())
