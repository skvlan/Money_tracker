from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Category, Expense, MonthlyIncome


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ("amount", "description", "category", "date")
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}
        labels = {
            "amount": "Amount (€)",
            "description": "What did you buy?",
            "category": "Category",
            "date": "Purchase date",
        }

    def __init__(self, *args, owner, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.filter(owner=owner)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "emoji")
        labels = {"name": "Name", "emoji": "Icon"}
        widgets = {"emoji": forms.TextInput(attrs={"maxlength": 8, "placeholder": "For example, 🛒"})}


class MonthlyIncomeForm(forms.ModelForm):
    class Meta:
        model = MonthlyIncome
        fields = ("amount",)
        labels = {"amount": "Income this month (€)"}
