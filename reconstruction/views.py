from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User
from .minio import add_pic, delete_pic
from reconstruction.serializers import WorkSerializer, ReconstructionSerializer, UserSerializer
from reconstruction.models import CustomUser, Work, Reconstruction, Space

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.utils import timezone
import random
from unittest.mock import patch

from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from django.contrib.auth import authenticate, login, logout
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes, permission_classes


# def user():
#     try:
#         user1 = User.objects.get(id=3) 
#     except:
#         print("No such user")
#     return user1
@permission_classes([AllowAny])
@authentication_classes([])
# @csrf_exempt
# @swagger_auto_schema(method='post', request_body=UserSerializer)
# @api_view(['Post'])
# def login_view(request):
#     username = request.data["username"] # допустим передали username и password
#     password = request.data["password"]
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         return HttpResponse("{'status': 'ok'}")
#     else:
#         return HttpResponse("{'status': 'error', 'error': 'login failed'}")

# def logout_view(request):
#     logout(request._request)
#     return Response({'status': 'Success'})

class UserViewSet(viewsets.ModelViewSet):
    """Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    model_class = CustomUser

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

class WorkList(APIView):
    work_class = Work
    work_serializer = WorkSerializer
    reconstruction_class = Reconstruction
    reconstruction_serializer = ReconstructionSerializer

    # def get(self, request, format=None):
    #     works = self.work_class.objects.filter(is_deleted=False)  
    #     work_title = request.data.get('work_title')
    #     if work_title:
    #         works = works.filter(title__icontains=work_title)      
    #     serializer = self.work_serializer(works, many=True)

    #     draft_reconstruction = self.reconstruction_class.objects.filter(user=user(), status='draft').first()
    #     draft_reconstruction_id = 0
    #     count_works = 0
    #     if draft_reconstruction is not None:
    #         draft_reconstruction_id = draft_reconstruction.id
    #         count_works = Space.objects.filter(reconstruction=draft_reconstruction).count()

    #     return Response({'works':serializer.data, 'draft_reconstruction_id':draft_reconstruction_id, 'count_works': count_works})
    
    @swagger_auto_schema(request_body=WorkSerializer)
    def post(self, request, format=None):
        serializer = self.work_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WorkDetail(APIView):
    work_class = Work
    serializer_work = WorkSerializer

    def get(self, request, pk, format=None):
        work = get_object_or_404(self.work_class, pk=pk)
        serializer = self.serializer_work(work)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=WorkSerializer)
    def put(self, request, pk, format=None):
        work = get_object_or_404(self.work_class, pk=pk)
        serializer = self.serializer_work(work, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(request_body=WorkSerializer)
    def post(self, request, pk, format=None):
        work = get_object_or_404(self.work_class, pk=pk)

        new_pic = request.FILES.get('pic')
        if not new_pic:
            return Response({"error": "Изображение не предоставлено."}, status=status.HTTP_400_BAD_REQUEST)
        delete_result = delete_pic(pk)
        if 'error' in delete_result.data:
            return add_result
        add_result = add_pic(work, new_pic)
        if 'error' in add_result.data:
            return add_result
    
        return Response({"message": "Изображение успешно обновлено."}, status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        work = get_object_or_404(self.work_class, pk=pk)
        work.is_deleted = True
        work.save()
        pic_result = delete_pic(pk)
        if 'error' in pic_result.data:
            return pic_result
        return Response({"message": "Работа успешно удалена."}, status=status.HTTP_204_NO_CONTENT)


class ReconstructionList(APIView):
    model_class = Reconstruction
    serializer_class = ReconstructionSerializer

    # def get(self, request, format=None):
    #     user_instance = user()        
    #     reconstructions = self.model_class.objects.filter(user=user_instance).exclude(status__in=['deleted', 'draft'])

    #     status = request.data.get('status')
    #     if status:
    #         reconstructions = reconstructions.filter(status=status)
            
    #     apply_date = request.data.get('apply_date')
    #     if apply_date:
    #         apply_date_datetime = timezone.datetime.fromisoformat(apply_date)
    #         reconstructions = reconstructions.filter(apply_date__date=apply_date_datetime)

    #     serializer = self.serializer_class(reconstructions, many=True)
    #     return Response({'reconstructions': serializer.data})
    
    # @swagger_auto_schema(request_body=WorkSerializer)
    # def post(self, request, format=None):
    #     user_instance = user()
    #     draft_reconstruction, created = Reconstruction.objects.get_or_create(user=user_instance, status='draft', defaults={'creation_date': timezone.now})
        
    #     work_id = request.data.get('work_id')
    #     work = get_object_or_404(Work, pk=work_id, is_deleted=False)

    #     if Space.objects.filter(reconstruction=draft_reconstruction, work=work):
    #         return Response({"error": "Данная работа уже добавлена в заявку"}, status=status.HTTP_400_BAD_REQUEST)
        
    #     Space.objects.create(reconstruction=draft_reconstruction, work=work)

    #     return Response({"message": "Работа успешно добавлена в заявку"}, status=status.HTTP_201_CREATED)


class ReconstructionDetail(APIView):
    work_class = Work
    work_serializer = WorkSerializer
    reconstruction_class = Reconstruction
    reconstruction_serializer = ReconstructionSerializer

    def get(self, request, pk, format=None):
        reconstruction = get_object_or_404(self.reconstruction_class, pk=pk)
        serializer = self.reconstruction_serializer(reconstruction)
        spaces = Space.objects.filter(reconstruction=reconstruction).order_by('space')

        works = []
        for space in spaces:
            if space.work.is_deleted == False:
                work_data = self.work_serializer(space.work).data
                work_data['space'] = space.space
                works.append(work_data)

        return Response({'reconstruction': serializer.data, 'works': works})
    
    @swagger_auto_schema(request_body=WorkSerializer)
    def put(self, request, pk, format=None):
        reconstruction = get_object_or_404(self.reconstruction_class, pk=pk)
        serializer = self.reconstruction_serializer(reconstruction, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        reconstruction = get_object_or_404(self.reconstruction_class, pk=pk)
        reconstruction.status = 'deleted'
        reconstruction.save()
        return Response({"message":"Заявка успешно удалена."},status=status.HTTP_204_NO_CONTENT)

class ReconstructionCreature(APIView):
    model_class = Reconstruction
    serializer_class = ReconstructionSerializer

    @swagger_auto_schema(request_body=WorkSerializer)
    def put(self, request, pk, format=None):
        reconstruction = get_object_or_404(self.model_class, pk=pk)

        if reconstruction.place is None:
            return Response({"error": "В заявке не указано место осуществления работ."}, status=status.HTTP_400_BAD_REQUEST)
        
        spaces = Space.objects.filter(reconstruction=reconstruction)
        for space in spaces:
            if space.space is None or space.space == '':
                return Response({"error": f"Объем для работы '{space.work.title}' не указан."}, status=status.HTTP_400_BAD_REQUEST)

        draft_status = request.data.get('status')
        if draft_status in ['completed', 'rejected']:
            return Response({"error": f"Текущий пользователь не яляется модератором."}, status=status.HTTP_403_FORBIDDEN)

        if reconstruction.status != 'deleted':
            reconstruction.status = 'created'
            reconstruction.apply_date = timezone.now().isoformat()
            reconstruction.save()
            return Response({"message": "Заявка сформирована"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message": "Заявка не найдена"}, status=status.HTTP_404_NOT_FOUND)

class ReconstructionCompletedRejected(APIView):
    model_class = Reconstruction
    serializer_class = ReconstructionSerializer

    # @swagger_auto_schema(request_body=WorkSerializer)
    # def put(self, request, pk, format=None):
    #      user_instance = user()

    #      with patch.object(user_instance, 'is_staff', True):
    #         if not user_instance.is_staff:
    #             return Response({'error': 'Текущий пользователь не является модератором'}, status=status.HTTP_403_FORBIDDEN)
    #         reconstruction = get_object_or_404(self.model_class, pk=pk)
    #         if reconstruction.status != 'created':
    #             return Response({'error': 'Заявка не может быть завершена до того, как будет сформирована'}, status=status.HTTP_403_FORBIDDEN)

    #         reconstruction.fundraising = round(random.uniform(5000, 500000), 2)

    #         draft_status = request.data.get('status')
    #         if draft_status in ['completed', 'rejected']:
    #             reconstruction.status = draft_status
    #         else:
    #             return Response({'error': 'Модератор может только завершить или отклонить заявку.'}, status=status.HTTP_400_BAD_REQUEST)
            
    #         reconstruction.moderator = user_instance
    #         reconstruction.end_date = timezone.now().isoformat()

    #         reconstruction.save()
    #         serializer = self.serializer_class(reconstruction)

    #         return Response(serializer.data)
    
class ReconstructionSpace(APIView):

    def delete(self, request, reconstruction_id=None, work_id=None, format=None):
        reconstruction = get_object_or_404(Reconstruction, pk=reconstruction_id)
        work = get_object_or_404(Work, pk=work_id)
        space_delete = get_object_or_404(Space, reconstruction=reconstruction, work=work)
        space_delete.delete()

        return Response({"message": "Объем работы удален."}, status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(request_body=WorkSerializer)
    def put(self, request, reconstruction_id=None, work_id=None, format=None):
        reconstruction = get_object_or_404(Reconstruction, pk=reconstruction_id, status='draft')
        work = get_object_or_404(Work, pk=work_id)

        change_space = get_object_or_404(Space, reconstruction=reconstruction, work=work)
        new_space_value = request.data.get('space')

        if new_space_value is not None:
            change_space.space = new_space_value
            change_space.save()

        return Response({"message": "Объем работ изменен."}, status=status.HTTP_200_OK)

class UserRegistration(APIView):
    serializer_class = UserSerializer
    
    @swagger_auto_schema(request_body=WorkSerializer)
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Регистрация успешна."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserProfile(APIView):
    model_class = User
    serializer_class = UserSerializer

    # @swagger_auto_schema(request_body=WorkSerializer)
    # def put(self, request, format=None):
    #     user_instance  = user()
    #     serializer = self.serializer_class(user_instance, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLogin(APIView):
    @swagger_auto_schema(request_body=WorkSerializer)
    def post(self, request, format=None):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({"error": "Необходимо указать имя пользователя и пароль."}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({"error": "Аутентификация успешна."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Неверное имя пользователя или пароль."}, status=status.HTTP_401_UNAUTHORIZED)

class UserLogout(APIView):

    @swagger_auto_schema(request_body=WorkSerializer)
    def post(self, request, format=None):
        logout(request)
        return Response({"message": "Выход успешен."}, status=status.HTTP_200_OK)