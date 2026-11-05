
# Create your views here.
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .models import *
from django.db import IntegrityError, transaction
from .models import owner, size, colour, category, Product
from decimal import Decimal, InvalidOperation
import os
import uuid
from user.models import Order

from django.conf import settings

def owner_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('owner_register')

        # Check username exists
        if owner.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('owner_register')

        # Check email exists
        if owner.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('owner_register')

        # Save owner
        owner.objects.create(
            name=name,
            username=username,
            email=email,
            phone=phone,
            password=password
        )

        messages.success(request, "Registration successful!")
        return redirect('owner_login')

    return render(request, 'registration.html')



# Owner Login
def owner_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = owner.objects.get(
                username=username,
                password=password
            )

            request.session["owner_id"] = user.id
            request.session["owner_name"] = user.name

            return redirect("owner_dashboard")

        except owner.DoesNotExist:
            return render(request, "owner_login.html", {
                "error": "Invalid Username or Password"
            })

    return render(request, "owner_login.html")


# Owner Dashboard
def owner_dashboard(request):

    # Check owner login
    owner_id = request.session.get('owner_id')

    if not owner_id:
        return redirect('owner_login')

    # Existing dashboard data
    sizes = size.objects.all()
    colours = colour.objects.all()
    categories = category.objects.all()
    products = Product.objects.all()

    # Get all orders with customer details and order items
    orders = (
        Order.objects
        .select_related('user')
        .prefetch_related('items')
        .order_by('-created_at')
    )

    context = {
        'sizes': sizes,
        'colours': colours,
        'categories': categories,
        'products': products,
        'orders': orders,
    }

    return render(request, 'owner_dashboard.html', context)


# Add Size
def add_size(request):
    if "owner_id" not in request.session:
        return redirect("owner_login")

    if request.method == "POST":
        size_name = request.POST.get("size_name", "").strip()

        if not size_name:
            messages.error(request, "Please enter a size name.")
            return redirect("add_size")

        if size.objects.filter(size_name__iexact=size_name).exists():
            messages.error(request, "This size already exists.")
            return redirect("add_size")

        size.objects.create(size_name=size_name)
        messages.success(request, "Size added successfully!")
        return redirect("owner_dashboard")

    return render(request, "size_form.html", {
        "page_title": "Add Size",
        "button_text": "Add Size"
    })


# Edit Size
def edit_size(request, id):
    if "owner_id" not in request.session:
        return redirect("owner_login")

    size_item = get_object_or_404(size, id=id)

    if request.method == "POST":
        size_name = request.POST.get("size_name", "").strip()

        if not size_name:
            messages.error(request, "Please enter a size name.")
            return render(request, "size_form.html", {
                "page_title": "Edit Size",
                "button_text": "Update Size",
                "size_item": size_item
            })

        if size.objects.filter(
            size_name__iexact=size_name
        ).exclude(id=id).exists():
            messages.error(request, "This size already exists.")
            return render(request, "size_form.html", {
                "page_title": "Edit Size",
                "button_text": "Update Size",
                "size_item": size_item
            })

        size_item.size_name = size_name
        size_item.save()

        messages.success(request, "Size updated successfully!")
        return redirect("owner_dashboard")

    return render(request, "size_form.html", {
        "page_title": "Edit Size",
        "button_text": "Update Size",
        "size_item": size_item
    })


# Delete Size
def delete_size(request, id):
    if "owner_id" not in request.session:
        return redirect("owner_login")

    size_item = get_object_or_404(size, id=id)

    if request.method == "POST":
        size_item.delete()
        messages.success(request, "Size deleted successfully!")

    return redirect("owner_dashboard")


def owner_logout(request):
    request.session.flush()
    return redirect("owner_login")

    

# Add Colour
def add_colour(request):
    if "owner_id" not in request.session:
        return redirect("owner_login")

    if request.method == "POST":
        colour_name = request.POST.get("colour_name", "").strip()

        if not colour_name:
            messages.error(request, "Colour name cannot be empty.")
            return redirect("add_colour")

        if colour.objects.filter(
            colour_name__iexact=colour_name
        ).exists():
            messages.error(request, "This colour already exists.")
            return redirect("add_colour")

        colour.objects.create(colour_name=colour_name)
        messages.success(request, "Colour added successfully!")
        return redirect("owner_dashboard")

    return render(request, "colour_form.html", {
        "page_title": "Add Colour",
        "button_text": "Add Colour",
    })


