from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Record, Note, Task
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    first_name = forms.CharField(label="", max_length="50", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length="50", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or ' \
                                            'fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too ' \
                                             'similar to your other personal information.</li><li>Your password must ' \
                                             'contain at least 8 characters.</li><li>Your password can\'t be a ' \
                                             'commonly used password.</li><li>Your password can\'t be entirely ' \
                                             'numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as ' \
                                             'before, for verification.</small></span>'


class AddRecordForm(forms.ModelForm):
    first_name = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'First Name', 'class': 'form-control'}), label='')
    last_name = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'Last Name', 'class': 'form-control'}), label='')
    email = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'Email', 'class': 'form-control'}), label='')
    phone = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'phone', 'class': 'form-control'}), label='')
    address = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'address', 'class': 'form-control'}), label='')
    city = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'city', 'class': 'form-control'}), label='')
    state = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'State', 'class': 'form-control'}), label='')
    zipcode = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'Zipcode', 'class': 'form-control'}), label='')
    category = forms.ChoiceField(choices=[
        ('lead', 'Lead'),
        ('client', 'Client'),
        ('vendor', 'Vendor'),
        ('partner', 'Partner'),
        ('other', 'Other'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}), required=True, label=''
    )

    class Meta:
        model = Record
        exclude = ('user', 'created_by')


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add a note..'}),
        }


class TaskForm(forms.ModelForm):

    due_date = forms.DateTimeField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Select due date & time',
        'id': 'id_due_date',  # This is important for JS selector
    }))

    class Meta:
        model = Task
        fields = ['title', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'eg: Call John Doe'}),
        }
