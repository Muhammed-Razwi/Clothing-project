from django.shortcuts import render,redirect, get_object_or_404
from .models import *
from django.contrib import messages
from owner.models import Product, category
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
from django.db import transaction
import uuid
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from .models import user, Product, CartItem

def user_reg(request):
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
            return redirect('user_reg')

        # Check username exists
        if user.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('user_reg')

        # Check email exists
        if user.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('user_reg')

        # Save user
        user.objects.create(
            name=name,
            username=username,
            email=email,
            phone=phone,
            password=password
        )

        messages.success(request, "Registration successful!")
        return redirect('user_login')

    return render(request, 'user_reg.html')


# Owner Login

def user_login(request):

    if request.method == "POST":

        # Get username and password
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # Check whether username exists
            user_data = user.objects.get(username=username)

            # Check password
            if user_data.password == password:

                # Store user details in session
                request.session['user_id'] = user_data.id
                request.session['user_name'] = user_data.name

                # Redirect to user dashboard
                return redirect('user_dashboard')

            else:
                return render(request, 'user_login.html', {
                    'error': 'Invalid username or password!'
                })

        except user.DoesNotExist:

            return render(request, 'user_login.html', {
                'error': 'Invalid username or password!'
            })

    return render(request, 'user_login.html')



# USER DASHBOARD

def user_dashboard(request):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    try:
        user_data = user.objects.get(id=user_id)

    except user.DoesNotExist:
        request.session.flush()
        return redirect('user_login')

    # Get all products
    products = Product.objects.all().order_by('-id')

    # Get all categories
    categories = category.objects.all()

    # Get category filter and search query
    selected_category = request.GET.get('category', '').strip()
    search_query = request.GET.get('search', '').strip()

    # Filter products by selected category
    if selected_category:
        products = products.filter(
            category_id=selected_category
        )

    # Search products by name, category and colour
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(category__category_name__icontains=search_query) |
            Q(colour__colour_name__icontains=search_query)
        ).distinct()

    # Get this user's wishlist
    wishlist_items = Wishlist.objects.filter(user=user_data)

    # Get product IDs already in the wishlist
    wishlist_product_ids = list(
        wishlist_items.values_list('product_id', flat=True)
    )

    # Calculate wishlist count
    wishlist_count = wishlist_items.count()

    # Get all cart items belonging to this user
    cart_items = CartItem.objects.filter(user=user_data)

    # Get product ID and its quantity
    cart_quantities = {
        item.product_id: item.quantity
        for item in cart_items
    }

    # Calculate total cart quantity
    cart_count = sum(cart_quantities.values())

    # Attach cart quantity to every product
    for product in products:
        product.cart_quantity = cart_quantities.get(
            product.id, 0
        )

    # Prepare dashboard context
    context = {
        'user_data': user_data,
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'wishlist_product_ids': wishlist_product_ids,
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,
    }

    return render(request, 'user_dashboard.html', context)
    

    


# ADD OR REMOVE WISHLIST

@require_POST
def wishlist_toggle(request, product_id):

    user_id = request.session.get('user_id')

    if not user_id:
        return JsonResponse({
            'success': False,
            'login_required': True
        }, status=401)

    try:
        user_data = user.objects.get(id=user_id)

    except user.DoesNotExist:
        request.session.flush()

        return JsonResponse({
            'success': False,
            'login_required': True
        }, status=401)

    product = get_object_or_404(Product, id=product_id)

    wishlist_item = Wishlist.objects.filter(
        user=user_data,
        product=product
    )

    if wishlist_item.exists():

        wishlist_item.delete()
        added = False

    else:

        Wishlist.objects.create(
            user=user_data,
            product=product
        )

        added = True

    # Get updated wishlist count immediately
    wishlist_count = Wishlist.objects.filter(
        user=user_data
    ).count()

    return JsonResponse({
        'success': True,
        'added': added,
        'wishlist_count': wishlist_count
    })

