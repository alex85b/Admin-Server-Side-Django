from rest_framework.generics import GenericAPIView
from rest_framework import mixins
# from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage

from admin.pagination import CustomPagination
from users.authentication import JWTAuthentication
from .models import Product
from .serializers import ProductSerializer


class ProductGenericAPIView(
        GenericAPIView,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin):

    # setup:
    authentication_classes = [JWTAuthentication]  # <-- is user authenticated.
    permission_classes = [IsAuthenticated]  # <-- does user have permissions.
    pagination_class = CustomPagination
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, pk=None):
        if pk:
            return Response({
                'data': self.retrieve(request, pk).data
            })

        return self.list(request)

    def post(self, request):
        return Response({
            'data': self.create(request).data
        })

    def put(self, request, pk=None):
        return Response({
            'data': self.partial_update(request, pk).data
        })

    def delete(self, request, pk=None):
        return self.destroy(request, pk)


class FileUploadView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser,)

    def post(self, request):
        file = request.FILES['image']
        file_name = default_storage.save(file.name, file)
        url = default_storage.url(file_name)

        return Response({
            'url': 'http://localhost:8000/api' + url
        })
