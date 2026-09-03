"""File and folder operations."""
from pathlib import Path
import shutil, hashlib
class FileManager:
    """Safe file-management utilities with confirmation handled by brain."""
    def create_folder(self, path): """Create a folder and parents."""; Path(path).mkdir(parents=True, exist_ok=True); return Path(path)
    def move(self, src, dst): """Move a file or folder."""; return shutil.move(src,dst)
    def organize(self, folder):
        """Sort files in a folder by extension into subfolders."""
        root=Path(folder); moved=[]
        for p in root.iterdir():
            if p.is_file():
                target=root/(p.suffix[1:].lower() or 'no_extension'); target.mkdir(exist_ok=True); moved.append(shutil.move(str(p), str(target/p.name)))
        return moved
    def duplicates(self, folder):
        """Find duplicate files by SHA-256 hash."""
        seen={}; dup=[]
        for p in Path(folder).rglob('*'):
            if p.is_file():
                h=hashlib.sha256(p.read_bytes()).hexdigest(); dup.append((seen[h],p)) if h in seen else seen.setdefault(h,p)
        return dup
