from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_GET

from django.db import connection

from django.contrib.auth.models import User
from reconstruction_app.models import Work, Application, Space

cards = [
    {
        'id': 1,
        'image': 'http://127.0.0.1:9000/fond-media/1.jpg',
        'title': 'Разборка и замена конструкций здания',
        'price': 4000,
        'description': 'Разборка и замена конструкций здания (стен, перекрытий и т. д.) — это процесс, который включает демонтаж старых или поврежденных элементов. Сначала проводится оценка состояния здания, чтобы определить степень повреждений и необходимость замены. Затем осуществляется аккуратный демонтаж. После этого подготавливается основание для установки новых конструкций. На заключительном этапе монтируются новые элементы, используя современные материалы, и выполняются финишные работы для подготовки здания к эксплуатации. Этот процесс необходим для обеспечения безопасности и продления срока службы здания.'
    },
    {
        'id': 2,
        'image': 'http://127.0.0.1:9000/fond-media/2.jpg',
        'title': 'Перепланировка помещений',
        'price': 14500,
        'description': 'Услуга перепланировки помещений включает в себя профессиональное изменение внутренней структуры, направленное на оптимизацию пространства. Мы предлагаем увеличение высоты или площади помещений, что позволяет создать более комфортные и функциональные условия для эксплуатации. Наша команда специалистов разработает индивидуальный проект, учитывающий ваши потребности и требования, обеспечивая максимальную эффективность использования каждого квадратного метра.'
    },
    {
        'id': 3,
        'image': 'http://127.0.0.1:9000/fond-media/3.jpg',
        'title': 'Усиление конструкций здания',
        'price': 6500,
        'description': 'Услуга усиления конструкций здания направлена на повышение прочности и устойчивости существующих строительных элементов. Мы предлагаем профессиональную оценку состояния конструкций, разработку индивидуальных решений и выполнение работ по укреплению, что обеспечивает безопасность и долговечность вашего здания. Наша команда специалистов использует современные технологии и материалы, чтобы гарантировать надежность и соответствие всем строительным нормам.'
    },
    {
        'id': 4,
        'image': 'http://127.0.0.1:9000/fond-media/4.jpg',
        'title': 'Усиление фундамента здания',
        'price': 20000,
        'description': 'Усиление фундамента здания включает мероприятия по укреплению и восстановлению его прочности. Это может включать инъекционные работы для заполнения трещин, установку дополнительных опор, подкрепление стен и улучшение грунта под фундаментом. Основная цель — обеспечить долговечность и безопасность здания.'
    },
    {
        'id': 5,
        'image': 'http://127.0.0.1:9000/fond-media/5.jpg',
        'title': 'Пристройка и надстройка здания',
        'price': 35000,
        'description': 'Пристройка и надстройка здания — это услуги, направленные на увеличение полезной площади существующих зданий. Пристройка подразумевает добавление новых помещений к уже существующему зданию, что позволяет расширить его функциональные возможности. Надстройка включает в себя возведение дополнительных этажей на крыше здания, что также увеличивает его площадь и может использоваться для создания новых жилых или офисных пространств. Оба процесса требуют тщательного проектирования и согласования с местными властями, а также соблюдения строительных норм и правил.'
    },
    {
        'id': 6,
        'image': 'http://127.0.0.1:9000/fond-media/6.jpg',
        'title': 'Ландшафтные работы',
        'price': 3000,
        'description': 'Ландшафтные работы — это комплекс услуг, направленных на благоустройство и озеленение территорий. Они включают проектирование и создание ландшафта, укладку газонов, посадку деревьев и кустарников, устройство цветников, водоемов и дорожек, а также установку малых архитектурных форм (беседок, фонтанов и т.д.). Основная цель ландшафтных работ — улучшение эстетического восприятия пространства, создание комфортной и функциональной среды для отдыха и досуга.'
    }
]

works = [
    {
        'id': 1,
        'place': 'Георгиевский храм',
        'fundraising': 56790,
        'card_id': [
            {
                'id': 1,
                'value': '34,6',   
            },
            {
                'id': 2,
                'value': '56,7',
            },
        ]  ,
        
    }
]

def page2(request, card_id):

    card = next((card for card in cards if card['id'] == card_id),None)

    return render(request, 'page2.html', {'card': card})

def page3(request, work_id):

    work = next((work for work in works if work['id'] == work_id), None)
    
    card_in_work = []
    for works_card in work['card_id']:
        for card in cards:
            if card['id'] == works_card['id']:
                card_with_value = card.copy()
                card_with_value['value'] = works_card['value']
                card_in_work.append(card_with_value)
 
    return render(request, 'page3.html', {'cards':card_in_work, 
        'work_id': work['id'],
        'place': work['place'],
        'fundraising': work['fundraising']})


# def main_page(request):
        
#     work = next((work for work in works if work['id'] == 1), None)
#     type_of_work = request.GET.get('type_of_work', '')
#     filtered_cards = cards

#     count = 0
#     if work: 
#         count = len(work['card_id']) 

#     if type_of_work:
#         filtered_cards = [card for card in cards if type_of_work.lower() in card['title'].lower()]
    
#     return render(request, 'index.html', {'cards': filtered_cards, 'type_of_work': type_of_work, 'work': work, 'count': count})
def main_page(request):
     
     work = next((work for work in works if work['id'] == 1), None)

     type_of_work = request.GET.get('type_of_work', '')
     all_works = Work.objects.filter(is_deleted=False)

     if type_of_work:
         all_works = all_works.filter(title=type_of_work)

     default_user = User.objects.get(id=2) # id = 1 is superuser
     user_applications = Application.objects.filter(user=default_user)
     draft_application = user_applications.filter(status='draft').first()

     spaces = Space.objects.filter(application=draft_application)
     application_size = 0

     for space in spaces:
        if space.work.is_deleted is False:
           application_size += 1    

     context = {
        'works': all_works,
        'application': draft_application,
        'application_counter': application_size,
        'work': work
    }
     
     return render(request, 'index.html', context)