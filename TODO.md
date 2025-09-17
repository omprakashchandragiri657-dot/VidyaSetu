# TODO: Fix Principal/HOD Uniqueness and Add Faculty Subjects

## Tasks
- [ ] Add Subject model to backend/core/models.py
- [ ] Update FacultyProfile model to include subjects ManyToManyField
- [ ] Update UserRegistrationSerializer to set College.principal and Department.hod fields
- [ ] Add validation in UserRegistrationSerializer to prevent multiple principals/HODs
- [ ] Update FacultyProfileSerializer to include subjects field
- [ ] Generate and run migrations for new models/fields
- [ ] Test faculty/principal/HOD creation with subject assignment
- [ ] Verify uniqueness constraints work properly
