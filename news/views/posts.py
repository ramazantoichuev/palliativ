from django.views.generic import DetailView, ListView

from news.models.posts import Category, Post


NEWS_CATEGORY_VISIBLE = 5
NEWS_CATEGORY_MORE_THRESHOLD = 7

def get_split_categories(categories_list, active_category_id=None):
    if not categories_list:
        return [], []
    total_count = len(categories_list)
    if total_count <= NEWS_CATEGORY_MORE_THRESHOLD:
        return list(categories_list), []
    visible = list(categories_list[:NEWS_CATEGORY_VISIBLE])
    more = list(categories_list[NEWS_CATEGORY_VISIBLE:])

    if active_category_id:
        active_category_id = int(active_category_id)
        in_more_idx = next((i for i, c in enumerate(more) if c.id == active_category_id), None)
        if in_more_idx is not None:
            active_item = more.pop(in_more_idx)
            replaced_item = visible.pop(-1)
            visible.append(active_item)
            more.insert(0, replaced_item)
    return visible, more

class PostListView(ListView):
    model = Post
    template_name = "news/post_list.html"
    context_object_name = "posts"
    paginate_by = 6
    paginate_orphans = 1

    def get_queryset(self):
        queryset = super().get_queryset()

        category_id = self.request.GET.get("category_id")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories_queryset = Category.objects.all()
        context["categories"] = categories_queryset
        category_id = self.request.GET.get("category_id")
        active_category = None
        if category_id and category_id.isdigit():
            active_category = next((c for c in categories_queryset if c.id == int(category_id)), None)
        visible_cats, more_cats = get_split_categories(categories_queryset, category_id)
        context.update({
            "active_category": active_category,
            "visible_categories": visible_cats,
            "more_categories": more_cats,
        })
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "news/post_detail.html"
    context_object_name = "post"
