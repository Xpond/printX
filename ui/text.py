"""All application copy, including messages for core error codes."""
APP = 'PrintShop Tools'
HOME_TITLE = 'Ready for the next job.'
HOME_DESCRIPTION = 'Choose a tool. Add your files. We’ll take care of the rest.'
TOOLS = [
    ('remove', 'Remove background', 'Cut out the subject, or remove anything else.', 'ai'),
    ('enhance', 'Enhance image', 'Upscale, restore or retouch a photo by describing it.', 'ai'),
    ('upscale', 'Upscale image', 'Make photos larger for printing.', 'image'),
    ('make', 'Make PDF', 'Bring images and PDFs together.', 'pdf'),
    ('compress', 'Compress PDF', 'Make a PDF smaller to send.', 'pdf'),
    ('split', 'Split PDF', 'Save just the pages you need.', 'pdf'),
    ('organize', 'Organize pages', 'Reorder, rotate or remove pages.', 'pdf'),
    ('render', 'PDF to images', 'Save PDF pages as JPG or PNG.', 'pdf'),
]
LATER = 'Coming in a later phase'
OFFLINE = 'Your files stay on this computer, except images you send to an AI tool.'
AI = 'AI'
BACK = 'Back'
SETTINGS = 'Settings'
IMAGES = '*.jpg *.jpeg *.png *.tif *.tiff *.bmp *.webp *.heic *.heif'
MAKE = {
    'title': 'Make PDF', 'browse': 'Choose images and PDFs', 'filter': f'Images and PDFs ({IMAGES} *.pdf)',
    'empty': 'Drop images or PDFs here, or click to choose files\nJPG, PNG, TIFF, BMP, WEBP, HEIC and PDF',
    'count': '{count} files · drag to reorder', 'count_one': '1 file · drag to reorder',
    'run_empty': 'Make PDF', 'run': 'Make PDF from {count} files', 'run_one': 'Make PDF from 1 file',
    'running': 'Making PDF…', 'progress': 'Processing {name} · {index} of {total}',
    'finishing': 'Saving your PDF…', 'success': 'Made {count} PDFs', 'success_one': 'Made 1 PDF'}
UPSCALE = {
    'title': 'Upscale image', 'browse': 'Choose images', 'filter': f'Images ({IMAGES})',
    'empty': 'Drop photos here, or click to choose files\nJPG, PNG, TIFF, BMP, WEBP and HEIC',
    'count': '{count} images', 'count_one': '1 image',
    'run_empty': 'Upscale images', 'run': 'Upscale {count} images', 'run_one': 'Upscale 1 image',
    'running': 'Upscaling…', 'progress': 'Upscaling · {index} of {total}',  # Files run in parallel.
    'finishing': 'Finishing…', 'success': 'Upscaled {count} images', 'success_one': 'Upscaled 1 image'}
CUTOUT = {
    **{key: UPSCALE[key] for key in ('browse', 'filter', 'empty', 'count', 'count_one', 'finishing')},
    'title': 'Remove background', 'run_empty': 'Remove background', 'run': 'Remove background from {count} images',
    'run_one': 'Remove background from 1 image', 'running': 'Removing background…',
    'progress': 'Removing background · {index} of {total}',
    'success': 'Removed the background from {count} images', 'success_one': 'Removed the background from 1 image'}
ERASE = {  # Remove when Something else is chosen.
    **CUTOUT, 'run_empty': 'Remove it', 'run': 'Remove it from {count} images', 'run_one': 'Remove it from 1 image',
    'running': 'Removing…', 'progress': 'Removing · {index} of {total}',
    'success': 'Removed it from {count} images', 'success_one': 'Removed it from 1 image'}
ENHANCE = {
    'title': 'Enhance image', 'browse': 'Choose a photo', 'filter': f'Images ({IMAGES})',
    'empty': 'Drop a photo here, or click to choose one\nJPG, PNG, TIFF, BMP, WEBP and HEIC',
    'count': '{count} photos', 'count_one': '1 photo', 'run_empty': 'Send', 'run': 'Send', 'run_one': 'Send',
    'running': 'Enhancing…', 'progress': 'Enhancing…', 'finishing': 'Saving…',
    'success': 'Saved the new version', 'success_one': 'Saved the new version',
    'saved': 'Each version saves next to the original. Existing files are kept.'}
PROMPT_HINT = 'Describe what to change, e.g. make it sharp and clear for printing'
PICK_TIP = 'Click to make the next change to this version'
CHOOSE_PHOTO = 'Choose photo'
NEW_PHOTO = 'New photo'
PDFS = {'browse': 'Choose PDFs', 'filter': 'PDFs (*.pdf)', 'empty': 'Drop PDFs here, or click to choose files',
        'count': '{count} PDFs', 'count_one': '1 PDF', 'finishing': 'Finishing…'}
