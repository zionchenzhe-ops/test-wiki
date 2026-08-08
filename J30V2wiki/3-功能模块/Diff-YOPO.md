# Diff-YOPO 端到端自主导航

!!! info "📖 本章导读"
    本章介绍基于 Diff-YOPO 的端到端自主导航功能。内容包括两大部分：

    1. **参数确认**：检查途径点坐标、任务执行方式、飞行速度及虚拟天花板等关键配置
    2. **自主导航飞行**：启动程序并执行自动/手动两种任务模式

**原理简介**：Diff-YOPO 是无人机端到端自主导航算法——与[自主导航](自主导航.md)中基于地图规划的 Diff-Navigation 不同，YOPO 直接"看到什么就决定怎么飞"，是神经网络驱动的飞行控制。两者可以互相补充。

**算法简介**：Diff-YOPO 是在天津大学开源端到端规划器 YOPO（You Only Plan Once，IEEE RA-L 2024）基础上，针对 非凸-α 平台深度优化的自主飞行规划方案。YOPO 的核心思想是用一个神经网络完成传统方案中"感知建图 → 路径搜索 → 轨迹优化"的全部工作，端到端输出飞行轨迹，结构简单、响应快。Diff-YOPO 在保留这一架构优势的同时，将感知与定位方案全面升级为激光雷达体系，使 非凸-α 具备高速、稳定的全自主避障飞行能力。

**核心特性**：
- **看得更远**：感知输入由双目相机升级为 MID360/MID360S 激光雷达，突破相机约 10 m 的感知距离限制，高速飞行下避障反应时间更充足
- **定位更稳**：标配 Fast-LIO2 激光惯性定位，在弱纹理、暗光环境及机身高速抖动等视觉定位易失效的场景下依然稳定可靠
- **感知不漏检**：针对室内墙面、门框、走廊等薄结构障碍物优化感知精度，显著降低漏检风险
- **飞行高度可控**：支持设定飞行高度上限，避免飞行过程中高度异常爬升
- **决策更可靠**：修正特定工况下目标方向判断异常的问题，自主飞行行为更符合预期

**与开源 YOPO 的主要差异**：

| 维度 | 开源 YOPO | Diff-YOPO（非凸-α） |
| --- | --- | --- |
| 感知输入 | 双目相机深度图（约 10 m 范围） | MID360/MID360S 激光雷达，感知距离大幅提升 |
| 定位方案 | 依赖外部提供里程计 | 标配 Fast-LIO2 激光惯性定位 |
| 高度约束 | 无 | 支持飞行高度上限设定 |
| 薄结构感知 | 一般 | 针对墙面、门框、走廊等场景专项优化 |
| 工程框架 | 多节点（论文版）/ 单节点（YOPO-Simple 分支） | 基于 YOPO-Simple 分支重构的单节点方案 |

**技术要点**：
- **激光雷达深度感知**：网络训练时"看"的是相机视角的透视深度图，直接喂雷达点云会导致障碍物大小、形状与训练数据不匹配。Diff-YOPO 通过自研的点云转深度图算法，将 360° 雷达点云严格按相机成像模型转换为与训练输入完全一致的深度图——相当于给激光雷达装了一个"相机视角翻译器"，感知范围变大而不损失识别精度
- **仿真与真机一致性**：训练数据生成链路做了同步改造，仿真中渲染出的雷达数据与真机数据采用同一套成像模型，保证网络在仿真里学到的能力可以完整迁移到真机，消除"仿真飞得好、真机不一样"的虚实差异
- **虚拟天花板**：通过设定一个不可见的高度上限，从感知层面阻止无人机向上爬升，解决原版容易飞高的问题，在室内等限高场景下更可控

**参考资料**：
- 论文：You Only Plan Once: A Learning-Based One-Stage Planner With Guidance Learning（IEEE RA-L 2024）
- 开源代码：https://github.com/TJU-Aerial-Robotics/YOPO

!!! warning "⚠️ 注意"
    * 无人机 YOPO 端到端自主导航安全通行临界间距为 1.7m——即通道宽度低于 1.7m 时无人机无法安全通过

## 参数确认

在启动程序之前，请务必核对以下关键参数。相关配置项位于 `Diff-YOPO/YOPO/config/config.yaml` 文件中。

