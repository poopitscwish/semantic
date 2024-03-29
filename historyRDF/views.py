from django.http import HttpResponse, Http404
from django.conf import settings
import os

def download_file(request, filename):
    # Путь к директории, где хранятся файлы
    file_path = os.path.join(settings.BASE_DIR, "historyRDF\\file\\" + filename)
    print(file_path)
    # Проверяем, существует ли файл
    if os.path.exists(file_path):
        # Открываем файл для чтения в бинарном режиме
        with open(file_path, 'rb') as fh:
            # Устанавливаем тип содержимого в ответе
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            # Устанавливаем заголовок для скачивания файла с оригинальным именем
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    # Если файл не найден, возвращаем ошибку 404
    raise Http404
