from django.db import models
from django.conf import settings
import math


class SavingsGoal(models.Model):
    """
    Model representing a financial savings goal for a user.
    Tracks progress toward a target amount and calculates required monthly savings.
    """
    user           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='goals')
    goal_name      = models.CharField(max_length=150)
    target_amount  = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline       = models.DateField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def get_progress_percent(self):
        """
        Calculates the current progress toward the goal as a percentage.
        Returns a value capped at 100%.
        """
        if self.target_amount == 0:
            return 0
        return min(round(float(self.current_amount / self.target_amount * 100), 1), 100)

    def get_remaining(self):
        """
        Returns the remaining amount required to reach the savings goal.
        """
        return max(self.target_amount - self.current_amount, 0)

    def get_monthly_savings_needed(self):
        """
        Estimates the amount a user needs to save monthly to reach the goal 
        by the specified deadline.
        """
        from django.utils import timezone
        import datetime
        if not self.deadline:
            return 0
        today = timezone.now().date()
        months = (self.deadline.year - today.year) * 12 + (self.deadline.month - today.month)
        if months <= 0:
            return float(self.get_remaining())
        return round(float(self.get_remaining()) / months, 2)

    def get_progress_color(self):
        """
        Determines the UI color indicator based on the current progress percentage.
        """
        pct = self.get_progress_percent()
        if pct >= 100:
            return 'success'
        elif pct >= 60:
            return 'primary'
        return 'warning'

    def __str__(self):
        return f"{self.goal_name} — {self.user}"