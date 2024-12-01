from django.contrib.auth import authenticate
from rest_framework import status

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly


from django.contrib.auth.models import User

from reconstruction.permissions import IsAdmin, IsManager
from .minio import add_pic, delete_pic
from reconstruction.serializers import WorkSerializer, ReconstructionSerializer, UserSerializer
from reconstruction.models import CustomUser, Work, Reconstruction, Space

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.utils import timezone
import random

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.contrib.auth import logout as django_logout

from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from django.contrib.auth import login, logout
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from django.conf import settings
import redis
from django.http import HttpResponse
import uuid


session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


@swagger_auto_schema(
    operation_summary="Аутентификация", 
    method='post', 
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['email', 'password']
    ),
)
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def login(request): 
    email = request.data["email"] 
    password = request.data["password"] 
    user = authenticate(request, email=email, password=password) 
    if user is not None:
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, user.pk)

        response = HttpResponse("{'status': 'ok'}")
        response.set_cookie("session_id", random_key)

        return response
    else:
        return HttpResponse("{'status': 'error', 'error': 'Неверный логин или пароль'}")

@swagger_auto_schema(
    method='post',
    operation_summary="Деавторизация"
)
@api_view(['POST'])
def logout(request):

    session_id = request.COOKIES.get('session_id')
    if session_id:
        session_storage.delete(session_id)  
        response = Response({"message": "Вы вышли из аккаунта."}, status=status.HTTP_200_OK)
        response.delete_cookie("session_id") 
        return response
    return Response({"error": "Необходима аутентификация."}, status=status.HTTP_401_UNAUTHORIZED)


