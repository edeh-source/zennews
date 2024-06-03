from django.shortcuts import render, redirect
from .forms import SubscriberForm
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.template.loader import render_to_string


def subscribe_email(request):
    forms = SubscriberForm()        
    return {'forms': forms }    


@require_POST
def index(request):
    
    context = None
    
    form = SubscriberForm(request.POST)
    if form.is_valid():
        subscriber = form.save()
        context = {'email': subscriber.email, 'form': form }
        email_content = render_to_string('news/subscribe_thank_you.html', context)
            
        email_subject = 'Thank You For Subscribing'
        recipient_list = [subscriber.email]
        from_email = settings.EMAIL_HOST_USER

        send_mail(
            email_subject,
            '',
            from_email,
            recipient_list,
            html_message = email_content,
            fail_silently=False
        )
        messages.success(request, 'EMAIL SUBSCRIBED SUCCESFULLY')


        return render(request, 'news/thank_you.html', context)
    else:
        messages.error(request, 'EMAIL ALREADY EXIST') 
    return redirect('home')
