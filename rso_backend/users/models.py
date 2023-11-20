from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Profile(models.Model):
    """Профиль"""
    # ---Основная информация---
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    patronymic = models.CharField(max_length=40, blank=True, default='', verbose_name='Отчество')
    last_name_lat = models.CharField(max_length=40, blank=True, default='', verbose_name='Фамилия (латиница)')
    first_name_lat = models.CharField(max_length=40, blank=True, default='', verbose_name='Имя (латиница)')
    patronymic_lat = models.CharField(max_length=40, blank=True, default='', verbose_name='Отчество (латиница)')

    # regional_office
    region = models.ForeignKey('Region', null=True, on_delete=models.PROTECT, verbose_name='Регион ОО')
    GENDERS = [('', '-'), ('Мужской', 'Мужской'), ('Женский', 'Женский')]
    gender = models.CharField(max_length=10, blank=True, choices=GENDERS, default='', verbose_name='Пол')
    date_of_birth = models.DateField(verbose_name='Дата рождения')
    telephone = models.CharField(max_length=30, blank=True, default='+7', verbose_name='Телефон')
    # detachment

    UNIT_TYPES = [
        ('detachment', 'Отряд'),
        ('other_unit', 'Другая структурная единица'),
        # Добавьте другие типы структурных единиц по мере необходимости
    ]
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPES, default='detachment',
                                 verbose_name='Тип структурной единицы')
    detachment = models.ForeignKey('Detachment', blank=True, null=True, on_delete=models.PROTECT, verbose_name='Отряд')

    # Направление ЛСО
    study_institution = models.CharField(max_length=40, blank=True, default='',
                                         verbose_name='Образовательная организация')
    study_faculty = models.CharField(max_length=40, blank=True, default='', verbose_name='Факультет')
    study_group = models.CharField(max_length=20, blank=True, default='', verbose_name='Курс')
    STUDY_FORMS = [('', '-'), ('очная', 'очная'), ('очно-заочная', 'очно-заочная'), ('вечерняя', 'вечерняя'),
                   ('заочная', 'заочная'), ('дистанционная', 'дистанционная')]
    study_form = models.CharField(max_length=15, blank=True, choices=STUDY_FORMS, default='', verbose_name='Форма '
                                                                                                           'обучения')
    study_year = models.CharField(max_length=10, blank=True, default='', verbose_name='Курс')
    study_spec = models.CharField(max_length=40, blank=True, default='', verbose_name='Специальность')

    # ---ДОКУМЕНТЫ---
    SNILS = models.CharField(max_length=15, blank=True, default='', verbose_name='СНИЛС')
    INN = models.CharField(max_length=15, blank=True, default='', verbose_name='ИНН')
    # INN_file
    # pass_file
    pass_ser_num = models.CharField(max_length=15, blank=True, default='', verbose_name='Номер и серия паспорта')
    # pass_nom = models.CharField(max_length=15, blank=True, default='', verbose_name='Номер паспорта')
    # pass_town = models.CharField(max_length=15, blank=True, default='', verbose_name='Город рождения')
    pass_whom = models.CharField(max_length=15, blank=True, default='', verbose_name='Кем выдан паспорт')
    pass_date = models.DateField(blank=True, null=True, verbose_name='Дата выдачи паспорта')
    # pass_kod = models.CharField(max_length=15, blank=True, default='', verbose_name='Код подразделения, выдавшего '
    #                                                                                 'паспорт')

    work_book_num = models.CharField(max_length=15, blank=True, default='', verbose_name='Трудовая книжка номер')
    inter_pass = models.CharField(max_length=15, blank=True, default='', verbose_name='Загранпаспорт номер')
    MILITARY_DOCUMENT_TYPES = [('', '-'), ('Приписной', 'Удостоверение гражданина пожлежащего вызову на срочную '
                                                        'военную службу'), ('Военник', 'Военный билет')]
    mil_reg_doc_type = models.CharField(max_length=10, blank=True, choices=MILITARY_DOCUMENT_TYPES, default='',
                                        verbose_name='Тип документа воинского учета')
    mil_reg_doc_ser_num = models.CharField(max_length=15, blank=True, default='',
                                           verbose_name='Номер и серия документа воинского учета')

    # pass_address = models.CharField(max_length=15, blank=True, default='',
    # verbose_name='Место регистрации по паспорту')
    # address = models.CharField(max_length=15, blank=True, default='', verbose_name='Фактическое место проживания')

    reg_region = models.ForeignKey('Region', null=True, blank=True, on_delete=models.PROTECT, related_name='reg',
                                   verbose_name='Регион прописки')
    reg_town = models.CharField(max_length=40, blank=True, default='', verbose_name='Населенный пункт прописки')
    reg_house = models.CharField(max_length=40, blank=True, default='', verbose_name='Улица,дом,кв прописки')
    reg_fac_same_address = models.BooleanField(default=False, verbose_name='Адреса регистрации и фактический совпадают')
    fact_region = models.ForeignKey('Region', null=True, blank=True, on_delete=models.PROTECT, related_name='fact',
                                    verbose_name='Регион проживания')
    fact_town = models.CharField(max_length=40, blank=True, default='', verbose_name='Населенный пункт проживания')
    fact_house = models.CharField(max_length=40, blank=True, default='', verbose_name='Улица,дом,кв проживания')

    # pass_sub Документ при отсутствии паспорта
    # ---Дополнительные данные---
    about = models.CharField(max_length=400, blank=True, default='', verbose_name='О себе')
    social_vk = models.CharField(max_length=50, blank=True, default='https://vk.com/', verbose_name='Ссылка на ВК')
    social_tg = models.CharField(max_length=50, blank=True, default='https://t.me/', verbose_name='Ссылка на Телеграм')

    banner = models.ImageField(upload_to='users/banner/%Y/%m/%d', blank=True, verbose_name='Баннер личной страницы')
    photo = models.ImageField(upload_to='users/avatar/%Y/%m/%d', blank=True, verbose_name='Аватарка')
    photo1 = models.ImageField(upload_to='users/photo/%Y/%m/%d', blank=True, verbose_name='Фото 1')
    photo2 = models.ImageField(upload_to='users/photo/%Y/%m/%d', blank=True, verbose_name='Фото 2')
    photo3 = models.ImageField(upload_to='users/photo/%Y/%m/%d', blank=True, verbose_name='Фото 3')
    photo4 = models.ImageField(upload_to='users/photo/%Y/%m/%d', blank=True, verbose_name='Фото 4')

    # document1_title
    # document1
    # document2_title
    # document2
    # document3_title
    # document3
    # document4_title
    # document4
    # document5_title
    # document5
    # document6_titlef
    # document6
    # ---Конфенденциальность (настройки приватности)---
    PRIVACIES = [('1', 'Все'), ('2', 'Члены отряда'), ('3', 'Руководство')]
    privacy_telephone = models.CharField(max_length=15, choices=PRIVACIES, default='1',
                                         verbose_name='Кто видит номер телефона')
    privacy_email = models.CharField(max_length=15, choices=PRIVACIES, default='1',
                                     verbose_name='Кто видит электронную почту')
    privacy_social = models.CharField(max_length=15, choices=PRIVACIES, default='1',
                                      verbose_name='Кто видит мои ссылки на соц сети')
    privacy_about = models.CharField(max_length=15, choices=PRIVACIES, default='1',
                                     verbose_name='Кто видит информацию обо мне')
    privacy_photo = models.CharField(max_length=15, choices=PRIVACIES, default='1',
                                     verbose_name='Кто видит мои фотографии')

    # ---Для несовершеннолетних---
    membership_fee = models.BooleanField(default=False, verbose_name='Членский взнос оплачен')

    detachment = models.ForeignKey('Detachment', blank=True, null=True, on_delete=models.PROTECT, verbose_name='Отряд')
    POSITIONS = [('', 'Без должности'), ('Комиссар', 'Комиссар'), ('Мастер-методист', 'Мастер-методист'),
                 ('Специалист', 'Специалист'), ('Командир', 'Командир')]
    position = models.CharField(max_length=20, blank=True, choices=POSITIONS, default='', verbose_name='Должность')

    @property
    def position_output(self):
        # Если должность в отряде то ЕЁ, инче если оплачен членский БОЕЦ, иначе КАНДИДАТ
        # return ''.join([self.detachment.name, ' Боец'])
        if self.unit_type == 'detachment':
            if self.position == '':
                if self.membership_fee:
                    return 'Боец'
                else:
                    return 'Кандидат'
            else:
                return self.position
        elif self.unit_type == 'other_unit':
            if self.position == '':
                return 'Специалист'
            else:
                return self.position

    def __str__(self):
        return f'Профиль пользователя {self.last_name_lat} {self.first_name_lat}. User id: {self.user.id}'

    class Meta:
        verbose_name_plural = 'профили'
        verbose_name = 'Профиль'


