from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        # Includes all fields
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        # for loop to add frendly names and id to a tuple
        friendly_names = []
        for c in categories:
            a = (c.id, c.friendly_name)
            friendly_names.append(a)
        # friendly_names = [(c.id, c.friendly_name) for c in categories]

        # Update field names too friendly names since this category has choices/Make dropdown menu
        # Will use the 2nd choice in the tuple
        self.fields['category'].choices = friendly_names
        # Add classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'