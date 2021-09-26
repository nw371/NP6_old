from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail, EmailMultiAlternatives
from django.http import request
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, TemplateView, FormView, UpdateView, DeleteView
from .forms import PostForm
from .filters import PostFilter
from .models import Post, Category, Subscriber


class News(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'news/news.html'  # указываем имя шаблона, в котором будет лежать HTML, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'news'  # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через HTML-шаблон
    queryset = Post.objects.order_by('-date')
    paginate_by = 10

class SearchNews(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'news/search.html'  # указываем имя шаблона, в котором будет лежать HTML, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'search'  # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через HTML-шаблон
    queryset = Post.objects.order_by('-date')
    paginate_by = 5

    def get_context_data(self, **kwargs):  # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса (привет, полиморфизм, мы скучали!!!)
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())  # вписываем наш фильтр в контекст
        return context

# создаём представление, в котором будут детали конкретного отдельного поста
class PostDetail(DetailView):
    model = Post  # модель всё та же, но мы хотим получать детали конкретно отдельного поста
    template_name = 'news/post.html'  # название шаблона будет post.html
    context_object_name = 'post'  # название объекта. в нём будет

class AddPub(PermissionRequiredMixin,FormView):
    permission_required = ('post.add_product',)
    model = Post
    template_name = 'news/add.html'
    context_object_name = 'add'
    form_class = PostForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)  # создаём новую форму, забиваем в неё данные из POST-запроса

        if form.is_valid():  # если пользователь ввёл всё правильно и нигде не ошибся, то сохраняем новый пост
            form.save()

        return super().get(request, *args, **kwargs)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['is_not_author'] = not self.request.user.groups.filter(name = 'author').exists()
    #     return context

class PostEdit(PermissionRequiredMixin, UpdateView):
    model = Post  # модель всё та же, но мы хотим получать детали конкретно отдельного поста
    template_name = 'news/edit.html'  # название шаблона будет edit.html
    #context_object_name = 'post'  # название объекта. в нём будет
    form_class = PostForm
    permission_required = ('news.edit_post',)

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name = 'author').exists()
        return context

class PostDelete(LoginRequiredMixin, DeleteView):

    template_name = 'news/delete.html'  # название шаблона будет product.html
    queryset = Post.objects.all()
    success_url = 'news/'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name = 'author').exists()
        return context

class CategoryList(ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'news/categories.html'
    queryset=Category.objects.all()

class CategoryView(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'news/category.html'  # указываем имя шаблона, в котором будет лежать HTML, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    paginate_by = 5

    def get_context_data(self, **kwargs):  # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса (привет, полиморфизм, мы скучали!!!)
        context = super().get_context_data(**kwargs)
        id = self.kwargs.get('pk')
        print(f"This is cat id: {id}")
        context['categoryview'] = Post.objects.filter(category=id).order_by('-date')  # вписываем наш фильтр в контекст
        return context



def send_email(request):
    print(f"Это контекст: {request}")
    cat = request.META.get('HTTP_REFERER')[-1]
    print("Cat: ", cat)
    user = request.user.id

    if not Subscriber.objects.get(user_id = user):
        Subscriber.objects.create(user_id = user)
    Subscriber.objects.get(user_id = user).category.add(Category.objects.get(id=cat))
    print(user)
    # отправляем письмо
    msg = EmailMultiAlternatives(
        subject=f'Вы подписались на категроию {Category.objects.get(id=cat)}',
        # имя клиента и дата записи будут в теме для удобства
        body='Спасибо за подписку на нашем сайте',  # сообщение с кратким описанием проблемы
        from_email='sergey@batalov.email',  # здесь указываете почту, с которой будете отправлять (об этом попозже)
        to=['sergey@batalov.email'], # здесь список получателей. Например, секретарь, сам врач и т. д.
    )
    msg.send()
    return redirect('/')