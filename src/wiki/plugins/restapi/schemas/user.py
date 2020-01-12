from django.contrib.auth.models import User, Group
from django.utils import timezone
from marshmallow import fields, validates_schema, pre_load
from marshmallow.validate import Length
from rest_framework.exceptions import ValidationError
from rest_marshmallow import Schema

from ds4reboot.api.utils import Map
from ds4reboot.api.validators import UniqueModelValidator
from user.models import Housemate


class PermissionSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    permission_id = fields.Int()


class GroupSchema(Schema):
    id = fields.Int(required=True, validate=[UniqueModelValidator(type=Group, error="This group does not exist")])
    name = fields.Str()


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)
    is_staff = fields.Bool(dump_only=False)
    is_superuser = fields.Bool(dump_only=False)
    groups = fields.Function(
        lambda user: GroupSchema(user.groups.all(), many=True).data,
        dump_only=True)
    user_permissions = fields.Function(
        lambda user: PermissionSchema(user.user_permissions.all(), many=True).data,
        dump_only=True)

    email = fields.Email(required=True)
    first_name = fields.Str(required=True, validate=[Length(min=2)])
    last_name = fields.Str(required=True, validate=[Length(min=2)], )

    password = fields.Str(load_only=True, validate=[Length(min=6)])
    password_repeat = fields.Str(load_only=True, validate=[Length(min=6)])

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))

        housemate = instance.housemate
        if 'housemate' in validated_data:
            housemate_data = validated_data.pop('housemate')
            for key, value in housemate_data.items():
                setattr(housemate, key, value)
            for key, value in validated_data.items():
                setattr(instance, key, value)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        # first save instance to prevent inconsistent state with SQL errors
        instance.save()
        housemate.save()
        return instance

    @validates_schema
    def check_passwords_equal(self, data, **kwargs):
        if 'password' in data and 'password_repeat' in data:
            if data['password'] != data['password_repeat']:
                raise ValidationError({'password': 'Passwords not equal.'})
            else:
                return data.pop('password_repeat')

    # we dont allow create, only admins can create profiles through UserFullSchema.


# Full detail
class UserFullSchema(UserSchema):
    is_active = fields.Bool(default=True)
    is_staff = fields.Bool(default=False)
    is_superuser = fields.Bool(default=False)
    last_login = fields.DateTime()
    date_joined = fields.DateTime(default=timezone.now())

    # only settable by admin
    username = fields.Str(required=True, validate=[Length(min=4)])
    password = fields.Str(required=True, load_only=True, validate=[Length(min=6)])
    password_repeat = fields.Str(required=True, load_only=True, validate=[Length(min=6)])

    def create(self, validated_data):
        try:
            housemate_data = validated_data.pop('housemate')
            new_user = User.objects.create_user(**validated_data)
            Housemate.objects.create(**housemate_data, user=new_user)
            return new_user
        except Exception as e:
            raise ValidationError({'exception': str(e)})
