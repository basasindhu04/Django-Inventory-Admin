# Django Inventory Admin Project

This project demonstrates a fully-customized Django Admin interface transformed into a product inventory management dashboard. It includes customized list views, complex admin actions with atomic transactions, custom reporting views, and robust row-level permissions.

## Features
- **Custom Admin Views and Actions:** Extends ModelAdmin to provide a clearance action and computed badges.
- **Custom Dashboard:** Adds a new view inside the secure admin site (`/admin/inventory/dashboard/`).
- **Row-Level Permissions:** Restricts editing rights based on internal staff profiles.
- **Read-Only Inlines:** Displays a non-editable audit history.

## Running the Application
The project is containerized. To get started, run:

```bash
# This will build the containers, run migrations, and automatically seed data
docker-compose up --build -d
```

Once started, wait a few seconds and the admin will be available at `http://localhost:8000/admin/`.

## Test Credentials
Test credentials configured by the entrypoint seeding:

- **Superuser**: `superadmin` / `superpassword`
- **Electronics Staff**: `elec_staff` / `elec_password`
- **Books Staff**: `books_staff` / `books_password`

## Running Tests
To run the automated tests validating the permission models:
```bash
docker-compose exec web python manage.py test inventory
```
