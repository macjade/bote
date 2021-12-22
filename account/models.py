from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

from datetime import timedelta
# Create your models here.
import random

import base64
import uuid


class BoteManager(BaseUserManager):

    def create_user(self, username, email, password=None, is_active=True, is_staff=False, is_admin=False):
        if not username:
            raise ValueError("User must have a username")

        if not email:
            raise ValueError("User must have an email address")

        if not password:
            raise ValueError("User must have a password")

        user_obj = self.model(
            username=username,
            email=self.normalize_email(email)
        )
        user_obj.set_password(password)
        user_obj.active = is_active
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.save(using=self._db)

        return user_obj

    def create_staffuser(self, username, email, password=None):

        user_staff = self.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True
        )

        return user_staff

    def create_superuser(self, username, email, password=None):

        user_admin = self.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True,
            is_admin=True
        )

        return user_admin


class Bote(AbstractBaseUser, PermissionsMixin):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    user = models.BooleanField(default=False)
    email_confirmation = models.BooleanField(default=False)
    date_of_joining = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username']

    objects = BoteManager()

    def __str__(self):
        return str(self.get_full_name()) + " - " + str(self.email)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_full_name(self):
        return str(self.firstname).capitalize() + " " + str(self.lastname).capitalize()

    def get_short_name(self):
        return str(self.firstname).capitalize()

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active

    def checkusername(self, username):
        if self.__class__.objects.filter(username=username).exists():
            return f"{username}_{random.randint(0, 1000)*2}"
        else: return username

    def createuser(self, firstname, lastname, email, password, country_code, phone):

        newuser = self
        newuser.firstname = firstname
        newuser.lastname = lastname
        newuser.email = email
        newuser.username = self.checkusername(f"{firstname}_{lastname}")
        newuser.user = True
        newuser.set_password(password)
        newuser.save()
        newuser.userprofile_set.create(
            country_code = country_code,
            phone = phone,
            user_string_id=uuid.uuid4(),
        )
        newuser.userprofile_set.get().usersetting_set.create()
        return newuser

    def changeusername(self, username):
        changeusername = self
        changeusername.username = username
        changeusername.save()

        return True

class UserProfile(models.Model):

    user = models.ForeignKey(Bote, on_delete=models.CASCADE)
    country_code = models.CharField(max_length=50, default='')
    phone = models.CharField(max_length=100, default='')
    user_string_id = models.CharField(max_length=255, default='', unique=True, blank=True, null=True)
    is_connected = models.BooleanField(default=False)
    profile_picture = models.URLField(default='https://res.cloudinary.com/do7imvim7/image/upload/v1640112764/bote/profile_images/default_updfcj.jpg')

    def __str__(self):
        return f"{self.user.get_full_name()}"

    def connect_user(self, user):

        connectuser = self.__class__.objects.get(user=user.pk)
        connectuser.is_connected = True
        connectuser.save()

        context = {
            "username": user.username,
            "status": "online"
        }

        return context

    def discount_user(self, user):
        disconnectuser = self.__class__.objects.get(user=user.pk)
        disconnectuser.is_connected = False
        disconnectuser.save()
        context = {
            "username": user.username,
            "status": "offline"
        }
        return context

    def change_picture(self, image_url):
        picture = self
        picture.profile_picture = image_url
        picture.save()
        return picture

class UserSetting(models.Model):

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    online_visibility = models.BooleanField(default=True)
    public_visibility = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.user.username}"

    def editusersettings(self, online_visibility, public_visibility):
        setting_user = self
        setting_user.online_visibility = online_visibility
        setting_user.public_visibility = public_visibility
        setting_user.save()

        return True

class TwoFAToken(models.Model):

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=100, default='', unique=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.user.get_full_name()} - {self.verification_code}"

    def generate_token(self):
        seq = '1234567890abcdef'
        token = ''.join(random.choice(seq) for i in range(0, 6))

        if self.__class__.objects.filter(verification_code=token).exists():
            return self.generate_token()

        return token

    def createtwofatoken(self, user):

        newtoken = self
        newtoken.user = user
        newtoken.verification_code = self.generate_token()
        newtoken.save()

        return newtoken

    def edittwofatoken(self):

        edittoken = self
        edittoken.verification_code = self.generate_token()
        edittoken.save()

        return edittoken


class ResetToken(models.Model):

    user = models.ForeignKey(Bote, on_delete=models.CASCADE)
    token = models.CharField(default='', max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.token}"

    def generate_reset_token(self):
        token = str(uuid.uuid4())

        find_token = self.__class__.objects.filter(token=token)
        if find_token.exists():
            return self.generate_reset_token()
        return token