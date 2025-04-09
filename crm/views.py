from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserRegisterForm, ContactForm, OrganizationForm, DealForm
from .models import Contact, Organization, Deal


def landing_page(request):
    """View for the landing page before login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'crm/landing_page.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Konto zostało utworzone!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'crm/register.html', {'form': form})


@login_required
def dashboard(request):
    contacts_count = Contact.objects.filter(created_by=request.user).count()
    organizations_count = Organization.objects.filter(created_by=request.user).count()
    deals_count = Deal.objects.filter(created_by=request.user).count()
    
    recent_contacts = Contact.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    recent_deals = Deal.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    
    context = {
        'contacts_count': contacts_count,
        'organizations_count': organizations_count,
        'deals_count': deals_count,
        'recent_contacts': recent_contacts,
        'recent_deals': recent_deals,
    }
    return render(request, 'crm/dashboard.html', context)


# Contact views
@login_required
def contact_list(request):
    contacts = Contact.objects.filter(created_by=request.user)
    return render(request, 'crm/contacts/contact_list.html', {'contacts': contacts})


@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk, created_by=request.user)
    return render(request, 'crm/contacts/contact_detail.html', {'contact': contact})


@login_required
def contact_create(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.created_by = request.user
            contact.save()
            messages.success(request, 'Kontakt został utworzony!')
            return redirect('contact_list')
    else:
        form = ContactForm()
    
    return render(request, 'crm/contacts/contact_form.html', {'form': form})


@login_required
def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kontakt został zaktualizowany!')
            return redirect('contact_detail', pk=contact.pk)
    else:
        form = ContactForm(instance=contact)
    
    return render(request, 'crm/contacts/contact_form.html', {'form': form, 'contact': contact})


@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Kontakt został usunięty!')
        return redirect('contact_list')
    
    return render(request, 'crm/contacts/contact_confirm_delete.html', {'contact': contact})
