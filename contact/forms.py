# -*- coding: utf-8 -*-
"""
Forms for the `contact` application.
"""
from django import forms, urls
from django.utils.html import escape, conditional_escape
from django.utils.translation import gettext_lazy as _

from contact.models import Contact


class ContactForm(forms.ModelForm):
    """
    Form to submit a contact message.
    """

    # ==================================================================================================================
    # Main fields
    # ==================================================================================================================

    name = forms.CharField(
        label=_("Name"),
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("How you want to be referred as")
        })
    )

    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _("Your email address")
        })
    )

    subject = forms.CharField(
        label=_("Subject"),
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("Subject of your message")
            })
    )

    message = forms.CharField(
        label=_("Message"),
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control-plaintext',
            'style': 'resize: vertical;',
        })
    )

    # ==================================================================================================================
    # Agreement
    # ==================================================================================================================

    agreement = forms.BooleanField(
        label=_("Agreement"),
        help_text=None, # The help text is edited in the __init__ method.
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    # ==================================================================================================================
    # Meta & init
    # ==================================================================================================================

    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
    # End class Meta

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['agreement'].error_messages = {
            'required': _("You must agree to the terms and conditions to submit the form.")
        }
        self.fields['agreement'].help_text = _(
            f"I agree to the terms and conditions specified in the "
            f"<a href=\"{urls.reverse('donnees-personnelles')}\">privacy policy</a>."
        )
    # End def __init__

    # ==================================================================================================================
    # Clean
    # ==================================================================================================================

    def clean_name(self):
        """
        Clean the name field.
        """
        name = self.cleaned_data['name']
        # Escape the name, to avoid any XSS attacks.
        name = conditional_escape(name)
        return name.strip()
    # End def clean_name

    def clean_email(self):
        """
        Clean the email field.
        """
        email = self.cleaned_data['email']
        return email.strip()
    # End def clean_email

    def clean_subject(self):
        """
        Clean the subject field.
        """
        subject = self.cleaned_data['subject']
        # Escape the subject, to avoid any XSS attacks.
        subject = conditional_escape(subject)
        return subject.strip()
    # End def clean_subject

    def clean_message(self):
        """
        Clean the message field.
        """
        message = self.cleaned_data['message']
        # Escape the message, to avoid any XSS attacks.
        message = escape(message)
        return message.strip()
    # End def clean_message
# End class ContactForm