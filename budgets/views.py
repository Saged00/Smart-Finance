from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models  import Budget, BudgetAlert
from .forms   import BudgetForm


@login_required
def dashboard_view(request):
    """
    عرض لوحة التحكم الرئيسية (Dashboard).
    يتم استرجاع ميزانيات المستخدم الحالي وآخر 5 تنبيهات تم إنشاؤها.
    """
    budgets = Budget.objects.filter(user=request.user)
    alerts  = BudgetAlert.objects.filter(budget__user=request.user).order_by('-triggered_at')[:5]
    return render(request, 'budgets/dashboard.html', {
        'budgets': budgets,
        'alerts':  alerts,
        'user':    request.user,
    })


@login_required
def budget_list_view(request):
    """
    عرض قائمة شاملة بجميع ميزانيات المستخدم الحالي.
    """
    budgets = Budget.objects.filter(user=request.user)
    return render(request, 'budgets/budget_list.html', {'budgets': budgets})


@login_required
def budget_create_view(request):
    """
    إنشاء ميزانية جديدة.
    يتم التحقق من صحة البيانات المسجلة، ربطها بالمستخدم، وتحديد حالتها (Status).
    """
    form = BudgetForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        budget      = form.save(commit=False)
        budget.user = request.user
        budget.status = budget.get_status()
        budget.save()
        return redirect('budget-list')
    return render(request, 'budgets/budget_form.html', {'form': form, 'action': 'Create'})


@login_required
def budget_edit_view(request, pk):
    """
    تعديل ميزانية موجودة مسبقاً.
    Args:
        pk: الرقم التعريفي للميزانية المراد تعديلها.
    """
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    form   = BudgetForm(request.POST or None, instance=budget)
    if request.method == 'POST' and form.is_valid():
        b = form.save(commit=False)
        b.status = b.get_status()
        b.save()
        return redirect('budget-list')
    return render(request, 'budgets/budget_form.html', {'form': form, 'action': 'Edit'})


@login_required
def budget_delete_view(request, pk):
    """
    حذف ميزانية محددة من النظام.
    Args:
        pk: الرقم التعريفي للميزانية.
    """
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        budget.delete()
    return redirect('budget-list')


@login_required
def budget_alerts_view(request):
    """
    عرض صفحة التنبيهات مع ملخص مالي.
    يتم حساب إجمالي الميزانيات وإجمالي المصروفات لعرضها في صفحة التنبيهات.
    """
    alerts  = BudgetAlert.objects.filter(budget__user=request.user).order_by('-triggered_at')
    budgets = Budget.objects.filter(user=request.user)
    total_budget = sum(b.budget_amount for b in budgets)
    total_spent  = sum(b.spent_amount  for b in budgets)
    return render(request, 'budgets/budgetAlert.html', {
        'alerts':       alerts,
        'budgets':      budgets,
        'total_budget': total_budget,
        'total_spent':  total_spent,
    })