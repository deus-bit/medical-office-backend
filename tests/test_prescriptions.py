from app.user.models import AccountModel, ProfileModel, RoleModel
from app.user.repositories import (
    AccountRepository, AccountFindQuery,
    InMemoryAccountRepository,

    ProfileRepository, ProfileFindQuery,
    InMemoryProfileRepository,

    RoleRepository, RoleFindQuery,
    InMemoryRoleRepository,
)

from app.medical_diagnosis.models import MedicalDiagnosisModel
from app.medical_diagnosis.repositories import (
    MedicalDiagnosisRepository, MedicalDiagnosisFindQuery,
    InMemoryMedicalDiagnosisRepository,
)

from app.prescription.models import PrescriptionModel, MedicationScheduleModel
from app.prescription.repositories import (
    PrescriptionRepository, PrescriptionFindQuery,
    InMemoryPrescriptionRepository,

    MedicationScheduleRepository, MedicationScheduleFindQuery,
    InMemoryMedicationScheduleRepository,
)

from app.schedule.models import ScheduleModel, ScheduleCycleModel
from app.schedule.repositories import (
    ScheduleRepository, ScheduleFindQuery,
    InMemoryScheduleRepository,

    ScheduleCycleRepository, ScheduleCycleFindQuery,
    InMemoryScheduleCycleRepository,
)

from app.medicine.models import MedicineModel
from app.medicine.repositories import (
    MedicineRepository, MedicineFindQuery,
    InMemoryMedicineRepository,
)

from app.exceptions import *
from app.utils import HttpxClient
from datetime import date
import pytest

@pytest.mark.parametrize(','.join((
    'account_repo', 'profile_repo', 'role_repo',
    'medical_diagnosis_repo', 'prescription_repo', 'medication_schedule_repo',
    'schedule_repo', 'schedule_cycle_repo',
    'medicine_repo'
)), [
    (InMemoryAccountRepository(),
     InMemoryProfileRepository(),
     InMemoryRoleRepository(),
     InMemoryMedicalDiagnosisRepository(),
     InMemoryPrescriptionRepository(),
     InMemoryMedicationScheduleRepository(),
     InMemoryScheduleRepository(),
     InMemoryScheduleCycleRepository(),
     InMemoryMedicineRepository())
])
async def test_prescription_repository(account_repo: AccountRepository,
                                       profile_repo: ProfileRepository,
                                       role_repo: RoleRepository,
                                       medical_diagnosis_repo: MedicalDiagnosisRepository,
                                       prescription_repo: PrescriptionRepository,
                                       medication_schedule_repo: MedicationScheduleRepository,
                                       schedule_repo: ScheduleRepository,
                                       schedule_cycle_repo: ScheduleCycleRepository,
                                       medicine_repo: MedicineRepository,
                                       ) -> None:
    await role_repo.create_defaults()
    assert await role_repo.find_by_name("Base User") is not None, "Base User role should exist."
    assert await role_repo.find_by_name("Family Medicine Doctor") is not None, "Family Medicine Doctor role should exist."
    assert await role_repo.find_by_name("Administrator") is not None, "Administrator role should exist."

    patient_profile = ProfileModel(
        name="John",
        paternal="Doe",
        maternal="Garcia",
        phone=77712345,
        birthdate=date(1983, 3, 22)
    )
    patient_profile = await profile_repo.add(patient_profile)
    assert patient_profile.id is not None, "Profile should have an ID after being added."

    patient_account = AccountModel(
        email="john.doe@gmail.com",
        password=b"john_secure_pwd",
        profile_id=patient_profile.id,
        role_id=(await role_repo.find_by_name("Base User")).id
    )
    patient_account = await account_repo.add(patient_account)
    assert patient_account.id is not None, "Account should have an ID after being added."

    doctor_profile = ProfileModel(
        name="Alex",
        paternal="Riley",
        maternal="Montgomery",
        phone=65829984,
        birthdate=date(1982, 6, 6)
    )
    doctor_profile = await profile_repo.add(doctor_profile)
    assert doctor_profile.id is not None, "Profile should have an ID after being added."

    doctor_account = AccountModel(
        email="alex.riley.montgomery@vidaplena.com",
        password=b"admin_secure_pwd",
        profile_id=doctor_profile.id,
        role_id=(await role_repo.find_by_name("Family Medicine Doctor")).id
    )
    doctor_account = await account_repo.add(doctor_account)
    assert doctor_account.id is not None, "Account should have an ID after being added."

    medical_diagnosis = MedicalDiagnosisModel(
        patient_id=patient_account.id,
        doctor_id=doctor_account.id,
        disease="Exploding Head Syndrome (EHS) with Comorbid Nocturnal Encephalophony"
    )
    medical_diagnosis = await medical_diagnosis_repo.add(medical_diagnosis)
    assert medical_diagnosis.id is not None, "Medical diagnosis should have an ID after being added."

    prescription = PrescriptionModel(
        patient_id=patient_account.id,
        doctor_id=doctor_account.id,
        medical_diagnosis_id=medical_diagnosis.id
    )
    prescription = await prescription_repo.add(prescription)
    assert prescription.id is not None, "Prescription should have an ID after being added."
