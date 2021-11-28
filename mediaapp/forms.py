from django import forms
from .models import Category
from .custom_validators import file_size, file_type


class CreateGallery(forms.ModelForm):
    # Extra fields automatically included
    is_customer = forms.BooleanField(required=False, label='Extra cheeze', initial=False)
    STATUS = [
        ('selected', 'Select from old category'),
    ]
    check = forms.MultipleChoiceField(label="", required=False, choices=STATUS,
                                      widget=forms.CheckboxSelectMultiple)

    # the crispy form does not allow to change class but in settings.py CRISPY_TEMPLATE_PACK = 'bootstrap3' does
    name = forms.CharField(required=False, label='Category name', widget=forms.TextInput(attrs={
        "class": "form-control"
    }))
    image = forms.ImageField(required=True, label='Image', validators=[file_size, file_type] ,widget=forms.ClearableFileInput(attrs={
        "multiple": True
    }))
    selected_category = forms.ModelChoiceField(required=False, label='Select category', queryset=Category.objects.all(),
                                               widget=forms.Select)

    # https://stackoverflow.com/questions/64588109/django-modelforms-how-to-show-a-select-for-a-charfield

    class Meta:
        model = Category
        fields = ['description']

        # widgets = {
        #     "check": forms.CheckboxSelectMultiple(attrs={"class": "custom-control-input"})
        # }

    # def __init__(self, *args, **kwargs):
    #     print("kwargs")
    #     print(kwargs)
    #     super(CreateGallery, self).__init__(*args, **kwargs)
    #     print("assign False Don't create as ")
    #     # for creating self.fields['name'].widget.attrs['required'] = False
    #     # self.fields["check"].required = False
    #     # print(self.fields['check'].widget.attrs['class'])

    # def clean_image(self):
    #     image = self.files.getlist("image")  # Don't use .clean_data['image']
    #     if image:
    #         for im in image:
    #             if im.size > 1 * 1024 * 1024:
    #                 raise forms.ValidationError(f"{im} file is larger than 1mb.")
    #         return image

    def clean_image(self):
        image = self.files.getlist("image")  # Don't use .clean_data['image']
        if len(image) > 3:
            raise forms.ValidationError("You can select maximum 3 files at a time.")
        return image

    # form.files.getlist("image") in views.py

    # def clean_image(self):
    #     image = self.files.get("image")  # Don't use .clean_data['image']
    #     print(image)
    #     if image.size > 1 * 1024 * 1024:
    #         raise forms.ValidationError(f"{image} file is larger than 1mb.")
    #     return image
    # # form.files.get("image") in views.py
    '''
    def clean_images(self):
    files = self.files.getlist('images')
    for file in files:
        if file:
            if file._size > 15*1024*1024:
                raise forms.ValidationError("Image file is too large ( > 15mb ).")
        else:
            raise forms.ValidationError("Could not read the uploaded file.")
    return files
    '''

    def clean_name(self):
        if self.cleaned_data['name']:
            name = self.cleaned_data['name']
            if Category.objects.filter(name=name).exists():
                # raise self.add_error("name", "Category already exists. Choose a different name")
                # self.add_error Does not work
                raise forms.ValidationError("Category already exists. Choose a different name")
            return name
        else:
            return None

    def clean_selected_category(self):
        # print(self.cleaned_data['selected_category'])
        if self.cleaned_data['selected_category']:
            return self.cleaned_data['selected_category']
        else:
            return None

    def clean_description(self):
        # print(self.cleaned_data['selected_category'])
        if self.cleaned_data['description']:
            return self.cleaned_data['description']
        else:
            return None

    def clean(self):
        cleaned_data = super().clean()
        # print('Checking name and selected value')
        check = cleaned_data.get("check")
        selected_category = cleaned_data.get("selected_category")
        description = cleaned_data.get('description')
        name = cleaned_data.get('name')
        # print(not cleaned_data.get("check"))
        if "selected" in check and selected_category is None:
            print("display error")
            self.add_error("selected_category", "This filed is not required")
        if not check and name is None:
            if description is None:
                self.add_error("description", "This filed is required")
            self.add_error("name", "This filed is required")

        if "selected" in check:  # assign name = None
            cleaned_data['name'] = None
        else:
            cleaned_data['selected_category'] = None
        return cleaned_data


'''
    () does not matter
    
    
    javascript undefined == []
    
    
    # DateField
    birth_year = forms.DateField(widget=forms.SelectDateWidget(years=["1996", "2000", "2005"], months={
        1: "Jan", 2: "Feb",
    }))
    datetime.date.today().year-5)
    
    STATUS = [(category.id,category.name) for category in Category.objects.all() ]
    or
    STATUS = [
        ('Street name 1', 'Street name 1'),
        ('Street name 2', 'Street name 2')
    ]
    

    
    # Checkbox
        check = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        required=False, choices=STATUS
    )
    # Must be MultipleChoiceField(choices=)/ModelMultipleChoiceField(queryset=) as it will return a list of values
    # But you cannot change class name, id etc, crispy form by default names it
    # queryset=Categories.objects.none() can be put here MultipleChoiceField
    # {{ form.check }} gives <input> inside <label> which is inside <ul> ;(
    # ModelMultipleChoiceField(queryset=)  if selected in browser gives back a model



    # Radio button
        radio = forms.________ChoiceField(
        widget=forms.RadioSelect,choices=STATUS
    )
    # ModelChoiceField(queryset=)/ChoiceField(choices=) with RadioSelect widget and it works there
    # But you cannot change class name, id etc, crispy form by default names it
    # ChoiceField/ModelChoiceField returns a single value
    # {{ form.radio }} gives <input> inside <label> which is inside <ul> ;(
    # ModelChoiceField(queryset=)  if selected in browser gives back a model
    
    # Files or images
    image = forms.ImageField(required=True, label='Image', widget=forms.ClearableFileInput(attrs={
        "multiple": True
    }))
    

    is_customer = forms.BooleanField(required=False, label='Extra cheeze', initial=False)
    # a check box appears 
'''


# https://stackoverflow.com/questions/64588109/django-modelforms-how-to-show-a-select-for-a-charfield

# def clean_name(self):
#     name = self.cleaned_data['name']
#     if Category.objects.filter(name=name).exists():
#         # raise self.add_error("name", "Category already exists. Choose a different name")
#         # self.add_error Does not work
#         raise forms.ValidationError("Category already exists. Choose a different name")
#     return name


class UpdateCategory(forms.Form):
    # Extra fields automatically included
    name = forms.CharField(required=False, label='Category name', widget=forms.TextInput(attrs={
        "class": "form-control"
    }))

    description = forms.CharField(required=False, label='Description', widget=forms.Textarea(attrs={
        "class": "form-control",
        "rows": "4"
    }))

    def __init__(self, *args, **kwargs):
        print(kwargs)
        self.request = kwargs.pop("request")
        super(UpdateCategory, self).__init__(*args, **kwargs)
        print("assign False Don't create as ")
        # for creating self.fields['name'].widget.attrs['required'] = False
        # self.fields["check"].required = False
        # print(self.fields['check'].widget.attrs['class'])

    def clean_name(self):
        if self.cleaned_data['name']:
            name = self.cleaned_data['name']
            return name
        raise forms.ValidationError("name is required")


class UpdatePicture(forms.Form):
    # Extra fields automatically included
    image_name = forms.CharField(required=False, label='Image name', widget=forms.TextInput(attrs={
        "class": "form-control"
    }))

    description = forms.CharField(required=False, label='Description', widget=forms.Textarea(attrs={
        "class": "form-control",
        "rows": "4"
    }))