# Edit Colour
def edit_colour(request, id):
    if "owner_id" not in request.session:
        return redirect("owner_login")

    colour_item = get_object_or_404(colour, id=id)

    if request.method == "POST":
        colour_name = request.POST.get("colour_name", "").strip()

        if not colour_name:
            messages.error(request, "Colour name cannot be empty.")
        elif colour.objects.filter(
            colour_name__iexact=colour_name
        ).exclude(id=id).exists():
            messages.error(request, "This colour already exists.")
        else:
            colour_item.colour_name = colour_name
            colour_item.save()

            messages.success(request, "Colour updated successfully!")
            return redirect("owner_dashboard")

    return render(request, "colour_form.html", {
        "page_title": "Edit Colour",
        "button_text": "Update Colour",
        "colour_item": colour_item,
    })


# Delete Colour
def delete_colour(request, id):
    if "owner_id" not in request.session:
        return redirect("owner_login")

    colour_item = get_object_or_404(colour, id=id)

    if request.method == "POST":
        colour_item.delete()
        messages.success(request, "Colour deleted successfully!")

    return redirect("owner_dashboard")

def add_category(request):

    if "owner_id" not in request.session:
        return redirect("owner_login")

    if request.method == "POST":

        category_name = request.POST.get(
            "category_name", ""
        ).strip()

        if not category_name:
            messages.error(
                request, "Please enter a category name."
            )

        elif category.objects.filter(
            category_name__iexact=category_name
        ).exists():
            messages.error(
                request, "This category already exists."
            )

        else:
            try:
                with transaction.atomic():
                    category.objects.create(
                        category_name=category_name
                    )

                messages.success(
                    request, "Category added successfully!"
                )

                return redirect("owner_dashboard")

            except IntegrityError:
                messages.error(
                    request, "This category already exists."
                )

    return render(request, "category_form.html", {
        "page_title": "Add Category",
        "button_text": "Add Category",
        "category_name": request.POST.get(
            "category_name", ""
        ) if request.method == "POST" else "",
    })


#Edit Category
def edit_category(request, id):

    # Check owner login

    # if "owner_id" not in request.session:
    

    # Get selected category
    item = get_object_or_404(category, id=id)

    if request.method == "POST":

        category_name = request.POST.get(
            "category_name", ""
        ).strip()

        if not category_name:
            messages.error(
                request, "Please enter a category name."
            )

        elif category.objects.filter(
            category_name__iexact=category_name
        ).exclude(id=item.id).exists():

            messages.error(
                request, "This category already exists."
            )

        else:
            item.category_name = category_name
            item.save()

            messages.success(
                request, "Category updated successfully!"
            )

            return redirect("owner_dashboard")

    return render(request, "edit_category.html", {
        "item": item,
    })



#Delete category

def delete_category(request, id):

    # Check owner login
    if "owner_id" not in request.session:
        return redirect("owner_login")

    # Get selected category
    item = get_object_or_404(category, id=id)

    # Delete category
    item.delete()

    messages.success(
        request, "Category deleted successfully!"
    )

    return redirect("owner_dashboard")



def add_product(request):

    if "owner_id" not in request.session:
        return redirect("owner_login")

    categories = category.objects.all()
    sizes = size.objects.all()
    colours = colour.objects.all()

    if request.method == "POST":

        product_name = request.POST.get("product_name", "").strip()
        category_id = request.POST.get("category")
        size_id = request.POST.get("size")
        colour_id = request.POST.get("colour")
        quantity = request.POST.get("quantity")
        mrp = request.POST.get("mrp")
        discount_rate = request.POST.get("discount_rate")

        try:
            if not product_name:
                raise ValueError("Please enter a product name.")

            selected_category = category.objects.get(id=category_id)
            selected_size = size.objects.get(id=size_id)
            selected_colour = colour.objects.get(id=colour_id)

            quantity_value = int(quantity)
            mrp_value = Decimal(mrp)
            discount_value = Decimal(discount_rate)

            if quantity_value < 0:
                raise ValueError("Quantity cannot be negative.")

            if mrp_value <= 0:
                raise ValueError("MRP must be greater than zero.")

            if discount_value < 0 or discount_value > 100:
                raise ValueError("Discount rate must be between 0 and 100.")

            # Image upload handling
            image_paths = {}

            for image_field in ["front_image", "back_image", "side_image"]:

                image = request.FILES.get(image_field)

                if image:
                    extension = os.path.splitext(image.name)[1].lower()
                    filename = f"{uuid.uuid4().hex}{extension}"

                    folder = os.path.join(settings.MEDIA_ROOT, "product_images")
                    os.makedirs(folder, exist_ok=True)

                    file_path = os.path.join(folder, filename)

                    with open(file_path, "wb+") as destination:
                        for chunk in image.chunks():
                            destination.write(chunk)

                    image_paths[image_field] = f"product_images/{filename}"

                else:
                    image_paths[image_field] = ""

            Product.objects.create(
                product_name=product_name,
                category=selected_category,
                size=selected_size,
                colour=selected_colour,
                quantity=quantity_value,
                mrp=mrp_value,
                discount_rate=discount_value,
                front_image=image_paths["front_image"],
                back_image=image_paths["back_image"],
                side_image=image_paths["side_image"]
            )

            messages.success(request, "Product added successfully!")
            return redirect("owner_dashboard")

        except (ValueError, InvalidOperation, TypeError):
            messages.error(request, "Please enter valid product details.")

        except (
            category.DoesNotExist,
            size.DoesNotExist,
            colour.DoesNotExist
        ):
            messages.error(request, "Please select valid category, size and colour.")

    return render(request, "product_form.html", {
        "categories": categories,
        "sizes": sizes,
        "colours": colours,
        "page_title": "Add Product",
        "button_text": "Add Product",
        "item": None,
    })

