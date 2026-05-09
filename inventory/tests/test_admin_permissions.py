from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.test.client import RequestFactory

from inventory.models import Product, Profile
from inventory.admin import ProductAdmin

class ProductAdminPermissionTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.product_admin = ProductAdmin(Product, self.site)
        
        self.superuser = User.objects.create_superuser('superuser', 'super@test.com', 'password')
        self.staff_user = User.objects.create_user('staffuser', 'staff@test.com', 'password', is_staff=True)
        Profile.objects.create(user=self.staff_user, managed_category='Electronics')

        self.product_electronics = Product.objects.create(name='Laptop', sku='ELEC-TEST-001', category='Electronics', price=1200)
        self.product_books = Product.objects.create(name='Django Book', sku='BOOK-TEST-001', category='Books', price=50)

    def test_staff_user_can_change_product_in_category(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        
        has_perm = self.product_admin.has_change_permission(request, self.product_electronics)
        self.assertTrue(has_perm)

    def test_staff_user_cannot_change_product_out_of_category(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        
        has_perm = self.product_admin.has_change_permission(request, self.product_books)
        self.assertFalse(has_perm)
