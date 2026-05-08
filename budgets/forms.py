from django import forms
from .models import Budget

class BudgetForm(forms.ModelForm):
    # Form for budgets
    class Meta:
        model  = Budget
        fields = ['category', 'budget_amount', 'start_date', 'end_date', 'alert_threshold']
        widgets = {
            'start_date':      forms.DateInput(attrs={'type': 'date'}),
            'end_date':        forms.DateInput(attrs={'type': 'date'}),
            'alert_threshold': forms.NumberInput(attrs={'min': 50, 'max': 100}),
        }

    def clean_budget_amount(self):
        # Validate amount
        amount = self.cleaned_data.get('budget_amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Budget amount must be positive.")
        return amount