class UserViewSet(viewsets.ModelViewSet): 
    """
    Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = CustomUser.objects.all() 
    serializer_class = UserSerializer 
    model_class = CustomUser 
 
    def get_permissions(self): 
        if self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['list']:
            permission_classes = [IsAdmin | IsManager]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes] 
     
    @swagger_auto_schema(
        operation_summary="Регистрация"
    )
    def create(self, request):
        """
        Функция регистрации новых пользователей
        Если пользователя c указанным в request email ещё нет, в БД будет добавлен новый пользователь.
        """
        if self.model_class.objects.filter(email=request.data['email']).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            self.model_class.objects.create_user(email=serializer.data['email'],
                                     password=serializer.data['password'],
                                     is_superuser=serializer.data['is_superuser'],
                                     is_staff=serializer.data['is_staff'])
            return Response({'status': 'Success'}, status=200)
        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes        
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator
    



# ------------------------------------МЕТОДЫ СПИСОК РАБОТ И ДОБАВЛЕНИЕ НОВОЙ РАБОТЫ------------------------------------------


  
class WorkList(APIView):
    work_class = Work
    work_serializer = WorkSerializer
    reconstruction_class = Reconstruction
    reconstruction_serializer = ReconstructionSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_summary="Список реконструкционных работ",
        manual_parameters=[
        openapi.Parameter(
            'work_title',
            openapi.IN_QUERY,
            description="Вид работы",
            type=openapi.TYPE_STRING,
        )
    ]
    )
    def get(self, request, format=None):
        works = self.work_class.objects.filter(is_deleted=False)  
        work_title = request.query_params.get('work_title')
        if work_title:
            works = works.filter(title__icontains=work_title)      
        serializer = self.work_serializer(works, many=True)

        draft_reconstruction = None
        user_instance = request.user

        if user_instance and user_instance.is_authenticated:
            draft_reconstruction = self.reconstruction_class.objects.filter(user=user_instance, status='draft').first()

        draft_reconstruction_id = 0
        count_works = 0
        if draft_reconstruction is not None:
            draft_reconstruction_id = draft_reconstruction.id
            count_works = len(Space.objects.filter(reconstruction=draft_reconstruction))

        return Response({'works': serializer.data, 'draft_reconstruction_id': draft_reconstruction_id, 'count_of_works': count_works})




    @swagger_auto_schema(
        request_body=WorkSerializer,
        operation_summary="Добавление работы", 
    )
    def post(self, request, format=None):
        user_instance=request.user
        if user_instance.is_authenticated:
            if user_instance.is_staff:             
                serializer = self.work_class(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
            else: return Response({"message": "Права на данное действие имеет только модератор"}, status=status.HTTP_403_FORBIDDEN)
        else: return Response({"message": "Вы не авторизованы"}, status=status.HTTP_401_UNAUTHORIZED)    
    



    # --------------------МЕТОД ДОБАВЛЕНИЯ ИЗОБРАЖЕНИЯ ДЛЯ РАБОТЫ -------------------------------------




@swagger_auto_schema(
    method='post',
    operation_summary="Добавление изображения"
)
@api_view(["Post"])
def add_image_work(reconstruction, pk, format=None):

    work = get_object_or_404(Work, pk=pk)

    new_pic = reconstruction.FILES.get('pic')
    if not new_pic:
        return Response({"error": "Изображение не предоставлено."}, status=status.HTTP_400_BAD_REQUEST)
    delete_result = delete_pic(pk)
    if 'error' in delete_result.data:
        return add_result
    add_result = add_pic(work, new_pic)
    if 'error' in add_result.data:
        return add_result

    return Response({"message": "Изображение успешно обновлено."}, status=status.HTTP_200_OK)


# ----------------------ДОБАВЛЕНИЕ В ЗАЯВКУ----------------------------------------------------------------------------

class ReconstructionDraft(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Добавление в заявку-черновик",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'work_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID работы"),
            },
        ),
    )
    def post(self, request, format=None): 
        print('lalalsklks')
        draft_reconstruction=None 

        # user_instance = request.user
        session_id = request.COOKIES.get('session_id')
        if session_id:
            user_id = session_storage.get(session_id)
            user_instance = CustomUser.objects.get(pk=int(user_id))
            if user_instance:
                draft_reconstruction, created = Reconstruction.objects.get_or_create(user=user_instance, status='draft', defaults={'creation_date': timezone.now})
            else:         
                return Response({'message':'Вы не авторизованы'}, status=401) 

        work_id = request.data.get('work_id') 
        work = get_object_or_404(Work, pk=work_id, is_deleted=False) 

        if Space.objects.filter(reconstruction=draft_reconstruction, work=work): 
            return Response({"error": "Данная работа уже добавлена в заявку"}, status=status.HTTP_400_BAD_REQUEST) 
            
        Space.objects.create(reconstruction=draft_reconstruction, work=work) 

        return Response({"message": "Работа успешно добавлена в заявку"}, status=status.HTTP_201_CREATED)




# -----------------------МЕТОДЫ ОДНА РАБОТА, ИЗМЕНЕНИЕ РАБОТЫ, УДАЛЕНИЕ РАБОТЫ--------------------------------------------

@swagger_auto_schema(
        method='get',
    operation_summary="Одна работа"
)
@api_view(["Get"])
def get_work(work, pk, format=None):
    work = get_object_or_404(Work, pk=pk)
    serializer = WorkSerializer(work)
    return Response(serializer.data)


   
@swagger_auto_schema(
    operation_summary="Изменение работы",
    method='put', 
    request_body=WorkSerializer
)
@api_view(["PUT"])
def put_work(reconstruction, pk, format=None):
    work = get_object_or_404(Work, pk=pk)
    serializer = WorkSerializer(work, data=reconstruction.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='delete',
    operation_summary="Удаление работы",
)
@api_view(["Delete"])
def delete_work(reconstruction, pk, format=None):

    work = get_object_or_404(Work, pk=pk)
    work.is_deleted = True
    work.save()
    pic_result = delete_pic(pk)
    if 'error' in pic_result.data:
        return pic_result
    return Response({"message": "Работа успешно удалена."}, status=status.HTTP_204_NO_CONTENT)
    




# -------------------------------------------СПИСОК ЗАЯВОК------------------------------------------------




class ReconstructionList(APIView):
    model_class = Reconstruction
    serializer_class = ReconstructionSerializer
    # permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Список заявок на реконструкцию",
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'apply_date',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING
            )
        ],
    )
    def get(self, request, format=None):

        reconstructions = None
        # user_instance = request.user
        session_id = request.COOKIES.get('session_id')
        if session_id:
            user_id = session_storage.get(session_id)
            user_instance = CustomUser.objects.get(pk=int(user_id))
            if user_instance:
                if user_instance.is_staff:
                    reconstructions = self.model_class.objects.all().exclude(status__in=['deleted', 'draft'])
                else:
                    reconstructions = self.model_class.objects.filter(user=user_instance).exclude(status__in=['deleted', 'draft'])
            else: return Response({'message':'Вы не авторизованы'}, status=401)

        status = request.query_params.get('status')
        apply_date = request.query_params.get('apply_date')

        if status:
            reconstructions = reconstructions.filter(status=status)
        if apply_date:
            apply_date_datetime = timezone.datetime.fromisoformat(apply_date)
            reconstructions = reconstructions.filter(apply_date__date=apply_date_datetime)

        serializer = self.serializer_class(reconstructions, many=True)

        return Response({'reconstructions': serializer.data})
       


# ----------------------------------ОДНА РЕКОНСТРУКЦИЯ, ИЗМЕНИТЬ, УДАЛИТЬ----------------------------------------------------------


class ReconstructionDetail(APIView):
    work_class = Work
    work_serializer = WorkSerializer
    reconstruction_class = Reconstruction
    reconstruction_serializer = ReconstructionSerializer
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Одна заявка на реконструкцию",
    )
    def get(self, request, pk, format=None):
        reconstruction = get_object_or_404(self.reconstruction_class, pk=pk)
        # user_instance = request.user

        session_id = request.COOKIES.get('session_id')
        if session_id:
            user_id = session_storage.get(session_id)
            user_instance = CustomUser.objects.get(pk=int(user_id))
            if user_instance != reconstruction.user and not user_instance.is_staff:
                return Response({"message": "Вы не являетесь создателем заявки"}, status=status.HTTP_403_FORBIDDEN)
            else: return Response({'message':'Вы не авторизованы'}, status=401)
        
        serializer = self.reconstruction_serializer(reconstruction)
        spaces = Space.objects.filter(reconstruction=reconstruction).order_by('space')

        works = []
        for space in spaces:
            if space.work.is_deleted == False:
                work_data = self.work_serializer(space.work).data
                work_data['space'] = space.space
                works.append(work_data)

        return Response({'reconstruction': serializer.data, 'works': works})
    
    @swagger_auto_schema(
        operation_summary="Изменение деталей заявки на реконструкцию",
        manual_parameters=[
        openapi.Parameter(
            'place',
            openapi.IN_QUERY,
            description="Место",
            type=openapi.TYPE_STRING,
        )
    ]
    )
    def put(self, request, pk, format=None):
        reconstruction = get_object_or_404(self.reconstruction_class, pk=pk)
        # user_instance = request.user

        session_id = request.COOKIES.get('session_id')
        if session_id:
            user_id = session_storage.get(session_id)
            user_instance = CustomUser.objects.get(pk=int(user_id))
            if user_instance != reconstruction.user and not user_instance.is_staff:
                return Response({"message": "Вы не являетесь создателем заявки"}, status=status.HTTP_403_FORBIDDEN)
            else: return Response({'message':'Вы не авторизованы'}, status=401)
        
        data = request.data.copy()
        place = request.query_params.get('place') 
        if place:
            data['place'] = place

        serializer = self.reconstruction_serializer(reconstruction, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="Удаление заявки на реконструкцию",
    )
    def delete(self, request, pk, format=None):
        reconstruction = get_object_or_404(self.reconstruction_class, pk=pk)
        # user_instance = request.user

        session_id = request.COOKIES.get('session_id')
        if session_id:
            user_id = session_storage.get(session_id)
            user_instance = CustomUser.objects.get(pk=int(user_id))
            if user_instance != reconstruction.user and not user_instance.is_staff:
                return Response({"message": "Вы не являетесь создателем заявки"}, status=status.HTTP_403_FORBIDDEN)
            else: return Response({'message':'Вы не авторизованы'}, status=401) 
        
        reconstruction.status = 'deleted'
        reconstruction.save()
        return Response({"message":"Заявка успешно удалена."},status=status.HTTP_204_NO_CONTENT)
    


#-------------------------ФОРМИРОВАНИЕ ПОЛЬЗОВАТЕЛЕМ------------------------------------------------------------------------------- 

class ReconstructionCreature(APIView):
    model_class = Reconstruction
    serializer_class = ReconstructionSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Формирование заявки создателем",
    )
    def put(self, request, pk, format=None):
        user_instance=request.user
        if user_instance and user_instance.is_authenticated:
            reconstruction = get_object_or_404(self.model_class, pk=pk)
            if reconstruction.place is None:
                return Response({"error": "В заявке не указано место осуществления работ."}, status=status.HTTP_400_BAD_REQUEST)
            
            spaces = Space.objects.filter(reconstruction=reconstruction)
            for space in spaces:
                if space.space is None or space.space == '':
                    return Response({"error": f"Объем для работы '{space.work.title}' не указан."}, status=status.HTTP_400_BAD_REQUEST)

            if reconstruction.status != 'deleted':
                reconstruction.status = 'created'
                reconstruction.apply_date = timezone.now().isoformat()
                reconstruction.save()
                return Response({"message": "Заявка сформирована"}, status=status.HTTP_204_NO_CONTENT)
            return Response({"message": "Заявка не найдена"}, status=status.HTTP_404_NOT_FOUND)
        else: return Response({"message": "Вы не авторизованы"}, status=status.HTTP_401_UNAUTHORIZED)



#------------------------------ЗАВЕРШЕНИЕ МОДЕРАТОРОМ-------------------------------------------------------------------------



class ReconstructionCompletedRejected(APIView):
    model_class = Reconstruction
    serializer_class = ReconstructionSerializer
    permission_classes = [IsAuthenticated]

    status_choices = openapi.Schema(
        type=openapi.TYPE_STRING,
        enum=['completed', 'rejected']
    )

    @swagger_auto_schema(
        operation_summary="Завершить/отклонить модератором",
        request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': status_choices,
        },
        required=['status'],
    ),
)
    def put(self, request, pk, format=None):
        user_instance = request.user
        if user_instance and user_instance.is_authenticated:
            if user_instance.is_staff:
                reconstruction = get_object_or_404(self.model_class, pk=pk)
                if reconstruction.status != 'created':
                    return Response({'error': 'Заявка не может быть завершена до того, как будет сформирована'}, status=status.HTTP_400_BAD_REQUEST)

                reconstruction.fundraising = round(random.uniform(5000, 500000), 2)

                reconstruction.status = request.data['status']
                reconstruction.moderator = user_instance
                reconstruction.end_date = timezone.now().isoformat()

                reconstruction.save()
                serializer = self.serializer_class(reconstruction)

                return Response(serializer.data)
            else: return Response({'message':'Заявку может завершить только модератор'}, status=status.HTTP_403_FORBIDDEN)
        else: return Response({'message':'Вы не авторизованы'}, status=status.HTTP_401_UNAUTHORIZED)



#------------------------------УДАЛИТЬ ИЗ ЗАЯВКИ, ИЗМЕНИТЬ ОБЪЕМ----------------------------------------------------------------------
    


class ReconstructionSpace(APIView):

    @swagger_auto_schema(
        operation_summary="Удалить работу из заявки"
    )
    def delete(self, request, reconstruction_id=None, work_id=None, format=None):
        reconstruction = get_object_or_404(Reconstruction, pk=reconstruction_id)
        work = get_object_or_404(Work, pk=work_id)
        space_delete = get_object_or_404(Space, reconstruction=reconstruction, work=work)
        space_delete.delete()

        return Response({"message": "Работа успешно удалена из заявки."}, status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(
        operation_summary="Изменить объем работы в заявке на реконструкцию",
        manual_parameters=[
        openapi.Parameter(
            'space',
            openapi.IN_QUERY,
            description="Объем работы",
            type=openapi.TYPE_STRING,
        )
    ]
    )
    def put(self, request, reconstruction_id=None, work_id=None, format=None):
        reconstruction = get_object_or_404(Reconstruction, pk=reconstruction_id, status='draft')
        work = get_object_or_404(Work, pk=work_id)

        change_space = get_object_or_404(Space, reconstruction=reconstruction, work=work)
        new_space_value = request.query_params.get('space')

        if new_space_value is not None:
            change_space.space = new_space_value
            change_space.save()

        return Response({"message": "Объем работ изменен."}, status=status.HTTP_200_OK)