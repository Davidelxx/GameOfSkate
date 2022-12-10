from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from cuenta.models import Cuenta


class RegistrationForm(UserCreationForm):
	email = forms.EmailField(max_length=254, help_text='Escribe una dirección de email válida.')

	class Meta:
		model = Cuenta
		fields = ('email', 'username', 'password1', 'password2', )

	def clean_email(self):
		email = self.cleaned_data['email'].lower()
		try:
			cuenta = Cuenta.objects.exclude(pk=self.instance.pk).get(email=email)
		except Cuenta.DoesNotExist:
			return email
		raise forms.ValidationError('El email "%s" ya está en uso.' % cuenta)

	def clean_username(self):
		username = self.cleaned_data['username']
		try:
			cuenta = Cuenta.objects.exclude(pk=self.instance.pk).get(username=username)
		except Cuenta.DoesNotExist:
			return username
		raise forms.ValidationError('El nombre de usuario "%s" ya está en uso.' % username)


class CuentaAuthenticationForm(forms.ModelForm):

	password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

	class Meta:
		model = Cuenta
		fields = ('email', 'password')

	def clean(self):
		if self.is_valid():
			email = self.cleaned_data['email']
			password = self.cleaned_data['password']
			if not authenticate(email=email, password=password):
				raise forms.ValidationError("Login no válido")


class ActualizarCuentaForm(forms.ModelForm):

    class Meta:
        model = Cuenta
        fields = ('username', 'email', 'profile_image', 'hide_email' )

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            cuenta = Cuenta.objects.exclude(pk=self.instance.pk).get(email=email)
        except Cuenta.DoesNotExist:
            return email
        raise forms.ValidationError('El email "%s" ya está en uso.' % cuenta)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            cuenta = Cuenta.objects.exclude(pk=self.instance.pk).get(username=username)
        except Cuenta.DoesNotExist:
            return username
        raise forms.ValidationError('El nombre de usuario "%s" ya está en uso.' % username)


    def save(self, commit=True):
        cuenta = super(ActualizarCuentaForm, self).save(commit=False)
        cuenta.username = self.cleaned_data['username']
        cuenta.email = self.cleaned_data['email'].lower()
        cuenta.profile_image = self.cleaned_data['profile_image']
        cuenta.hide_email = self.cleaned_data['hide_email']
        if commit:
            cuenta.save()
        return cuenta











