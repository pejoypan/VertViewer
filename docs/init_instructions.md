# init.yaml

```yaml
ui:
  size: [1920, 1080]   # 窗口总尺寸
  stretch: [16, 0, 9]  # [左半边的stretch, _, 右半边的stretch]
  image_port: "tcp://127.0.0.1:5555"  # 用于获取图片的端口
  # log_port: "tcp://127.0.0.1:5556"  # 用于获取日志的端口
  frame_window:
    size_hint: [352, 352]
    scale_hint: 0.34375
    num_cols: 3        # 列
    num_rows: 2        # 行
    spacing: [20, 10]  # 窗口间的间隔 [横向，竖向]
    user_id: ["cam#0", "cam#1", "cam#2", "cam#3", "cam#4"] 
```

- 单个图像的原始尺寸应 == size_hint / scale_hint
- user_id 应该与 VisionEdgeRT 中 basler_camera/basler_emulator 节点的 user_id 相对应

