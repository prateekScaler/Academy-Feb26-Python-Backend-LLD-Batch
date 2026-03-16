from django.contrib import admin



from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from .models import Category, MenuItem


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')
        import_id_fields = ('name',)


class MenuItemResource(resources.ModelResource):
    # Use category NAME instead of ID (much easier!)
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, field='name')
    )

    class Meta:
        model = MenuItem
        fields = ('id', 'name', 'description', 'price', 'is_available', 'category')
        import_id_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(MenuItem)
class MenuItemAdmin(ImportExportModelAdmin):
    resource_class = MenuItemResource
    list_display = ['name', 'price', 'category', 'is_available']
    list_filter = ['category', 'is_available']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_available']
