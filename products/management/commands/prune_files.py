from django.core.management.base import BaseCommand
from products.services import ProductFileCleaner


class Command(BaseCommand):
    help = "Удаляет файлы продуктов, срок хранения файлов для которых истек"

    def handle(self, *args, **options):
        self.stdout.write("Pruning outdated files...")
        files = ProductFileCleaner.prune_outdated_files()
        self.stdout.write(self.style.SUCCESS(f'Successfully pruned outdated files: {", ".join(files)}'))
