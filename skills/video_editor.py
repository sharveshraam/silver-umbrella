"""FFmpeg/MoviePy video editing helpers."""
import subprocess
from pathlib import Path
class VideoEditor:
    """Trim, merge, subtitle, crop, and mix videos using FFmpeg."""
    def trim(self, src, dst, start, duration):
        """Trim a clip with fast H.264 output."""; subprocess.run(['ffmpeg','-y','-ss',str(start),'-i',src,'-t',str(duration),'-c:v','libx264','-preset','veryfast','-c:a','aac',dst],check=True); return dst
    def crop_vertical(self, src: str, dst: str) -> str:
        """Crop to 9:16 vertical for YouTube Shorts."""; subprocess.run(["ffmpeg","-y","-i",src,"-vf","crop=ih*9/16:ih","-c:v","libx264","-preset","veryfast","-c:a","aac",dst], check=True); return dst
    def merge(self, clips: list[str], dst: str) -> str:
        """Concatenate a list of video clips into one file."""
        list_path = Path(dst).with_suffix(".txt"); list_path.write_text("\n".join(f"file '{c}'" for c in clips), encoding='utf-8')
        subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(list_path),"-c","copy",dst], check=True); list_path.unlink(missing_ok=True); return dst
    def add_subtitles(self, src: str, srt_path: str, dst: str) -> str:
        """Burn SRT subtitles into a video."""; subprocess.run(["ffmpeg","-y","-i",src,"-vf",f"subtitles={srt_path}","-c:v","libx264","-preset","veryfast","-c:a","aac",dst], check=True); return dst
    def add_audio(self, src: str, audio: str, dst: str) -> str:
        """Mix background audio track into a video."""; subprocess.run(["ffmpeg","-y","-i",src,"-i",audio,"-filter_complex","[1:a]volume=0.3[a2];[0:a][a2]amix=inputs=2[a]","-map","0:v","-map","[a]","-c:v","libx264","-preset","veryfast","-shortest",dst], check=True); return dst
