"""
Views for expense management API.
All views are protected by JWT authentication and scoped to the current user.
"""
from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.utils import timezone

from .models import ExpenseCategory, Income, Expense, Saving, Budget
from .serializers import (
    ExpenseCategorySerializer, IncomeSerializer, ExpenseSerializer,
    SavingSerializer, BudgetSerializer,
)
from apps.core.permissions import IsOwner


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD for expense categories.

    GET    /api/v1/categories/       - List all categories
    POST   /api/v1/categories/       - Create category (admin only)
    GET    /api/v1/categories/{id}/  - Get category detail
    PUT    /api/v1/categories/{id}/  - Update category (admin only)
    DELETE /api/v1/categories/{id}/  - Delete category (admin only)
    """
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data})


class IncomeViewSet(viewsets.ModelViewSet):
    """
    CRUD for user income records.

    GET    /api/v1/incomes/       - List user's incomes
    POST   /api/v1/incomes/       - Create income
    GET    /api/v1/incomes/{id}/  - Get income detail
    PUT    /api/v1/incomes/{id}/  - Update income
    DELETE /api/v1/incomes/{id}/  - Delete income
    GET    /api/v1/incomes/summary/ - Get income summary
    """
    serializer_class = IncomeSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['date', 'source']
    ordering_fields = ['date', 'amount', 'created_at']

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Optional month/year filtering
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        if month and year:
            queryset = queryset.filter(date__month=int(month), date__year=int(year))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data})

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """GET /api/v1/incomes/summary/ - Total income for current month."""
        now = timezone.now()
        total = self.get_queryset().filter(
            date__month=now.month, date__year=now.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        return Response({'success': True, 'data': {'total_income': float(total), 'month': now.month, 'year': now.year}})


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    CRUD for user expense records.

    GET    /api/v1/expenses/       - List user's expenses
    POST   /api/v1/expenses/       - Create expense
    GET    /api/v1/expenses/{id}/  - Get expense detail
    PUT    /api/v1/expenses/{id}/  - Update expense
    DELETE /api/v1/expenses/{id}/  - Delete expense
    GET    /api/v1/expenses/summary/ - Get expense summary
    GET    /api/v1/expenses/by-category/ - Expenses grouped by category
    """
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['category', 'date']
    ordering_fields = ['date', 'amount', 'created_at']
    search_fields = ['description']

    def get_queryset(self):
        queryset = Expense.objects.filter(user=self.request.user)

        # Optional month/year filtering
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month and year:
            queryset = queryset.filter(date__month=int(month), date__year=int(year))

        # Date range filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """GET /api/v1/expenses/summary/ - Total expenses for current month."""
        now = timezone.now()
        total = Expense.objects.filter(
            user=request.user, date__month=now.month, date__year=now.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        return Response({'success': True, 'data': {'total_expenses': float(total), 'month': now.month, 'year': now.year}})

    @action(detail=False, methods=['get'], url_path='by-category')
    def by_category(self, request):
        """GET /api/v1/expenses/by-category/ - Expenses grouped by category."""
        now = timezone.now()
        month = request.query_params.get('month', now.month)
        year = request.query_params.get('year', now.year)

        data = Expense.objects.filter(
            user=request.user, date__month=int(month), date__year=int(year)
        ).values(
            'category__name', 'category__color', 'category__icon'
        ).annotate(
            total=Sum('amount')
        ).order_by('-total')

        result = [
            {
                'category': item['category__name'],
                'color': item['category__color'],
                'icon': item['category__icon'],
                'total': float(item['total']),
            }
            for item in data
        ]
        return Response({'success': True, 'data': result})


class SavingViewSet(viewsets.ModelViewSet):
    """
    CRUD for user savings records.

    GET    /api/v1/savings/       - List user's savings
    POST   /api/v1/savings/       - Create saving
    GET    /api/v1/savings/{id}/  - Get saving detail
    PUT    /api/v1/savings/{id}/  - Update saving
    DELETE /api/v1/savings/{id}/  - Delete saving
    GET    /api/v1/savings/summary/ - Get savings summary
    """
    serializer_class = SavingSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['date', 'goal']
    ordering_fields = ['date', 'amount', 'created_at']

    def get_queryset(self):
        return Saving.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """GET /api/v1/savings/summary/ - Total savings."""
        total = self.get_queryset().aggregate(total=Sum('amount'))['total'] or 0
        now = timezone.now()
        monthly = self.get_queryset().filter(
            date__month=now.month, date__year=now.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        return Response({
            'success': True,
            'data': {'total_savings': float(total), 'monthly_savings': float(monthly)}
        })


class BudgetViewSet(viewsets.ModelViewSet):
    """
    CRUD for user budget records.

    GET    /api/v1/budgets/       - List user's budgets
    POST   /api/v1/budgets/       - Create budget
    GET    /api/v1/budgets/{id}/  - Get budget detail
    PUT    /api/v1/budgets/{id}/  - Update budget
    DELETE /api/v1/budgets/{id}/  - Delete budget
    """
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'month', 'year']

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DashboardView(generics.GenericAPIView):
    """
    GET /api/v1/dashboard/
    Returns a summary of the user's financial data for the current month.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        month = int(request.query_params.get('month', now.month))
        year = int(request.query_params.get('year', now.year))

        total_income = Income.objects.filter(
            user=request.user, date__month=month, date__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_expenses = Expense.objects.filter(
            user=request.user, date__month=month, date__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_savings = Saving.objects.filter(
            user=request.user, date__month=month, date__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0

        balance = float(total_income) - float(total_expenses) - float(total_savings)

        # Recent expenses
        recent_expenses = Expense.objects.filter(
            user=request.user
        ).select_related('category')[:5]

        # Budget overview
        budgets = Budget.objects.filter(
            user=request.user, month=month, year=year
        ).select_related('category')

        # Expenses by category
        expenses_by_category = Expense.objects.filter(
            user=request.user, date__month=month, date__year=year
        ).values('category__name', 'category__color').annotate(
            total=Sum('amount')
        ).order_by('-total')

        return Response({
            'success': True,
            'data': {
                'month': month,
                'year': year,
                'total_income': float(total_income),
                'total_expenses': float(total_expenses),
                'total_savings': float(total_savings),
                'balance': balance,
                'recent_expenses': ExpenseSerializer(recent_expenses, many=True).data,
                'budget_overview': BudgetSerializer(budgets, many=True).data,
                'expenses_by_category': [
                    {
                        'category': item['category__name'],
                        'color': item['category__color'],
                        'total': float(item['total']),
                    }
                    for item in expenses_by_category
                ],
            }
        })


# ===== KHATABOOK (Ledger) VIEWS =====

from .models import Contact, LedgerEntry
from .serializers import ContactSerializer, LedgerEntrySerializer


class ContactViewSet(viewsets.ModelViewSet):
    """
    CRUD for contacts (people you lend/borrow money).

    GET    /api/v1/contacts/       - List contacts with balances
    POST   /api/v1/contacts/       - Add a new contact
    GET    /api/v1/contacts/{id}/  - Contact detail with balance
    PUT    /api/v1/contacts/{id}/  - Update contact
    DELETE /api/v1/contacts/{id}/  - Delete contact
    """
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'phone']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LedgerEntryViewSet(viewsets.ModelViewSet):
    """
    CRUD for ledger entries (gave/got transactions).

    GET    /api/v1/ledger/                - List all ledger entries
    POST   /api/v1/ledger/                - Create entry (gave or got)
    GET    /api/v1/ledger/{id}/           - Entry detail
    DELETE /api/v1/ledger/{id}/           - Delete entry
    GET    /api/v1/ledger/by-contact/     - Entries for a specific contact
    POST   /api/v1/ledger/send-reminder/  - Send payment reminder
    """
    serializer_class = LedgerEntrySerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['contact', 'transaction_type', 'date']
    ordering_fields = ['date', 'amount', 'created_at']

    def get_queryset(self):
        return LedgerEntry.objects.filter(user=self.request.user).select_related('contact')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='by-contact')
    def by_contact(self, request):
        """GET /api/v1/ledger/by-contact/?contact_id=1 - Get entries for a contact."""
        contact_id = request.query_params.get('contact_id')
        if not contact_id:
            return Response(
                {'success': False, 'error': {'message': 'contact_id query param is required.'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        entries = self.get_queryset().filter(contact_id=contact_id)
        serializer = self.get_serializer(entries, many=True)
        return Response({'success': True, 'data': serializer.data})

    @action(detail=False, methods=['post'], url_path='send-reminder')
    def send_reminder(self, request):
        """
        POST /api/v1/ledger/send-reminder/
        Body: { "contact_id": 1 }
        Generates an SMS link to send a payment reminder via default messaging app.
        """
        contact_id = request.data.get('contact_id')
        if not contact_id:
            return Response(
                {'success': False, 'error': {'message': 'contact_id is required.'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            contact = Contact.objects.get(id=contact_id, user=request.user)
        except Contact.DoesNotExist:
            return Response(
                {'success': False, 'error': {'message': 'Contact not found.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        # Calculate balance
        gave = LedgerEntry.objects.filter(
            user=request.user, contact=contact, transaction_type='gave'
        ).aggregate(t=Sum('amount'))['t'] or 0
        got = LedgerEntry.objects.filter(
            user=request.user, contact=contact, transaction_type='got'
        ).aggregate(t=Sum('amount'))['t'] or 0
        balance = float(gave) - float(got)

        if balance <= 0:
            return Response({
                'success': False,
                'error': {'message': f'{contact.name} does not owe you any money.'}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Generate SMS message
        sender_name = request.user.first_name or request.user.username
        message = (
            f"Hi {contact.name}, this is a reminder from {sender_name}. "
            f"You have a pending payment of Rs.{balance:,.2f}. "
            f"Please settle it at your earliest convenience. Thank you!"
        )
        phone = contact.phone.replace('+', '').replace(' ', '')

        # SMS link (opens default messaging app)
        import urllib.parse
        encoded_msg = urllib.parse.quote(message)
        sms_link = f"sms:{phone}?body={encoded_msg}"

        # WhatsApp link as alternative
        whatsapp_link = f"https://wa.me/{phone}?text={encoded_msg}"

        # Mark entries as notified
        LedgerEntry.objects.filter(
            user=request.user, contact=contact, transaction_type='gave', notify_sent=False
        ).update(notify_sent=True)

        return Response({
            'success': True,
            'data': {
                'contact_name': contact.name,
                'phone': contact.phone,
                'balance_owed': balance,
                'message': message,
                'sms_link': sms_link,
                'whatsapp_link': whatsapp_link,
            }
        })
