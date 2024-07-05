from rest_framework import serializers
from .models import DefaultPermission, Product
import json
import os
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_json_extension(value):
    ext = os.path.splitext(value.name)[1]  # Get the file extension from the name
    valid_extensions = ['.json']
    if not ext.lower() in valid_extensions:
        raise ValidationError(_('Unsupported file extension. Only .json files are allowed.'))


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class DefaultPermissionSerializer1(serializers.ModelSerializer):

    class Meta:
        model = DefaultPermission
        fields = '__all__'


class DefaultPermissionSerializer2(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    permissions = serializers.FileField(validators=[validate_json_extension])

    def create(self, validated_data):
        data = self.file_handle(validated_data['permissions'])
        return DefaultPermission.objects.create(product=validated_data['product'], permissions=data)

    def update(self, instance, validated_data):
        data = None
        if validated_data.get('permissions'):
            data = self.file_handle(validated_data['permissions'])
        instance.product = validated_data.get('product', instance.product)
        instance.permissions = data if data else instance.permissions
        instance.save()
        return instance

    @staticmethod
    def file_handle(permissions_file):
        file_name = os.path.join('', permissions_file.name)

        # Write the file to the desired location
        with open(file_name, 'wb+') as destination:
            for chunk in permissions_file.chunks():
                destination.write(chunk)
        
        with open(file_name, 'r') as f:
            data = json.load(f)
        os.remove(file_name)
        return data
