from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Receipe


def login_view(request):
    
    if request.user.is_authenticated:
        return redirect('reciepe')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('reciepe')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('reciepe')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
    return render(request, "register.html")


@login_required
def receipes(request):
    message = None

    if request.method == "POST":
        if not request.user.is_staff and not request.user.is_superuser:
            messages.error(request, "Only admin can add recipes.")
            return redirect('reciepe')
        
        data = request.POST
        recipe_image = request.FILES.get('recipe_image')
        recipe_name = data.get('recipe_name')
        recipe_description = data.get('recipe_description')
        if recipe_name and recipe_description:
            Receipe.objects.create(
                receipe_image=recipe_image,
                receipe_name=recipe_name,
                receipe_description=recipe_description
            )
            message = "Recipe added successfully!"
        else:
            message = "All fields are required."

    recipes = Receipe.objects.all().order_by('-id')
    is_admin = request.user.is_staff or request.user.is_superuser
    return render(request, "receipe.html", {"recipes": recipes, "message": message, "is_admin": is_admin})


from django.shortcuts import get_object_or_404, redirect

def admin_required(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
@user_passes_test(admin_required, login_url='reciepe')
def update_recipe(request, id):
    recipe = get_object_or_404(Receipe, id=id)
    message = None
    if request.method == "POST":
        data = request.POST
        recipe_name = data.get('recipe_name')
        recipe_description = data.get('recipe_description')
        recipe_image = request.FILES.get('recipe_image')
        if recipe_name and recipe_description:
            recipe.receipe_name = recipe_name
            recipe.receipe_description = recipe_description
            if recipe_image:
                recipe.receipe_image = recipe_image
            recipe.save()
            message = "Recipe updated successfully!"
            return redirect('reciepe')
        else:
            message = "All fields are required."
    return render(request, "update_recipe.html", {"recipe": recipe, "message": message})

@login_required
@user_passes_test(admin_required, login_url='reciepe')
def delete_recipe(request, id):
    recipe = get_object_or_404(Receipe, id=id)
    if request.method == "POST":
        recipe.delete()
        return redirect('reciepe')
    return render(request, "delete_recipe.html", {"recipe": recipe})
