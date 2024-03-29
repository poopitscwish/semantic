import os
from semantic import settings
from .forms import TextUploadForm
from scripts.natashaNLP import create_triple, generate_rdf
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
@require_http_methods(["POST"])
@csrf_exempt
def upload_text(request):
        text_data = request.POST.get('text', '')
        result = create_triple(text_data)  
        return JsonResponse(result, safe=False)
@require_http_methods(["POST"])
@csrf_exempt
def download_file(request):
    print("POST")
    triples = json.loads(request.body)   
    print(request)
    rdf_resuld = generate_rdf(triples)
    rdf_content = rdf_resuld.serialize(format="xml")
    rdf_directory = os.path.join(settings.BASE_DIR, 'historyRDF\\file') 
    # Создание директории, если она не существует
    if not os.path.exists(rdf_directory):
        os.makedirs(rdf_directory)
    
    # Определение пути к файлу
    base_filename = 'ontology'
    extension = 'rdf'
    unique_filepath = get_unique_filename(rdf_directory, base_filename, extension)  
    # Сохранение содержимого в файл
    with open(unique_filepath, 'wb') as rdf_file:
        rdf_file.write(rdf_content.encode('utf-8'))
    response = HttpResponse(rdf_content, content_type='application/rdf+xml')
    response['Content-Disposition'] = 'attachment; filename="ontology.rdf"'
    return response

#Илон Маск основал SpaceX которую посетил Владимир Путин
def get_unique_filename(directory, base_filename, extension):
    counter = 0
    while True:
        if counter == 0:
            filename = f"{base_filename}.{extension}"
        else:
            filename = f"{base_filename}({counter}).{extension}"
        
        filepath = os.path.join(directory, filename)

        # Если файл с таким именем уже существует, увеличиваем счетчик и повторяем попытку
        if os.path.exists(filepath):
            counter += 1
        else:
            # Как только находим уникальное имя, возвращаем его
            return filepath