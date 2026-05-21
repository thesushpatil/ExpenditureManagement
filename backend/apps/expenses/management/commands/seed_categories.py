"""
Management command to seed default expense categories.
Usage: python manage.py seed_categories
"""
from django.core.management.base import BaseCommand
from apps.expenses.models import ExpenseCategory


DEFAULT_CATEGORIES = [
    {'name': 'Food & Dining', 'icon': 'utensils', 'color': '#ef4444'},
    {'name': 'Transportation', 'icon': 'car', 'color': '#f97316'},
    {'name': 'Shopping', 'icon': 'shopping-bag', 'color': '#eab308'},
    {'name': 'Entertainment', 'icon': 'film', 'color': '#22c55e'},
    {'name': 'Bills & Utilities', 'icon': 'file-text', 'color': '#06b6d4'},
    {'name': 'Healthcare', 'icon': 'heart', 'color': '#8b5cf6'},
    {'name': 'Education', 'icon': 'book-open', 'color': '#6366f1'},
    {'name': 'Rent & Housing', 'icon': 'home', 'color': '#ec4899'},
    {'name': 'Groceries', 'icon': 'shopping-cart', 'color': '#14b8a6'},
    {'name': 'Personal Care', 'icon': 'user', 'color': '#f43f5e'},
    {'name': 'Travel', 'icon': 'plane', 'color': '#0ea5e9'},
    {'name': 'Other', 'icon': 'more-horizontal', 'color': '#64748b'},
]


class Command(BaseCommand):
    help = 'Seed default expense categories'

    def handle(self, *args, **options):
        created_count = 0
        for cat_data in DEFAULT_CATEGORIES:
            _, created = ExpenseCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'icon': cat_data['icon'], 'color': cat_data['color']}
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully seeded {created_count} new categories. '
                               f'Total: {ExpenseCategory.objects.count()}')
        )
