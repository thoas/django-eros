from optparse import make_option

from django.core.management.base import BaseCommand

from eros.models import Resource


class Command(BaseCommand):
    help = 'Sync like count of each resources in cache'
    option_list = BaseCommand.option_list + (
        make_option('--length',
                    action='store_true',
                    dest='length',
                    default=10000,
                    help='Chunk length'),
    )

    def handle(self, *args, **options):
        total = Resource.objects.count()

        print 'Syncing %s resources in cache' % total

        for r in xrange(0, total, options['length']):
            print 'Syncing resources in cache [%s:%s]' % (r, r + options['length'])

            resources = Resource.objects.select_related('content_type')[r:r + options['length']]

            for resource in resources:
                resource.sync_count()
