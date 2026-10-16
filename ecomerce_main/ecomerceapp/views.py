from rest_framework import viewsets, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, CartItem, Order
from .serializers import CategorySerializer, ProductSerializer, CartItemSerializer, OrderSerializer
from .sslcommerz import initiate_sslcommerz_payment


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)



class PaymentInitiateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
           
            order = Order.objects.get(id=order_id, user=request.user)
            payment_url = initiate_sslcommerz_payment(order, request.user, request)
            return Response({"payment_url": payment_url}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "অর্ডারটি পাওয়া যায়নি!"}, status=status.HTTP_404_NOT_FOUND)


class PaymentSuccessView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        tran_id = request.data.get('tran_id')
        if not tran_id:
            return Response({"error": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)

        order_id = tran_id.replace('TXN-', '')
        try:
            order = Order.objects.get(id=order_id)
            order.payment_status = Order.PaymentStatusChoices.PAID
            order.status = Order.StatusChoices.PROCESSING
            order.transaction_id = tran_id
            order.save()
            return Response({"message": "পেমেন্ট সফলভাবে সম্পন্ন হয়েছে!"}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "অর্ডার পাওয়া যায়নি!"}, status=status.HTTP_400_BAD_REQUEST)