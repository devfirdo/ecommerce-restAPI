from rest_framework import serializers
from core.models import Category, Product, Cart, OrderItem, Order, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']  # Slug is auto-generated


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'stock', 'image', 'created_at']
        read_only_fields = ['created_at']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value



class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.product.price * obj.quantity
    


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product_name', 'quantity', 'price_at_order']


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='user.username', read_only=True)  # Include customer name
    order_items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ['id','customer_name', 'status', 'payment_status', 'created_at', 'total_price', 'order_items']



class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = Review
        fields = ['id', 'username', 'product', 'product_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['username', 'product_name', 'created_at', 'product']  # Make 'product' read-only

    def create(self, validated_data):
        product = self.context['product']  # Get product from view context
        return Review.objects.create(product=product, **validated_data)