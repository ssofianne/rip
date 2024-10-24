from django.http import Http404, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_GET

from django.db import connection

from django.contrib.auth.models import User
from reconstruction_app.models import Work, Reconstruction, Space


def page2(request, work_id):

    searched_work = get_object_or_404(Work, pk=work_id)
    
    if searched_work.is_deleted == True:
      return Http404("Реконструкционная работа удалена")
    
    context = {
        'work': searched_work
    }
    return render(request, 'page2.html', context)


def page3(request, reconstruction_id):
    reconstruction = get_object_or_404(Reconstruction, pk=reconstruction_id)

    if reconstruction.status != 'draft':
       return render(request, 'error_404.html')

    spaces = Space.objects.filter(reconstruction=reconstruction).order_by('space')

    reconstruction_works = []
    index = 1
    for space in spaces:
      if space.work.is_deleted is False:
        reconstruction_works.append({ 'work': space.work,'space': space.space, 'index': index })
        index += 1

    place = ''
    if reconstruction.place is not None:
       place = reconstruction.place
    fundraising = ''
    if reconstruction.fundraising is not None:
       fundraising = reconstruction.fundraising   

    context = {
      'id': reconstruction.id,
      'place': place,
      'fundraising':fundraising,
      'works': reconstruction_works,
    }

    return render(request, 'page3.html', context)


def main_page(request):

     type_of_work = request.GET.get('type_of_work', '')
     all_works = Work.objects.filter(is_deleted=False)

     if type_of_work:
      all_works = all_works.filter(title__istartswith=type_of_work)

     default_user = User.objects.get(id=3) # id = 1 is superuser
     user_reconstructions = Reconstruction.objects.filter(user=default_user)
     draft_reconstruction = user_reconstructions.filter(status='draft').first()

     spaces = Space.objects.filter(reconstruction=draft_reconstruction)
     reconstruction_size = 0

     for space in spaces:
        if space.work.is_deleted is False:
           reconstruction_size += 1    

     context = {
        'works': all_works,
        'reconstruction': draft_reconstruction,
        'reconstruction_counter': reconstruction_size,
    }
     
     return render(request, 'index.html', context)



def add_work(request, work_id):
    default_user = User.objects.get(id=3) # id = 1 is superuser
    user_reconstructions = Reconstruction.objects.filter(user=default_user)
    draft_reconstruction = user_reconstructions.filter(status='draft').first()

    chosen_work = Work.objects.get(pk=work_id)

    if not draft_reconstruction:
        draft_reconstruction = Reconstruction.objects.create(user=default_user, status='draft')

    spaces = Space.objects.filter(reconstruction=draft_reconstruction)

    if spaces.filter(work=chosen_work):
        print('Данная реконструкционная работа уже добавлена в заявку')
        return redirect('main_page')
    
    Space.objects.create(reconstruction=draft_reconstruction, work=chosen_work)

    return redirect('main_page')

def reconstruction_delete(request, reconstruction_id):
    reconstruction = Reconstruction.objects.get(id=reconstruction_id)

    with connection.cursor() as cursor:
        cursor.execute("UPDATE reconstruction SET status = 'deleted' WHERE id = %s", [reconstruction_id])
        print("Заявка удалена.")
        
    return redirect('main_page')