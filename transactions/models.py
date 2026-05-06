from django.db import models
from django.conf import settings


class Transaction(models.Model):
    """
    Abstract base class for all financial activities.
    
    Provides shared attributes including amount, date, description, and 
    payment method. This class is not instantiated directly but serves 
    as a template for Income and Expense models.
    """

    PAYMENT_CHOICES = [
        ('cash',        'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card',  'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('e_wallet',    'E-Wallet'),
        ('other',       'Other'),
    ]

    user           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount         = models.DecimalField(max_digits=10, decimal_places=2)
    date           = models.DateField()
    description    = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['-date', '-created_at']

    def get_payment_display_text(self):
        """Returns the human-readable label for the selected payment method."""
        return dict(self.PAYMENT_CHOICES).get(self.payment_method, self.payment_method)

    def __str__(self):
        return f"{self.description} — ${self.amount}"


class Income(Transaction):
    """
    Concrete class for recording income transactions.
    
    Inherits from Transaction and includes a specific source (e.g., Salary, Freelance)
    to categorize incoming funds.
    """

    SOURCE_CHOICES = [
        ('salary',      'Salary'),
        ('freelance',   'Freelance'),
        ('investment',  'Investment'),
        ('gift',        'Gift'),
        ('bonus',       'Bonus'),
        ('other',       'Other'),
    ]

    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='salary')

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"[Income] {self.description} — ${self.amount}"


class Expense(Transaction):
    """
    Concrete class for recording expense transactions.
    
    Links to the Budget model to track spending progress. Overrides save 
    and delete methods to maintain real-time synchronization with 
    associated budget limits.
    """

    notes  = models.TextField(blank=True, default='')
    budget = models.ForeignKey(
        'budgets.Budget',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
    )

    class Meta:
        ordering = ['-date', '-created_at']

    def save(self, *args, **kwargs):
        """
        Saves the expense and synchronizes the associated budget.
        
        Calculates the difference if the amount is updated and updates 
        the 'spent_amount' in the related Budget instance.
        """
        is_new = self.pk is None
        old_amount = None
        if not is_new:
            old = Expense.objects.filter(pk=self.pk).first()
            if old:
                old_amount = old.amount
        super().save(*args, **kwargs)
        
        if self.budget:
            if is_new:
                self.budget.update_spent(self.amount)
            elif old_amount is not None and old_amount != self.amount:
                diff = self.amount - old_amount
                self.budget.update_spent(diff)

    def delete(self, *args, **kwargs):
        """
        Removes the expense and reverts the spent amount in the associated budget.
        
        Ensures the budget's spent_amount remains accurate and updates its status.
        """
        if self.budget:
            self.budget.spent_amount -= self.amount
            if self.budget.spent_amount < 0:
                self.budget.spent_amount = 0
            self.budget.status = self.budget.get_status()
            self.budget.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"[Expense] {self.description} — ${self.amount}"