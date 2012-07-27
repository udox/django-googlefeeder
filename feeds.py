import itertools
from django.contrib.syndication.views import Feed
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.html import strip_tags

from sorl.thumbnail.base import ThumbnailException

from store.models import Product, OptionItem, ProductCategory
from google import GoogleProductsFeed

SETTINGS = settings.FEEDS

current_site = Site.objects.get_current()


class GoogleProducts(Feed):
    feed_type = GoogleProductsFeed

    title = 'Products From Your Store'
    link = 'http://www.yoursite.com/'
    description = 'Google Product Search feed'

    DESC_LEN = 10000
    MAX_ATTRS = 10
    ROOT_CAT_TO_GCAT = {
        'Sneakers': 'Clothing & Accessories > Shoes',
        'Clothing': 'Clothing & Accessories > Clothing',
        }

    def __call__(self, request, *args, **kwargs):
        self.item_sizes = {}
        return super(GoogleProducts, self).__call__(request, *args, **kwargs)

    def body_func(self, item):
        return item.body

    def get_item_sizes(self, item):
        return self.item_sizes[item.pk]

    def item_title(self, item):
        return '%s %s, %s' % (item.brand.name, item.short_name, item.colour)

    def item_description(self, item):
        """
        We append the in-stock sizes to the end of the description because
        Google reject the product if > 10 sizes submitted in size attributes:
        http://www.google.com/support/forum/p/base/thread?tid=342324990311782f&hl=en
        """
        sizes_str = ' Sizes in stock: %s' % ','.join(self.get_item_sizes(item))
        return '%s%s' % (
            strip_tags(item.editors_notes)[:self.DESC_LEN - len(sizes_str)],# char limit
            sizes_str
        )

    def item_link(self, item):
        return "http://%s%s?utm_source=google_product_search&utm_medium=organic&utm_campaign=google_product_search" % (current_site.domain, item.get_absolute_url())

    def item_extra_kwargs(self, item):
        def filter_sizes(sizes):
            "trims the set of in-stock sizes down to 10 significant ones"
            surplus = len(sizes) - self.MAX_ATTRS
            # start by eliminating half-sizes
            i = 0
            while surplus > 0 and i < len(sizes):
                if str(sizes[i])[-2:] == '.5':
                    sizes.pop(i)
                    surplus -= 1
                i += 1
            # then chop sizes off the end
            while surplus > 0:
                sizes.pop()
                surplus -= 1
            return sizes

        def get_root_cat(item):
            try:
                cat = item.categories.all()[0]
            except ProductCategory.DoesNotExist, IndexError:
                return None
            root_category = cat.get_root()
            return self.ROOT_CAT_TO_GCAT.get(root_category.title, None)

        product_data = {
            'google_category': get_root_cat(item),
            'brand': item.brand.name,
            'colors': list(item.colour_tags.values_list('name', flat=True))[:self.MAX_ATTRS-1] + [item.colour],
            'condition': 'new',
            'ean': None,
            'features': None,
            'image_links': None,
            'made_in': None,
            'manufacturer': item.brand.name,
            'materials': None,
            'model_number': None, # this must be unique, not as important as below
            'mpn': item.manufacturer_product_code,
            'online_only': 'y',
            'payments_accepted': ['Visa', 'MasterCard', 'AmericanExpress', ],
            'payment_notes': 'PayPal',
            'price': str(item.get_prices()['selling']),
            'currency': 'GBP',
            'price_type': None,
            'product_types': list(set(itertools.chain.from_iterable([cat.google_taxonomy_list for cat in item.categories.all()])))[:self.MAX_ATTRS],
            'quantity': str(item.denorm_stock),
            'sizes': filter_sizes(list(self.get_item_sizes(item))),
            'upc': None,
            'youtube_videos': None,
        }

        # use 1 + self.MAX_ATTRS items, as [1:] images are put as 10 "additional" image links
        if item.gallery() is not None:
            try:
                product_data['image_links'] = ['http://%s%s' % \
                    (current_site.domain, img.image.extra_thumbnails['product_fullsize']) \
                    for img in item.gallery().images.all()[:1+self.MAX_ATTRS] \
                    if 'product_fullsize' in img.image.extra_thumbnails]
            except OverflowError:
                pass
            except ThumbnailException:
                pass

        return product_data

    def items(self):
        return Product.live_objects.all().select_related()

