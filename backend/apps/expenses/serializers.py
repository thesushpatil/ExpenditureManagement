"""
Serializers for expense management models.
"""
from rest_framework import serializers
from django.db.models import Sum
from .models import ExpenseCategory, Income, Expense, Saving, Budget


class ExpenseCategorySerializer(serializers.ModelSerializer):
    """Serializer for expense categories."""

    class Meta:
        model = ExpenseCategory
        fields = ('id', 'name', 'icon', 'color', 'created_at')
        read_only_fields = ('id', 'created_at')


class IncomeSerializer(serializers.ModelSerializer):
    """Serializer for income records."""

    class Meta:
        model = Income
        fields = ('id', 'amount', 'source', 'date', 'description', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for expense records."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)

    class Meta:
        model = Expense
        fields = (
            'id', 'amount', 'category', 'category_name', 'category_color',
            'category_icon', 'date', 'description', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        """Check if expense exceeds budget limit."""
        request = self.context.get('request')
        if request and request.user:
            category = attrs.get('category')
            amount = attrs.get('amount')
            date = attrs.get('date')

            if category and amount and date:
                budget = Budget.objects.filter(
                    user=request.user,
                    category=category,
                    month=date.month,
                    year=date.year,
                ).first()

                if budget:
                    current_total = Expense.objects.filter(
                        user=request.user,
                        category=category,
                        date__month=date.month,
                        date__year=date.year,
                    ).aggregate(total=Sum('amount'))['total'] or 0

                    # If updating, subtract the current instance amount
                    if self.instance:
                        current_total -= self.instance.amount

                    if (current_total + amount) > budget.limit:
                        raise serializers.ValidationError({
                            'amount': f'This expense would exceed your budget of {budget.limit} '
                                      f'for {category.name}. Current spending: {current_total}.'
                        })
        return attrs


class SavingSerializer(serializers.ModelSerializer):
    """Serializer for savings records."""

    class Meta:
        model = Saving
        fields = ('id', 'amount', 'goal', 'date', 'description', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for budget records."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    spent = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    percentage_used = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = (
            'id', 'category', 'category_name', 'limit', 'month', 'year',
            'spent', 'remaining', 'percentage_used', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_spent(self, obj):
        total = Expense.objects.filter(
            user=obj.user,
            category=obj.category,
            date__month=obj.month,
            date__year=obj.year,
        ).aggregate(total=Sum('amount'))['total'] or 0
        return float(total)

    def get_remaining(self, obj):
        spent = self.get_spent(obj)
        return float(obj.limit) - spent

    def get_percentage_used(self, obj):
        spent = self.get_spent(obj)
        if obj.limit > 0:
            return round((spent / float(obj.limit)) * 100, 1)
        return 0

    def validate(self, attrs):
        """Ensure no duplicate budget for same user/category/month/year."""
        request = self.context.get('request')
        if request:
            existing = Budget.objects.filter(
                user=request.user,
                category=attrs.get('category'),
                month=attrs.get('month'),
                year=attrs.get('year'),
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise serializers.ValidationError(
                    'A budget for this category and month already exists.'
                )
        return attrs


class DashboardSerializer(serializers.Serializer):
    """Serializer for dashboard summary data."""
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_savings = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    recent_expenses = ExpenseSerializer(many=True)
    budget_overview = BudgetSerializer(many=True)
    expenses_by_category = serializers.ListField()


# ===== KHATABOOK (Ledger) SERIALIZERS =====

from .models import Contact, LedgerEntry


class ContactSerializer(serializers.ModelSerializer):
    """Serializer for contacts (people you lend/borrow money)."""
    balance = serializers.SerializerMethodField()
    total_gave = serializers.SerializerMethodField()
    total_got = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = ('id', 'name', 'phone', 'notes', 'balance', 'total_gave', 'total_got', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_total_gave(self, obj):
        """Total money you gave to this contact."""
        total = obj.entries.filter(transaction_type='gave').aggregate(t=Sum('amount'))['t'] or 0
        return float(total)

    def get_total_got(self, obj):
        """Total money you got back from this contact."""
        total = obj.entries.filter(transaction_type='got').aggregate(t=Sum('amount'))['t'] or 0
        return float(total)

    def get_balance(self, obj):
        """
        Positive = they owe you money
        Negative = you owe them money
        """
        gave = self.get_total_gave(obj)
        got = self.get_total_got(obj)
        return gave - got

    def validate_phone(self, value):
        """Check phone uniqueness for this user."""
        request = self.context.get('request')
        if request:
            existing = Contact.objects.filter(user=request.user, phone=value)
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise serializers.ValidationError("You already have a contact with this phone number.")
        return value


class LedgerEntrySerializer(serializers.ModelSerializer):
    """Serializer for ledger entries (gave/got transactions)."""
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    contact_phone = serializers.CharField(source='contact.phone', read_only=True)

    class Meta:
        model = LedgerEntry
        fields = (
            'id', 'contact', 'contact_name', 'contact_phone',
            'amount', 'transaction_type', 'date', 'description',
            'notify_sent', 'created_at'
        )
        read_only_fields = ('id', 'notify_sent', 'created_at')

    def validate_contact(self, value):
        """Ensure the contact belongs to the current user."""
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError("This contact does not belong to you.")
        return value
