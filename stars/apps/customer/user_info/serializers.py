# coding=utf-8
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from stars.apps.accounts.models import UserProfile
from stars.apps.address.models import Province, City, District


class UserInfoSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='user.email')
    username = serializers.ReadOnlyField(source='user.username')
    province_id = serializers.ReadOnlyField(source='region.city.province_id')
    city_id = serializers.ReadOnlyField(source='region.city_id')
    district_id = serializers.ReadOnlyField(source='region.id')

    class Meta:
        model = UserProfile
        fields = ('email', 'username', 'avatar', 'mobile_phone','real_name', 'sex', 'birthday',
                  'interest','address', 'nickname',
                  'district_id',
                  'province_id',
                  'city_id',
                  )
        read_only_fields = ('mobile_phone', 'real_name', 'avatar',
                            'district_id',
                            'province_id',
                            'city_id',
                            )


class RegionSerializer(serializers.ModelSerializer):
    # city = PrimaryKeyRelatedField(queryset=City.objects.all())
    # cities=PrimaryKeyRelatedField(queryset=City.objects.all())

    class Meta:
        model = District
        fields = ('id', 'name', 'city',
                  # 'cities',

                  )
        read_only_fields = ('id', 'name', 'city',
                            # 'cities',
                            )
        depth=3