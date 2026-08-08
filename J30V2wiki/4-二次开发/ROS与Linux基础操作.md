# ROS 与 Linux 基础操作

!!! info "📖 本章导读"
    * 非凸-α 机载电脑运行 Ubuntu 20.04 + ROS Noetic，所有程序（启动、调试、查看状态）都需要通过终端命令完成
    * 本章面向零基础用户，简要介绍 Linux 终端和 ROS 的核心概念与最常用命令，帮助你快速入门
    * 每个主题只做入门概览。想深入学习请跳转到末尾的[推荐学习资源](#四推荐学习资源)

## 一、Linux 终端基础

### 1.1 认识终端

终端（Terminal）是人机交互的命令行界面。非凸-α 机载电脑是无图形界面的 Ubuntu 系统，所有操作都要在终端里敲命令完成。

**如何打开终端**：

- **NoMachine 远程桌面**：连接后，桌面右键选择 "Open Terminal"，或按 `Ctrl + Alt + T`
- **SSH 远程登录**：在你自己的电脑终端中输入 `ssh nv@<无人机 IP>`（用户名和密码均为 `nv`）
- **外接显示屏**：HDMI 连接后，和普通 Ubuntu 一样 `Ctrl + Alt + T`

> 💡 更多连接方式见[实名激活与连接机载电脑](../1-快速上手/实名激活与连接机载电脑.md)。

### 1.2 常用文件操作

在终端里，你需要通过命令来浏览和管理文件。以下是最常用的几个：

| 命令 | 作用 | 示例 |
| --- | --- | --- |
| `pwd` | 查看当前所在目录 | `pwd` → `/home/nv` |
| `ls` | 列出当前目录的文件和子目录 | `ls`、`ls -la`（显示隐藏文件） |
| `cd <目录>` | 切换到指定目录 | `cd ~/Diff-Navigation`（`~` 表示 home 目录） |
| `mkdir <目录>` | 新建目录 | `mkdir my_project` |
| `cp <源> <目标>` | 复制文件或目录 | `cp file.txt backup/` |
| `mv <源> <目标>` | 移动/重命名文件 | `mv old_name.txt new_name.txt` |
| `rm <文件>` | 删除文件（不可恢复） | `rm temp.txt`、`rm -rf` 删除目录 |

> 📖 深入学习：[Ubuntu 命令行入门教程](https://ubuntu.com/tutorials/command-line-for-beginners)

### 1.3 权限与超级用户

Linux 是多用户系统，部分操作（如安装软件、访问硬件串口）需要管理员权限：

- **`sudo`**：以超级用户身份执行一条命令。例如 `sudo apt install vim`
- **`sudo chmod 777 /dev/tty*`**：修改硬件设备（串口）的读写权限，非凸-α 在启动 mavros 前经常需要这条命令

> ⚠️ `sudo` 权限很高，不要随便复制网上的 `sudo` 命令执行。只在确认安全后使用。

> 📖 深入学习：[Linux 权限详解](https://linux.vbird.org/linux_basic/centos7/0210filepermission.php)

### 1.4 进程管理

运行中的程序叫"进程"。以下是最常用的进程控制操作：

| 操作 | 作用 |
| --- | --- |
| `Ctrl + C` | 终止当前终端正在运行的程序（最常用） |
| `Ctrl + Z` | 暂停当前程序并放入后台 |
| `ps aux` | 列出所有正在运行的进程 |
| `kill <PID>` | 强制终止指定进程（PID 从 `ps aux` 获取） |

**实用场景**：如果程序卡死，`Ctrl + C` 无效，可以新开一个终端，用 `ps aux | grep ros` 找到相关进程的 PID，然后用 `kill -9 <PID>` 强制终止。

> 📖 深入学习：[Linux 进程管理入门](https://linux.vbird.org/linux_basic/centos7/0440processcontrol.php)

### 1.5 文本编辑器

在终端中编辑配置文件时，需要用到终端编辑器。推荐新手从 **nano** 开始：

```bash
nano 文件名    # 打开文件编辑
```

- 编辑完成后按 `Ctrl + X` → 提示是否保存时按 `Y` → 回车确认文件名
- 界面底部有快捷键提示（`^` 表示 Ctrl 键），上手门槛极低

**vim** 功能更强大但学习曲线较陡，建议先会用 `nano` 解决日常需求，再根据需要学习 vim。

> 📖 深入学习：[vim 交互式教程](https://www.openvim.com/) | [nano 官方指南](https://www.nano-editor.org/dist/latest/nano.html)

### 1.6 软件包管理

Ubuntu 使用 `apt` 管理软件包：

```bash
sudo apt update              # 刷新软件包列表（安装新软件前必做）
sudo apt install <包名>      # 安装软件（如 sudo apt install terminator）
sudo apt upgrade             # 升级所有已安装的软件包
```

> 📖 深入学习：[apt 包管理指南](https://ubuntu.com/server/docs/package-management)

---

## 二、ROS 基础概念

ROS（Robot Operating System）是一个开源的机器人软件开发框架。非凸-α 使用 **ROS Noetic** 版本。

### 2.1 什么是 ROS

ROS 的核心概念可以用三句话概括：

- **节点（Node）**：每个节点是一个独立的程序，负责一项具体工作（如相机驱动、路径规划）。多个节点共同协作完成无人机飞行任务
- **话题（Topic）**：节点之间通过"话题"传递数据。比如相机节点把图像发布到 `/camera/image` 话题上，检测节点订阅这个话题来读取图像
- **消息（Message）**：话题上传输的数据格式，类似于结构体。图像、雷达点云、电池状态都是不同类型的消息


### 2.2 工作空间与编译

非凸-α 上的每个功能模块都是一个独立的 **ROS 工作空间**（workspace），目录结构如下：

```text
~/Diff-Navigation/          ← 工作空间根目录
├── src/                    ← 源代码
├── devel/                  ← 编译产物（setup.zsh 在这里）
└── sh_files/               ← 启动脚本
```

**关键操作**：

| 命令 | 作用 | 什么时候用 |
| --- | --- | --- |
| `catkin_make` | 编译工作空间中的所有代码 | 修改源码后、首次拉取代码后 |
| `source devel/setup.zsh` | 让终端识别该工作空间中的 ROS 包 | 每次打开新终端都必须执行 |

**为什么每次都要 `source`**：不执行这条命令，终端就不知道你写的包在哪里。每次新开终端都是一个全新的环境，所以启动脚本（如 `navigation.sh`）里通常已经帮你写好了 `source` 命令。

> 📖 深入学习：[ROS 工作空间教程](http://wiki.ros.org/catkin/Tutorials/create_a_workspace)

### 2.3 常用 ROS 命令

非凸-α 日常使用中最常接触的 ROS 命令：

| 命令 | 作用 | 示例 |
| --- | --- | --- |
| `roslaunch` | 启动一个或多个节点（最常用） | `roslaunch mavros px4.launch` |
| `rostopic echo <话题>` | 查看话题上的实时数据 | `rostopic echo /mavros/battery` |
| `rostopic list` | 列出所有当前活跃的话题 | — |
| `rosnode list` | 列出所有正在运行的节点 | — |
| `rosbag record <话题>` | 录制数据到 bag 文件 | `rosbag record /camera/image_raw` |
| `rqt_image_view` | 打开图像可视化窗口 | — |

> 📖 深入学习：[ROS Wiki 官方教程](http://wiki.ros.org/ROS/Tutorials)（推荐从 Beginner Level 开始）

---

## 三、在非凸-α 上的典型工作流

### 3.1 多终端操作

非凸-α 的功能模块通常需要同时运行多个程序（例如 mavros 占一个终端、定位占一个、规划占一个）。你需要学会管理多个终端窗口：

- **方法一**：开多个终端标签页（NoMachine 终端自带标签功能）
- **方法二**：使用 **Terminator**（推荐）—— 一个终端窗口可以分割成多个小窗口，还能同时向所有窗口广播相同命令

```bash
sudo apt install terminator    # 安装 Terminator
```

> 💡 如果你在做集群实验，多机操控技巧见[集群避障飞行](../3-功能模块/集群.md)。

### 3.2 启动程序的通用步骤

无论使用哪个功能模块（自主导航、目标跟踪、YOPO 等），启动流程都是类似的：

1. **进入工作空间**：`cd ~/<工作空间名>`（如 `cd ~/Diff-Navigation`）
2. **（如果需要）编译**：`catkin_make`（只在首次或修改源码后需要）
3. **启动脚本**：`./sh_files/<脚本名>.sh`（脚本里已经写好了 `source` 和 `roslaunch`）
4. **等待就绪**：等待约 30-50 秒，直到终端不再刷屏、没有红色报错
5. **操作无人机**：通过遥控器 SD 键等方式触发飞行任务
6. **结束程序**：任务完成后，在终端按 `Ctrl + C` 逐个停止程序

### 3.3 程序异常时怎么办

| 现象 | 处理方式 |
| --- | --- |
| 程序无响应 | 先按 `Ctrl + C`，等程序退出后重新启动 |
| `Ctrl + C` 无效 | 新开一个终端，`ps aux \| grep ros` 找到进程 PID，`kill -9 <PID>` 强制终止 |
| 报错 `Permission denied` | 加上 `sudo` 或 `sudo chmod 777 /dev/设备名` |
| 报错 `command not found` | 检查是否漏了 `source devel/setup.zsh`，或包名拼写错误 |
| 报错 `roscore` 相关 | 确认 ROS 环境已正确安装（`/opt/ros/noetic/setup.zsh`） |
| 定位发散、飞行失控 | 立即按遥控器 SE 键切换悬停，或 SC 键紧急上锁 |

> 💡 飞行中的救机流程见[异常处置](../5-速查与排障/异常处置.md)；更多排障技巧见[FAQ](../5-速查与排障/FAQ.md)。

---

## 四、推荐学习资源

本章只做入门概览，以下资源适合系统学习：

### Linux

| 资源 | 说明 | 链接 |
| --- | --- | --- |
| Ubuntu 官方命令行教程 | 英文，零基础友好，从"什么是终端"开始 | [ubuntu.com/tutorials](https://ubuntu.com/tutorials/command-line-for-beginners) |
| 鸟哥的 Linux 私房菜 | 中文经典，体系完整，适合系统学习 | [linux.vbird.org](https://linux.vbird.org/) |
| Linux 命令行基础 | 菜鸟教程，中文，速查式学习 | [runoob.com/linux](https://www.runoob.com/linux/linux-tutorial.html) |

### ROS

| 资源 | 说明 | 链接 |
| --- | --- | --- |
| ROS Wiki 官方教程 | 英文，ROS 权威教程，从 Beginner Level 开始读 | [wiki.ros.org/ROS/Tutorials](http://wiki.ros.org/ROS/Tutorials) |
| 古月居 ROS 入门 | 中文 ROS 入门系列，视频 + 文章 | [guyuehome.com](https://www.guyuehome.com/) |
| ROS Noetic 文档 | ROS Noetic 版本的官方文档 | [wiki.ros.org/noetic](http://wiki.ros.org/noetic) |

---

**相关章节**：[代码获取与维护](代码获取与维护.md) | [二次开发接口说明](二次开发接口说明.md) | [指令速查手册](../5-速查与排障/指令速查手册.md) | [FAQ](../5-速查与排障/FAQ.md)
