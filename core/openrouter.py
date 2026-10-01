"""OpenRouter's image API: send one image with instructions, get back the images the model made."""
import base64
import json
import logging
from io import BytesIO

from core.files import JobError

URL = 'https://openrouter.ai/api/v1/images'
MODELS = {'remove': 'inclusionai/ming-image-0.1-design-layer', 'enhance': 'meta/muse-image'}
SIDE = 2048  # Longest side sent; the models answer at one to two and a half megapixels anyway.


def edit(image, prompt, key, model):
    """An RGB Pillow image in; Pillow images out, whatever format the model answers in (Muse uses WEBP)."""
    import http.client
    import urllib.error
    import urllib.request
    from PIL import Image
    image = image.copy()
    image.thumbnail((SIDE, SIDE))
    data = BytesIO()
    image.save(data, 'JPEG', quality=95, subsampling=0)
    reference = 'data:image/jpeg;base64,' + base64.b64encode(data.getvalue()).decode()
    body = {'model': model, 'prompt': prompt,
            'input_references': [{'type': 'image_url', 'image_url': {'url': reference}}]}
    request = urllib.request.Request(URL, json.dumps(body).encode(),
                                     {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            answer = json.load(response)
    except urllib.error.HTTPError as error:
        logging.warning('OpenRouter answered %s: %s', error.code, error.read(1000))
        if error.code in (408, 429) or error.code >= 500:
            raise JobError('ai_busy')
        raise JobError({401: 'ai_key', 402: 'ai_credit', 404: 'ai_model'}.get(error.code, 'ai_failed'))
    except (OSError, ValueError, http.client.HTTPException):  # No connection, a timeout, or a cut-off answer.
        logging.warning('Could not reach OpenRouter', exc_info=True)
        raise JobError('ai_offline')
    images = [Image.open(BytesIO(base64.b64decode(item['b64_json']))) for item in answer.get('data', [])
              if item.get('b64_json')]
    if not images:
        logging.warning('OpenRouter sent no image: %s', str(answer)[:1000])
        raise JobError('ai_failed')
    return images


def key_problem(key):
    """OpenRouter's reason for refusing a key, '' when it accepts it, or None when it cannot be reached."""
    import http.client
    import urllib.error
    import urllib.request
    request = urllib.request.Request('https://openrouter.ai/api/v1/key', headers={'Authorization': f'Bearer {key}'})
    try:
        with urllib.request.urlopen(request, timeout=30):
            return ''
    except urllib.error.HTTPError as error:
        try:
            return json.load(error)['error']['message']
        except (ValueError, KeyError, TypeError):
            return f'HTTP {error.code}'
    except (OSError, ValueError, http.client.HTTPException):
        return None
