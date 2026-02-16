from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer untuk registrasi user baru"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])  # noqa: E501
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm Password")  # noqa: E501
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2", "name")
        extra_kwargs = {
            "name": {"required": False},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})  # noqa: E501

        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "Email already exists."})

        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError({"username": "Username already exists."})

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data.get("name", ""),
        )


class LoginSerializer(TokenObtainPairSerializer):
    """Serializer untuk login dengan JWT token"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        # Tambahkan info user
        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "name": self.user.name,
        }

        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer untuk ubah password"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])  # noqa: E501
    new_password2 = serializers.CharField(required=True, write_only=True, label="Confirm New Password")  # noqa: E501

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})  # noqa: E501
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            msg = "Old password is incorrect."
            raise serializers.ValidationError(msg)
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class ResetPasswordRequestSerializer(serializers.Serializer):
    """Serializer untuk request reset password"""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            msg = "User with this email does not exist."
            raise serializers.ValidationError(msg)
        return value


class ResetPasswordConfirmSerializer(serializers.Serializer):
    """Serializer untuk konfirmasi reset password dengan token"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])  # noqa: E501
    new_password2 = serializers.CharField(required=True, write_only=True, label="Confirm New Password")  # noqa: E501

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})  # noqa: E501
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer untuk user profile (get me)"""
    class Meta:
        model = User
        fields = ("id", "username", "email", "name", "date_joined", "last_login", "is_active", "is_staff")  # noqa: E501
        read_only_fields = ("id", "username", "date_joined", "last_login", "is_staff")
