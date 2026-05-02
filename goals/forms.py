from django import forms
from .models import SavingsGoal


class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model  = SavingsGoal
        fields = ['goal_name', 'target_amount', 'current_amount', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_target_amount(self):
        amount = self.cleaned_data.get('target_amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Target amount must be positive.")
        return amount

    def clean_deadline(self):
        from django.utils import timezone
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline <= timezone.now().date():
            raise forms.ValidationError("Deadline must be a future date.")
        return deadline