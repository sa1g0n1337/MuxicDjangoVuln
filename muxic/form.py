from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import *
from django import forms
import re
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import filesizeformat

from MuxicProject import settings
from muxic.models import UserProfile, Song
from django.utils.translation import gettext as _


class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput,
        max_length=254,
    )
    email = forms.CharField(
        widget=forms.EmailInput,
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        strip=False,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        strip=False,
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password')

    def clean_confirm_password(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if len(password) < 6:
            print("check1")
            raise forms.ValidationError("Mật khẩu từ 6 đến 24 kí tự!")

        elif len(password) > 24:
            print("check2")
            raise forms.ValidationError("Mật khẩu từ 6 đến 24 kí tự!")

        elif password != confirm_password:
            raise forms.ValidationError("Mật khẩu bạn nhập không trùng!")
            # raise ValidationError("Mật khẩu bạn nhập không trùng!")
        else:
            return confirm_password

    def clean_username(self):
        clean_data = super(RegisterForm, self).clean()
        username = clean_data.get('username')
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError("Tên tài khoản có ký tự đặc biệt!")

        if len(username) < 6:
            raise forms.ValidationError("Tên tài khoản từ 6 đến 24 kí tự!")

        if len(username) > 24:
            raise forms.ValidationError("Tên tài khoản từ 6 đến 24 kí tự!")

        try:
            UserProfile.objects.get(user__username=username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError("Tài khoản đã tồn tại")

    def clean_email(self):
        clean_data = super(RegisterForm, self).clean()
        email = clean_data.get('email')

        try:
            UserProfile.objects.get(user__email=email)
        except ObjectDoesNotExist:
            return email
        raise forms.ValidationError("Email đã tồn tại")


class CreateSongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'artist', 'genre', 'logo', 'file', 'date_release', 'lyric']
        widgets = {
            'date_release': forms.SelectDateWidget(),
        }

    def clean_logo(self):
        cleaned_data = super(CreateSongForm, self).clean()
        logo = cleaned_data.get('logo')
        logo_type = logo.content_type.split('/')[0]
        if logo_type in settings.LOGO_TYPES:
            if logo._size > settings.MAX_UPLOAD_SIZE:
                raise forms.ValidationError(
                    _('Vui lòng tải lên hình ảnh có dung lượng dưới %s. Dung lượng hiện tại %s') % (
                        filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(logo._size)))
        else:
            raise forms.ValidationError(_('Không hỗ trợ kiểu file'))
        return logo

    def clean_file(self):
        cleaned_data = super(CreateSongForm, self).clean()
        file = cleaned_data.get('file')
        file_type = file.content_type.split('/')[0]
        if file_type in settings.MUSIC_TYPES:
            if file._size > settings.MAX_UPLOAD_SIZE:
                raise forms.ValidationError(
                    _('Vui lòng tải lên bài hát có dung lượng dưới %s. Dung lượng hiện tại %s') % (
                        filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(file._size)))
        else:
            raise forms.ValidationError(_("Vui lòng tải lên file nhạc (.mp3)"))
        return file


class UpdateSongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'artist', 'genre', 'logo', 'file', 'date_release', 'lyric']
        widgets = {
            'date_release': forms.SelectDateWidget()
        }

    def clean_logo(self):
        cleaned_data = super(UpdateSongForm, self).clean()
        logo = cleaned_data.get('logo')
        logo_type = logo.content_type.split('/')[0]
        if logo_type in settings.LOGO_TYPES:
            if logo._size > settings.MAX_UPLOAD_SIZE:
                raise forms.ValidationError(
                    _('Vui lòng tải lên hình ảnh có dung lượng dưới %s. Dung lượng hiện tại %s') % (
                        filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(logo._size)))
        else:
            raise forms.ValidationError(_('Không hỗ trợ kiểu file'))
        return logo

    def clean_file(self):
        cleaned_data = super(UpdateSongForm, self).clean()
        file = cleaned_data.get('file')
        file_type = file.content_type.split('/')[0]
        if file_type in settings.MUSIC_TYPES:
            if file._size > settings.MAX_UPLOAD_SIZE:
                raise forms.ValidationError(
                    _('Vui lòng tải lên bài hát có dung lượng dưới %s. Dung lượng hiện tại %s') % (
                        filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(file._size)))
        else:
            raise forms.ValidationError(_("Vui lòng tải lên file nhạc (.mp3)"))
        return file
