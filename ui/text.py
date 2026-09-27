"""All application copy, including messages for core error codes."""
APP = 'PrintShop Tools'
HOME_TITLE = 'Ready for the next job.'
HOME_DESCRIPTION = 'Choose a tool. Add your files. We’ll take care of the rest.'
TOOLS = [
    ('upscale', 'Upscale image', 'Make photos larger for printing.', 'image'),
    ('make', 'Make PDF', 'Bring images and PDFs together.', 'pdf'),
    ('compress', 'Compress PDF', 'Make a PDF smaller to send.', 'pdf'),
    ('split', 'Split PDF', 'Save just the pages you need.', 'pdf'),
    ('organize', 'Organize pages', 'Reorder, rotate or remove pages.', 'pdf'),
    ('render', 'PDF to images', 'Save PDF pages as JPG or PNG.', 'pdf'),
    ('vector', 'Logo to vector', 'Make a logo sharp at any size.', 'image'),
]
LATER = 'Coming in a later phase'
OFFLINE = 'Your files stay on this computer.'
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
BLURRY_ONE = ('1 image needs more than 4× and will print soft. Print smaller, use Hard edges for a QR code, '
              'or Logo to vector for a logo.')
BLURRY = ('{count} images need more than 4× and will print soft. Print smaller, use Hard edges for QR codes, '
          'or Logo to vector for logos.')
HUGE_TITLE = 'Very large result'
HUGE = 'The largest result will be about {megapixels} megapixels. It needs a lot of memory and disk space.'
HUGE_YES = 'Upscale anyway'
HUGE_NO = 'Go back'
CANCEL = 'Cancel'
CANCELLING = 'Cancelling…'
CANCELLED = 'Cancelled. Unfinished files were removed.'
OPEN = 'Open file'
SHOW = 'Show in folder'
AGAIN = 'Do another'
SAVED_NEXT = 'Saves next to the first original. Existing files are kept.'
SAVED_EACH = 'Saves next to each original. Existing files are kept.'
SAVED_FIXED = 'Saves in {folder}. Existing files are kept.'
SKIPPED = 'Skipped {name}: {reason}'
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
    'memory': 'There is not enough memory for a result this big. Choose a smaller size or close other apps.',
    'names_exhausted': 'Too many files have this name. Choose another output folder.',
    'worker': 'Processing stopped unexpectedly. Try fewer files; details were saved to the log.',
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
THUMB = {'locked': 'Password protected', 'unreadable': 'Preview unavailable'}
PAGES = '{count} pages'
PIXELS = '{width} × {height} px'
READING = 'Loading preview…'
CLOSE_TITLE = 'A job is running'
CLOSE_MESSAGE = 'Cancel the current job and close? Finished files will be kept.'
YES = 'Cancel job and close'
NO = 'Keep working'
OUTPUT_FAILED = 'Could not open this location. Open it from File Explorer instead.'
