from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from .forms import BaseRegisterForm
from ..news.models import Author


@login_required
def add_to_authors(request):
    print('1')
    user = request.user
    print(user)
    user_obj = User.objects.get(username=user.username, first_name=user.first_name, last_name=user.last_name)
    author_group = Group.objects.get(name='authors')
    print(author_group)
    if not request.user.groups.filter(name='authors').exists():
        print('2')
        author_group.user_set.add(user)
        Author.objects.create(authorUsername=user_obj)
    return redirect('/')


class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/news/'

    # def post(self, request, *args, **kwargs):
    #     appointment = Appointment(
    #         date = datetime.strptime(request.POST['date'], '%Y-%m-%d'),
    #         client_name = request.POST['client_name'],
    #         message = request.POST['message'],
    #     )
    #     appointment.save()
    #
    #     return redirect('appointments:make_appointment')


