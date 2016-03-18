# coding=utf-8

from rest_framework import serializers

from oscar.core.loading import get_model

from stars.apps.address.models import ReceivingAddress
from stars.apps.catalogue.models import Product
from stars.apps.commission.models import UserPickupAddr

WishLine = get_model('wishlists', 'Line')

class NameValueField(serializers.Field):
    """
    Color objects are serialized into 'rgb(#, #, #)' notation.
    """
    def to_representation(self, obj):
        return obj.name


class WishLineProductSerializer(serializers.ModelSerializer):
    current_price = serializers.ReadOnlyField(source='product.buy_price')
    market_price = serializers.ReadOnlyField(source='product.current_price_for_display')
    img_url = serializers.ImageField(source='product.primary_image_url')
    product_id = serializers.ReadOnlyField(source='product.id')
    product_title = serializers.ReadOnlyField(source='product.title')
    volume = serializers.ReadOnlyField(source='product.volume')

    class Meta:
        model = WishLine
        fields = ('product_id',
                  'product_title',
                  'img_url',
                  'market_price',
                  'current_price',
                  'volume'
                  )
        read_only_fields = fields


class UserPickupAddressSerializer(serializers.ModelSerializer):
    pickup_name = serializers.ReadOnlyField(source='pickup_addr.name')
    address = serializers.ReadOnlyField(source='pickup_addr.addr')
    tel = serializers.ReadOnlyField(source='pickup_addr.tel')
    contact = serializers.ReadOnlyField(source='pickup_addr.contact')
    province = serializers.ReadOnlyField(source='pickup_addr.province.name')
    city = serializers.ReadOnlyField(source='pickup_addr.city.name')
    district = serializers.ReadOnlyField(source='pickup_addr.district.name')
    address_id = serializers.ReadOnlyField(source='pickup_addr_id')

    class Meta:
        model = UserPickupAddr
        fields = ('id', 'is_default',
                  'pickup_name',
                  'contact',
                  'address',
                  'province',
                  'city',
                  'district',
                  'tel',
                  'address_id',
                  )
        read_only_fields = fields


class ReceivingAddressSerializer(serializers.ModelSerializer):
    mobile = serializers.ReadOnlyField(source='mobile_phone')
    name = serializers.ReadOnlyField(source='consignee')
    city = NameValueField()
    province = NameValueField()
    district = NameValueField()

    class Meta:
        model = ReceivingAddress
        fields = ('id', 'is_default', 'address',
                  'mobile',
                  'name',
                  'province',
                  'city',
                  'district',
                  'telephone',
                  'email',
                  )
        read_only_fields = fields


class ProductSimpleSerializer(serializers.ModelSerializer):
    current_price = serializers.ReadOnlyField(source='buy_price')
    market_price = serializers.ReadOnlyField(source='current_price_for_display')
    img_url = serializers.ImageField(source='primary_image_url')

    class Meta:
        model = Product
        fields = ('id', 'title',
                  'img_url',
                  'market_price',
                  'current_price',
                  )
        read_only_fields = fields


class ProductSearchResultSerializer(ProductSimpleSerializer):

    class Meta:
        model = Product
        fields = ('id', 'title',
                  'img_url',
                  'market_price',
                  'current_price',
                  'volume',
                  )
        read_only_fields = fields