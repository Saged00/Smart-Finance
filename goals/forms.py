from django import forms
from .models import SavingsGoal


class SavingsGoalForm(forms.ModelForm):
    """
    SavingsGoalForm handles the input and validation for users' financial goals.
    It provides a user-friendly interface for setting target amounts and deadlines.
    """
    class Meta:
        model  = SavingsGoal
        fields = ['goal_name', 'target_amount', 'current_amount', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_target_amount(self):
        """
        Validates that the target amount is a positive number.
        Ensures users cannot set a goal with zero or negative financial targets.
        """
        amount = self.cleaned_data.get('target_amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Target amount must be positive.")
        return amount

    def clean_deadline(self):
        """
        Validates the deadline date.
        Ensures that the selected deadline is in the future relative to the current date.
        """
        from django.utils import timezone
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline <= timezone.now().date():
            raise forms.ValidationError("Deadline must be a future date.")
        return deadline