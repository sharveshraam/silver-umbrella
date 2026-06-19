"""FFmpeg/MoviePy video editing helpers."""
import subprocess
class VideoEditor:
    """Trim, merge, subtitle, and export videos using FFmpeg."""
    def trim(self, src, dst, start, duration):
        """Trim a clip with fast H.264 output."""; subprocess.run(['ffmpeg','-y','-ss',str(start),'-i',src,'-t',str(duration),'-c:v','libx264','-preset','veryfast','-c:a','aac',dst],check=True); return dst