# WISHLIST PAGE
def user_wishlist(request):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    try:
        user_data = user.objects.get(id=user_id)

    except user.DoesNotExist:
        request.session.flush()
        return redirect('user_login')

    wishlist_items = Wishlist.objects.filter(
        user=user_data
    ).select_related(
        'product',
        'product__category',
        'product__size',
        'product__colour'
    ).order_by('-added_at')

    context = {
        'user_data': user_data,
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_items.count(),
    }

    return render(request, 'wishlist.html', context)

# REMOVE PRODUCT FROM WISHLIST

@require_POST
def remove_from_wishlist(request, product_id):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    try:
        user_data = user.objects.get(id=user_id)

    except user.DoesNotExist:
        request.session.flush()
        return redirect('user_login')

    # Delete selected product from this user's wishlist
    Wishlist.objects.filter(
        user=user_data,
        product_id=product_id
    ).delete()

    return redirect('user_wishlist')


# USER LOGOUT
def user_logout(request):

    request.session.flush()

    messages.success(
        request,
        'You have successfully logged out.'
    )

    return redirect('user_login')



# PRODUCT DETAILS PAGE

def product_details(request, product_id):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    try:
        user_data = user.objects.get(id=user_id)

    except user.DoesNotExist:
        request.session.flush()
        return redirect('user_login')

    product = get_object_or_404(
        Product.objects.select_related(
            'category',
            'size',
            'colour'
        ),
        id=product_id
    )

    wishlist_count = Wishlist.objects.filter(
        user=user_data
    ).count()

    context = {
        'user_data': user_data,
        'product': product,
        'wishlist_count': wishlist_count,
    }

    return render(
        request,
        'product_details.html',
        context
    )

# ADD PRODUCT TO CART

# ADD PRODUCT TO CART
@require_POST
def add_to_cart(request, product_id):

    user_id = request.session.get('user_id')

    if not user_id:
        return JsonResponse({
            'success': False,
            'message': 'Please login first.'
        }, status=401)

    try:
        user_data = user.objects.get(id=user_id)
    except user.DoesNotExist:
        request.session.flush()
        return JsonResponse({
            'success': False,
            'message': 'Your session has expired. Please login again.'
        }, status=401)

    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    quantity = max(1, quantity)

    if product.quantity < quantity:
        return JsonResponse({
            'success': False,
            'message': 'Sorry, this quantity is not available.'
        }, status=400)

    with transaction.atomic():
        cart_item = CartItem.objects.select_for_update().filter(
            user=user_data,
            product=product
        ).first()

        if cart_item:
            new_quantity = cart_item.quantity + quantity

            if new_quantity > product.quantity:
                return JsonResponse({
                    'success': False,
                    'message': 'You have reached the available stock limit.'
                }, status=400)

            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                user=user_data,
                product=product,
                quantity=quantity
            )

    cart_count = sum(
        CartItem.objects.filter(user=user_data).values_list(
            'quantity', flat=True
        )
    )

    return JsonResponse({
        'success': True,
        'message': 'Product added to cart!',
        'quantity': cart_item.quantity,
        'cart_count': cart_count
    })


# UPDATE CART QUANTITY
@require_POST
def update_cart_quantity(request, product_id):

    user_id = request.session.get('user_id')

    if not user_id:
        return JsonResponse({
            'success': False,
            'message': 'Please login first.'
        }, status=401)

    try:
        user_data = user.objects.get(id=user_id)
    except user.DoesNotExist:
        request.session.flush()
        return JsonResponse({
            'success': False,
            'message': 'Your session has expired. Please login again.'
        }, status=401)

    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get('quantity'))
    except (TypeError, ValueError):
        return JsonResponse({
            'success': False,
            'message': 'Invalid quantity.'
        }, status=400)

    if quantity < 0:
        return JsonResponse({
            'success': False,
            'message': 'Invalid quantity.'
        }, status=400)

    with transaction.atomic():
        cart_item = CartItem.objects.select_for_update().filter(
            user=user_data,
            product=product
        ).first()

        if not cart_item:
            return JsonResponse({
                'success': False,
                'message': 'This product is not in your cart.'
            }, status=404)

        if quantity > product.quantity:
            return JsonResponse({
                'success': False,
                'message': 'Only {} item(s) are available.'.format(
                    product.quantity
                )
            }, status=400)

        if quantity == 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()

    cart_count = sum(
        CartItem.objects.filter(user=user_data).values_list(
            'quantity', flat=True
        )
    )

    return JsonResponse({
        'success': True,
        'quantity': quantity,
        'cart_count': cart_count,
        'removed': quantity == 0,
        'message': 'Cart updated successfully.'
    })


