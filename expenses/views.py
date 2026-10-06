from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CategoryForm, ExpenseForm, MonthlyIncomeForm, SignUpForm
from .models import Category, Expense, MonthlyIncome

DEFAULT_CATEGORIES = [
    ("Groceries", "🛒"),
    ("Housing", "🏠"),
    ("Transport", "🚇"),
    ("Health", "💊"),
    ("Shopping", "🛍️"),
    ("Entertainment", "🎬"),
    ("Other", "✨"),
]


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        Category.objects.bulk_create(
            [Category(owner=user, name=name, emoji=emoji) for name, emoji in DEFAULT_CATEGORIES]
        )
        login(request, user)
        return redirect("dashboard")
    return render(request, "registration/signup.html", {"form": form})


@login_required
def dashboard(request):
    today = timezone.localdate()
    month_expenses = Expense.objects.filter(owner=request.user, date__year=today.year, date__month=today.month)
    year_expenses = Expense.objects.filter(owner=request.user, date__year=today.year)
    spent_month = month_expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    spent_year = year_expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    income, _ = MonthlyIncome.objects.get_or_create(
        owner=request.user, year=today.year, month=today.month, defaults={"amount": Decimal("0.00")}
    )
    category_totals = list(
        Category.objects.filter(owner=request.user)
        .annotate(
            spent=Sum(
                "expenses__amount",
                filter=Q(expenses__owner=request.user, expenses__date__year=today.year, expenses__date__month=today.month),
            )
        )
        .order_by("name")
    )
    for category in category_totals:
        category.spent = category.spent or Decimal("0.00")
        category.share = (category.spent / spent_month * 100) if spent_month else 0

    return render(
        request,
        "expenses/dashboard.html",
        {
            "today": today,
            "spent_month": spent_month,
            "spent_year": spent_year,
            "income": income.amount,
            "remaining": income.amount - spent_month,
            "category_totals": category_totals,
            "recent_expenses": Expense.objects.filter(owner=request.user).select_related("category")[:6],
            "month_expense_count": month_expenses.count(),
        },
    )


@login_required
def expense_create(request):
    form = ExpenseForm(request.POST or None, owner=request.user)
    if request.method == "POST" and form.is_valid():
        expense = form.save(commit=False)
        expense.owner = request.user
        expense.save()
        messages.success(request, "Expense added.")
        return redirect("dashboard")
    return render(
        request,
        "expenses/expense_form.html",
        {"form": form, "title": "Add an expense", "has_categories": Category.objects.filter(owner=request.user).exists()},
    )


@login_required
def expense_list(request):
    expenses = Expense.objects.filter(owner=request.user).select_related("category")
    return render(request, "expenses/expense_list.html", {"expenses": expenses})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, owner=request.user)
    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense deleted.")
        return redirect("expense_list")
    return render(request, "expenses/expense_confirm_delete.html", {"expense": expense})


@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        category = form.save(commit=False)
        category.owner = request.user
        category.save()
        messages.success(request, "Category added.")
        return redirect("expense_create")
    return render(request, "expenses/category_form.html", {"form": form})


@login_required
def income_update(request):
    today = timezone.localdate()
    income, _ = MonthlyIncome.objects.get_or_create(
        owner=request.user, year=today.year, month=today.month, defaults={"amount": Decimal("0.00")}
    )
    form = MonthlyIncomeForm(request.POST or None, instance=income)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Monthly income saved.")
        return redirect("dashboard")
    return render(request, "expenses/income_form.html", {"form": form, "today": today})
