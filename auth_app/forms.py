from django.contrib.auth.forms import UserCreationForm
from auth_app.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.contrib.auth import get_user_model

User = get_user_model()

class PersonRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'contact_number','password1']
        
    def __init__(self, *args, **kwargs):
        super(PersonRegistrationForm, self).__init__(*args, **kwargs)
        attrs = {'required': True}
        for field in self.fields.values():
            field.widget.attrs = attrs
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        if password1:
            try:
                validate_password(password1, self.instance)
            except forms.ValidationError as error:
                self.add_error("password1", error)
        # Remove the validation error for 'password2'
        self._errors.pop('password2', None)

        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email

class PersonLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            status = User.objects.filter(email=email).exists()
            if not status:
                self.add_error('email', 'Invalid credentials')
            else:
                user = authenticate(username=email, password=password)
                if user is None:
                    self.add_error('password', 'Invalid credentials.')

        return cleaned_data
