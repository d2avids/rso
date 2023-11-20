from rest_framework import serializers

from users.models import Area, Detachment, Profile, Region, Unit


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id',
                  'name',
                  'branch')


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ('id',
                  'name',
                  'commander',
                  'about',
                  'emblem',
                  'social_vk',
                  'social_tg',
                  'banner',
                  'slogan',
                  'founding_date')


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id',
                  'name')


class DetachmentSerializer(serializers.ModelSerializer):
    area = AreaSerializer()

    class Meta:
        model = Detachment
        fields = ('id',
                  'name',
                  'commander',
                  'about',
                  'emblem',
                  'social_vk',
                  'social_tg',
                  'banner',
                  'slogan',
                  'founding_date',
                  'area')


class ProfileSerializer(serializers.ModelSerializer):
    detachment = DetachmentSerializer()
    region = RegionSerializer()

    class Meta:
        model = Profile
        fields = ('id',
                  'user',
                  'patronymic',
                  'last_name_lat',
                  'first_name_lat',
                  'patronymic_lat',
                  'region',
                  'gender',
                  'date_of_birth',
                  'telephone',
                  'unit_type',
                  'detachment',
                  'study_institution',
                  'study_faculty',
                  'study_group',
                  'study_form',
                  'study_year',
                  'study_spec',
                  'SNILS',
                  'INN',
                  'pass_ser_num',
                  'pass_whom',
                  'pass_date',
                  'work_book_num',
                  'inter_pass',
                  'mil_reg_doc_type',
                  'mil_reg_doc_ser_num',
                  'reg_region',
                  'reg_town',
                  'reg_house',
                  'reg_fac_same_address',
                  'fact_region',
                  'fact_town',
                  'fact_house',
                  'about',
                  'social_vk',
                  'social_tg',
                  'banner',
                  'photo', 'photo1', 'photo2', 'photo3', 'photo4',
                  'privacy_telephone',
                  'privacy_email',
                  'privacy_social',
                  'privacy_about',
                  'privacy_photo',
                  'membership_fee',
                  'position',
                  'position_output')