# 练习 06：在 Linux 上运行并定位失败

每天怎么做：[阶段六逐日教程](../docs/daily/06-linux.md)，含 Linux 专用环境、可执行的 Bash 命令、四种故障与完成标准。

材料：[Linux 章节](../docs/LINUX.md)、scripts/run_regression.sh。

1. 在 Linux/WSL 新建自己的虚拟环境，安装依赖，运行本地回归。
2. 手动启动靶场，用 ps、ss、curl 找到正确进程、监听地址和健康响应。
3. 完成四种故障：服务未启动、端口占用、错误 token、测试路径不存在。每次保留命令、输出、退出码和结论。
4. 阅读脚本并解释路径引用、stderr、tee、set -euo pipefail。
5. 故意传不存在的测试路径给脚本，确认失败非零退出且仍保存日志；随后正常运行通过。

交付：docs/linux_practice.md、发行版/Python 版本、回归和排障证据。验收：在真实 Linux/WSL 完成，不用 Windows PowerShell 的运行记录替代；不通过 sudo 或批量 kill 绕过原因定位。