# CART PAGE

def user_cart(request):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    try:
        user_data = user.objects.get(id=user_id)

    except user.DoesNotExist:
        request.session.flush()
        return redirect('user_login')

    cart_items = CartItem.objects.filter(
        user=user_data
    ).select_related(
        'product',
        'product__category',
        'product__size',
        'product__colour'
    ).order_by('-added_at')

    total_amount = 0

    for item in cart_items:
        item.subtotal = item.product.selling_price * item.quantity
        total_amount += item.subtotal

    cart_count = sum(item.quantity for item in cart_items)

    context = {
        'user_data': user_data,
        'cart_items': cart_items,
        'cart_count': cart_count,
        'total_amount': total_amount,
    }

    return render(request, 'cart.html', context)


# REMOVE PRODUCT FROM CART

@require_POST
def remove_from_cart(request, cart_id):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    try:
        user_data = user.objects.get(id=user_id)

    except user.DoesNotExist:
        request.session.flush()
        return redirect('user_login')

    cart_item = get_object_or_404(
        CartItem,
        id=cart_id,
        user=user_data
    )

    cart_item.delete()

    return redirect('user_cart')

def product_details(request, product_id):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    try:
        user_data = user.objects.get(id=user_id)
    except user.DoesNotExist:
        request.session.flush()
        return redirect('user_login')

    product = get_object_or_404(Product, id=product_id)

    context = {
        'user_data': user_data,
        'product': product,
        'wishlist_count': Wishlist.objects.filter(user=user_data).count(),
    }

    return render(request, 'product_details.html', context)

# REMOVE PRODUCT FROM WISHLIST

def remove_from_wishlist(request, product_id):

    if request.method == 'POST':

        user_id = request.session.get('user_id')

        if not user_id:
            return redirect('user_login')

        try:
            user_data = user.objects.get(id=user_id)

        except user.DoesNotExist:
            request.session.flush()
            return redirect('user_login')

        # Find and delete the wishlist item
        Wishlist.objects.filter(
            user=user_data,
            product_id=product_id
        ).delete()

    return redirect('user_wishlist')

def checkout(request):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    try:
        user_data = user.objects.get(id=user_id)
    except user.DoesNotExist:
        request.session.flush()
        return redirect('user_login')

    cart_items = CartItem.objects.filter(
        user=user_data
    ).select_related('product')

    if not cart_items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect('user_cart')

    total_amount = Decimal('0.00')
    cart_count = 0

    for item in cart_items:
        item.subtotal = item.product.selling_price * item.quantity
        total_amount += item.subtotal
        cart_count += item.quantity

    context = {
        'user_data': user_data,
        'cart_items': cart_items,
        'cart_count': cart_count,
        'total_amount': total_amount,
    }

    if request.method == 'POST':

        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        payment_method = request.POST.get('payment_method', '')

        if not all([full_name, phone, address, pincode]):
            context['error'] = "Please fill in all delivery details."
            return render(request, 'buy_now.html', context)

        if payment_method not in ['COD', 'ONLINE']:
            context['error'] = "Please select a valid payment method."
            return render(request, 'buy_now.html', context)

        with transaction.atomic():

            # Get the current cart items again
            current_cart_items = list(
                CartItem.objects
                .filter(user=user_data)
                .select_related('product')
            )

            if not current_cart_items:
                messages.info(request, "Your cart is empty.")
                return redirect('user_cart')

            # Recalculate total using current cart items
            total_amount = Decimal('0.00')

            for item in current_cart_items:
                item.subtotal = (
                    item.product.selling_price * item.quantity
                )
                total_amount += item.subtotal

            # Create order
            order = Order.objects.create(
                user=user_data,
                order_number='FS-' + uuid.uuid4().hex[:10].upper(),
                full_name=full_name,
                phone=phone,
                address=address,
                pincode=pincode,
                payment_method=payment_method,
                payment_status='PENDING',
                order_status='PLACED',
                total_amount=total_amount
            )

            # Create order items with Product foreign key
            for item in current_cart_items:

                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.product_name,
                    quantity=item.quantity,
                    price=item.product.selling_price,
                    subtotal=item.subtotal
                )

            # Clear cart after successful order creation
            CartItem.objects.filter(user=user_data).delete()

        return redirect('order_placed', order_id=order.id)

    return render(request, 'buy_now.html', context)


