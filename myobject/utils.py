from datetime import datetime
from pytils import translit


def translit_filename(instance, filename):
    """Транслитерирует имя файла"""
    filename = filename.split('.')
    ext = filename[-1]
    filename = ' '.join(filename[:-1])
    filename = ''.join([
        "object_photos/{0}/".format(datetime.strftime(datetime.now(), '%Y%m')),
        translit.slugify(filename)
    ])
    full_filename = '.'.join((filename, ext))
    return full_filename
