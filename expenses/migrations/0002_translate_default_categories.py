from django.db import migrations


CATEGORY_RENAMES = {
    "Продукты": "Groceries",
    "Жильё": "Housing",
    "Транспорт": "Transport",
    "Здоровье": "Health",
    "Покупки": "Shopping",
    "Развлечения": "Entertainment",
    "Другое": "Other",
}


def translate_default_categories(apps, schema_editor):
    Category = apps.get_model("expenses", "Category")
    Expense = apps.get_model("expenses", "Expense")
    database = schema_editor.connection.alias

    for owner_id in Category.objects.using(database).values_list("owner_id", flat=True).distinct():
        for old_name, new_name in CATEGORY_RENAMES.items():
            source = Category.objects.using(database).filter(owner_id=owner_id, name=old_name).first()
            if source is None:
                continue

            existing = Category.objects.using(database).filter(owner_id=owner_id, name=new_name).first()
            if existing is not None:
                Expense.objects.using(database).filter(category_id=source.pk).update(category_id=existing.pk)
                source.delete(using=database)
            else:
                source.name = new_name
                source.save(using=database, update_fields=["name"])


class Migration(migrations.Migration):
    dependencies = [("expenses", "0001_initial")]

    operations = [migrations.RunPython(translate_default_categories, migrations.RunPython.noop)]
