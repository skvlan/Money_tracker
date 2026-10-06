from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .currencies import CURRENCY_CHOICES
from .models import Category, Expense, GoalContribution, MonthlyIncome, SavingsGoal, UserPreferences


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False, label=_("Email address"))
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES, label=_("Preferred currency"))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(("username", "email", "currency", "password1", "password2"))


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ("amount", "description", "category", "date")
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}
        labels = {
            "amount": _("Amount"),
            "description": _("What did you buy?"),
            "category": _("Category"),
            "date": _("Purchase date"),
        }

    def __init__(self, *args, owner, currency_code="EUR", **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.filter(owner=owner)
        self.fields["amount"].label = _("Amount (%(currency)s)") % {"currency": currency_code}


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "emoji")
        labels = {"name": _("Name"), "emoji": _("Icon")}
        widgets = {"emoji": forms.TextInput(attrs={"maxlength": 8, "placeholder": "For example, 🛒"})}


class CategoryDeleteForm(forms.Form):
    replacement = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        label=_("Move its expenses to"),
        empty_label=_("Choose a replacement category"),
    )

    def __init__(self, *args, owner, category, expense_count, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["replacement"].queryset = Category.objects.filter(owner=owner).exclude(pk=category.pk)
        self.fields["replacement"].required = expense_count > 0


class MonthlyIncomeForm(forms.ModelForm):
    class Meta:
        model = MonthlyIncome
        fields = ("amount",)
        labels = {"amount": _("Monthly income")}

    def __init__(self, *args, currency_code="EUR", **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount"].label = _("Monthly income (%(currency)s)") % {"currency": currency_code}


class UserPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = ("currency", "language")
        labels = {"currency": _("Preferred currency"), "language": _("Language")}


class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ("name", "target_amount")
        labels = {"name": _("Goal name"), "target_amount": _("Target amount")}

    def __init__(self, *args, currency_code="EUR", **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["target_amount"].label = _("Target amount (%(currency)s)") % {"currency": currency_code}


class GoalContributionForm(forms.ModelForm):
    class Meta:
        model = GoalContribution
        fields = ("amount",)
        labels = {"amount": "Amount to add"}

    def __init__(self, *args, currency_code="EUR", **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount"].label = _("Amount to add (%(currency)s)") % {"currency": currency_code}
