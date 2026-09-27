# Forge Neo [自动打码]

这是一个独立的 SD WebUI Forge Neo 扩展，专门处理二次元静态图片自动打码。图片压缩、水印和透明图超分仍由 [图片工坊](https://github.com/removeshort-prog/sd-webui-forge-neo-image-workshop) 负责。

## 功能

- 使用 `dghs-imgutils` 检测二次元图片中的 `penis`、`pussy`，可选 `nipple_f`。
- 支持 PNG、WebP、JPEG、BMP、TIFF，保留 PNG/WebP/TIFF 的透明 Alpha。
- 支持 GrabCut 贴合轮廓、椭圆、矩形遮罩。
- 支持马赛克和高斯模糊，支持扩边缘、置信度和像素上限。
- 支持多图、文件夹、递归、自然排序、取消、ZIP 和 CSV 报告。
- 只接受静态单帧图片；GIF、视频和真人检测不属于本扩展范围。

## 安装

将仓库放入 Forge Neo 的 `extensions/sd-webui-forge-auto-censor`，完整重启 Forge Neo。也可以运行 `install.ps1` 或 `安装到Forge.bat`。

然后在 Forge Neo 根目录执行：

```powershell
$forge = "D:\A-forge neo\sd-webui-forge-neo"
& "$forge\venv\Scripts\python.exe" -m pip install --no-deps -r `
  "$forge\extensions\sd-webui-forge-auto-censor\requirements-censor.txt"
```

`dghs-imgutils 0.19.0` 的旧元数据要求 `numpy<2`，但 Forge Neo 使用 NumPy 2。安装命令使用 `--no-deps`，并在 requirements 中列出直接依赖，避免自动降级 Forge 核心环境。首次检测时，模型会从 Hugging Face 下载；网络受限时可在启动 Forge 前设置：

```powershell
$env:HF_ENDPOINT = "https://hf-mirror.com"
```

## 使用

打开 Forge Neo 的 **[自动打码]** 页签，上传图片或选择图片文件夹，先点击“试处理首张图片”，确认遮罩后再批量处理。结果会保存到 `Forge/outputs/auto-censor/` 的独立任务目录。

## 测试

```powershell
python -B -m unittest discover -s tests -v
```

模型下载、模型识别准确率和人工审核由使用者自行确认；自动检测结果不能替代人工检查。
