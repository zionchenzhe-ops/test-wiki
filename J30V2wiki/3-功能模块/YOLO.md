# YOLO 目标检测

!!! info "📖 本章导读"
    本章介绍如何使用 YOLO 模型进行目标检测。内容包括配置文件参数说明以及 YOLO 目标检测程序的启动与可视化查看。

**原理简介**：YOLO 是一种流行的目标检测算法，可以在图像中实时框出并识别出物体（如人、自行车、汽车等）。本章使用官方预训练模型（基于 COCO 数据集，支持 80 类目标），以识别"人"为例演示使用流程。

> 💡 本章需要**视觉追踪选配包**（单目摄像头）。

## 配置文件参数说明

- 配置文件位置：`YOLO/src/recognition/detection/config/yolo_config.yaml`
- 数据集说明：模型为官方模型，位于 `YOLO/src/recognition/detection/assets/yolov8m_int8.engine`，基于 COCO 数据集训练，包含80类目标，这里使用 person 类进行演示
- 参数说明：

```bash
# 一种类别的配置示例：
names: ["person"]  # 识别 person
colors
  "0": [0, 255, 255]  # 颜色为 黄色

# 多种类别的配置示例：
names: ["person", "bicycle", "car"]  # 分别识别 person，bicycle，car三类目标
colors
  "0": [0, 255, 255]  # person 颜色为 黄色
  "1": [255, 0, 0]  # bicycle 颜色为 蓝色
  "2": [0, 255, 0]  # car 颜色为 绿色
```

!!! warning "⚠️ 注意"
    * 当前默认仅支持"人"的识别。若需识别其他物体，需自行修改源码。

## 启动 YOLO 目标检测程序

按照以下步骤启动 YOLO 目标检测程序：

```bash
# 第一个终端输入
cd ~/YOLO
source devel/setup.zsh
roslaunch recognition yolo_detection_usb_camera.launch

# 第二个终端输入
rqt_image_view
```

## 查看检测结果

在 `rqt_image_view` 界面中选择 `/yolo_detection/visualization` 话题，即可看到 YOLO 检测结果，如下图：

<img src="https://cdn.jsdelivr.net/gh/zionchenzhe-ops/test-wiki@main/J30V2wiki/manual_media/media/image89.png" height="550" />

---

**相关章节**：[目标跟踪](目标跟踪.md) | [FAQ](../5-速查与排障/FAQ.md)
