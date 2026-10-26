from django.views.generic import DetailView, ListView
from django.utils.dateparse import parse_date
from news.models.posts import Category, Post

NEWS_CATEGORY_VISIBLE = 5
NEWS_CATEGORY_MORE_THRESHOLD = 7


def get_split_categories(categories_list, active_category_id=None):
    if not categories_list:
        return [], []
    if len(categories_list) <= NEWS_CATEGORY_MORE_THRESHOLD:
        return list(categories_list), []
    try:
        active_id = int(active_category_id)
    except (TypeError, ValueError):
        active_id = None

    visible = list(categories_list[:NEWS_CATEGORY_VISIBLE])
    more = list(categories_list[NEWS_CATEGORY_VISIBLE:])

    if active_id is not None:
        idx = next((i for i, c in enumerate(more) if c.id == active_id), None)
        if idx is not None:
            active_item = more.pop(idx)
            replaced_item = visible.pop()
            visible.append(active_item)
            more.insert(0, replaced_item)
    return visible, more

def parse_category_id(value):
    if value and value.isascii() and value.isdigit():
        return int(value)
    return None


def parse_filter_date(value):
    if not value:
        return None
    try:
        return parse_date(value)
    except ValueError:
        return None

class PostListView(ListView):
    model = Post
    template_name = "news/post_list.html"
    context_object_name = "posts"
    paginate_by = 6
    paginate_orphans = 1

    def get_filters(self):
        params = self.request.GET
        return {
            "category_id": parse_category_id(params.get("category_id")),
            "date_from": parse_filter_date(params.get("date_from")),
            "date_to": parse_filter_date(params.get("date_to")),
        }

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = self.get_filters()

        if filters["category_id"] is not None:
            queryset = queryset.filter(category_id=filters["category_id"])

        if filters["date_from"] is not None:
            queryset = queryset.filter(created_at__date__gte=filters["date_from"])

        if filters["date_to"] is not None:
            queryset = queryset.filter(created_at__date__lte=filters["date_to"])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filters = self.get_filters()
        categories_queryset = Category.objects.all()
        context["categories"] = categories_queryset
        category_id = filters["category_id"]
        active_category = None
        if category_id is not None:
            active_category = next(
                (c for c in categories_queryset if c.id == category_id), None
            )
        visible_cats, more_cats = get_split_categories(
            categories_queryset, category_id
        )
        context.update({
            "active_category": active_category,
            "visible_categories": visible_cats,
            "more_categories": more_cats,
            "date_from": (
                filters["date_from"].isoformat() if filters["date_from"] else ""
            ),
            "date_to": (
                filters["date_to"].isoformat() if filters["date_to"] else ""
            ),
        })
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "news/post_detail.html"
    context_object_name = "post"
