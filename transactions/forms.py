from django import forms
from .models import Income, Expense


class TransactionForm(forms.Form):
    """Unified form for creating both Income and Expense transactions."""

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
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be positive.")
        return amount


class IncomeForm(forms.ModelForm):
    class Meta:
        model  = Income
        fields = ['amount', 'date', 'description', 'payment_method', 'source']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be positive.")
        return amount


class ExpenseForm(forms.ModelForm):
    class Meta:
        model  = Expense
        fields = ['amount', 'date', 'description', 'payment_method', 'notes', 'budget']
        widgets = {
            'date':  forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['budget'].queryset = self.fields['budget'].queryset.filter(user=user)
        self.fields['budget'].required = False
        self.fields['notes'].required = False

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be positive.")
        return amount
