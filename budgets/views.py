from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from .models  import Budget, BudgetAlert
from .forms   import BudgetForm
from transactions.models import Income, Expense


@login_required
def dashboard_view(request):
    # Main dashboard
    budgets = Budget.objects.filter(user=request.user)
    alerts  = BudgetAlert.objects.filter(budget__user=request.user).order_by('-triggered_at')[:5]

    # Transaction stats
    now = timezone.now()
    total_income  = Income.objects.filter(user=request.user).aggregate(s=Sum('amount'))['s'] or 0
    total_expense = Expense.objects.filter(user=request.user).aggregate(s=Sum('amount'))['s'] or 0
    total_balance = total_income - total_expense

    month_income  = Income.objects.filter(user=request.user, date__year=now.year, date__month=now.month).aggregate(s=Sum('amount'))['s'] or 0
    month_expense = Expense.objects.filter(user=request.user, date__year=now.year, date__month=now.month).aggregate(s=Sum('amount'))['s'] or 0

    return render(request, 'budgets/dashboard.html', {
        'budgets':       budgets,
        'alerts':        alerts,
        'user':          request.user,
        'total_balance': total_balance,
        'month_income':  month_income,
        'month_expense': month_expense,
        'current_month': now.strftime('%B %Y').upper(),
    })


@login_required
def budget_list_view(request):
    # List budgets
    budgets = Budget.objects.filter(user=request.user)
    return render(request, 'budgets/budget_list.html', {'budgets': budgets})


@login_required
def budget_create_view(request):
    # Create budget
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
    # Edit budget
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
    # Delete budget
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        budget.delete()
    return redirect('budget-list')


@login_required
def budget_alerts_view(request):
    # View alerts
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