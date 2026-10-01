"""The API key at rest: Windows encrypts it for the signed-in user (DPAPI), so the registry never holds it in plain text."""
import base64
import sys


def dpapi(name, data):
    import ctypes
    from ctypes import wintypes

    class Blob(ctypes.Structure):
        _fields_ = [('size', wintypes.DWORD), ('data', ctypes.POINTER(ctypes.c_char))]

    buffer = ctypes.create_string_buffer(data, len(data))
    source, result = Blob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char))), Blob()
    # 1 = CRYPTPROTECT_UI_FORBIDDEN: never show a prompt.
    if not getattr(ctypes.windll.crypt32, name)(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(result)):
        raise ctypes.WinError()
    try:
        return ctypes.string_at(result.data, result.size)
    finally:
        ctypes.windll.kernel32.LocalFree(result.data)


def seal(text):
    data = text.encode()
    return base64.b64encode(dpapi('CryptProtectData', data) if sys.platform == 'win32' else data).decode()


def unseal(value):
    """The key, or '' when none is saved or it was sealed for another Windows user."""
    try:
        data = base64.b64decode(value or '')
        return (dpapi('CryptUnprotectData', data) if sys.platform == 'win32' and data else data).decode()
    except (OSError, ValueError):
        return ''