<img src="https://cdn.jsdelivr.net/gh/zionchenzhe-ops/test-wiki@main/J30V2wiki/images/modules/YOPO/111.png" width="1000" />

### 1. 检查途径点坐标 `points`

<img src="https://cdn.jsdelivr.net/gh/zionchenzhe-ops/test-wiki@main/J30V2wiki/images/modules/YOPO/point.png" width="1000" />

| 参数名 | 默认值 | 说明 |
| --- | --- | --- |
| points | - | 航点列表（统一格式: [x, y, z, time]）<br>x, y, z - 目标位置坐标 (m)<br>time - 到达后停留时间 (秒)，0 表示不停留 |

### 2. 检查多点巡航参数

* **自动执行任务**时的参数设置：
  * `auto_planning` 设为 `1`：无人机起飞并悬停后将自动开始执行航线规划。
  * `auto_landing` 设为 `1`：无人机到达最后一个目标点后将自动降落。
* **手动执行任务**时的参数设置：
  * `auto_planning` 设为 `0`：无人机起飞悬停后需手动按下遥控器 SD 键触发航线规划；执行完毕后，再次按下 SD 键方可触发返航至 `back_points` 点。
  * `auto_landing` 设为 `0`：到达最后一个目标点后需手动按下遥控器 SD 键，方可触发降落。

<img src="https://cdn.jsdelivr.net/gh/zionchenzhe-ops/test-wiki@main/J30V2wiki/images/modules/YOPO/auto.png" width="1000" />

| 参数名 | 默认值 | 说明 |
| --- | --- | --- |
| auto_planning | 1 | 起飞悬停后是否自动开始规划 |
| auto_landing | 1 | 到达最后一个点后是否自动降落 |

### 3. 检查飞行速度 `velocity`

<img src="https://cdn.jsdelivr.net/gh/zionchenzhe-ops/test-wiki@main/J30V2wiki/images/modules/YOPO/velocity.png" width="1000" />

| 参数名 | 默认值 | 说明 |
| --- | --- | --- |
| velocity | 2 | 飞行速度 |

### 4. 检查虚拟天花板参数

`virtual_ceiling_enable` 应设置为 `true`。

<img src="https://cdn.jsdelivr.net/gh/zionchenzhe-ops/test-wiki@main/J30V2wiki/images/modules/YOPO/virtual.png" width="1000" />

| 参数名 | 默认值 | 说明 |
| --- | --- | --- |
| virtual_ceiling_enable | true | 无人机的飞行高度将被限制在指定的绝对高度以下，防止意外飞得过高 |
| virtual_ceiling_z | 2.0 | 世界坐标系下的绝对高度上限，无人机的 Z 坐标（高度）将不会超过此值 |

## 自主导航飞行

1. 将无人机放置于安全、平整地面，以无人机为中心半径50cm的四周请勿放置任何障碍物。打开遥控器，SC键切换成解锁模式，将左侧摇杆保持中位，右侧摇杆保持中位，将SB键切换到自主飞行模式（一档），SE键保持弹出状态。

2. 进入 `Diff-YOPO` 工作空间并启动脚本：

```bash
cd ~/Diff-YOPO
./sh_files/run_all.sh
```

!!! warning "⚠️ 注意"
    * 程序启动完成前，请勿移动无人机，否则会导致定位出错

3. **开始执行任务**：

- **方式一：自动执行任务**（`auto_planning=1`、`auto_landing=1`）
  按下SD键，此时无人机会自主起飞至设定高度，然后开始自动规划至目标点，依次到达目标点后，自动降落。待飞机安全着陆后，将遥控器的SC键改为上锁模式。

- **方式二：手动执行任务**（`auto_planning=0`、`auto_landing=0`）
  按下SD键，此时无人机会自主起飞至设定高度。**第二次**按下SD键，无人机开始依次自动规划至各个目标点。**第三次**按下SD键，无人机开始自动规划到返航点。**第四次**按下SD键，自动降落。待飞机安全着陆后，将遥控器的SC键改为上锁模式。

自动执行任务视频演示：

<p>
  <video width="950" controls>
    <source src="https://diffrobots.oss-cn-hangzhou.aliyuncs.com/j30v2-wiki/video/YOPO.mp4" type="video/mp4">
  </video>
</p>

---

**相关章节**：[自主导航](自主导航.md) | [异常处置](../5-速查与排障/异常处置.md)
