# Forge Neo [自动打码]

这是一个独立的 SD WebUI Forge Neo 扩展，专门处理二次元静态图片自动打码。图片压缩、水印和透明图超分仍由 [图片工坊](https://github.com/removeshort-prog/sd-webui-forge-neo-image-workshop) 负责。

<img width="2193" height="1351" alt="image" src="https://github.com/user-attachments/assets/803e329f-6b10-467f-8255-ba2ffacdd23d" />


## 功能

- 使用 `dghs-imgutils` 检测二次元图片中的 `penis`、`pussy`，可选 `nipple_f`。
- 提供标准 `s` 和轻量 `n` 两种二次元检测模型，可在页签中切换；未缓存的模型首次使用时下载。
- 支持 PNG、WebP、JPEG、BMP、TIFF，保留 PNG/WebP/TIFF 的透明 Alpha。
- 支持 GrabCut 贴合轮廓、椭圆、矩形遮罩。
- 支持马赛克和高斯模糊，支持扩边缘、置信度和像素上限。
- 支持多图、文件夹、递归、自然排序、取消和 ZIP 下载包。
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

扩展会优先从本扩展的 `models/` 目录读取 `censor_detect_v1.0_s/model.onnx`。首次找到或下载模型后会复制到这里长期保存；模型权重不提交到 GitHub。已保存时会自动使用离线读取，不再因为 Hugging Face 的网络检查失败而报 `LocalEntryNotFoundError`。如果模型还没有下载，先关闭 Forge，在 Forge 根目录执行下面的命令（镜像不可用时可去掉 `HF_ENDPOINT`）：

```powershell
$forge = "D:\A-forge neo\sd-webui-forge-neo"
$env:HF_ENDPOINT = "https://hf-mirror.com"
$env:HF_HOME = "$env:USERPROFILE\.cache\huggingface"
& "$forge\venv\Scripts\python.exe" -c "from huggingface_hub import hf_hub_download; print(hf_hub_download(repo_id='deepghs/anime_censor_detection', filename='censor_detect_v1.0_s/model.onnx'))"
```

如果模型已经下载但插件目录尚未建立模型文件，重新打开一次 `[自动打码]` 会自动从当前用户 Hugging Face 缓存复制；也可以在启动前固定目录：

```powershell
$env:HF_HOME = "C:\Users\cc9re\.cache\huggingface"
$env:HF_HUB_CACHE = "$env:HF_HOME\hub"
```

`webui-user.bat` 必须在 Forge 根目录启动，否则它找不到旁边的 `webui.bat`。PowerShell 请这样启动（变量名中的下划线前不要加反斜杠）：

```powershell
Push-Location $forge
& ".\webui-user.bat"
Pop-Location
```

## 使用

打开 Forge Neo 的 **[自动打码]** 页签，选择检测模型，上传图片或选择图片文件夹，先点击“试处理首张图片”，确认遮罩后再批量处理。结果会保存到 `Forge/outputs/auto-censor/YYYY-MM-DD/`，同一天的处理共用当天文件夹。

日期取任务开始时的本机日期，自定义输出目录也使用相同规则。文件名包含时间、随机编号、序号和原文件名，重复处理不会覆盖先前结果。ZIP 只包含本次任务的图片；处理统计和错误显示在页面，不生成 CSV 文件。

## 测试

```powershell
python -B -m unittest discover -s tests -v
```

模型下载、模型识别准确率和人工审核由使用者自行确认；自动检测结果不能替代人工检查。
