from django.db import models
from patients.models import Patient
from doctors.models import Doctor


class PatientDoctorMapping(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='doctor_mappings'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='patient_mappings'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patient', 'doctor') 
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.patient.name} → Dr. {self.doctor.name}"