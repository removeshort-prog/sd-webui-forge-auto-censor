from __future__ import annotations

import html
import threading
import uuid
from pathlib import Path

import gradio as gr
from modules import call_queue, shared

from .censor import ANIME_EXTRA_TARGETS, IMAGE_EXTENSIONS, MODEL_LEVELS, CensorOptions, media_sources, run_censor_batch
from .engine import Cancelled

_jobs = {}
_jobs_lock = threading.Lock()


def directories_allowed():
    return not getattr(shared.cmd_opts, "hide_ui_dir_config", False)


def default_output():
    from modules.paths_internal import script_path

    return Path(script_path) / "outputs" / "auto-censor"


def open_output_folder(last_output, configured_output):
    if not directories_allowed():
        raise gr.Error("Forge 已禁用本机目录访问")
    from modules import util

    try:
        latest = str(last_output or "").strip()
        configured = str(configured_output or "").strip()
        directory = Path(latest or configured or default_output()).expanduser().resolve()
        if latest and not directory.is_dir():
            raise ValueError("最近一次输出文件夹已被移动或删除")
        directory.mkdir(parents=True, exist_ok=True)
        util.open_folder(str(directory))
    except (OSError, ValueError) as exc:
        raise gr.Error(f"无法打开输出文件夹：{exc}") from exc


def cancel_job(session):
    with _jobs_lock:
        event = _jobs.get(session)
        if event:
            event.set()
    return "<p>已请求停止，将在当前图片结束后保存已完成的结果。</p>" if event else "<p>当前没有自动打码任务。</p>"


def summary_html(result):
    esc = html.escape
    rows = []
    for row in result.rows[:100]:
        cells = [row.get(key, "") for key in ("输入文件", "状态", "检测框", "错误")]
        rows.append("<tr>" + "".join(f"<td>{esc(str(cell))}</td>" for cell in cells) + "</tr>")
    status = "已停止" if result.cancelled else "处理结束"
    return (
        f"<div class='fiw-report'><p><b>{status}</b> · 完成 {result.completed}/{result.total} 张图片 · "
        f"失败 {result.failed} 张 · {result.elapsed:.1f} 秒</p>"
        f"<p>保存位置：<code>{esc(str(result.directory))}</code></p>"
        "<table><thead><tr><th>输入</th><th>状态</th><th>检测框</th><th>错误</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
        "<p>自动检测不是人工审核的替代品，请抽查导出的图片。</p></div>"
    )


def execute(values, session, first_only, progress):
    event = threading.Event()
    with _jobs_lock:
        if session in _jobs:
            return [], [], "<p>本会话已有任务，请等待完成或先停止。</p>", gr.update()
        _jobs[session] = event
    try:
        options = CensorOptions(
            extra_targets=tuple(values.get("targets") or []),
            model_level=values.get("model_level", "s"),
            confidence=float(values["confidence"]), shape=values["shape"], mode=values["mode"],
            dilate_px=int(values["dilate"]), strength=int(values["strength"]),
            max_megapixels=float(values["max_megapixels"]),
        )
        options.validate()
        allow_dirs = directories_allowed()
        configured_output = str(values.get("output_dir") or "").strip()
        destination = Path(configured_output).expanduser() if configured_output else default_output()
        input_directory = str(values.get("input_dir") or "").strip()
        if values["input_mode"] == "本机文件夹" and input_directory:
            source_dir = Path(input_directory).expanduser().resolve()
            output_dir = destination.resolve()
            if source_dir == output_dir or output_dir in source_dir.parents:
                raise ValueError("输出目录不能等于输入目录或是它的上级目录")
        sources = media_sources(
            values["input_mode"], values.get("uploads"), input_directory,
            bool(values["recursive"]), values["sort"], allow_dirs, destination,
        )
        if first_only:
            sources = sources[:1]

        def check_cancel():
            if event.is_set() or shared.state.interrupted:
                raise Cancelled()

        progress(0, desc="等待 Forge 自动打码任务")
        with call_queue.queue_lock:
            shared.state.begin(job="自动打码")
            try:
                result = run_censor_batch(
                    sources, destination, options, check_cancel,
                    lambda fraction, description: progress(fraction, desc=description),
                    bool(values["make_zip"]),
                )
            finally:
                shared.state.end()
                shared.state.interrupted = False
                shared.state.skipped = False
                shared.state.stopping_generation = False
        downloads = ([str(result.archive)] if result.archive else []) + [str(result.report)]
        downloads.extend(str(path) for path in result.outputs[:100])
        return result.previews, downloads, summary_html(result), str(result.directory)
    except Exception as exc:
        return [], [], f"<div class='error'><b>无法自动打码：</b>{html.escape(str(exc))}</div>", gr.update()
    finally:
        with _jobs_lock:
            _jobs.pop(session, None)


