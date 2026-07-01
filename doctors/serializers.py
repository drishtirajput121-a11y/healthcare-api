from rest_framework import serializers
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = (
            "id",
            "name",
            "specialization",
            "experience_years",
            "phone",
            "email",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def validate_name(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "Name must contain at least 2 characters."
            )

        return value

    def validate_email(self, value):
        return value.lower()

    def validate_experience_years(self, value):
        if value < 0 or value > 70:
            raise serializers.ValidationError(
                "Enter a valid number of experience years."
            )
        return value

    def validate_phone(self, value):
        phone = (
            value.replace("+", "")
                 .replace("-", "")
                 .replace(" ", "")
        )

        if not phone.isdigit():
            raise serializers.ValidationError(
                "Enter a valid phone number."
            )

        return value