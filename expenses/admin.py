from django.contrib import admin

from .models import Category, Expense, MonthlyIncome


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