class Region(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Название')
    branch = models.CharField(max_length=100, db_index=True, default='региональное отделение',
                              verbose_name='Региональное отделение')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'регионы'
        verbose_name = 'Регион'


class Unit(models.Model):
    """Структурная единица"""
    name = models.CharField(max_length=100, db_index=True, verbose_name='Название')
    commander = models.OneToOneField(Profile, related_name='commander', null=True, blank=True, on_delete=models.PROTECT,
                                     verbose_name='Командир')
    about = models.CharField(max_length=500, blank=True, verbose_name='Описание', default='')
    emblem = models.ImageField(upload_to='emblems/%Y/%m/%d', blank=True, verbose_name='Эмблема')
    social_vk = models.CharField(max_length=50, blank=True, verbose_name='Ссылка ВК', default='https://vk.com/')
    social_tg = models.CharField(max_length=50, blank=True, verbose_name='Ссылка Телеграм', default='https://')
    banner = models.ImageField(upload_to='emblems/%Y/%m/%d', blank=True, verbose_name='Баннер')
    slogan = models.CharField(max_length=100, blank=True, default='', verbose_name='Девиз')
    founding_date = models.DateField(blank=True, null=True, verbose_name='Дата основания')

    # Уровень Линейный отряд, Штаб учебного заведения, Региональное отделение, (Направление)
    # area = models.ForeignKey('Area', null=True, blank=True, on_delete=models.PROTECT, verbose_name='Направление')
    #
    # flag = models.ImageField(upload_to='flags/%Y/%m/%d', blank=True, verbose_name='Флаг')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'структурные единицы'
        verbose_name = 'Структурная единица'


class Area(models.Model):
    name = models.CharField(max_length=50, blank=False, verbose_name='Название направления')

    # Направления определяются админом/ЦШ или же региональными штабами? Точно должно быть отдельной сущностью.

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'направления'
        verbose_name = 'Направление'


class Detachment(Unit):
    area = models.ForeignKey(Area, null=False, blank=False, on_delete=models.PROTECT, verbose_name='Направление')

    def clean(self):
        if not self.commander:
            raise ValidationError('Отряд должен иметь командира.')

    # регион
    # institution = models.ForeignKey('Institution', null=True, blank=True, on_delete=models.PROTECT,
    #                                verbose_name='Учебное заведение')
    # город
    # Местный штаб

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'отряды'
        verbose_name = 'Отряд'

# Штаб Образовательной Организации
# Регион
# Учебное заведение
# Местный штаб
#
# МестныйШтаб
# Регион
# Номер участника в реестре
# Дата участника в реестре
#
# Региональный Штаб
# Регион
# Год появления Отрядов в регионе
# Дата учредительной конференции
# Номер участника в реестре
# Дата участника в реестре
# Окружной штаб
#
# Окружной Штаб


# class Event(models.Model):
# Формат (онлайн)
# Масштаб
# Название
# Адрес
# Ссылка на конференцию
# Количество участников
# Баннер
# О мероприятии
# Направление (?)
# Вид заявок
# Кто может отправлять заявку
# Многодневное
# Дата начала
# Время начала
# Дата конца
# Время конца
# Дата и время окончания регистрации
# Нужен паспорт
# Нужен СНИЛС
# Нужен ИНН
# Нужна Трудовая книжка
# Нужен Военный билет или приписное свидетельство
# Нужно согласие на обработку персональных данных
# Дополнительный вопрос 1
# Дополнительный вопрос 2
# Дополнительный вопрос 3
