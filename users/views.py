from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
@csrf_exempt
def login_view(request):
    # Получение данных из запроса
    data = json.loads(request.body.decode('utf-8'))
    print(data)
    username = data.get('email')
    password = data.get('password')
    # Аутентификация пользователя
    print(username, password)
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        user_data = {
            'id': user.id,
            'username': user.email,
            'email': user.email,
            'name': user.name,
            'role_id': user.role_id
        }
        login(request, user)
        return JsonResponse({'message': 'Вы успешно вошли в систему.', 'user': user_data}, status=200)
    else:
        # Аутентификация не удалась
        return JsonResponse({'error': 'Неверный логин или пароль.'}, status=401)