# ORDER PLACED

def order_placed(request, order_id):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    try:
        user_data = user.objects.get(id=user_id)
    except user.DoesNotExist:
        request.session.flush()
        return redirect('user_login')

    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id=order_id,
        user=user_data
    )

    context = {
        'order': order,
        'order_items': order.items.all(),
    }

    return render(request, 'order_placed.html', context)


# USER ORDERS

def user_orders(request):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    orders = (
        Order.objects
        .filter(user_id=user_id)
        .prefetch_related('items__product')
        .order_by('-created_at')
    )

    context = {
        'orders': orders,
    }

    return render(request, 'user_orders.html', context)


# ORDER DETAILS

def order_details(request, order_id):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id=order_id,
        user_id=user_id
    )

    cancellation_deadline = order.created_at + timedelta(hours=5)

    can_cancel = (
        timezone.now() <= cancellation_deadline
        and order.order_status in ['PLACED', 'PROCESSING']
    )

    context = {
        'order': order,
        'can_cancel': can_cancel,
        'cancellation_deadline': cancellation_deadline,
    }

    return render(request, 'order_details.html', context)


# CANCEL ORDER

@require_POST
def cancel_order(request, order_id):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    with transaction.atomic():

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
            user_id=user_id
        )

        cancellation_deadline = order.created_at + timedelta(hours=5)

        if timezone.now() > cancellation_deadline:

            messages.error(
                request,
                'Sorry! The 5-hour cancellation period has expired.'
            )

        elif order.order_status not in ['PLACED', 'PROCESSING']:

            messages.error(
                request,
                'This order cannot be cancelled because it is already '
                'shipped, delivered or cancelled.'
            )

        else:

            order.order_status = 'CANCELLED'
            order.save(update_fields=['order_status'])

            messages.success(
                request,
                'Your order has been cancelled successfully.'
            )

    return redirect('order_details', order_id=order_id)

def user_profile(request):
    if 'user_id' not in request.session:
        return redirect('user_login')

    user_id = request.session['user_id']
    user_data = get_object_or_404(user, id=user_id)

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        pincode = request.POST.get('pincode', '').strip()

        profile_image = request.FILES.get('profile_image')

        if not name or not username or not email or not phone:
            messages.error(request, 'Please fill all required fields.')

        elif user.objects.filter(
            username__iexact=username
        ).exclude(id=user_data.id).exists():
            messages.error(request, 'Username already exists.')

        elif user.objects.filter(
            email__iexact=email
        ).exclude(id=user_data.id).exists():
            messages.error(request, 'Email already exists.')

        else:
            user_data.name = name
            user_data.username = username
            user_data.email = email
            user_data.phone = phone
            user_data.address = address
            user_data.pincode = pincode

            if profile_image:
                user_data.profile_image = profile_image

            user_data.save()

            # Update the session name
            request.session['user_name'] = user_data.name

            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile')

    return render(request, 'user_profile.html', {
        'user_data': user_data
    })
