from django.test import TestCase
from users.models import RSOUser, UserDocuments, UserEducation, UserForeignDocuments, UserMedia, UserParent, UserPrivacySettings, UserRegion, UserStatementDocuments


class RSOUserModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_adult = RSOUser.objects.create(
            username='vasya',
            email='qzQpH@example.com',
            password='dddddddd8',
            first_name='Вася',
            last_name='Петров',
            patronymic_name='Иванович',
            date_of_birth='2000-01-01',
            last_name_lat='Petrov',
            first_name_lat='Vasya',
            patronymic_lat='Ivanovich',
            phone_number='+79995771202',
            gender='male',
            address='Москва',
            bio='О себе',
            social_vk='https://vk.com/1',
            social_tg='https://t.me/1',
        )

    def test_title_label(self):
        """verbose_name поля username совпадает с ожидаемым."""
        user_adult = RSOUserModelTest.user_adult

        verbose = user_adult._meta.get_field('username').verbose_name
        self.assertEqual(verbose, 'Ник')

    def test_create_objects_in_tables(self):
        """Создание объектов в таблицах."""
        user_adult = RSOUserModelTest.user_adult
        models = [
            UserEducation,
            UserDocuments,
            UserForeignDocuments,
            UserRegion,
            UserPrivacySettings,
            UserMedia,
            UserStatementDocuments,
            UserParent,
        ]
        for model in models:
            with self.subTest(model=model):
                self.assertTrue(model.objects.filter(user=user_adult).exists())

