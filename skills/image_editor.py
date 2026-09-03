"""Pillow image editing."""
from PIL import Image, ImageEnhance, ImageDraw
class ImageEditor:
    """Crop, resize, watermark, and convert images."""
    def resize(self, src, dst, size): """Resize an image."""; Image.open(src).resize(size).save(dst); return dst
    def watermark(self, src, dst, text): """Add a small text watermark."""; im=Image.open(src).convert('RGBA'); d=ImageDraw.Draw(im); d.text((20,20),text,fill=(0,255,255,220)); im.save(dst); return dst