COMPRESS = {
    **PDFS, 'title': 'Compress PDF', 'run_empty': 'Compress PDFs', 'run': 'Compress {count} PDFs',
    'run_one': 'Compress 1 PDF', 'running': 'Compressing…', 'progress': 'Compressing {name} · {index} of {total}',
    'success': 'Compressed {count} PDFs', 'success_one': 'Compressed 1 PDF'}
SPLIT = {
    **PDFS, 'title': 'Split PDF', 'run_empty': 'Split PDFs', 'run': 'Split {count} PDFs', 'run_one': 'Split 1 PDF',
    'running': 'Splitting…', 'progress': 'Splitting {name} · {index} of {total}',
    'success': 'Split {count} PDFs', 'success_one': 'Split 1 PDF',
    'saved': 'Saves a folder next to each original. Existing files are kept.'}
ADD = 'Add files'
REMOVE = 'Remove selected'
SELECT_ALL = 'Select all'
REMOVE_TIP = 'Tip: Ctrl+A selects every file and Delete removes the selection.'
SORT = 'Sort by name'
EMPTY_LIST = 'No files yet'
OUTPUT = 'Save as'
NAME = 'File name'
EXTENSION = '.pdf'
COMBINED = 'One combined PDF'
SEPARATE = 'One PDF per file'
IMAGE_SIZE = 'Image pages'
PAPERS = [('A4', 'A4'), ('Letter', 'Letter'), ('Same as image', 'image')]
MARGINS = [('None', 'none'), ('Small', 'small'), ('Large', 'large')]
MARGIN = 'Margins'
PDF_SIZE_NOTE = 'Existing PDF pages keep their original size.'
SIZE = 'Size'
SIZES = [('Fit print size', 'fit'), ('2×', '2'), ('3×', '3'), ('4×', '4')]
PRINT_PAPERS = [('A6', 'A6'), ('A5', 'A5'), ('A4', 'A4'), ('A3', 'A3'), ('A2', 'A2'), ('A1', 'A1'), ('A0', 'A0'),
                (('10 × 15 cm', '4 × 6 in'), '4x6'), (('13 × 18 cm', '5 × 7 in'), '5x7'),
                (('20 × 25 cm', '8 × 10 in'), '8x10'), ('Letter', 'Letter'), ('Legal', 'Legal'),
                ('Tabloid', 'Tabloid'), ('Custom size', 'custom')]
PAPER_TIP = 'Each image is sized to fit this paper, turned to match the image.'
BY = '×'
DPIS = [('300 DPI', 300), ('150 DPI', 150)]
DPI_TIP = '300 DPI for prints seen up close; 150 DPI for large posters seen from a distance.'
SHARPENING = 'Sharpening'
SHARPEN_LEVELS = [('Off', 'off'), ('Light', 'light'), ('Strong', 'strong')]
HARD_EDGES = 'Hard edges for QR codes and pixel art'
HARD_TIP = 'Keeps every pixel a crisp square instead of smoothing, at a whole-number size.'
SHARP_TO = 'Sharp to {width} × {height} {unit}'
GRADES = {'big': 'Already big enough', 'sharp': '{scale}× · sharp', 'soft': '{scale}× · slightly soft',
          'blurry': '{scale}× · soft'}
BLURRY_ONE = '1 image needs more than 4× and will print soft. Print smaller, or use Hard edges for a QR code.'
BLURRY = '{count} images need more than 4× and will print soft. Print smaller, or use Hard edges for QR codes.'
HUGE_TITLE = 'Very large result'
HUGE = 'The largest result will be about {megapixels} megapixels. It needs a lot of memory and disk space.'
HUGE_YES = 'Upscale anyway'
HUGE_NO = 'Go back'
COMPRESSION = 'Compression'
LEVELS = [('Smallest (email)', 'smallest'), ('Recommended', 'recommended'), ('Print quality', 'print')]
LEVEL_NOTES = {'smallest': 'The smallest file, for email. Images at 100 DPI.',
               'recommended': 'Sharp on screen and office printers. Images at 150 DPI.',
               'print': 'For professional printing. Images at 300 DPI, CMYK colours kept.'}
SHRUNK = '{before} → {after}'
SMALLER = '{percent}% smaller'
TOTAL = '{status} · {before} → {after}, {percent}% smaller'
OPTIMIZED = 'Already optimized'
SPLIT_BY = 'Split'
SPLIT_MODES = [('Every page', 'pages'), ('Page ranges', 'ranges'), ('Every N pages', 'every')]
SPLIT_NOTES = {'pages': 'Each page becomes its own PDF.', 'ranges': 'Each range becomes one PDF.',
               'every': 'Each group becomes one PDF.'}
