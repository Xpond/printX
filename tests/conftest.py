import os
import sys
from pathlib import Path

os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['QT_QPA_PLATFORMTHEME'] = 'generic'
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from PIL import Image
import pymupdf


@pytest.fixture(autouse=True)
def isolated_logs(tmp_path, monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path / 'state'))
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path / 'state'))


@pytest.fixture
def photo(tmp_path):
    path = tmp_path / 'café photo 🖨.jpg'
    Image.new('RGB', (600, 400), '#318ba0').save(path, quality=95, dpi=(300, 300))
    return path


@pytest.fixture
def pdf(tmp_path):
    path = tmp_path / 'original.pdf'
    with pymupdf.open() as doc:
        for i in range(3):
            page = doc.new_page(width=300 + i * 10, height=420)
            page.insert_text((30, 50), f'Original page {i + 1}')
        doc[1].set_rotation(90)
        doc.save(path)
    return path
