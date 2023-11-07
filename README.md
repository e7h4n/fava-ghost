# fava-ghost

`fava-ghost`是一个为运行和管理[fava](https://github.com/beancount/fava)实例而设计的高效后台守护进程，它结合了Docker容器化技术，使得部署、更新和管理fava服务变得简单快捷。

## 特性

- **自动化同步**：自动从git仓库同步fava账本文件。
- **依赖性管理**：自动管理和安装Python依赖，确保 fava 运行环境始终为最新状态。
- **冲突解决**：在发现合并冲突时会提醒用户手动解决。
- **自动备份**：定期备份你的 fava 账本，确保数据安全。
- **容器化**：使用 Docker 容器，简化部署和迁移。