def edit_product(request, id):

    if "owner_id" not in request.session:
        return redirect("owner_login")

    item = get_object_or_404(Product, id=id)

    categories = category.objects.all()
    sizes = size.objects.all()
    colours = colour.objects.all()

    if request.method == "POST":

        product_name = request.POST.get("product_name", "").strip()
        category_id = request.POST.get("category")
        size_id = request.POST.get("size")
        colour_id = request.POST.get("colour")
        quantity = request.POST.get("quantity")
        mrp = request.POST.get("mrp")
        discount_rate = request.POST.get("discount_rate")

        try:
            if not product_name:
                raise ValueError("Please enter a product name.")

            selected_category = category.objects.get(id=category_id)
            selected_size = size.objects.get(id=size_id)
            selected_colour = colour.objects.get(id=colour_id)

            quantity_value = int(quantity)
            mrp_value = Decimal(mrp)
            discount_value = Decimal(discount_rate)

            if quantity_value < 0:
                raise ValueError("Quantity cannot be negative.")

            if mrp_value <= 0:
                raise ValueError("MRP must be greater than zero.")

            if discount_value < 0 or discount_value > 100:
                raise ValueError("Discount rate must be between 0 and 100.")

            item.product_name = product_name
            item.category = selected_category
            item.size = selected_size
            item.colour = selected_colour
            item.quantity = quantity_value
            item.mrp = mrp_value
            item.discount_rate = discount_value

            # Image upload handling
            for image_field in ["front_image", "back_image", "side_image"]:

                image = request.FILES.get(image_field)

                if image:
                    extension = os.path.splitext(image.name)[1].lower()
                    filename = f"{uuid.uuid4().hex}{extension}"

                    folder = os.path.join(settings.MEDIA_ROOT, "product_images")
                    os.makedirs(folder, exist_ok=True)

                    file_path = os.path.join(folder, filename)

                    with open(file_path, "wb+") as destination:
                        for chunk in image.chunks():
                            destination.write(chunk)

                    setattr(item, image_field, f"product_images/{filename}")

            item.save()

            messages.success(request, "Product updated successfully!")
            return redirect("owner_dashboard")

        except (ValueError, InvalidOperation, TypeError):
            messages.error(request, "Please enter valid product details.")

        except (
            category.DoesNotExist,
            size.DoesNotExist,
            colour.DoesNotExist
        ):
            messages.error(request, "Please select valid category, size and colour.")

    return render(request, "product_form.html", {
        "categories": categories,
        "sizes": sizes,
        "colours": colours,
        "page_title": "Edit Product",
        "button_text": "Update Product",
        "item": item,
    })

def delete_product(request, id):

    if "owner_id" not in request.session:
        return redirect("owner_login")

    item = get_object_or_404(Product, id=id)

    # Delete image files from media folder
    for image_field in [item.front_image, item.back_image, item.side_image]:

        if image_field:
            file_path = os.path.join(settings.MEDIA_ROOT, image_field)

            if os.path.exists(file_path):
                os.remove(file_path)

    item.delete()

    messages.success(request, "Product deleted successfully!")

    return redirect("owner_dashboard")


front_image = models.ImageField(upload_to='products/', blank=True, null=True)
back_image = models.ImageField(upload_to='products/', blank=True, null=True)
side_image = models.ImageField(upload_to='products/', blank=True, null=True)


def billing_page(request, order_id):
    if "owner_id" not in request.session:
        return redirect("owner_login")

    order = get_object_or_404(Order, id=order_id)

    context = {
        "order": order,
        "order_items": order.items.all(),
    }

    return render(request, "billing.html", context)