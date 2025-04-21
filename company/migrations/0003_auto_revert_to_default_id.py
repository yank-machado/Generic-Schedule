# Generated manually

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [        
        ('company', '0002_alter_company_id'),
    ]

    operations = [
        # Primeiro, adicionar uma coluna temporária para o novo ID
        migrations.AddField(
            model_name='company',
            name='new_id',
            field=models.BigAutoField(primary_key=False, auto_created=True, serialize=False, verbose_name='ID'),
        ),
        # Remover a restrição de chave primária do campo UUID
        migrations.AlterField(
            model_name='company',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=False),
        ),
        # Definir o novo campo como chave primária
        migrations.AlterField(
            model_name='company',
            name='new_id',
            field=models.BigAutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID'),
        ),
        # Renomear o novo campo para 'id'
        migrations.RemoveField(
            model_name='company',
            name='id',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='new_id',
            new_name='id',
        ),
    ]