# fava-ghost

`fava-ghost`是一个为运行和管理[fava](https://github.com/beancount/fava)实例而设计的高效后台守护进程，它结合了 Docker 容器化技术，使得部署、更新和管理 fava 服务变得简单快捷。

## 特性

- **自动化同步**：自动从 git 仓库同步 fava 账本文件。
- **依赖性管理**：自动管理和安装 Python 依赖，确保 fava 运行环境始终为最新状态。
- **冲突解决**：在发现合并冲突时会提醒用户手动解决。
- **容器化**：使用 Docker 容器，简化部署和迁移。

# Beancount 项目准备

fava-ghost 并不强制用户使用特定的 fava / beancount 版本，所以用户需要在自己的项目中指定 fava / beancount 版本。fava-ghost 使用 `pip install -e .` 来安装 fava / beancount，所以你需要在你的项目中添加 `setup.py` 文件，内容如下：

```python
from setuptools import setup

setup(
    install_requires=[
        'fava==1.26.2',
        'beancount==2.3.6',
    ],
)
```

# 使用

首先安装 fava-ghost:

```bash
pip install fava-ghost
```

fava-ghost 需要有读写仓库权限的 Github Credentials 来同步账本文件。你可以在 [这里](https://github.com/settings/tokens?type=beta) 申请一个 Github Fine-grained personal access token。然后启动 fava-ghost:

```bash
fava-ghost --repo-url https://github.com/REPO --repo-credentials GITHUB_TOKEN --repo-path PATH_TO_REPO
```

其中 PATH_TO_REPO 是你的账本仓库的本地路径，比如 `~/Documents/Beancount`。

就可以开始自动同步账本文件了。一旦启动，fava-ghost 会自动开始做如下事情:

1. clone 你的账本仓库到 PATH_TO_REPO
2. 在账本仓库下执行 pip 安装所需依赖
3. 启动 fava 服务
4. 每隔 10 秒尝试进行同步本地账本和代码仓库

# 同步策略

对于不同的情况，fava-ghost 会采取不同的同步策略：

1. 远程有更新，本地没有更新：自动 pull
2. 远程没有更新，本地有更新：自动 push
3. 远程和本地都有更新：执行 merge，如果没有冲突，则自动 push。如果有冲突，则需要用户手动编辑文件到文件中不存在冲突标记后，自动 push

# docker

fava-ghost 也可以通过 docker 运行。镜像是 `e7h4n/fava-ghost`。你可以通过如下命令运行：

```bash
docker run e7h4n/fava-ghost -d -p 5000:5000 --repo-url REPO_URL --repo-credentials GITHUB_TOKEN
```

通过 docker，你可以在任意一个环境下快速启动 fava 服务来托管你的 beancount 账本，无需解决环境问题。