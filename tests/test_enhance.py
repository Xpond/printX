import threading
import uuid
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image
import core.enhance
from core.enhance import enhance
from core.thumbnails import thumbnail


def run(path, original, prompt):
    options = {'token': uuid.uuid4().hex, 'key': 'sk-test', 'model': 'test/model', 'prompt': prompt,
               'original': str(original)}
    output, = enhance([str(path)], options, lambda *event: None, threading.Event())
    return output


def test_versions_are_named_after_the_original_and_unstretched(tmp_path, monkeypatch):
    original = tmp_path / 'photo 🖨.png'
    Image.new('RGB', (300, 200), '#318ba0').save(original, dpi=(150, 150))
    prompts = []

    def answer(image, prompt, key, model):
        prompts.append(prompt)
        return [Image.new('RGB', (600, 390), 'red')]  # 2.6% squashed, as Muse's size grid does.

    monkeypatch.setattr(core.enhance, 'edit', answer)
    first = run(original, original, 'Make it sharp ')
    second = run(first, original, 'Make it warmer')  # The next instruction builds on the last version.
    assert prompts[0] == 'Make it sharp\nKeep everything else exactly as it is.'
    assert Path(first).name == 'photo 🖨_enhanced.png' and Path(second).name == 'photo 🖨_enhanced (2).png'
    with Image.open(second) as result:
        assert result.size == (600, 400)
        assert result.info['dpi'] == pytest.approx((150, 150), abs=.05)  # PNG stores pixels per metre.


def test_a_new_shape_that_was_asked_for_is_kept(tmp_path, monkeypatch):
    original = tmp_path / 'photo.jpg'
    Image.new('RGB', (300, 200)).save(original)
    monkeypatch.setattr(core.enhance, 'edit', lambda image, prompt, key, model: [Image.new('RGB', (400, 400))])
    with Image.open(run(original, original, 'Make it square')) as result:
        assert result.size == (400, 400)


def test_thumbnails_can_be_bigger(photo):
    data, kind, size = thumbnail(photo, 512)
    assert kind == 'pixels' and size == (600, 400)
    assert Image.open(BytesIO(data)).size == (512, 341)
