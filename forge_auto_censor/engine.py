class Cancelled(Exception):
    """The current Forge task was cancelled."""


def check_pixels(size, max_megapixels):
    if size[0] * size[1] > max_megapixels * 1_000_000:
        raise ValueError(f"图像 {size[0]}×{size[1]} 超过 {max_megapixels:g} 百万像素限制")
