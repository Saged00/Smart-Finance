from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SavingsGoal
from .forms  import SavingsGoalForm
from budgets.models import Budget


@login_required
def goals_view(request):
    goals = SavingsGoal.objects.filter(user=request.user)
    form  = SavingsGoalForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        goal      = form.save(commit=False)
        goal.user = request.user
        goal.save()
        return redirect('goals')

    return render(request, 'goals/savingGoals.html', {
        'goals': goals,
        'form':  form,
        'user':  request.user,
    })


@login_required
def goal_delete_view(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
    return redirect('goals')


@login_required
def reports_view(request):
    budgets = Budget.objects.filter(user=request.user)

    # بيانات للـ charts
    categories = [b.category        for b in budgets]
    spent      = [float(b.spent_amount)  for b in budgets]
    limits     = [float(b.budget_amount) for b in budgets]

    total_budget = sum(limits)
    total_spent  = sum(spent)

    return render(request, 'goals/Reports.html', {
        'user':         request.user,
        'budgets':      budgets,
        'categories':   categories,
        'spent':        spent,
        'limits':       limits,
        'total_budget': total_budget,
        'total_spent':  total_spent,
    })