from django import forms
from .models import Income, Expense


class TransactionForm(forms.Form):
    """
    A unified non-model form used for creating both Income and Expense transactions.
    
    This form provides a 'kind' field to switch between transaction types 
    and handles shared fields like amount, category, and date.
    """

    KIND_CHOICES = [
        ('',        '---------'),
        ('income',  'Income'),
        ('expense', 'Expense'),
    ]

    INCOME_CATEGORIES = [
        ('',           '---------'),
        ('salary',     'Salary'),
        ('freelance',  'Freelance'),
        ('investment', 'Investment'),
        ('gift',       'Gift'),
        ('bonus',      'Bonus'),
        ('other',      'Other'),
    ]

    kind        = forms.ChoiceField(choices=KIND_CHOICES)
    amount      = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    category    = forms.CharField(max_length=100)
    description = forms.CharField(max_length=255)
    occurred_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    def clean_amount(self):
        """Validates that the transaction amount is a positive value."""
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be positive.")
        return amount


class IncomeForm(forms.ModelForm):
    """
    ModelForm for creating and updating Income records.
    
    Maps directly to the Income model and includes validation for the amount field.
    """
    class Meta:
        model  = Income
        fields = ['amount', 'date', 'description', 'payment_method', 'source']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_amount(self):
        """Ensures the income amount is greater than zero."""
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be positive.")
        return amount


class ExpenseForm(forms.ModelForm):
    """
    ModelForm for managing Expense records.
    
    Includes logic to filter the available budgets to only those belonging 
    to the current user. Ensures expenses are correctly linked to user-specific 
    financial limits.
    """
    class Meta:
        model  = Expense
        fields = ['amount', 'date', 'description', 'payment_method', 'notes', 'budget']
        widgets = {
            'date':  forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        """
        Initializes the form and filters the budget queryset based on the 
        provided user to ensure data isolation.
        """
        super().__init__(*args, **kwargs)
        if user:
            self.fields['budget'].queryset = self.fields['budget'].queryset.filter(user=user)
        self.fields['budget'].required = False
        self.fields['notes'].required = False

    def clean_amount(self):
        """Validates that the expense amount is a positive value."""
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be positive.")
        return amount