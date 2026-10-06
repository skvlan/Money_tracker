from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from .currencies import CURRENCY_CHOICES


class UserPreferences(models.Model):
    LANGUAGE_CHOICES = (
        ("en", "English"),
        ("ru", "Русский"),
        ("uk", "Українська"),
        ("pl", "Polski"),
        ("de", "Deutsch"),
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="money_preferences"
    )
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="EUR")
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default="en")

    def __str__(self):
        return f"{self.user.username} ({self.currency})"


class Category(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="expense_categories")
    name = models.CharField(max_length=40)
    emoji = models.CharField(max_length=8, default="•")

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["owner", "name"], name="unique_category_per_owner")]
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.emoji} {self.name}"


class Expense(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="expenses")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    description = models.CharField(max_length=160)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="expenses")
    date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.description} — {self.amount} {self.owner.money_preferences.currency}"


class MonthlyIncome(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="monthly_incomes")
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        ordering = ["-year", "-month"]
        constraints = [
            models.UniqueConstraint(fields=["owner", "year", "month"], name="unique_monthly_income_per_owner")
        ]

    def __str__(self):
        return f"{self.year}-{self.month:02d}: {self.amount} {self.owner.money_preferences.currency}"


class SavingsGoal(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="savings_goals")
    name = models.CharField(max_length=80)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "name"]

    def __str__(self):
        return f"{self.name} — {self.target_amount}"


class GoalContribution(models.Model):
    goal = models.ForeignKey(SavingsGoal, on_delete=models.CASCADE, related_name="contributions")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.goal.name}: {self.amount}"
