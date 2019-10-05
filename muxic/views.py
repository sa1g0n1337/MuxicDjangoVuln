from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, CreateView, FormView, RedirectView, ListView, DetailView, UpdateView, \
    DeleteView
from django.views.generic.base import View
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from muxic.form import RegisterForm, CreateSongForm, UpdateSongForm
from muxic.models import *


class IndexView(TemplateView):
    template_name = 'muxic/index.html'


class AllSong(ListView):
    template_name = 'muxic/song_list.html'
    context_object_name = 'song_list'
    paginate_by = 10

    def get_queryset(self):
        return Song.objects.all()


class SongDetailView(DetailView):
    template_name = 'muxic/song_detail.html'
    model = Song

    def get_context_data(self, **kwargs):
        context = super(SongDetailView, self).get_context_data(**kwargs)  # get the default context data
        if self.request.user.is_authenticated:
            song = Song.objects.get(id=self.kwargs['pk'])
            user = self.request.user
            if song.favorite_song.filter(user=user).exists():
                is_favorite = True
            else:
                is_favorite = False
            context['is_favorite'] = is_favorite  # add extra field to the context
            return context
        return context


class ProfileView(View):
    template_name = 'muxic/song_upload.html'

    def get(self, request, username):
        user = User.objects.get(username=username)
        user_profile = UserProfile.objects.get(user=user)
        favorite_song = user_profile.favorite.all()
        return render(request, self.template_name, {'user_profile': user_profile, 'favorite_song': favorite_song})


class ProfileFavoriteView(View):
    template_name = 'muxic/song_favorite.html'

    def get(self, request, username):
        user = User.objects.get(username=username)
        user_profile = UserProfile.objects.get(user=user)
        favorite_song = user_profile.favorite.all()
        return render(request, self.template_name, {'user_profile': user_profile, 'favorite_song': favorite_song})


class RegisterView(View):
    form_class = RegisterForm
    template_name = 'muxic/registration_form.html'

    # Display blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # Process form data
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            # Clean data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            # returns User objects if credentials are correct
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('muxic:index')

        return render(request, self.template_name, {'form': form})


class LoginView(FormView):
    form_class = AuthenticationForm
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = 'muxic/login.html'
    success_url = '../../'

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        The user has provided valid credentials (this was checked in AuthenticationForm.is_valid()). So now we
        can log him in.
        """
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if self.success_url:
            redirect_to = self.success_url
        else:
            redirect_to = 'muxic/index.html'
        return redirect_to

    def set_test_cookie(self):
        self.request.session.set_test_cookie()

    def check_and_delete_test_cookie(self):
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
            return True
        return False

    def get(self, request, *args, **kwargs):
        """
        Same as django.views.generic.edit.ProcessFormView.get(), but adds test cookie stuff
        """
        self.set_test_cookie()
        return super(LoginView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Same as django.views.generic.edit.ProcessFormView.post(), but adds test cookie stuff
        """

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            self.check_and_delete_test_cookie()
            return self.form_valid(form)
        else:
            self.set_test_cookie()
            return self.form_invalid(form)


class LogoutView(RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'muxic:index'

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return super().get_redirect_url(*args, **kwargs)


class Search(ListView):
    template_name = 'muxic/song_list.html'

    def get(self, request):
        song_list = Song.objects.all().order_by("-date_release")
        query = request.GET.get("q")
        if query:
            song_list = song_list.filter(
                Q(title__icontains=query)
            ).distinct()

            return render(request, self.template_name, {'song_list': song_list})
        else:
            return render(request, self.template_name, )


class SongCreate(CreateView):
    form_class = CreateSongForm
    model = Song
    template_name = 'muxic/song_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(SongCreate, self).form_valid(form)


class SongUpdate(UpdateView):
    model = Song
    form_class = UpdateSongForm


class SongDelete(DeleteView):
    model = Song

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        user = request.user
        success_url = reverse_lazy('muxic:user', kwargs={'username': user.username})
        self.object.delete()
        return HttpResponseRedirect(success_url)


class FavoriteView(View):

    def get(self, request, *args, **kwargs):
        if 'pk' in self.kwargs:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            song = Song.objects.get(id=self.kwargs['pk'])
            song.favorite.add(user)
            user_profile.favorite.add(song)
            song.save()
            user_profile.save()
            # template = request.GET.get('path')  # Lấy link trước đó để quay lại trang trước
            success_url = reverse_lazy('muxic:songdetail', kwargs={'pk': song.pk})
        return HttpResponseRedirect(success_url)


class UnFavoriteView(View):

    def get(self, request, *args, **kwargs):
        if 'pk' in self.kwargs:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            song = Song.objects.get(id=self.kwargs['pk'])
            song.favorite.remove(user)
            user_profile.favorite.remove(song)
            song.save()
            user_profile.save()
            success_url = reverse_lazy('muxic:songdetail', kwargs={'pk': song.pk})
        return HttpResponseRedirect(success_url)


class GenreFilter(ListView):
    template_name = 'muxic/song_list.html'

    def get(self, request, genre):
        song_list = Song.objects.filter(genre=genre)
        return render(request, self.template_name, {'song_list': song_list})
