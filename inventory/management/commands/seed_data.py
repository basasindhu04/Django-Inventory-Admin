import os
import json
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import Profile, Product

class Command(BaseCommand):
    help = 'Seeds the database with test users and products'

    def handle(self, *args, **kwargs):
        # Read from submission.json
        submission_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'submission.json')
        
        if not os.path.exists(submission_path):
            self.stdout.write(self.style.ERROR(f'submission.json not found at {submission_path}'))
            return

        with open(submission_path, 'r') as f:
            data = json.load(f)
            creds = data.get('testCredentials', {})

        # Superuser
        su_cred = creds.get('superuser', {})
        if not User.objects.filter(username=su_cred.get('username')).exists():
            User.objects.create_superuser(
                username=su_cred.get('username', 'superadmin'),
                password=su_cred.get('password', 'superpassword'),
                email='super@test.com'
            )
            self.stdout.write(self.style.SUCCESS(f'Created superuser: {su_cred.get("username")}'))

        # Staff Users
        elec_cred = creds.get('electronicsStaff', {})
        if not User.objects.filter(username=elec_cred.get('username')).exists():
            u = User.objects.create_user(
                username=elec_cred.get('username', 'elec_staff'),
                password=elec_cred.get('password', 'elec_password'),
                is_staff=True,
            )
            Profile.objects.create(user=u, managed_category='Electronics')
            self.stdout.write(self.style.SUCCESS(f'Created electronics staff: {elec_cred.get("username")}'))

        books_cred = creds.get('booksStaff', {})
        if not User.objects.filter(username=books_cred.get('username')).exists():
            u = User.objects.create_user(
                username=books_cred.get('username', 'books_staff'),
                password=books_cred.get('password', 'books_password'),
                is_staff=True,
            )
            Profile.objects.create(user=u, managed_category='Books')
            self.stdout.write(self.style.SUCCESS(f'Created books staff: {books_cred.get("username")}'))

        # Seed Products
        if not Product.objects.filter(category='Electronics').exists():
            for i in range(1, 11):
                Product.objects.create(
                    name=f'Electronic Item {i}',
                    sku=f'ELEC-{i:03}',
                    price=10.00 * i,
                    stock=i * 5,
                    category='Electronics'
                )
            self.stdout.write(self.style.SUCCESS('Created 10 Electronics products'))

        if not Product.objects.filter(category='Books').exists():
            for i in range(1, 11):
                Product.objects.create(
                    name=f'Book Item {i}',
                    sku=f'BOOK-{i:03}',
                    price=5.00 * i,
                    stock=i * 8, # Some >10, some <10 depending on index if needed, wait, i*8 might not be below 10 for any i > 1
                    category='Books'
                )
            # ensure some low stock items for badges test
            p = Product.objects.last()
            p.stock = 5
            p.save()
            
            self.stdout.write(self.style.SUCCESS('Created 10 Books products'))
