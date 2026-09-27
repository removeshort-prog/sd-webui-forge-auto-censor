# 更新日志

## v1.0.0 · 2026-09-27

- 从图片工坊拆出独立的 `[自动打码]` Forge Neo 扩展。
- 只处理静态图片，使用 dghs-imgutils 二次元检测。
- 支持 GrabCut/椭圆/矩形遮罩、马赛克/高斯模糊、透明 Alpha、批量 ZIP/CSV 报告。
- 安装器保留 Forge Neo NumPy 版本，避免 dghs-imgutils 的旧元数据触发降级。
