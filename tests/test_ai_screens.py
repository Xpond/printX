import sys

import pytest
from PIL import Image
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QLabel, QLineEdit
from core.openrouter import MODELS
from core.secret import seal, unseal
from ui import text as T
import ui.settings
from ui.settings import Settings
from ui.window import Window


@pytest.fixture(autouse=True)
def accepted_keys(monkeypatch):
    """Settings ask OpenRouter about the saved key; here every key is accepted unless a test says otherwise."""
    monkeypatch.setattr(ui.settings, 'key_problem', lambda key: '')


def test_api_key_is_write_only_and_models_follow_the_defaults(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / 'settings.ini'), QSettings.Format.IniFormat)
    window = Window(settings)
    qtbot.addWidget(window)
    page = window.preferences
    assert page.key.echoMode() == QLineEdit.EchoMode.Normal  # You can see what you pasted before saving.
    assert page.key.placeholderText() == T.KEY_HINT
    page.key.setText(' sk-or-v1-secret ')
    page.models['enhance'].setText('meta/muse-image-2')
    page.save()
    assert page.key.text() == '' and page.key.placeholderText() == T.KEY_SAVED  # The empty box says so.
    qtbot.waitUntil(lambda: page.message.text() == T.KEY_WORKS)  # Checked with OpenRouter after saving.
    assert unseal(settings.value('ai/key')) == 'sk-or-v1-secret'
    assert settings.value('ai/remove_model') == '' and settings.value('ai/enhance_model') == 'meta/muse-image-2'
    page.save()  # Saving again without a new key keeps the old one.
    assert unseal(settings.value('ai/key')) == 'sk-or-v1-secret'
    reopened = Window(settings)
    qtbot.addWidget(reopened)
    assert reopened.preferences.key.text() == '' and reopened.preferences.key.placeholderText() == T.KEY_SAVED
    assert reopened.preferences.models['remove'].text() == MODELS['remove']


def test_remove_needs_a_key_and_a_description(qtbot, tmp_path, photo, monkeypatch):
    settings = QSettings(str(tmp_path / 'settings.ini'), QSettings.Format.IniFormat)
    window = Window(settings)
    qtbot.addWidget(window)
    window.show()
    window.home.selected.emit('remove')
    screen = window.remove
    assert window.stack.currentWidget() == screen and window.ai.isVisible()
    screen.add_files([str(photo)])
    assert not screen.run.isEnabled() and screen.output_hint.text() == T.NEEDS_KEY
    window.preferences.key.setText('sk-or-v1-secret')
    window.preferences.save()
    assert screen.run.isEnabled() and screen.run.text() == 'Remove background from 1 image'
    screen.mode.setCurrentIndex(screen.mode.findData('object'))
    assert screen.target.isVisible() and not screen.keep.isVisible() and not screen.run.isEnabled()
    screen.target.setPlainText('the watermark')
    assert screen.run.isEnabled() and screen.run.text() == 'Remove it from 1 image'
    started = {}
    monkeypatch.setattr(screen.jobs, 'start', lambda paths, options: started.update(options))
    qtbot.keyClick(screen.target, Qt.Key.Key_Return)  # Enter runs it.
    assert started['tool'] == 'remove' and started['mode'] == 'object' and started['what'] == 'the watermark'
    assert started['key'] == 'sk-or-v1-secret' and started['model'] == MODELS['remove']
    assert settings.value('remove/mode') == 'object' and settings.value('remove/target') == 'the watermark'
    window.go_back()
    assert not window.ai.isVisible()


