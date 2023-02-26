from django.contrib import admin
from .models import StaticInformation, TranlsationGroups, Articles, Languages, Translations,  ArticleCategories, MetaTags, FAQ
from django.contrib.auth.models import Permission
# Register your models here.



admin.site.register(StaticInformation)
admin.site.register(Translations)
admin.site.register(TranlsationGroups)
admin.site.register(Languages)
admin.site.register(Articles)
admin.site.register(ArticleCategories)
admin.site.register(MetaTags)
admin.site.register(Permission)
admin.site.register(FAQ)