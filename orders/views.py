from rest_framework.generics import GenericAPIView
from rest_framework import mixins
# from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
# from rest_framework.parsers import MultiPartParser
# from django.core.files.storage import default_storage
from django.http import HttpResponse
import csv
from django.db import connection

from admin.pagination import CustomPagination
from users.authentication import JWTAuthentication
from .models import Order, OrderItem
from .serializers import OrderSerializer


class OrderGenericAPIView(
        GenericAPIView,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request, pk=None):
        if pk:
            return Response({
                'data': self.retrieve(request, pk).data
            })

        return self.list(request)


class ExportAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=orders.csv'

        orders = Order.objects.all()
        writer = csv.writer(response)

        writer.writerow(
            ['ID', 'Name', 'Email', 'Product Title', 'Price', 'Quantity'])

        for order in orders:

            writer.writerow([order.id,  # type: ignore
                             order.name, order.email, '', '', ''])
            orderItems = OrderItem.objects.all().filter(order_id=order.id)  # type: ignore

            for item in orderItems:
                writer.writerow(
                    ['', '', '', item.product_title, item.price, item.quantity])

        return response


class ChartAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, _):
        with connection.cursor() as cursor:
            # Sum of orders per date
            cursor.execute(
                """
                SELECT
                    DATE_FORMAT(ord.created_at, '%Y-%m-%d') as date
                    , SUM(ordi.quantity * ordi.price) as sum
                FROM orders_order as ord
                    JOIN orders_orderitem as ordi
                        ON ord.id = ordi.order_id
                GROUP BY date
                """)

            query_results = cursor.fetchall()
            return_data = [{
                'date': result[0],
                'sum': result[1]
            } for result in query_results]

        return Response({
            'data': return_data
        })
