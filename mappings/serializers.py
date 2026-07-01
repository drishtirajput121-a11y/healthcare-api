from rest_framework import serializers
from .models import PatientDoctorMapping
from patients.models import Patient
from doctors.models import Doctor


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    # Nested read-only details for responses
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_specialization = serializers.CharField(
        source='doctor.specialization',
        read_only=True
    )

    class Meta:
        model = PatientDoctorMapping
        fields = (
            'id',
            'patient',
            'patient_name',
            'doctor',
            'doctor_name',
            'doctor_specialization',
            'assigned_at',
        )
        read_only_fields = ('id', 'assigned_at')

    def validate(self, data):
        patient = data.get('patient')
        doctor = data.get('doctor')

        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Authentication required.")

        if patient.created_by != request.user:
            raise serializers.ValidationError(
            "You can only assign doctors to your own patients."
            )

        if PatientDoctorMapping.objects.filter(
            patient=patient,
            doctor=doctor
        ).exists():
            raise serializers.ValidationError(
                "This doctor is already assigned to this patient."
            )

        return data