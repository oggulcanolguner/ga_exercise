from django.contrib.auth.signals import user_logged_in
from rest_framework import permissions, status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users import models, serializers
from utils.cache import cache_method
from utils.error import ApiError, ApiErrorCodes


class JWTObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed as e:
            raise ApiError(
                message=str(e),
                error_code=ApiErrorCodes.USERS_INVALID_CREDENTIALS,
                status_code=401,
            )
        except ValidationError as e:
            raise ApiError.from_validation_error(e)

        user = models.User.objects.get(email=request.data["email"])
        user_logged_in.send(sender=user.__class__, request=request, user=user)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class JWTRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise ApiError(
                message=str(e),
                error_code=ApiErrorCodes.USERS_TOKEN_NOT_FOUND,
                status_code=404,
            )

        user = models.User.objects.get(email=request.data["email"])
        user_logged_in.send(sender=user.__class__, request=request, user=user)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class SignUpView(CreateAPIView):

    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)
        else:
            raise serializer.get_api_error()
        user_logged_in.send(sender=user.__class__, request=request, user=user)
        return Response(
            serializers.LoggedInUserSerializer(instance=user).data,
            status=status.HTTP_201_CREATED,
        )


class ProfileView(RetrieveAPIView):
    @cache_method(arg_getters=["user"])
    def get(self, request, *args, **kwargs):
        serializer = serializers.UserSerializer(request.user)
        return Response(serializer.data)


class SearchUserView(GenericAPIView):

    serializer_class = serializers.UserSummarySerializer

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("keyword")
        if not query:
            raise ApiError(
                "Keyword for search not found.",
                error_code=ApiErrorCodes.GENERIC_MISSING_QUERY_PARAMETER,
                status_code=400,
            )

        queryset = models.User.objects.search(query)
        queryset = self.paginate_queryset(queryset)
        serializer = self.serializer_class(queryset, many=True)
        response = self.get_paginated_response(serializer.data)
        return response
