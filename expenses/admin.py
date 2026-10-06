from django.contrib import admin

from .models import Category, Expense, GoalContribution, MonthlyIncome, SavingsGoal, UserPreferences


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "emoji")
    search_fields = ("name", "owner__username")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("description", "amount", "category", "owner", "date")
    list_filter = ("date", "category")
    search_fields = ("description", "owner__username")


@admin.register(MonthlyIncome)
class MonthlyIncomeAdmin(admin.ModelAdmin):
    list_display = ("owner", "year", "month", "amount")
    list_filter = ("year", "month")


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ("user", "currency")


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "target_amount", "created_at")
    search_fields = ("name", "owner__username")


@admin.register(GoalContribution)
class GoalContributionAdmin(admin.ModelAdmin):
    list_display = ("goal", "amount", "date")
    list_filter = ("date",)
