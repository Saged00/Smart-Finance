from django.db import models
from django.conf import settings

class Budget(models.Model):
    """
    Class: Budget Model
    Description: يمثل ميزانية محددة لمستخدم معين في فئة (Category) معينة.
    يتبع هذا الموديل مبدأ التتبع المالي ويحدد حالة الصرف (On Track, Near Limit, Exceeded).
    """
    STATUS_ON_TRACK   = 'on_track'
    STATUS_NEAR_LIMIT = 'near_limit'
    STATUS_EXCEEDED   = 'exceeded'
    STATUS_CHOICES = [
        (STATUS_ON_TRACK,   'On Track'),
        (STATUS_NEAR_LIMIT, 'Near Limit'),
        (STATUS_EXCEEDED,   'Exceeded'),
    ]

    user            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    category        = models.CharField(max_length=100)
    budget_amount   = models.DecimalField(max_digits=10, decimal_places=2)
    spent_amount    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date      = models.DateField()
    end_date        = models.DateField()
    alert_threshold = models.IntegerField(default=80)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ON_TRACK)

    def get_percentage_used(self):
        """
        يحسب النسبة المئوية لما تم صرفه من الميزانية الكلية.
        """
        if self.budget_amount == 0:
            return 0
        return float(self.spent_amount / self.budget_amount * 100)

    def get_remaining(self):
        """
        يسترجع المبلغ المتبقي في الميزانية (الفرق بين المحدد والمصروف).
        """
        return self.budget_amount - self.spent_amount

    def get_status(self):
        """
        يحدد حالة الميزانية الحالية بناءً على نسبة الصرف مقارنة بـ alert_threshold.
        """
        pct = self.get_percentage_used()
        if pct >= 100:
            return self.STATUS_EXCEEDED
        elif pct >= self.alert_threshold:
            return self.STATUS_NEAR_LIMIT
        return self.STATUS_ON_TRACK

    def update_spent(self, amount):
        """
        تحديث المبلغ المصروف، إعادة تقييم الحالة، وتشغيل تنبيهات الميزانية.
        Traceability: هذا التابع يربط بين Budget و BudgetAlert.
        """
        self.spent_amount += amount
        self.status = self.get_status()
        self.save()
        BudgetAlert.check_and_fire(self)

    def __str__(self):
        return f"{self.category} — {self.user}"


class BudgetAlert(models.Model):
    """
    Class: BudgetAlert Model
    Description: يقوم بتخزين التنبيهات الناتجة عن تخطي الميزانية أو الاقتراب من الحد المسموح.
    """
    budget       = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='alerts')
    triggered_at = models.DateTimeField(auto_now_add=True)
    message      = models.TextField()

    @classmethod
    def check_and_fire(cls, budget):
        """
        دالة منطقية تقوم بفحص حالة الميزانية وإنشاء سجل تنبيه جديد إذا لزم الأمر.
        Args:
            budget: كائن من نوع Budget المراد فصحه.
        """
        status = budget.get_status()
        if status == Budget.STATUS_NEAR_LIMIT:
            msg = f"{budget.category}: {budget.get_percentage_used():.0f}% used — near limit."
        elif status == Budget.STATUS_EXCEEDED:
            msg = f"{budget.category}: Budget exceeded by ${abs(budget.get_remaining())}."
        else:
            return
        cls.objects.create(budget=budget, message=msg)

    def __str__(self):
        return self.message