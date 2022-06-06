from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Review, Category, Tag


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('name', )}


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}


admin.site.register(User, UserAdmin)
UserAdmin.fieldsets += (("Custom fields", {"fields":("nickname","profile_pic","intro")}),)
admin.site.register(Review)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)