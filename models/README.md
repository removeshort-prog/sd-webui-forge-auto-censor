# 本地模型目录

将对应的 ONNX 权重直接放在此文件夹中：

```text
models/
  censor_detect_v1.0_s.onnx  # 标准模型
  censor_detect_v1.0_n.onnx  # 轻量模型
```

在页面选择 s 或 n 即加载对应文件。已有文件时无需联网或设置 Hugging Face 缓存变量。没有本地文件时，扩展先复制已下载的权重；找不到时才从 Hub 下载。两个模型按需安装，不必全部下载。

手动下载地址：

- [标准模型](https://huggingface.co/deepghs/anime_censor_detection/resolve/main/censor_detect_v1.0_s/model.onnx)，保存为 `censor_detect_v1.0_s.onnx`。
- [轻量模型](https://huggingface.co/deepghs/anime_censor_detection/resolve/main/censor_detect_v1.0_n/model.onnx)，保存为 `censor_detect_v1.0_n.onnx`。

权重是普通的本地文件，已加入 `.gitignore`。备份或手动迁移扩展时保留这些文件；删除后再次使用需要重新取得权重。
