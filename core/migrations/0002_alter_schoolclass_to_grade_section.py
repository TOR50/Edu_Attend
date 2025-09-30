import django.core.validators
from django.db import migrations, models


def split_name_to_grade_section(apps, schema_editor):
    SchoolClass = apps.get_model('core', 'SchoolClass')

    def parse(name: str):
        if not name:
            return 1, 'A'
        s = name.strip().upper()
        # Common patterns: "CLASS 5-A", "5-A", "5 A", "5A", "GRADE 6-B", "Class 10 C"
        for prefix in ("CLASS ", "GRADE "):
            if s.startswith(prefix):
                s = s[len(prefix):]
        s = s.replace(" ", "-")
        if '-' in s:
            left, right = s.split('-', 1)
            try:
                g = int(''.join(ch for ch in left if ch.isdigit()))
                sec = ''.join(ch for ch in right if ch.isalpha()) or 'A'
                return max(1, min(12, g)), sec[:2]
            except ValueError:
                pass
        # Fallback: digits followed by letters, e.g. "5A" or "12B"
        digits = ''.join(ch for ch in s if ch.isdigit())
        letters = ''.join(ch for ch in s if ch.isalpha())
        try:
            g = int(digits) if digits else 1
        except ValueError:
            g = 1
        sec = letters or 'A'
        return max(1, min(12, g)), sec[:2]

    for sc in SchoolClass.objects.all():
        grade, section = parse(getattr(sc, 'name', '') or '')
        setattr(sc, 'grade', grade)
        setattr(sc, 'section', section)
        sc.save(update_fields=['grade', 'section'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='schoolclass',
            name='grade',
            field=models.PositiveSmallIntegerField(
                default=1,
                help_text='Class/Grade number (1-12)',
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(12),
                ],
            ),
        ),
        migrations.AddField(
            model_name='schoolclass',
            name='section',
            field=models.CharField(default='A', help_text='Section letter, e.g., A, B, C', max_length=2),
        ),
        migrations.RunPython(split_name_to_grade_section, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='schoolclass',
            unique_together={('academic_year', 'grade', 'section')},
        ),
        migrations.RemoveField(
            model_name='schoolclass',
            name='name',
        ),
    ]
