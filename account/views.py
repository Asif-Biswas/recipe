from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import re
from django.contrib.auth.decorators import login_required
from .models import UserProfile, OTPVerification
from django.core.mail import send_mail
import random
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from django.conf import settings
from django.template.loader import render_to_string
import json

# Create your views here.


def handleLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is None:
            # try to authenticate with email
            try:
                user = User.objects.get(email=username)
                user = authenticate(
                    request, username=user.username, password=password)
                print(user)
            except User.DoesNotExist:
                messages.error(request, 'Invalid username or password')
                return render(request, 'account/login.html')

        if user is not None:
            login(request, user)
            return redirect('main:home')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'account/login.html')
    return render(request, 'account/login.html')


def handleLogout(request):
    logout(request)
    return redirect('account:login')


def handleSignup(request):
    if request.method == 'POST':
        fullname = request.POST.get('full-name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # check fullname is char and space only
        if not re.fullmatch(r'[A-Za-z ]+', fullname):
            messages.error(request, 'Invalid fullname. Only characters and spaces allowed')
            return render(request, 'account/signup.html')

        # check valid email
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            messages.error(request, 'Invalid email')
            return render(request, 'account/signup.html')

        username = email.split('@')[0]
        if User.objects.filter(username=username).exists():
            username = username + \
                str(User.objects.filter(username=username).count())

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'account/signup.html')
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters')
            return render(request, 'account/signup.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'account/signup.html')

        user = User.objects.create_user(username, email, password)
        if ' ' in fullname:
            user.first_name = ' '.join(fullname.split(' ')[:-1])
            user.last_name = fullname.split(' ')[-1]
        else:
            user.first_name = fullname
        user.save()

        userProfile = UserProfile.objects.get_or_create(
            user=user,
            full_name=fullname,
        )[0]
        userProfile.save()

        # login user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            otp = random.randint(100000, 999999)

            otpVerification = OTPVerification.objects.get_or_create(user=request.user)[
                0]
            otpVerification.otp = otp
            otpVerification.sent_at = timezone.now()
            otpVerification.save()

            # send otp to email
            name = request.user.first_name
            template = render_to_string(
                'account/otpEmail.html', {'name': name, 'otp': otp, 'action': 'Verify Email'})
            send_mail(
                'OTP for Email Verification',
                template,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
                html_message=template,
            )
            message = 'OTP sent to ' + email
            messages.success(request, message)
            context = {
                'verifyEmailPage': True,
                'title': 'Verify Email',
            }
            return render(request, 'account/verifyEmail.html', context)
        return redirect('account:login')
    return render(request, 'account/signup.html')


@login_required(login_url='account:login')
def verifyEmail(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        otpVerification = OTPVerification.objects.get(user=request.user)
        now = timezone.now()
        if now - otpVerification.sent_at > timedelta(minutes=5):
            messages.error(request, 'OTP expired')
            context = {
                'verifyEmailPage': True,
                'title': 'Verify Email',
                'resend_button': True
            }
            return render(request, 'account/verifyEmail.html', context)

        if str(otpVerification.otp) == otp:
            messages.success(request, 'Email verified successfully')
            user = request.user
            userProfile = UserProfile.objects.get_or_create(user=user)[0]
            userProfile.verified = True
            userProfile.save()
            return redirect('main:home')
        else:
            messages.error(request, 'Invalid OTP')
            context = {
                'verifyEmailPage': True,
                'title': 'Verify Email',
            }
            return render(request, 'account/verifyEmail.html', context)

    email = request.user.email
    otp = random.randint(100000, 999999)

    otpVerification = OTPVerification.objects.get_or_create(user=request.user)[
        0]
    now = timezone.now()
    if now - otpVerification.sent_at < timedelta(minutes=2):
        try_after = 2 - (now - otpVerification.sent_at).seconds // 60
        messages.error(request, f'Otp already sent. Try after {try_after} minutes')
        context = {
            'verifyEmailPage': True,
            'title': 'Verify Email',
            'resend_button': True,
        }
        return render(request, 'account/verifyEmail.html', context)
    otpVerification.otp = otp
    otpVerification.sent_at = timezone.now()
    otpVerification.save()

    # send otp to email
    name = request.user.first_name
    template = render_to_string(
        'account/otpEmail.html', {'name': name, 'otp': otp, 'action': 'Verify Email'})
    send_mail(
        'OTP for Email Verification',
        template,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
        html_message=template,
    )
    message = 'OTP sent to ' + email
    messages.success(request, message)
    context = {
        'verifyEmailPage': True,
        'title': 'Verify Email',
    }
    return render(request, 'account/verifyEmail.html', context)


def verifyOTP(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        email = request.POST.get('email')
        forget_password = request.POST.get('forget_password')
        otpVerification = OTPVerification.objects.get(
            user=User.objects.get(email=email))
        now = timezone.now()
        otp_sent_at = otpVerification.sent_at
        if now - otp_sent_at > timedelta(minutes=5):
            messages.error(request, 'OTP expired. Please try again.')
            return render(request, 'account/forgetPassword.html')

        if otp == str(otpVerification.otp):
            otpVerification.verified = True
            otpVerification.save()
            if forget_password:
                context = {
                    'resetPasswordPage': True,
                    'title': 'Reset Password',
                    'email': email,
                }
                return render(request, 'account/resetPassword.html', context)
            return redirect('main:home')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            context = {
                'verifyEmailPage': True,
                'title': 'Verify Email',
                'email': email,
            }
            return render(request, 'account/verifyOTP.html', context)

    return render(request, 'account/forgetPassword.html')


def forgetPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        print(email)
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            otpVerification = OTPVerification.objects.get_or_create(user=user)[
                0]
            prev_otp_sent_at = otpVerification.sent_at
            now = timezone.now()
            if now - prev_otp_sent_at < timedelta(minutes=2):
                try_again_in = 2 - (now - prev_otp_sent_at).seconds // 60
                messages.error(request, f'OTP already sent. Try again in {try_again_in} minutes')
                context = {
                    'verifyEmailPage': True,
                    'title': 'Forget Password',
                    'email': email,
                    'otp_already_sent': True,
                }
                return render(request, 'account/verifyOTP.html', context)
            otp = random.randint(100000, 999999)
            otpVerification.otp = otp
            otpVerification.sent_at = now
            otpVerification.save()

            # send otp to email
            name = user.first_name
            template = render_to_string(
                'account/otpEmail.html', {'name': name, 'otp': otp})
            send_mail(
                'OTP for password reset',
                template,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
                html_message=template,
            )

            message = f'OTP sent to {email}'
            messages.success(request, message)
            context = {
                'verifyEmailPage': True,
                'title': 'Verify Email',
                'email': email,
                'forget_password': True,
            }
            return render(request, 'account/verifyOTP.html', context)
        else:
            messages.error(request, 'Email does not exists')
            return render(request, 'account/forgetPassword.html')

    return render(request, 'account/forgetPassword.html')


def resetPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            messages.error(request, 'Password does not match')
            context = {
                'resetPasswordPage': True,
                'title': 'Reset Password',
                'email': email,
            }
            return render(request, 'account/resetPassword.html', context)

        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return redirect('account:login')

    return render(request, 'account/forgetPassword.html')


@login_required(login_url='account:login')
def profile(request):
    userProfile = UserProfile.objects.get(user=request.user)
    context = {
        'profilePage': True,
        'title': 'Profile',
        'userProfile': userProfile,
    }
    return render(request, 'account/profile.html', context)


def editProfile(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        username = request.POST.get('username')
        bio = request.POST.get('bio')
        profile_picture = request.FILES.get('profile-picture')
        facebook_link = request.POST.get('facebook-link')
        twitter_link = request.POST.get('twitter-link')
        instagram_link = request.POST.get('instagram-link')
        youtube_link = request.POST.get('youtube-link')
        website_link = request.POST.get('website-link')
        social_media_links = {
            'facebook': facebook_link,
            'twitter': twitter_link,
            'instagram': instagram_link,
            'youtube': youtube_link,
        }

        # validate username
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if user != request.user:
                messages.error(request, 'Username already exists')
                userProfile = UserProfile.objects.get(user=request.user)
                context = {
                    'profilePage': True,
                    'title': 'Profile',
                    'userProfile': userProfile,
                }
                return render(request, 'account/profile.html', context)

        # username can contain only letters, numbers and underscores
        if not re.match(r'^[\w.@+-]+$', username):
            userProfile = UserProfile.objects.get(user=request.user)
            messages.error(request, 'Username can contain only letters, numbers and underscores')
            context = {
                'profilePage': True,
                'title': 'Profile',
                'userProfile': userProfile,
            }
            return render(request, 'account/profile.html', context)

        # fullname can contain only letters and spaces
        if not re.match(r'^[a-zA-Z ]+$', fullname):
            userProfile = UserProfile.objects.get(user=request.user)
            messages.error(request, 'Fullname can contain only letters and spaces')
            context = {
                'profilePage': True,
                'title': 'Profile',
                'userProfile': userProfile,
            }
            return render(request, 'account/profile.html', context)

        # update user
        user = request.user
        user.username = username
        user.first_name = fullname.split(' ')[0]
        user.last_name = ' '.join(fullname.split(' ')[1:])
        user.save()

        # update user profile
        userProfile = UserProfile.objects.get(user=request.user)
        userProfile.full_name = fullname
        userProfile.bio = bio
        userProfile.website_link = website_link
        userProfile.social_media_links = json.dumps(social_media_links)
        if profile_picture:
            userProfile.profile_picture = profile_picture
        userProfile.save()

        messages.success(request, 'Profile updated successfully')
        context = {
            'profilePage': True,
            'title': 'Profile',
            'userProfile': userProfile,
        }
        return render(request, 'account/profile.html', context)

    return redirect('account:profile')


def userProfile(request, username):
    user = User.objects.get(username=username)
    userProfile = UserProfile.objects.get(user=user)
    context = {
        'userProfile': userProfile,
        'title': 'Profile',
    }
    return render(request, 'account/profile.html', context)



