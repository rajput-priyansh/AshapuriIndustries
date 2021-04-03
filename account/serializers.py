from django.contrib.auth import authenticate
from django.db.models import Q

from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def get_user(self, username_or_email):
        return User.objects.filter(
            Q(username=username_or_email) | Q(email__iexact=username_or_email)
        ).first()

    def validate_username(self, value):
        if self.get_user(value):
            return value
        else:
            raise serializers.ValidationError('Username or email does not exist.')

    def validate(self, data):
        user = authenticate(
            username=self.get_user(data['username']).username,
            password=data['password']
        )

        if user is not None:
            # profile = Account.objects.get(user=user, profile_type=Account.PROFILE_TYPE_ADMIN)

            # if profile is not None and not profile.is_active:
            #     raise serializers.ValidationError({
            #         'inactive': 'Your account is currently inactive.',
            #     })

            return data
        else:
            raise serializers.ValidationError({
                'password': 'Sorry this is not the user name or password we have on record, please re-enter or request a reset.',
            })


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'email', 'full_name', 'mobile_number', 'is_approved', 'address',
                  'city', 'pan_number', 'gst_number',
                  'is_favourite']


class SettingAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingAccount
        fields = '__all__'


class SettingGSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingGST
        fields = '__all__'


class TermsConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsConditions
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
        ]