def create_ui():
    allow_dirs = directories_allowed()
    with gr.Blocks(analytics_enabled=False) as panel:
        gr.HTML("<div class='fiw-header'><h2>[自动打码]</h2><p>二次元图片检测 · 马赛克/模糊 · 批量导出</p></div>")
        session = gr.State(value=lambda: uuid.uuid4().hex)
        last_output = gr.State(value="")
        with gr.Row():
            with gr.Column(scale=5):
                input_mode = gr.Radio(
                    ["上传图片", "本机文件夹"] if allow_dirs else ["上传图片"],
                    value="上传图片", label="输入方式")
                uploads = gr.File(label="上传静态图片（可多选）", file_count="multiple", type="filepath",
                                  file_types=sorted(IMAGE_EXTENSIONS))
                with gr.Group(visible=False) as folder_group:
                    input_dir = gr.Textbox(label="本机图片文件夹", placeholder="例如 D:\\待处理图片")
                    recursive = gr.Checkbox(label="包含子文件夹", value=True)
                sort = gr.Dropdown(
                    ["路径自然排序", "文件名自然排序", "修改时间从旧到新", "修改时间从新到旧"],
                    value="路径自然排序", label="处理顺序")
                model_level = gr.Dropdown(
                    [(label, code) for code, label in MODEL_LEVELS.items()],
                    value="s", label="二次元检测模型",
                    info="标准模型精度更高；轻量模型占用更低、速度更快。未缓存的模型首次使用会联网下载。",
                )
                confidence = gr.Slider(0.01, 0.99, value=0.25, step=0.01, label="置信度阈值")
                targets = gr.CheckboxGroup(
                    [(label, code) for code, label in ANIME_EXTRA_TARGETS.items()],
                    value=[], label="额外检测部位（penis / pussy 始终开启）")
                with gr.Row():
                    shape = gr.Radio(
                        [("贴合轮廓（GrabCut，失败回退椭圆）", "fit"), ("椭圆", "ellipse"), ("矩形", "rect")],
                        value="fit", label="遮罩形状")
                    mode = gr.Radio(
                        [("马赛克", "mosaic"), ("高斯模糊", "blur")], value="mosaic", label="打码方式")
                with gr.Row():
                    dilate = gr.Slider(0, 100, value=15, step=1, label="扩边缘（像素）")
                    strength = gr.Slider(4, 300, value=100, step=1, label="马赛克粒度 / 模糊强度")
                output_dir = gr.Textbox(
                    label="输出文件夹（留空使用 Forge/outputs/auto-censor）", visible=allow_dirs)
                with gr.Row():
                    make_zip = gr.Checkbox(label="生成 ZIP 和 CSV 报告", value=True)
                    max_megapixels = gr.Slider(1, 256, value=64, step=1, label="单张像素上限（百万像素）")
                gr.Markdown("首次使用请先安装 `requirements-censor.txt`；模型首次运行可能联网下载。")
            with gr.Column(scale=6):
                with gr.Row():
                    start = gr.Button("开始自动打码", variant="primary")
                    preview = gr.Button("试处理首张图片")
                    stop = gr.Button("停止打码")
                    open_folder = gr.Button("📂 打开输出文件夹", visible=allow_dirs)
                gallery = gr.Gallery(label="打码结果预览（最多 20 张）", columns=2, height=520,
                                     elem_id="fac-gallery")
                downloads = gr.File(label="下载 ZIP / 报告 / 图片", file_count="multiple", interactive=False)
                status = gr.HTML("<p>尚未运行自动打码。</p>")

        values = {
            "input_mode": input_mode, "uploads": uploads, "input_dir": input_dir,
            "recursive": recursive, "sort": sort, "model_level": model_level,
            "confidence": confidence, "targets": targets,
            "shape": shape, "mode": mode, "dilate": dilate, "strength": strength,
            "output_dir": output_dir, "make_zip": make_zip, "max_megapixels": max_megapixels,
        }

        def run(data, progress=gr.Progress()):
            return execute({key: data[component] for key, component in values.items()}, data[session], False, progress)

        def run_preview(data, progress=gr.Progress()):
            return execute({key: data[component] for key, component in values.items()}, data[session], True, progress)

        input_mode.change(lambda value: gr.update(visible=value == "本机文件夹" and allow_dirs),
                          inputs=input_mode, outputs=folder_group, queue=False)
        inputs = set(values.values()) | {session}
        start.click(run, inputs=inputs, outputs=[gallery, downloads, status, last_output])
        preview.click(run_preview, inputs=inputs, outputs=[gallery, downloads, status, last_output])
        stop.click(cancel_job, inputs=session, outputs=status, queue=False)
        open_folder.click(open_output_folder, inputs=[last_output, output_dir], outputs=[], queue=False, show_progress=False)
    return [(panel, "[自动打码]", "forge_auto_censor")]
