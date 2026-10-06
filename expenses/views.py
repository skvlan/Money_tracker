from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.db.models.functions import ExtractMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _

from .forms import (
    CategoryDeleteForm,
    CategoryForm,
    ExpenseForm,
    GoalContributionForm,
    MonthlyIncomeForm,
    SavingsGoalForm,
    SignUpForm,
    UserPreferencesForm,
)
from .models import Category, Expense, GoalContribution, MonthlyIncome, SavingsGoal, UserPreferences

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
        UserPreferences.objects.create(user=user, currency=form.cleaned_data["currency"])
        Category.objects.bulk_create(
            [Category(owner=user, name=name, emoji=emoji) for name, emoji in DEFAULT_CATEGORIES]
        )
        login(request, user)
        return redirect("dashboard")
    return render(request, "registration/signup.html", {"form": form})


@login_required
def dashboard(request):
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)
    current_month_start = today.replace(day=1)
    month_expenses = Expense.objects.filter(
        owner=request.user, date__gte=current_month_start, date__lte=today
    )
    previous_month_date = today.replace(day=1) - timedelta(days=1)
    previous_month_start = previous_month_date.replace(day=1)
    previous_month_end = previous_month_date.replace(day=min(today.day, previous_month_date.day))
    previous_month_expenses = Expense.objects.filter(
        owner=request.user, date__gte=previous_month_start, date__lte=previous_month_end
    )
    year_expenses = Expense.objects.filter(owner=request.user, date__year=today.year, date__lte=today)
    spent_month = month_expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    goal_contributions_month = GoalContribution.objects.filter(
        goal__owner=request.user, date__gte=current_month_start, date__lte=today
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    spent_previous_month = previous_month_expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    spent_year = year_expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    if spent_previous_month:
        total_change_status = "up" if spent_month > spent_previous_month else "down" if spent_month < spent_previous_month else "same"
        total_change_percent = abs((spent_month - spent_previous_month) / spent_previous_month * 100)
    else:
        total_change_status = "new" if spent_month else "none"
        total_change_percent = Decimal("0.00")
    income, _created = MonthlyIncome.objects.get_or_create(
        owner=request.user, year=today.year, month=today.month, defaults={"amount": Decimal("0.00")}
    )
    category_totals = list(
        Category.objects.filter(owner=request.user)
        .annotate(
            spent=Sum(
                "expenses__amount",
                filter=Q(
                    expenses__owner=request.user,
                    expenses__date__gte=current_month_start,
                    expenses__date__lte=today,
                ),
            ),
            previous_spent=Sum(
                "expenses__amount",
                filter=Q(
                    expenses__owner=request.user,
                    expenses__date__gte=previous_month_start,
                    expenses__date__lte=previous_month_end,
                ),
            ),
        )
        .order_by("name")
    )
    for category in category_totals:
        category.spent = category.spent or Decimal("0.00")
        category.previous_spent = category.previous_spent or Decimal("0.00")
        category.share = (category.spent / spent_month * 100) if spent_month else 0
        if category.previous_spent:
            category.change_status = "up" if category.spent > category.previous_spent else "down" if category.spent < category.previous_spent else "same"
            category.change_percent = abs((category.spent - category.previous_spent) / category.previous_spent * 100)
        else:
            category.change_status = "new" if category.spent else "none"
            category.change_percent = Decimal("0.00")

    return render(
        request,
        "expenses/dashboard.html",
        {
            "today": today,
            "yesterday": yesterday,
            "spent_month": spent_month,
            "spent_previous_month": spent_previous_month,
            "total_change_status": total_change_status,
            "total_change_percent": total_change_percent,
            "spent_year": spent_year,
            "income": income.amount,
            "goal_contributions_month": goal_contributions_month,
            "remaining": income.amount - spent_month - goal_contributions_month,
            "category_totals": category_totals,
            "recent_expenses": Expense.objects.filter(owner=request.user).select_related("category")[:6],
            "month_expense_count": month_expenses.count(),
        },
    )


@login_required
def yearly_report(request):
    today = timezone.localdate()
    preferences, _created = UserPreferences.objects.get_or_create(user=request.user)
    current_month_income, _income_created = MonthlyIncome.objects.get_or_create(
        owner=request.user,
        year=today.year,
        month=today.month,
        defaults={"amount": Decimal("0.00")},
    )
    current_month_spent = Expense.objects.filter(
        owner=request.user,
        date__gte=today.replace(day=1),
        date__lte=today,
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    current_month_goal_savings = GoalContribution.objects.filter(
        goal__owner=request.user,
        date__gte=today.replace(day=1),
        date__lte=today,
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    years_with_expenses = Expense.objects.filter(owner=request.user).dates("date", "year", order="DESC")
    available_years = sorted({today.year, *(item.year for item in years_with_expenses)}, reverse=True)
    try:
        selected_year = int(request.GET.get("year", today.year))
    except (TypeError, ValueError):
        selected_year = today.year
    if selected_year not in available_years:
        selected_year = today.year

    expenses = Expense.objects.filter(owner=request.user, date__year=selected_year)
    if selected_year == today.year:
        expenses = expenses.filter(date__lte=today)
    total = expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    active_month_count = expenses.dates("date", "month", order="ASC").count()
    average = total / active_month_count if active_month_count else Decimal("0.00")
    month_totals = {
        row["month"]: row["total"]
        for row in expenses.annotate(month=ExtractMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"))
    }
    month_names = [
        (_("January"), _("Jan")), (_("February"), _("Feb")), (_("March"), _("Mar")), (_("April"), _("Apr")),
        (_("May"), _("May")), (_("June"), _("Jun")), (_("July"), _("Jul")), (_("August"), _("Aug")),
        (_("September"), _("Sep")), (_("October"), _("Oct")), (_("November"), _("Nov")), (_("December"), _("Dec")),
    ]
    peak_month = max(month_totals.values(), default=Decimal("0.00"))
    monthly_totals = []
    for month_number, (full_name, short_name) in enumerate(month_names, start=1):
        amount = month_totals.get(month_number, Decimal("0.00"))
        height = (amount / peak_month * 100) if peak_month else 0
        monthly_totals.append(
            {"name": full_name, "short": short_name, "total": amount, "height": height}
        )

    category_totals = list(
        Category.objects.filter(owner=request.user)
        .annotate(spent=Sum("expenses__amount", filter=Q(expenses__owner=request.user, expenses__date__year=selected_year)))
        .order_by("-spent", "name")
    )
    for category in category_totals:
        category.spent = category.spent or Decimal("0.00")
        category.share = (category.spent / total * 100) if total else 0

    savings_goals = list(
        SavingsGoal.objects.filter(owner=request.user)
        .annotate(saved_amount=Sum("contributions__amount"))
    )
    for goal in savings_goals:
        goal.saved_amount = goal.saved_amount or Decimal("0.00")
        goal.amount_left = max(Decimal("0.00"), goal.target_amount - goal.saved_amount)
        goal.progress = min(100, goal.saved_amount / goal.target_amount * 100)

    return render(
        request,
        "expenses/yearly_report.html",
        {
            "current_month": today,
            "current_month_income": current_month_income.amount,
            "current_month_spent": current_month_spent,
            "current_month_goal_savings": current_month_goal_savings,
            "current_month_remaining": current_month_income.amount - current_month_spent - current_month_goal_savings,
            "savings_goals": savings_goals,
            "currency_code": preferences.currency,
            "selected_year": selected_year,
            "available_years": available_years,
            "total": total,
            "average": average,
            "active_month_count": active_month_count,
            "monthly_totals": monthly_totals,
            "category_totals": category_totals,
        },
    )


@login_required
def expense_create(request):
    preferences, _created = UserPreferences.objects.get_or_create(user=request.user)
    form = ExpenseForm(request.POST or None, owner=request.user, currency_code=preferences.currency)
    if request.method == "POST" and form.is_valid():
        expense = form.save(commit=False)
        expense.owner = request.user
        expense.save()
        messages.success(request, _("Expense added."))
        return redirect("dashboard")
    return render(
        request,
        "expenses/expense_form.html",
        {
            "form": form,
            "title": _("Add an expense"),
            "submit_text": _("Save expense"),
            "has_categories": Category.objects.filter(owner=request.user).exists(),
        },
    )


@login_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk, owner=request.user)
    preferences, _created = UserPreferences.objects.get_or_create(user=request.user)
    form = ExpenseForm(
        request.POST or None,
        instance=expense,
        owner=request.user,
        currency_code=preferences.currency,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Expense updated."))
        return redirect("expense_list")
    return render(
        request,
        "expenses/expense_form.html",
        {"form": form, "title": _("Edit expense"), "submit_text": _("Save changes"), "has_categories": True},
    )


@login_required
def expense_list(request):
    expenses = Expense.objects.filter(owner=request.user).select_related("category")
    return render(
        request,
        "expenses/expense_list.html",
        {"expenses": expenses, "today": timezone.localdate(), "yesterday": timezone.localdate() - timedelta(days=1)},
    )


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, owner=request.user)
    if request.method == "POST":
        expense.delete()
        messages.success(request, _("Expense deleted."))
        return redirect("expense_list")
    return render(request, "expenses/expense_confirm_delete.html", {"expense": expense})


@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        category = form.save(commit=False)
        category.owner = request.user
        category.save()
        messages.success(request, _("Category added."))
        return redirect("expense_create")
    return render(
        request,
        "expenses/category_form.html",
        {"form": form, "title": _("New category"), "submit_text": _("Save category")},
    )


@login_required
def category_list(request):
    categories = Category.objects.filter(owner=request.user).annotate(expense_count=Count("expenses"))
    return render(request, "expenses/category_list.html", {"categories": categories})


@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk, owner=request.user)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Category updated."))
        return redirect("category_list")
    return render(
        request,
        "expenses/category_form.html",
        {"form": form, "title": _("Edit category"), "submit_text": _("Save changes")},
    )


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, owner=request.user)
    expense_count = Expense.objects.filter(owner=request.user, category=category).count()
    form = CategoryDeleteForm(
        request.POST or None,
        owner=request.user,
        category=category,
        expense_count=expense_count,
    )
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            category = get_object_or_404(
                Category.objects.select_for_update(), pk=pk, owner=request.user
            )
            expenses = Expense.objects.filter(owner=request.user, category=category)
            if expenses.exists():
                expenses.update(category=form.cleaned_data["replacement"])
            category.delete()
        if expense_count:
            messages.success(request, _("Category deleted. Its expenses were kept in the replacement category."))
        else:
            messages.success(request, _("Category deleted."))
        return redirect("category_list")
    return render(
        request,
        "expenses/category_confirm_delete.html",
        {"category": category, "expense_count": expense_count, "form": form},
    )


@login_required
def income_update(request):
    today = timezone.localdate()
    income, _created = MonthlyIncome.objects.get_or_create(
        owner=request.user, year=today.year, month=today.month, defaults={"amount": Decimal("0.00")}
    )
    preferences, _preferences_created = UserPreferences.objects.get_or_create(user=request.user)
    form = MonthlyIncomeForm(request.POST or None, instance=income, currency_code=preferences.currency)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Monthly income saved."))
        return redirect("dashboard")
    return render(request, "expenses/income_form.html", {"form": form, "today": today})


@login_required
def currency_settings(request):
    preferences, _created = UserPreferences.objects.get_or_create(user=request.user)
    form = UserPreferencesForm(request.POST or None, instance=preferences)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Settings saved."))
        return redirect("dashboard")
    return render(request, "expenses/currency_settings.html", {"form": form})


@login_required
def savings_goal_create(request):
    preferences, _created = UserPreferences.objects.get_or_create(user=request.user)
    form = SavingsGoalForm(
        request.POST or None,
        currency_code=preferences.currency,
    )
    if request.method == "POST" and form.is_valid():
        goal = form.save(commit=False)
        goal.owner = request.user
        goal.save()
        messages.success(request, _("Savings goal created."))
        return redirect("yearly_report")
    return render(
        request,
        "expenses/savings_goal_form.html",
        {
            "form": form,
            "title": _("Create a savings goal"),
            "submit_text": _("Create goal"),
            "description": _("Choose something to save for and set your target amount."),
        },
    )


@login_required
def savings_goal_contribute(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, owner=request.user)
    preferences, _created = UserPreferences.objects.get_or_create(user=request.user)
    form = GoalContributionForm(request.POST or None, currency_code=preferences.currency)
    if request.method == "POST" and form.is_valid():
        contribution = form.save(commit=False)
        contribution.goal = goal
        contribution.save()
        messages.success(request, _("Savings added to %(goal)s.") % {"goal": goal.name})
        return redirect("yearly_report")
    return render(
        request,
        "expenses/savings_goal_form.html",
        {
            "form": form,
            "title": _("Add savings to %(goal)s") % {"goal": goal.name},
            "submit_text": _("Add savings"),
            "description": _("This amount will be set aside from your free monthly balance."),
        },
    )


@login_required
def savings_goal_update(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, owner=request.user)
    preferences, _created = UserPreferences.objects.get_or_create(user=request.user)
    form = SavingsGoalForm(request.POST or None, instance=goal, currency_code=preferences.currency)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Savings goal updated."))
        return redirect("yearly_report")
    return render(
        request,
        "expenses/savings_goal_form.html",
        {
            "form": form,
            "title": _("Edit savings goal"),
            "submit_text": _("Save changes"),
            "description": _("Update the goal name or target. Recorded contributions will stay unchanged."),
        },
    )


@login_required
def savings_goal_delete(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, owner=request.user)
    saved_amount = goal.contributions.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    today = timezone.localdate()
    month_saved_amount = goal.contributions.filter(
        date__gte=today.replace(day=1), date__lte=today
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    if request.method == "POST":
        goal.delete()
        messages.success(request, _("Savings goal and its recorded contributions were deleted."))
        return redirect("yearly_report")
    return render(
        request,
        "expenses/savings_goal_confirm_delete.html",
        {"goal": goal, "saved_amount": saved_amount, "month_saved_amount": month_saved_amount},
    )
