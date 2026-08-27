from django.views.generic import DetailView, ListView

from news.models.posts import Category, Post

class PostListView(ListView):
    model = Post
    template_name = 'news/post_list.html'
    context_object_name = 'posts'
    paginate_by = 6
    paginate_orphans = 1

    def get_queryset(self):
        queryset = super().get_queryset()

        category_id = self.request.GET.get('category_id')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'news/post_detail.html'
    context_object_name = 'post'