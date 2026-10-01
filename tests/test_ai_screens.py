from PIL import Image
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QLabel, QLineEdit
from core.openrouter import MODELS
from core.secret import seal, unseal
from ui import text as T
from ui.window import Window


def test_api_key_is_write_only_and_models_follow_the_defaults(qtbot, tmp_path):
    settings = QSettings(str(tmp_path / 'settings.ini'), QSettings.Format.IniFormat)
    window = Window(settings)
    qtbot.addWidget(window)
    page = window.preferences
    assert page.key.echoMode() == QLineEdit.EchoMode.Password and page.key_note.text() == T.KEY_MISSING
    page.key.setText(' sk-or-v1-secret ')
    page.models['enhance'].setText('meta/muse-image-2')
    page.save()
    assert page.key.text() == '' and page.key_note.text() == T.KEY_SAVED
    assert unseal(settings.value('ai/key')) == 'sk-or-v1-secret'
    assert settings.value('ai/remove_model') == '' and settings.value('ai/enhance_model') == 'meta/muse-image-2'
    page.save()  # Saving again without a new key keeps the old one.
    assert unseal(settings.value('ai/key')) == 'sk-or-v1-secret'
    reopened = Window(settings)
    qtbot.addWidget(reopened)
    assert reopened.preferences.key.text() == '' and reopened.preferences.key_note.text() == T.KEY_SAVED
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
    screen.target.setText('the watermark')
    assert screen.run.isEnabled() and screen.run.text() == 'Remove it from 1 image'
    started = {}
    monkeypatch.setattr(screen.jobs, 'start', lambda paths, options: started.update(options))
    screen.start()
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
    screen.prompt.setText('Make it sharp')
    started = {}

    def begin(paths, options):
        started.update(options, paths=paths)
        screen.jobs.busy = True

    monkeypatch.setattr(screen.jobs, 'start', begin)
    screen.start()
    assert started['paths'] == [str(photo)] and started['prompt'] == 'Make it sharp'
    assert started['original'] == str(photo) and started['key'] == 'sk-or-v1-secret'
    assert started['model'] == MODELS['enhance'] and screen.prompt.text() == '' and screen.progress.maximum() == 0
    version = tmp_path / 'café photo 🖨_enhanced.jpg'
    Image.new('RGB', (900, 600)).save(version)
    screen.on_event('output', {'path': str(version)})
    screen.jobs.busy = False
    screen.on_event('done', [str(version)])
    assert screen.model.paths == [str(version)] and screen.outputs.currentData() == str(version)
    screen.on_event('skipped', {'path': str(version), 'code': 'ai_busy'})
    assert T.ERRORS['ai_busy'] in [label.text() for label in screen.chat.findChildren(QLabel)]
    screen.chat.picked.emit(str(photo))  # Go back: the next change starts from the original.
    assert screen.model.paths == [str(photo)] and not screen.chat.pictures[str(version)][0].property('current')
    screen.again.click()
    assert screen.model.paths == [] and not screen.chat.pictures
