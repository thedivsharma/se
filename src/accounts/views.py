"""Views for public pages, authentication, and user portals.

Each view keeps previous behavior (simple render or redirect). Minor refactor:
    * Common render helper to avoid repetition.
    * Inline comments clarified; functionality unchanged for URLs.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils.safestring import mark_safe
from django.utils import timezone
import json
import uuid

from .models import UserProfile, Product, CartItem, Order, OrderItem


def _render(request, template_name):
    return render(request, template_name)


# -------------------------
# PUBLIC PAGES
# -------------------------

def home_page(request):
    return _render(request, "HomePage.html")


def product_details(request, product_id):
    return _render(request, "ProductDetails.html")


def shopping_cart(request):
    items = CartItem.objects.filter(user=request.user) if request.user.is_authenticated else []
    total = sum(i.product.price * i.quantity for i in items)

    return render(request, "ShoppingCart.html", {
        "items": items,
        "total": total
    })


def checkout(request):
    return _render(request, "Checkout.html")


def review_page(request, product_id):
    return _render(request, "Review.html")


# -------------------------
# AUTHENTICATION
# -------------------------

def login_register(request):
    return _render(request, "LoginRegister.html")


def login_user(request):
    if request.method == "POST":
        email = request.POST.get("login-email")
        password = request.POST.get("login-password")

        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            messages.error(request, "No account with that email.")
            return redirect("login_register")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            profile = UserProfile.objects.filter(user=user).first()
            if profile and profile.role == "artisan":
                return redirect("artisan_dashboard")

            return redirect("home")
        else:
            messages.error(request, "Incorrect password.")
            return redirect("login_register")

    return redirect("login_register")


def register_user(request):
    if request.method == "POST":
        full_name = request.POST.get("register-fullname")
        role = request.POST.get("register-role")
        email = request.POST.get("register-email")
        password = request.POST.get("register-password")
        confirm = request.POST.get("register-confirm-password")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect("login_register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect("login_register")

        if not role:
            messages.error(request, "Please select a role.")
            return redirect("login_register")

        username = email.split("@")[0]

        user = User.objects.create_user(username=username, email=email, password=password)

        name_parts = full_name.strip().split(" ")
        user.first_name = name_parts[0]
        user.last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        user.save()

        UserProfile.objects.create(user=user, role=role)

        login(request, user)

        if role == "artisan":
            return redirect("artisan_dashboard")
        return redirect("home")

    return redirect("login_register")


def logout_user(request):
    logout(request)
    return redirect("home")


# -------------------------
# BUYER PORTAL
# -------------------------

@login_required
def buyer_profile(request):
    return _render(request, "BuyerProfile.html")


@login_required
def order_history(request):
    return _render(request, "OrderHistory.html")


@login_required
def invoice_page(request, order_id=None):
    if order_id:
        order = Order.objects.filter(order_id=order_id).first()
        if not order:
            return HttpResponse("Invalid order ID")

        items = OrderItem.objects.filter(order=order)
        serialized_items = [{
            "name": it.product.name,
            "price": float(it.price),
            "quantity": it.quantity,
        } for it in items]

        order_json = {
            "order_id": order.order_id,
            "created_at": order.created_at.strftime("%Y-%m-%d"),
            "user_name": f"{order.user.first_name} {order.user.last_name}",
            "shipping_address": "Default Address"
        }

        return render(request, "Invoice.html", {
            "order": order_json,
            "items": serialized_items,
        })

    return _render(request, "Invoice.html")


# -------------------------
# ARTISAN / SELLER PORTAL
# -------------------------

@login_required
def artisan_dashboard(request):

    profile = UserProfile.objects.get(user=request.user)
    if profile.role != "artisan":
        return redirect("home")

    products = Product.objects.filter(seller=request.user)
    sold_items = OrderItem.objects.filter(product__seller=request.user)

    total_sales = sum(i.price * i.quantity for i in sold_items)
    total_orders = sold_items.values("order").distinct().count()
    low_stock_products = products.filter(stock__lt=5)

    pending_orders = (
        Order.objects.filter(orderitem__product__seller=request.user).distinct()
    )

    recent_listings = products.order_by("-id")[:5]

    return render(request, "ArtisanDashboard.html", {
        "products": products,
        "sold_items": sold_items,
        "total_sales": total_sales,
        "total_orders": total_orders,
        "low_stock_products": low_stock_products,
        "pending_orders": pending_orders,
        "recent_listings": recent_listings,
    })


@login_required
def create_edit_listing(request, product_id=None):
    return _render(request, "CreateEditListing.html")


@login_required
def fulfillment_page(request):
    return _render(request, "Fulfillment.html")


@login_required
def inventory_manager(request):
    return _render(request, "InventoryManager.html")


@login_required
def reports_page(request):
    return _render(request, "Reports.html")


# -------------------------
# CART & CHECKOUT
# -------------------------

@require_POST
@login_required
def add_to_cart(request):
    product_id = request.POST.get("product_id")
    quantity = int(request.POST.get("quantity", 1))

    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    cart_count = CartItem.objects.filter(user=request.user).count()
    return JsonResponse({"success": True, "cart_count": cart_count})


@login_required
def update_cart_quantity(request, item_id, action):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)

    if action == "increase":
        item.quantity += 1
    elif action == "decrease" and item.quantity > 1:
        item.quantity -= 1

    item.save()
    return redirect('shopping_cart')


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('shopping_cart')


@login_required
def checkout_page(request):
    items = CartItem.objects.filter(user=request.user)

    items_json = []
    subtotal = 0

    for item in items:
        price = float(item.product.price)
        qty = item.quantity

        items_json.append({
            "name": item.product.name,
            "price": price,
            "quantity": qty,
            "color": "7c2d12"
        })

        subtotal += price * qty

    return render(request, "Checkout.html", {
        "items_json": items_json,
        "subtotal": subtotal,
        "total": subtotal,
    })


@login_required
def place_order(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect("shopping_cart")

    order_id = "WW-" + uuid.uuid4().hex[:8].upper()

    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    tax = subtotal * 0.08
    total = subtotal + tax

    order = Order.objects.create(
        user=request.user,
        order_id=order_id,
        subtotal=subtotal,
        tax=tax,
        total=total,
        created_at=timezone.now(),
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    cart_items.delete()

    return redirect(f"/invoice/?orderId={order_id}")