RANGES_EXAMPLE = '1-3, 5, 8-10'
RANGES_HELP = 'Type pages like 1-3, 5, 8-10.'
PAGES_PER_PDF = ' pages per PDF'
PARTS = '{status} into {count} PDFs'
REMOVE_WHAT = 'Remove'
REMOVE_MODES = [('Background', 'background'), ('Something else', 'object')]
KEEP_HINT = 'Optional: describe what to keep, e.g. the woman on the left and her dog'
TARGET_HINT = 'Describe what to remove, e.g. the watermark in the corner or the date stamp'
NEEDS_KEY = 'Add an OpenRouter API key in Settings to use AI tools.'
CANCEL = 'Cancel'
CANCELLING = 'Cancelling…'
CANCELLED = 'Cancelled. Unfinished files were removed.'
OPEN = 'Open file'
OPEN_FOLDER = 'Open folder'
SHOW = 'Show in folder'
AGAIN = 'Do another'
SAVED_NEXT = 'Saves next to the first original. Existing files are kept.'
SAVED_EACH = 'Saves next to each original. Existing files are kept.'
SAVED_FIXED = 'Saves in {folder}. Existing files are kept.'
SKIPPED = 'Skipped {name}: {reason}'
OPENROUTER_SAID = '{reason} OpenRouter said: “{detail}”'
NOTICES = {'first_page': 'Only the first page of {name} was upscaled.'}
PASSWORD_TITLE = 'Enter PDF password'
PASSWORD = '{name} is password protected. Enter its password to continue, or cancel to skip it.'
ERRORS = {
    'permission': 'This file or folder cannot be accessed. Close apps using it or choose another output folder.',
    'missing': 'This file was moved or deleted. Add it again from its current location.',
    'disk_full': 'There is not enough free space. Free up space or choose another output folder.',
    'corrupt': 'This file could not be read. Try opening it in another app and saving a fresh copy.',
    'unsupported': 'Choose an image or PDF. Office documents will be supported in a later phase.',
    'empty_pdf': 'This PDF has no pages. Choose a PDF containing at least one page.',
    'password_skipped': 'No password was entered. Add the file again when you have its password.',
    'no_outputs': 'Nothing was saved. Check the messages above and try again.',
    'big_enough': 'It is already big enough for this print size, so it was left as it is.',
    'not_image': 'Choose a JPG, PNG, TIFF, BMP, WEBP or HEIC image.',
    'not_pdf': 'Choose a PDF file.',
    'optimized': 'It is already optimized, so it was left as it is.',
    'missing_pages': 'This PDF does not have all the pages you typed. Check its page count.',
    'memory': 'There is not enough memory for a result this big. Choose a smaller size or close other apps.',
    'names_exhausted': 'Too many files have this name. Choose another output folder.',
    'worker': 'Processing stopped unexpectedly. Try fewer files; details were saved to the log.',
    'ai_offline': 'Could not reach OpenRouter. Check the internet connection and try again.',
    'ai_key': 'OpenRouter did not accept the saved API key. Open Settings to see why and paste a new key.',
    'ai_credit': 'The OpenRouter account is out of credit. Add credit at openrouter.ai and try again.',
    'ai_busy': 'The AI service is busy. Wait a minute and try again.',
    'ai_model': 'OpenRouter has no model with this name. Check the model names in Settings.',
    'ai_failed': 'The AI could not edit this image. Try again, or describe it differently.',
    'ai_nothing': 'The AI found nothing to remove. Describe it differently and try again.',
}
OUTPUT_FOLDER = 'Output folder'
NEXT_ORIGINAL = 'Next to the original file'
FIXED_FOLDER = 'Use one folder for every job'
CHOOSE_FOLDER = 'Choose folder'
FOLDER_HINT = 'Choose where finished files should go'
UNITS = 'Default units'
UNIT_OPTIONS = [('Centimetres', 'cm'), ('Inches', 'in')]
DEFAULT_PAPER = 'Default paper size'
REGION_NOTE = 'Initial defaults follow your Windows region.'
SAVE_SETTINGS = 'Save settings'
SETTINGS_SAVED = 'Settings saved'
FOLDER_REQUIRED = 'Choose an output folder first.'
APPEARANCE = 'Appearance follows your system’s light or dark mode.'
AI_TOOLS = 'AI tools'
API_KEY = 'OpenRouter API key'
KEY_HINT = 'Paste your key from openrouter.ai'
KEY_SAVED = 'Key saved · paste a new one to replace it'
KEY_CHECKING = 'Checking the saved key with OpenRouter…'
KEY_WORKS = 'OpenRouter accepts the saved key. The AI tools are ready.'
KEY_REFUSED = ('OpenRouter refuses the saved key: “{reason}” Paste the whole key once (the box shows it) '
               'and save, or create a new key at openrouter.ai.')
KEY_UNCHECKED = 'Could not reach OpenRouter to check the saved key. Check the internet connection.'
MODEL_TITLES = {'remove': 'Remove background model', 'enhance': 'Enhance image model'}
THUMB = {'locked': 'Password protected', 'unreadable': 'Preview unavailable'}
PAGES = '{count} pages'
PIXELS = '{width} × {height} px'
READING = 'Loading preview…'
CLOSE_TITLE = 'A job is running'
CLOSE_MESSAGE = 'Cancel the current job and close? Finished files will be kept.'
YES = 'Cancel job and close'
NO = 'Keep working'
OUTPUT_FAILED = 'Could not open this location. Open it from File Explorer instead.'
