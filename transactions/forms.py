from django import forms
from .models import Income, Expense
from budgets.models import Budget


class TransactionForm(forms.Form):
    # Main transaction form

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
    category    = forms.CharField(max_length=100, required=False)
    description = forms.CharField(max_length=255)
    budget      = forms.ModelChoiceField(
        queryset=Budget.objects.none(), 
        required=True,
        error_messages={'required': 'You must select a budget for this transaction.'}
    )
    occurred_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    def __init__(self, *args, user=None, **kwargs):
    # Filter budgets by user
        super().__init__(*args, **kwargs)
        if user:
            self.fields['budget'].queryset = Budget.objects.filter(user=user)

    def clean_amount(self):
    # Validate amount
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be positive.")
        return amount


class IncomeForm(forms.ModelForm):
    # Income model form
    class Meta:
        model  = Income
        fields = ['amount', 'date', 'description', 'payment_method', 'source', 'budget']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, user=None, **kwargs):
    # Filter budgets
        super().__init__(*args, **kwargs)
        if user:
            self.fields['budget'].queryset = self.fields['budget'].queryset.filter(user=user)
        self.fields['budget'].required = False

    def clean_amount(self):
    # Validate amount
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be positive.")
        return amount


class ExpenseForm(forms.ModelForm):
    # Expense model form
    class Meta:
        model  = Expense
        fields = ['amount', 'date', 'description', 'payment_method', 'notes', 'budget']
        widgets = {
            'date':  forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
    # Filter budgets
        super().__init__(*args, **kwargs)
        if user:
            self.fields['budget'].queryset = self.fields['budget'].queryset.filter(user=user)
        self.fields['budget'].required = False
        self.fields['notes'].required = False

    def clean_amount(self):
    # Validate amount
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be positive.")
        return amount