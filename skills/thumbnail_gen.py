"""YouTube thumbnail generator."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2
class ThumbnailGenerator:
    """Extract a strong frame and overlay bold high-contrast text."""
    def best_frame(self, video_path: str) -> Image.Image:
        """Pick a frame near the middle of the video."""
        cap=cv2.VideoCapture(video_path); total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1); cap.set(cv2.CAP_PROP_POS_FRAMES,total//2); ok,frame=cap.read(); cap.release()
        if not ok: return Image.new('RGB',(1280,720),'#07111f')
        frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB); return Image.fromarray(frame).resize((1280,720))
    def generate(self, video_path: str, title: str, output: str) -> Path:
        """Generate a 1280x720 thumbnail with glow text."""
        im=self.best_frame(video_path).filter(ImageFilter.UnsharpMask()); overlay=Image.new('RGBA',im.size,(0,0,0,60)); im=Image.alpha_composite(im.convert('RGBA'),overlay); d=ImageDraw.Draw(im)
        font=ImageFont.truetype('arial.ttf',80) if Path('C:/Windows/Fonts/arial.ttf').exists() else ImageFont.load_default()
        d.text((60,520),title[:28],font=font,fill=(0,240,255,255),stroke_width=4,stroke_fill=(0,0,0,255)); out=Path(output); out.parent.mkdir(parents=True,exist_ok=True); im.convert('RGB').save(out,quality=92); return out
