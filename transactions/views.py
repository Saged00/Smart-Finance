from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Income, Expense
from .forms  import TransactionForm, IncomeForm, ExpenseForm
from budgets.models import Budget


@login_required
def transaction_list_view(request):
    """Main transactions page — shows the Add Transaction form
    and a list of recent transactions below."""

    user_budgets = Budget.objects.filter(user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            kind        = form.cleaned_data['kind']
            amount      = form.cleaned_data['amount']
            category    = form.cleaned_data['category']
            description = form.cleaned_data['description']
            occurred_at = form.cleaned_data['occurred_at']

            if kind == 'income':
                Income.objects.create(
                    user=request.user,
                    amount=amount,
                    date=occurred_at.date(),
                    description=description,
                    source=category,
                )
            else:
                # Try to match category to a user budget
                budget = user_budgets.filter(category=category).first()
                expense = Expense(
                    user=request.user,
                    amount=amount,
                    date=occurred_at.date(),
                    description=description,
                    budget=budget,
                )
                expense.save()

            return redirect('transactions')
    else:
        form = TransactionForm(initial={'occurred_at': timezone.now()})

    # Gather recent transactions for the list
    incomes  = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    all_transactions = []
    for i in incomes:
        all_transactions.append({
            'type':        'income',
            'id':          i.pk,
            'description': i.description,
            'amount':      i.amount,
            'date':        i.date,
            'category':    i.get_source_display(),
            'created_at':  i.created_at,
        })
    for e in expenses:
        all_transactions.append({
            'type':        'expense',
            'id':          e.pk,
            'description': e.description,
            'amount':      e.amount,
            'date':        e.date,
            'category':    e.budget.category if e.budget else 'General',
            'created_at':  e.created_at,
        })

    all_transactions.sort(key=lambda x: (x['date'], x['created_at']), reverse=True)

    total_income  = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)

    # Budget categories for expense kind
    budget_categories = list(user_budgets.values_list('category', flat=True))

    return render(request, 'transactions/transaction_list.html', {
        'form':              form,
        'transactions':      all_transactions,
        'total_income':      total_income,
        'total_expense':     total_expense,
        'net_balance':       total_income - total_expense,
        'budget_categories': budget_categories,
        'user':              request.user,
    })


# ── Income CRUD ──────────────────────────────────────────────

@login_required
def income_create_view(request):
    form = IncomeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        income      = form.save(commit=False)
        income.user = request.user
        income.save()
        return redirect('transactions')
    return render(request, 'transactions/income_form.html', {
        'form': form, 'action': 'Add', 'user': request.user,
    })


@login_required
def income_edit_view(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    form   = IncomeForm(request.POST or None, instance=income)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('transactions')
    return render(request, 'transactions/income_form.html', {
        'form': form, 'action': 'Edit', 'user': request.user,
    })


@login_required
def income_delete_view(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    income.delete()
    return redirect('transactions')


# ── Expense CRUD ─────────────────────────────────────────────

@login_required
def expense_create_view(request):
    form = ExpenseForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        expense      = form.save(commit=False)
        expense.user = request.user
        expense.save()
        return redirect('transactions')
    return render(request, 'transactions/expense_form.html', {
        'form': form, 'action': 'Add', 'user': request.user,
    })


@login_required
def expense_edit_view(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    form    = ExpenseForm(request.POST or None, instance=expense, user=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('transactions')
    return render(request, 'transactions/expense_form.html', {
        'form': form, 'action': 'Edit', 'user': request.user,
    })


@login_required
def expense_delete_view(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    return redirect('transactions')
