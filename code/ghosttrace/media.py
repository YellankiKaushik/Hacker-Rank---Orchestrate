"""Local OCR and PDF text extraction. OCR cache is keyed by source content."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import sys


def image_text(path, cache_dir=None):
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    cached = Path(cache_dir)/f'{digest}.txt' if cache_dir else None
    if cached and cached.exists():
        return cached.read_text(encoding='utf-8')
    if sys.platform == 'win32':
        command = ['powershell.exe', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
                   '-File', str(Path(__file__).with_name('ocr.ps1')), '-ImagePath', str(Path(path).resolve())]
    elif shutil.which('tesseract'):
        command = ['tesseract', str(path), 'stdout', '-l', 'eng']
    else:
        raise RuntimeError('Screenshot OCR requires Windows English OCR or tesseract with English data')
    run = subprocess.run(command, capture_output=True, timeout=60)
    if run.returncode:
        raise RuntimeError(f'Local OCR failed for {Path(path).name}: {run.stderr.decode(errors="replace")[:400]}')
    text = run.stdout.decode('utf-8-sig')
    if not text.strip():
        raise ValueError(f'Empty OCR extraction: {Path(path).name}')
    if cached:
        cached.parent.mkdir(parents=True, exist_ok=True)
        cached.write_text(text, encoding='utf-8')
    return text


def pdf_text(path):
    from pypdf import PdfReader
    return '\n'.join(page.extract_text() or '' for page in PdfReader(path).pages)
