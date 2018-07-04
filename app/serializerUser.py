from rest_framework.serializers import ModelSerializer
from rest_framework_jwt.serializers import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'is_active',)