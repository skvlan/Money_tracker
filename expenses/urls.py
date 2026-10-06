from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("reports/", views.yearly_report, name="yearly_report"),
    path("goals/add/", views.savings_goal_create, name="savings_goal_create"),
    path("goals/<int:pk>/contribute/", views.savings_goal_contribute, name="savings_goal_contribute"),
    path("goals/<int:pk>/edit/", views.savings_goal_update, name="savings_goal_update"),
    path("goals/<int:pk>/delete/", views.savings_goal_delete, name="savings_goal_delete"),
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/add/", views.expense_create, name="expense_create"),
    path("expenses/<int:pk>/edit/", views.expense_update, name="expense_update"),
    path("expenses/<int:pk>/delete/", views.expense_delete, name="expense_delete"),
    path("categories/add/", views.category_create, name="category_create"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/<int:pk>/edit/", views.category_update, name="category_update"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
    path("income/", views.income_update, name="income_update"),
    path("settings/currency/", views.currency_settings, name="currency_settings"),
    path("accounts/signup/", views.signup, name="signup"),
]
