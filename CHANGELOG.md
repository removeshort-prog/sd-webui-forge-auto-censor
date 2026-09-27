# 更新日志

## v1.0.1 · 2026-09-28

- 模型已存在于 Hugging Face 本地缓存时自动离线读取，避免网络不可达导致的 `LocalEntryNotFoundError` 和无谓重试。
- 模型缺失或缓存目录错误时提供可执行的修复提示。

## v1.0.0 · 2026-09-27

- 从图片工坊拆出独立的 `[自动打码]` Forge Neo 扩展。
- 只处理静态图片，使用 dghs-imgutils 二次元检测。
- 支持 GrabCut/椭圆/矩形遮罩、马赛克/高斯模糊、透明 Alpha、批量 ZIP/CSV 报告。
- 安装器保留 Forge Neo NumPy 版本，避免 dghs-imgutils 的旧元数据触发降级。
