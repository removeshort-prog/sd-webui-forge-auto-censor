# [自动打码] 开发交接说明

本扩展只负责二次元静态图片自动打码，与图片工坊的压缩、水印、透明超分保持独立。不要把两个扩展重新合并。

## 数据流

```text
图片 → RGBA 读取/方向校正 → BGR 检测 → 目标框
     → 矩形/椭圆/GrabCut 遮罩 → 扩边缘
     → 全图马赛克或模糊 → 只替换遮罩区域 → 保留 Alpha → 日期文件夹输出
```

`AnimeDetector` 延迟导入 `imgutils.detect.detect_censors`，所以没有安装检测依赖时 Forge 仍能启动。检测器只返回半开区间框 `(x0, y0, x1, y1)`，渲染逻辑不依赖具体模型。

## 为什么使用 imgutils

GitHub 对比后选择 `deepghs/imgutils`：MIT 许可证、持续维护，并直接提供 `detect_censors` 和二次元检测模型。NudeNet 面向真人内容且使用 AGPL-3.0，不属于本扩展范围。

## 依赖边界

`dghs-imgutils 0.19.0` 是当前可用版本，但元数据声明 `numpy<2`。Forge Neo 使用 NumPy 2，因此安装器必须使用 `pip install --no-deps -r requirements-censor.txt`，再按文件补齐直接依赖。不要改回普通 `pip install -r`，也不要为了它降级 Forge 的 NumPy。

模型文件由 Hugging Face Hub 按需下载。网络受限时使用 `HF_ENDPOINT=https://hf-mirror.com` 启动 Forge；不要把模型权重提交到仓库。

## Forge 规则

- `scripts/auto_censor.py` 只注册一个 `[自动打码]` 页签。
- GPU/检测任务通过 `call_queue.queue_lock` 串行，并在 `finally` 中恢复 Forge 状态。
- `--hide-ui-dir-config` 时隐藏目录输入和打开文件夹按钮，后端仍拒绝目录操作。
- 输出写入 `YYYY-MM-DD` 日期文件夹，不创建每次任务的子文件夹；文件名带运行编号，避免同一天重复处理时覆盖已有结果。
- 日期取任务开始时的本机日期；输出根目录不能等于输入目录或其上级。
- `rows` 仅用于页面统计和错误提示，不生成 CSV。ZIP 只从本次 `result.outputs` 打包，不能扫描整个日期目录。
- 取消时保留已经写出的图片和 ZIP。

## 验证

```powershell
python -B -m unittest discover -s tests -v
```

纯算法测试不等于模型下载或真实检测通过。交接时分别记录测试、Gradio 页面构建、模型下载和人工抽查结果。
