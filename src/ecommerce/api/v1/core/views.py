from django.shortcuts import get_object_or_404
from django.db.models import Q  # For searching


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status


from core.models import Category, Product, Cart, Order, OrderItem, User, Review
from api.v1.core.serializers import (
    CategorySerializer, ProductSerializer, CartSerializer, 
    OrderSerializer, OrderItemSerializer, ReviewSerializer
)
from api.v1.auth.serializers import UserSerializer




# CATEGORY VIEWS
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def category_list_create(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        if not request.user.is_staff:  # Only admin can create categories
            return Response({"error": "Only admins can create categories"}, status=status.HTTP_403_FORBIDDEN)

        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:  # Allow both full and partial updates
        if not request.user.is_staff:
            return Response({"error": "Only admins can update categories"}, status=status.HTTP_403_FORBIDDEN)

        partial = request.method == 'PATCH'  # Only PATCH allows partial updates
        serializer = CategorySerializer(category, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user.is_staff:
            return Response({"error": "Only admins can delete categories"}, status=status.HTTP_403_FORBIDDEN)

        category.delete()
        return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_list_create(request):
    if request.method == 'GET':
        products = Product.objects.filter(is_deleted=False)

        # Filtering by category
        category_id = request.GET.get('category')
        if category_id:
            products = products.filter(category_id=category_id)

        # Searching by name or description
        search_query = request.GET.get('search')
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        if not request.user.is_staff:  # Only admin can create products
            return Response({"error": "Only admins can add products"}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_deleted=False)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:  # Allow both full and partial updates
        if not request.user.is_staff:
            return Response({"error": "Only admins can update products"}, status=status.HTTP_403_FORBIDDEN)

        partial = request.method == 'PATCH'  # Only PATCH should allow partial updates
        serializer = ProductSerializer(product, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user.is_staff:
            return Response({"error": "Only admins can delete products"}, status=status.HTTP_403_FORBIDDEN)

        product.is_deleted = True  # Soft delete
        product.save()
        return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cart_list_create(request):
    if request.method == 'GET':
        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True)
        
        # Calculate grand total price
        grand_total = sum(item.product.price * item.quantity for item in cart_items)
        
        return Response({"cart_items": serializer.data, "grand_total": grand_total}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)

        try:
            quantity = int(quantity)  # Convert quantity to an integer
        except ValueError:
            return Response({"error": "Quantity must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if product exists
        product = get_object_or_404(Product, id=product_id)

        # Check if product is already in cart
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

        if created:
            cart_item.quantity = quantity  # New entry, set quantity
        else:
            cart_item.quantity += quantity  # Existing entry, increase quantity

        cart_item.save()
        return Response(CartSerializer(cart_item).data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_detail(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)

    if request.method in ['PUT', 'PATCH']:
        serializer = CartSerializer(cart_item, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        cart_item.delete()
        return Response({"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        return Response({"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ **Step 1: Check stock availability first**
    for cart_item in cart_items:
        if cart_item.quantity > cart_item.product.stock:
            return Response({"error": f"Not enough stock for {cart_item.product.name}."}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ **Step 2: Create the order only if all stock is available**
    order = Order.objects.create(user=user, payment_status="Paid")

    total_price = 0

    # ✅ **Step 3: Deduct stock & create order items**
    for cart_item in cart_items:
        cart_item.product.stock -= cart_item.quantity
        cart_item.product.save()

        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price_at_order=cart_item.product.price
        )

        total_price += cart_item.quantity * cart_item.product.price

    # ✅ **Step 4: Clear the cart only after successful order placement**
    cart_items.delete()

    return Response({"message": "Order placed successfully!", "order_id": order.id, "total_price": total_price}, status=status.HTTP_201_CREATED)



    




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list(request):
    """Get all orders for the logged-in user"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    """Get details of a specific order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def track_order_status(request, order_id):
    """Retrieve order status"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return Response({"order_id": order.id, "status": order.status}, status=status.HTTP_200_OK)


#admin
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """Allow admin to update order status"""
    if not request.user.is_staff:
        return Response({"error": "Only admins can update order status"}, status=status.HTTP_403_FORBIDDEN)

    order = get_object_or_404(Order, id=order_id)
    
    new_status = request.data.get("status")
    valid_statuses = ['Pending', 'Shipped', 'Delivered', 'Cancelled']

    if new_status not in valid_statuses:
        return Response({"error": "Invalid status. Choose from Pending, Shipped, Delivered, or Cancelled."},
                        status=status.HTTP_400_BAD_REQUEST)

    order.status = new_status
    order.save()

    return Response({"message": f"Order status updated to {new_status}"}, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_orders(request):
    """Allow admin to view all orders"""
    if not request.user.is_staff:
        return Response({"error": "Only admins can view all orders"}, status=status.HTTP_403_FORBIDDEN)

    orders = Order.objects.all().order_by('-created_at')  # Latest orders first
    serializer = OrderSerializer(orders, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    """Admin can cancel an order"""
    if not request.user.is_staff:
        return Response({"error": "Only admins can cancel orders"}, status=status.HTTP_403_FORBIDDEN)

    order = get_object_or_404(Order, id=order_id)

    if order.status in ["Shipped", "Delivered"]:
        return Response({"error": "Cannot cancel a shipped or delivered order"}, status=status.HTTP_400_BAD_REQUEST)

    order.status = "Cancelled"
    order.save()

    return Response({"message": "Order cancelled successfully"}, status=status.HTTP_200_OK)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """Admin can view all registered users"""
    if not request.user.is_staff:
        return Response({"error": "Only admins can view users"}, status=status.HTTP_403_FORBIDDEN)

    users = User.objects.filter(is_staff=False)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def block_user(request, user_id):
    """Admin can block (deactivate) a user"""
    if not request.user.is_staff:
        return Response({"error": "Only admins can block users"}, status=status.HTTP_403_FORBIDDEN)

    user = get_object_or_404(User, id=user_id)

    if not user.is_active:
        return Response({"message": "User is already blocked"}, status=status.HTTP_400_BAD_REQUEST)

    user.is_active = False  # Deactivate user
    user.save()
    return Response({"message": "User blocked successfully"}, status=status.HTTP_200_OK)



@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def unblock_user(request, user_id):
    """Admin can unblock (reactivate) a user"""
    if not request.user.is_staff:
        return Response({"error": "Only admins can unblock users"}, status=status.HTTP_403_FORBIDDEN)

    user = get_object_or_404(User, id=user_id)

    if user.is_active:
        return Response({"message": "User is already active"}, status=status.HTTP_400_BAD_REQUEST)

    user.is_active = True  # Reactivate user
    user.save()
    return Response({"message": "User unblocked successfully"}, status=status.HTTP_200_OK)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    """Admin can delete a user"""
    if not request.user.is_staff:
        return Response({"error": "Only admins can delete users"}, status=status.HTTP_403_FORBIDDEN)

    user = get_object_or_404(User, id=user_id)
    user.delete()
    return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_deleted=False)

    if request.method == 'GET':
        reviews = Review.objects.filter(product=product)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        has_purchased = OrderItem.objects.filter(order__user=request.user, product=product).exists()
        if not has_purchased:
            return Response({"error": "You can only review products you've purchased."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = ReviewSerializer(data=request.data, context={'product': product})  # Pass product
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


