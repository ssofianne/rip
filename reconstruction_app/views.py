from django.http import Http404, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_GET

from django.db import connection

from django.contrib.auth.models import User
from reconstruction_app.models import Work, Application, Space


def page2(request, work_id):

    searched_work = get_object_or_404(Work, pk=work_id)
    
    if searched_work.is_deleted == True:
      return Http404("Реконструкционная работа удалена")
    
    context = {
        'work': searched_work
    }
    return render(request, 'page2.html', context)


def page3(request, application_id):
    application = get_object_or_404(Application, pk=application_id)

    if application.status != 'draft':
       return render(request, 'error_404.html')

    spaces = Space.objects.filter(application=application).order_by('space')

    application_works = []
    index = 1
    for space in spaces:
      if space.work.is_deleted is False:
        application_works.append({ 'work': space.work,'space': space.space, 'index': index })
        index += 1

    place = ''
    if application.place is not None:
       place = application.place
    fundraising = ''
    if application.fundraising is not None:
       fundraising = application.fundraising   

    context = {
      'id': application.id,
      'place': place,
      'fundraising':fundraising,
      'works': application_works,
    }

    return render(request, 'page3.html', context)


def main_page(request):

     type_of_work = request.GET.get('type_of_work', '')
     all_works = Work.objects.filter(is_deleted=False)

     if type_of_work:
      all_works = all_works.filter(title__istartswith=type_of_work)

     default_user = User.objects.get(id=3) # id = 1 is superuser
     user_applications = Application.objects.filter(user=default_user)
     draft_application = user_applications.filter(status='draft').first()

    #  if not draft_application:
    #     draft_application = Application.objects.create(user=default_user, status='draft')

     spaces = Space.objects.filter(application=draft_application)
     application_size = 0

     for space in spaces:
        if space.work.is_deleted is False:
           application_size += 1    

     context = {
        'works': all_works,
        'application': draft_application,
        'application_counter': application_size,
    }
     
     return render(request, 'index.html', context)



def add_work(request, work_id):
    default_user = User.objects.get(id=3) # id = 1 is superuser
    user_applications = Application.objects.filter(user=default_user)
    draft_application = user_applications.filter(status='draft').first()

    chosen_work = Work.objects.get(pk=work_id)

    if not draft_application:
        draft_application = Application.objects.create(user=default_user, status='draft')

    spaces = Space.objects.filter(application=draft_application)

    if spaces.filter(work=chosen_work):
        print('Данная реконструкционная работа уже добавлена в заявку')
        return redirect('main_page')
    
    Space.objects.create(application=draft_application, work=chosen_work)

    return redirect('main_page')

def application_delete(request, application_id):
    application = Application.objects.get(id=application_id)
    spaces_counter = Space.objects.filter(application=application).count()

    with connection.cursor() as cursor:
        cursor.execute("UPDATE application SET status = 'deleted'", [spaces_counter, application_id])
        print("Заявка удалена.")
        
    return redirect('main_page')