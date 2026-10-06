from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/add/", views.expense_create, name="expense_create"),
    path("expenses/<int:pk>/delete/", views.expense_delete, name="expense_delete"),
    path("categories/add/", views.category_create, name="category_create"),
    path("income/", views.income_update, name="income_update"),
    path("accounts/signup/", views.signup, name="signup"),
]
