import os
import re
import subprocess
import time
import multiprocessing
import argparse
from git import Repo, exc
import signal


class DaemonProcess(multiprocessing.Process):
    BEAN_CHECK_FILE = "main.bean"

    def __init__(
        self, repo_url, repo_credentials, repo_path, install_command, fava_command
    ):
        super().__init__()
        self.repo_path = repo_path
        self.install_command = install_command
        self.fava_command = fava_command
        self.repo = None
        self.fava_process = None

    def run(self):
        self.setup_repo()
        while True:
            time.sleep(10)
            try:
                self.update_and_run()
            except Exception as e:
                print(f"Error occurred: {e}")

    def setup_repo(self):
        self.repo = self.clone_or_open_repo()
        if not self.repo:
            raise Exception("Git repository initialization failed.")

        self.install_dependencies()
        self.run_fava()

    def clone_or_open_repo(self):
        if not os.path.exists(self.repo_path):
            return Repo.clone_from(self.formatted_git_url(), self.repo_path)
        return Repo(self.repo_path)

    def formatted_git_url(self):
        return self.GIT_REPO_URL.replace(
            "https://", f"https://{self.GIT_REPO_CREDENTIALS}@"
        )

    def update_and_run(self):
        if self.pull_changes():
            self.install_dependencies()
            self.run_fava()

    def pull_changes(self):
        if self.repo_has_conflicts() or self.repo_is_dirty():
            self.commit_local_changes()
        return self.fetch_and_merge_changes()

    def repo_has_conflicts(self):
        return any(self.has_conflict_markers(f) for f in self.find_conflicted_files())

    def find_conflicted_files(self):
        unmerged_blobs = self.repo.index.unmerged_blobs()
        return {
            path
            for path, blobs in unmerged_blobs.items()
            if any(stage != 0 for stage, _ in blobs)
        }

    def has_conflict_markers(self, file_path):
        conflict_markers = re.compile(r"^<<<<<<< |^======= |^>>>>>>> ", re.M)
        with open(file_path, "r") as file:
            return bool(conflict_markers.search(file.read()))

    def repo_is_dirty(self):
        return self.repo.is_dirty(untracked_files=True)

    def commit_local_changes(self):
        self.repo.git.add(A=True)
        if self.run_bean_check(self.BEAN_CHECK_FILE):
            self.repo.index.commit("Auto-commit by daemon process")

    def fetch_and_merge_changes(self):
        try:
            origin = self.repo.remotes.origin
            origin.fetch()
            local_commit = self.repo.head.commit
            remote_commit = origin.refs[self.repo.active_branch.name].commit

            is_behind = sum(
                1 for x in self.repo.iter_commits(f"{local_commit}..{remote_commit}")
            )
            is_ahead = sum(
                1 for x in self.repo.iter_commits(f"{remote_commit}..{local_commit}")
            )

            if is_behind or is_ahead:
                print(f"Is behind: {is_behind}, is ahead: {is_ahead}")

            if is_behind:
                origin.pull()
                return self.resolve_conflicts_if_any()

            if is_ahead:
                origin.push()

            return False
        except exc.GitCommandError as e:
            print(f"Git operation failed: {e}")
            return False

    def resolve_conflicts_if_any(self):
        if self.repo_has_conflicts():
            print("Merge conflicts detected after pull. Waiting for manual resolution.")
            return False
        return True

    def run_bean_check(self, file_path):
        try:
            result = subprocess.run(
                ["bean-check", file_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.repo_path,
            )
            print(result.stdout.decode())
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"Bean-check failed: {e.output.decode()}")
            return False

    def install_dependencies(self):
        subprocess.run(self.install_command, shell=True, check=True, cwd=self.repo_path)

    def run_fava(self):
        if self.is_fava_running():
            return
        self.terminate_fava_process()
        self.fava_process = subprocess.Popen(
            self.fava_command, shell=True, cwd=self.repo_path
        )

    def is_fava_running(self):
        return self.fava_process and self.fava_process.poll() is None

    def terminate_fava_process(self):
        if self.fava_process and self.fava_process.poll() is not None:
            try:
                os.kill(self.fava_process.pid, signal.SIGTERM)
                self.fava_process.wait()
            except OSError as e:
                print(f"Error terminating fava process: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="启动 fava-ghost 守护进程。")

    # 添加参数
    parser.add_argument("--repo-path", required=True, help="本地克隆仓库的路径")
    parser.add_argument("--repo-url", required=True, help="仓库的远程URL")
    parser.add_argument("--repo-credentials", required=True, help="访问远程仓库的凭证")

    # 解析命令行参数
    args = parser.parse_args()

    repo_path = args.repo_path
    repo_url = args.repo_url
    repo_credentials = args.repo_credentials
    install_command = "pip install -e ."
    fava_command = "fava main.bean"

    daemon = DaemonProcess(
        repo_url, repo_credentials, repo_path, install_command, fava_command
    )
    daemon.start()
