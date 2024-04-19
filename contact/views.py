# -*- coding: utf-8 -*-
"""
Views for the `contact` application.
"""
from django import urls
from django.shortcuts import render
from django.views.generic import FormView

from contact.forms import ContactForm
from contact.models import Contact


class ContactView(FormView):
    """
    Display the contact form.
    """
    form_class = ContactForm
    template_name = 'contact/form.html'

    def get_success_url(self):
        return urls.reverse('contact:success')
    # End def get_success_url

    def form_invalid(self, form : ContactForm):
        response = super(ContactView, self).form_invalid(form)
        response.status_code = 400
        return response
    # End def form_invalid
    def form_valid(self, form : ContactForm):
        email = form.cleaned_data['email']
        name = form.cleaned_data['name']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']

        # Add the contact message to the database.
        Contact.objects.create(
            email=email,
            name=name,
            subject=subject,
            message=message
        ).save()

        # TODO: Send the email.

        # Redirect to the success page.
        return super(ContactView, self).form_valid(form)

    class ErrorList:
        error_class = 'content-form__errors'

# End class ContactView




def contact_success_view(request):
    """
    Display the contact success page.
    """
    return render(request, 'contact/success.html')
# End def contact_success_view