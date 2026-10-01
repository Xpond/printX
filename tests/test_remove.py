import base64
import json
import sys
import threading
import urllib.error
import urllib.request
import uuid
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image, ImageDraw
import core.remove
from core.files import JobError
from core.openrouter import edit
from core.remove import remove
from core.secret import seal, unseal


@pytest.fixture
def scene(tmp_path):
    """A red square on blue, with a white mark in the corner to remove."""
    path = tmp_path / 'product 🖨.jpg'
    image = Image.new('RGB', (800, 600), '#2050c0')
    draw = ImageDraw.Draw(image)
    draw.rectangle((300, 200, 500, 400), fill='#d02020')
    draw.rectangle((20, 20, 120, 60), fill='white')
    image.save(path, quality=95, dpi=(300, 300))
    return path


def model(prompts, *layers):
    """Stands in for the AI: answers at half size, base layer first to show the order does not matter."""
    def answer(image, prompt, key, name):
        assert image.size == (800, 600) and key == 'sk-test' and name == 'test/model'
        prompts.append(prompt)
        return [layer.copy() for layer in layers]
    return answer


def run(paths, events, **options):
    options = {'token': uuid.uuid4().hex, 'key': 'sk-test', 'model': 'test/model', 'what': '', **options}
    return remove([str(path) for path in paths], options, lambda *event: events.append(event), threading.Event())


def test_background_keeps_full_size_pixels_and_uses_the_cutout_alpha(scene, monkeypatch):
    base = Image.new('RGBA', (400, 300), '#2050c0')
    cutout = Image.new('RGBA', (400, 300), (0, 0, 0, 0))
    ImageDraw.Draw(cutout).rectangle((150, 100, 250, 200), fill='#c03030')  # The model's colours are ignored.
    prompts, events = [], []
    monkeypatch.setattr(core.remove, 'edit', model(prompts, base, cutout))
    output, = run([scene], events, mode='background', what='the red box ')
    assert prompts == ['Number of layers: 2. Layer 1: the red box, with a transparent background. '
                       'Layer 2: the background.']
    with Image.open(output) as result:
        assert Path(output).name == 'product 🖨_no_background.png'
        assert result.mode == 'RGBA' and result.size == (800, 600)
        assert result.info['dpi'] == pytest.approx((300, 300), abs=.01)  # PNG stores pixels per metre.
        assert result.getpixel((50, 500))[3] == 0
        red, green, blue, alpha = result.getpixel((400, 300))
        assert alpha == 255 and red > 190 and green < 50  # The original's pixels, not the model's.
    assert ('output', {'path': output}) in events


def test_something_else_patches_only_what_changed(scene, monkeypatch):
    base = Image.new('RGBA', (400, 300), '#2050c0')
    ImageDraw.Draw(base).rectangle((150, 100, 250, 200), fill='#d02020')  # The mark is gone; the rest is unchanged.
    mark = Image.new('RGBA', (400, 300), (0, 0, 0, 0))
    ImageDraw.Draw(mark).rectangle((10, 10, 60, 30), fill='white')
    prompts, events = [], []
    monkeypatch.setattr(core.remove, 'edit', model(prompts, base, mark))
    output, = run([scene], events, mode='object', what='the white mark')
    assert prompts == ['Number of layers: 2. Layer 1: the white mark, with a transparent background. '
                       'Layer 2: everything except the white mark.']
    with Image.open(scene) as original, Image.open(output) as result:
        assert Path(output).name == 'product 🖨_edited.jpg'
        assert result.size == (800, 600) and result.info['dpi'] == pytest.approx((300, 300))
        assert all(abs(a - b) < 40 for a, b in zip(result.getpixel((70, 40)), (0x20, 0x50, 0xc0)))
        for point in [(300, 200), (500, 400), (700, 550)]:  # Sharp edges far from the mark stay the original's.
            assert all(abs(a - b) < 8 for a, b in zip(result.getpixel(point), original.getpixel(point)))


def test_an_answer_with_nothing_removed_is_skipped(scene, monkeypatch, tmp_path):
    with Image.open(scene) as original:
        unchanged = original.convert('RGBA').resize((400, 300))
    events = []
    monkeypatch.setattr(core.remove, 'edit', model([], unchanged))
    for mode in ('background', 'object'):
        with pytest.raises(JobError, match='no_outputs'):
            run([scene], events, mode=mode, what='the moon')
    assert [payload['code'] for kind, payload in events if kind == 'skipped'] == ['ai_nothing'] * 2
    assert list(tmp_path.iterdir()) == [scene]  # Nothing saved, staging removed.


class Answer(BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def test_openrouter_request_and_errors(monkeypatch):
    sent = {}
    data = BytesIO()
    Image.new('RGB', (10, 10), 'red').save(data, 'WEBP')

    def reply(request, timeout):
        sent.update(json.loads(request.data), auth=request.get_header('Authorization'))
        return Answer(json.dumps({'data': [{'b64_json': base64.b64encode(data.getvalue()).decode()}]}).encode())

    monkeypatch.setattr(urllib.request, 'urlopen', reply)
    image, = edit(Image.new('RGB', (3000, 1000)), 'Remove it', 'sk-test', 'test/model')
    assert image.format == 'WEBP' and image.size == (10, 10)
    reference = sent['input_references'][0]
    assert sent['auth'] == 'Bearer sk-test' and sent['model'] == 'test/model' and sent['prompt'] == 'Remove it'
    assert reference['type'] == 'image_url' and reference['image_url']['url'].startswith('data:image/jpeg;base64,')
    sent_image = Image.open(BytesIO(base64.b64decode(reference['image_url']['url'].partition(',')[2])))
    assert sent_image.size == (2048, 683)  # Shrunk before sending.
    for code, expected in [(401, 'ai_key'), (402, 'ai_credit'), (429, 'ai_busy'), (503, 'ai_busy'), (404, 'ai_model'),
                           (400, 'ai_failed')]:
        def refuse(request, timeout, code=code):
            raise urllib.error.HTTPError(request.full_url, code, 'No', {}, BytesIO(b'{"error": "no"}'))
        monkeypatch.setattr(urllib.request, 'urlopen', refuse)
        with pytest.raises(JobError, match=expected):
            edit(Image.new('RGB', (10, 10)), 'Remove it', 'sk-test', 'test/model')

    def offline(request, timeout):
        raise urllib.error.URLError('no route')
    monkeypatch.setattr(urllib.request, 'urlopen', offline)
    with pytest.raises(JobError, match='ai_offline'):
        edit(Image.new('RGB', (10, 10)), 'Remove it', 'sk-test', 'test/model')
    monkeypatch.setattr(urllib.request, 'urlopen', lambda request, timeout: Answer(b'{"data": []}'))
    with pytest.raises(JobError, match='ai_failed'):
        edit(Image.new('RGB', (10, 10)), 'Remove it', 'sk-test', 'test/model')


def test_key_is_sealed_at_rest():
    sealed = seal('sk-or-v1-secret')
    assert unseal(sealed) == 'sk-or-v1-secret'
    assert unseal('') == '' and unseal('not base64!') == ''
    if sys.platform == 'win32':
        assert b'secret' not in base64.b64decode(sealed)  # Encrypted for this Windows user, not just encoded.