def test_enhance_is_a_conversation_about_one_photo(qtbot, tmp_path, photo, monkeypatch):
    settings = QSettings(str(tmp_path / 'settings.ini'), QSettings.Format.IniFormat)
    settings.setValue('ai/key', seal('sk-or-v1-secret'))
    window = Window(settings)
    qtbot.addWidget(window)
    window.show()
    window.home.selected.emit('enhance')
    screen = window.enhance
    assert window.ai.isVisible() and not screen.run.isEnabled()
    screen.add_files([str(tmp_path / 'notes.pdf'), str(photo)])  # Only the photo is used.
    image, caption = screen.chat.pictures[str(photo)]
    assert screen.model.paths == [str(photo)]
    qtbot.waitUntil(lambda: caption.text().endswith('600 × 400 px'), timeout=10000)  # Its preview loaded.
    assert not image.pixmap().isNull() and image.property('current')
    screen.prompt.setPlainText('Make it sharp')
    started = {}

    def begin(paths, options):
        started.update(options, paths=paths)
        screen.jobs.busy = True

    monkeypatch.setattr(screen.jobs, 'start', begin)
    screen.prompt.moveCursor(screen.prompt.textCursor().MoveOperation.End)
    qtbot.keyClick(screen.prompt, Qt.Key.Key_Return, Qt.KeyboardModifier.ShiftModifier)  # A new line, not sent.
    qtbot.keyClicks(screen.prompt, 'for printing')
    assert not started
    qtbot.keyClick(screen.prompt, Qt.Key.Key_Return)
    assert started['paths'] == [str(photo)] and started['prompt'] == 'Make it sharp\nfor printing'
    assert started['original'] == str(photo) and started['key'] == 'sk-or-v1-secret'
    assert started['model'] == MODELS['enhance'] and not screen.prompt.toPlainText() and screen.progress.maximum() == 0
    version = tmp_path / 'café photo 🖨_enhanced.jpg'
    Image.new('RGB', (900, 600)).save(version)
    screen.on_event('output', {'path': str(version)})
    screen.jobs.busy = False
    screen.on_event('done', [str(version)])
    assert screen.model.paths == [str(version)] and screen.outputs.currentData() == str(version)
    screen.on_event('skipped', {'path': str(version), 'code': 'ai_key', 'detail': 'User not found.'})
    said = T.OPENROUTER_SAID.format(reason=T.ERRORS['ai_key'], detail='User not found.')
    assert said in [label.text() for label in screen.chat.findChildren(QLabel)]  # OpenRouter's own words.
    screen.chat.picked.emit(str(photo))  # Go back: the next change starts from the original.
    assert screen.model.paths == [str(photo)] and not screen.chat.pictures[str(version)][0].property('current')
    screen.again.click()
    assert screen.model.paths == [] and not screen.chat.pictures


@pytest.mark.skipif(sys.platform != 'win32', reason='The installed app keeps settings in the Windows registry.')
def test_key_survives_the_windows_registry(qtbot):
    settings = QSettings('PrintShop Tools tests', 'Registry')  # The same storage as the installed app.
    settings.clear()
    page = Settings(settings)
    qtbot.addWidget(page)
    page.key.setText('sk-or-v1-secret')
    page.save()
    try:
        assert unseal(QSettings('PrintShop Tools tests', 'Registry').value('ai/key')) == 'sk-or-v1-secret'
    finally:
        settings.clear()
        settings.sync()


def test_settings_say_why_openrouter_refuses_the_saved_key(qtbot, tmp_path, monkeypatch):
    monkeypatch.setattr(ui.settings, 'key_problem', lambda key: 'API key expired.' if key == 'sk-old' else '')
    settings = QSettings(str(tmp_path / 'settings.ini'), QSettings.Format.IniFormat)
    settings.setValue('ai/key', seal('sk-old'))
    window = Window(settings)
    qtbot.addWidget(window)
    window.show()
    window.show_screen(window.preferences)  # Opening Settings checks the saved key.
    page = window.preferences
    qtbot.waitUntil(lambda: page.message.text() == T.KEY_REFUSED.format(reason='API key expired.'))
    page.key.setText(' sk-new\n')
    page.save()
    qtbot.waitUntil(lambda: page.message.text() == T.KEY_WORKS)
    assert unseal(settings.value('ai/key')) == 'sk-new'

