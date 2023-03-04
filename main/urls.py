from django.urls import path, include
from . import views


urlpatterns = [
    path('articles', views.ArticlesList.as_view()),
    path("articles/<slug:slug>", views.ArticlesDetail.as_view()),
    path("static_infos", views.StaticInfView.as_view()),
    path("translations", views.TranslationsView.as_view()),
    path('languages', views.LangsList.as_view()),
    path('categories', views.CategoryList.as_view()),
    path("categories/<int:pk>", views.CategoryDetailView.as_view()),
    path('products', views.ProductsList.as_view()),
    path("top_products", views.TopProducts.as_view()),
    path("cart_view", views.CartView.as_view()),
    path("faq", views.FAQview.as_view()),
    path("search", views.Search.as_view()),
    path("baners", views.BanersView.as_view()),
    path("subscribe", views.AddNewslatter.as_view())
]
