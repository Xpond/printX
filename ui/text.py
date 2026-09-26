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
MAKE_TITLE = 'Make PDF'
MAKE_DESCRIPTION = 'Images and PDF pages, in the order you choose.'
DROP = 'Drop images or PDFs here'
DROP_HINT = 'or click to choose files'
DROP_MORE = 'Drop more files here or click to add'
FORMATS = 'JPG, PNG, TIFF, BMP, WEBP, HEIC and PDF'
BROWSE = 'Choose images and PDFs'
FILTER = 'Images and PDFs (*.jpg *.jpeg *.png *.tif *.tiff *.bmp *.webp *.heic *.heif *.pdf)'
ADD = 'Add files'
REMOVE = 'Remove selected'
SELECT_ALL = 'Select all'
REMOVE_TIP = 'Tip: Ctrl+A selects every file and Delete removes the selection.'
SORT = 'Sort by name'
FILE_COUNT = '{count} files · drag to reorder'
FILE_COUNT_ONE = '1 file · drag to reorder'
EMPTY_LIST = 'Your files will appear here.'
OUTPUT = 'Save as'
COMBINED = 'One combined PDF'
SEPARATE = 'One PDF per file'
IMAGE_SIZE = 'Image pages'
PAPERS = [('A4', 'A4'), ('Letter', 'Letter'), ('Same as image', 'image')]
MARGINS = [('None', 'none'), ('Small', 'small'), ('Large', 'large')]
MARGIN = 'Margins'
MORE = 'More options'
PDF_SIZE_NOTE = 'Existing PDF pages keep their original size.'
RUN_EMPTY = 'Make PDF'
RUN = 'Make PDF from {count} files'
RUN_ONE = 'Make PDF from 1 file'
RUNNING = 'Making PDF…'
PROGRESS = 'Processing {name} · {index} of {total}'
FINISHING = 'Saving your PDF…'
CANCEL = 'Cancel'
CANCELLING = 'Cancelling…'
CANCELLED = 'Cancelled. Unfinished files were removed.'
SUCCESS = 'Made {count} PDFs'
SUCCESS_ONE = 'Made 1 PDF'
OPEN = 'Open file'
SHOW = 'Show in folder'
AGAIN = 'Do another'
SAVED_NEXT = 'Saves next to the first original. Existing files are kept.'
SAVED_EACH = 'Saves next to each original. Existing files are kept.'
SAVED_FIXED = 'Saves in {folder}. Existing files are kept.'
SKIPPED = 'Skipped {name}: {reason}'
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
    'no_outputs': 'No PDFs were made. Check the messages above and try again.',
    'names_exhausted': 'Too many files have this name. Choose another output folder.',
    'worker': 'Processing stopped unexpectedly. Try fewer files; details were saved to the log.',
}
SETTINGS_DESCRIPTION = 'Set things up once. Keep every job simple.'
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
