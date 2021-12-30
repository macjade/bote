from django.contrib.auth import logout
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework_simplejwt.tokens import RefreshToken
from .models import Bote, TwoFAToken, ResetToken, UserSetting
from django.utils import timezone
from django.core.mail import send_mail


import cloudinary
import cloudinary.uploader
import cloudinary.api
import requests

class UserRegister(APIView):

    permission_classes = (permissions.AllowAny, )

    def post(self, request):
        data = request.data

        firstname = data['firstname']
        lastname = data['lastname']
        country_code = data['country_code']
        phone = data['phone']
        email = data['email']
        password = data['password']

        if Bote.objects.filter(email=email).exists():
            return Response({
                "status": False,
                "message": 'email already exists'
            })

        newuser = Bote().createuser(firstname, lastname, email, password, country_code, phone)
        if newuser:
            token = TokenObtainPairSerializer().validate({
                "email": email,
                "password": password
            })
            return Response({
                "status": True,
                "user": email,
                "username": newuser.username,
                "token": token,
                "profile_image": f'{newuser.userprofile_set.get().profile_picture}'
            })
        return Response({
            "status": False,
            "message": 'Unable to complete registration at the moment'
        })

class ManageUsername(APIView):

    def get(self, request):
        data = request.GET
        username = data["username"]
        auth_user = request.user

        check_user = Bote.objects.filter(username=username).exists()
        context = {}
        print(check_user)
        if check_user:
            context["status"] = False
        else:
            context["status"] = True

        return Response(context)


    def post(self, request):
        data = request.data
        username = data["username"]
        auth_user = request.user

        changeusername = auth_user.changeusername(username)
        context = {}
        context["status"] = True
        return Response(context)

class ChangeProfileImage(APIView):

    def uploadimageanddocument(self, file):
        upload_result = cloudinary.uploader.upload(file, folder='bote/profile_images')
        return upload_result['secure_url']

    def post(self, request):
        data = request.data
        media = data["media"]
        auth_user = request.user.userprofile_set.get()

        changed_image = auth_user.change_picture(self.uploadimageanddocument(media))
        context = {}
        context["status"] = True
        context["profile_image"] = changed_image.profile_picture
        return Response(context)

class NewTwoFAToken(APIView):

    def post(self, request):
        context = {}
        user = request.user.userprofile_set.get()

        get_user = TwoFAToken.objects.filter(user=user.pk)

        if get_user.exists():
            newtoken = get_user[0].edittwofatoken()
        else:
            newtoken = TwoFAToken().createtwofatoken(user)

        if newtoken:
            subject = 'Verification Code'
            body = f"""
                <p>Your Bote verification code</p>
                <b>{newtoken.verification_code}</b>
            """
            send_mail(subject, body, 'noreply <bote@gorlas.net>', [user.user.email], fail_silently=False, html_message=body)
            context['status'] = True
            return Response(context)

        context['status'] = False
        context['message'] = 'Unable to send message at the moment'
        return Response(context)

class VerifyTwoFA(APIView):

    def post(self, request):
        context = {}
        data = request.data
        code = data['code']
        user = request.user.userprofile_set.get()

        find_code = TwoFAToken.objects.filter(user=user.pk, verification_code=code)

        if find_code.exists():
            tz_now = timezone.now()
            expired_time = tz_now - timezone.timedelta(minutes=15)

            if find_code.filter(timestamp__gte=expired_time, timestamp__lte=tz_now).exists():
                context['status'] = True
                context['username'] = str(user.user.username)
                context['profile_image'] = user.profile_picture
            else:
                context['status'] = False
                context['message'] = 'Code has expired'
            find_code.delete()
        else:
            context['status'] = False
            context['message'] = 'Invalid code'

        return Response(context)

class VerifyNumber(APIView):

    def run_number_api(self, api_key, number, country_code):
        verify_num = requests.get(f'http://apilayer.net/api/validate?access_key={api_key}&number={number}&country_code={country_code}&format=1')
        return verify_num.json()

    def verify_number_api(self, number, code):
        apikeys = ['bbc722bff9aa52c1dd58f53941d71177', '1c7b103759c8a2a7328ccc5fadc4f47d', '46e708ee69f17a987d426ac389598892']
        result = {}
        # for i in apikeys:
        temp_result = self.run_number_api(apikeys[0], number, code)
        result = temp_result
        return result

    def get(self, request):
        context = {}
        data = request.GET
        number = data['number']
        code = data['code']

        get_number = self.verify_number_api(number, code)
        if get_number.get('valid', False):
            context['status'] = True
        else:
            context['status'] = True

        return Response(context)

class SendPasswordResetEmail(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request):
        context = {}
        data = request.data

        email = data['email']

        find_email = Bote.objects.filter(email=email)

        if find_email.exists():
            newresettoken = find_email[0].resettoken_set.create(
                token = ResetToken().generate_reset_token()
            )

            subject = 'Password Reset'
            body = f"""
                            <p>Your Bote password reset link</p>
                            <a href="https://festive-albattani-dba546.netlify.app/resetpassword/{newresettoken.token}/">Click here to reset you password</a>
                        """
            send_mail(subject, body, 'noreply <bote@gorlas.net>', [email], fail_silently=False, html_message=body)
            context['status'] = True
            context['message'] = "Instructions has been sent to your email"
        else:
            context['status'] = False
            context['message'] = 'User not found in our record'

        return Response(context)

class ResetPasswordView(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request):
        context = {}
        data = request.GET

        token = data['token']

        find_token = ResetToken.objects.filter(token=token)

        if find_token.exists():
            now_tz = timezone.now()
            d_time = now_tz - timezone.timedelta(minutes=15)

            if find_token.filter(timestamp__gte=d_time, timestamp__lte=now_tz).exists():
                context['status'] = True
            else:
                find_token.delete()
                context['status'] = False
        else:
            context['status'] = False

        return Response(context)

    def post(self, request):
        context = {}
        data = request.data

        token = data['id']
        password = data['password']

        get_token = ResetToken.objects.get(token=token)

        get_token.user.set_password(password)
        get_token.user.save()

        get_token.delete()

        context['status'] = True
        context['message'] = "password changed successfully"

        return Response(context)

class ChangePasswordView(APIView):

    def post(self, request):
        data = request.data
        auth_user = request.user
        password = data["password"]
        confirm_password = data["cnf_password"]
        context = {}
        if password != confirm_password:
            context["status"] = False
            context["message"] = "Password doesn't match"
            return Response(context)

        auth_user.set_password(password)
        auth_user.save()
        context["status"] = True
        return Response(context)

class UserSettingView(APIView):

    def get(self, request):
        auth_user = request.user

        userprofile = auth_user.userprofile_set.get()
        usersetting = userprofile.usersetting_set.get()
        context = {}
        context["status"] = True
        context["settings"] = {
            "online_visibility": usersetting.online_visibility,
            "public_visibility": usersetting.public_visibility
        }

        return Response(context)

    def post(self, request):
        data = request.data
        auth_user = request.user
        userprofile = auth_user.userprofile_set.get()
        online_visibility = data["online_visibility"]
        public_visibility = data["public_visibility"]

        usersetting = userprofile.usersetting_set.get()
        setting_change = usersetting.editusersettings(online_visibility, public_visibility)

        context = {}

        if setting_change:
            context["status"] = True
        else:
            context["status"] = True
            context["message"] = "Unable to change setting"

        return Response(context)

