from django.utils.feedgenerator import Rss201rev2Feed


class GoogleProductsFeed(Rss201rev2Feed):
    """
    This class will output most of the non type-specific fields from the
    attribute list here:
    http://www.google.com/support/merchants/bin/answer.py?answer=160085&hl=en

    Note: the per-item shipping and tax fields are omitted as we don't
    currently need them.
    """

    PAYMENT_TYPES = ('Cash', 'Check', 'Visa', 'MasterCard', 'AmericanExpress', 'Discover', 'GoogleCheckout', 'wiretransfer',)
    PRICE_TYPES = ('negotiable', 'starting',)
    ONLINE_ONLY = ('y', 'n',)
    CONDITIONS = ('new', 'used', 'refurbished',)
    FREE_SHIPPING_PRICE = "0.00"

    def rss_attributes(self):
        attrs = super(GoogleProductsFeed, self).rss_attributes()
        attrs['xmlns:g'] = 'http://base.google.com/ns/1.0'
        attrs['xmlns:c'] = 'http://base.google.com/cns/1.0'
        return attrs

    def add_item_elements(self, handler, item):
        super(GoogleProductsFeed, self).add_item_elements(handler, item)

        # we only show in stock products
        handler.addQuickElement(u"g:availability", 'in stock')

        if item['google_category'] is not None:
            handler.addQuickElement(u"g:google_product_category", item['google_category'])

        if item['brand'] is not None:
            handler.addQuickElement(u"g:brand", item['brand'])

        if item['colors'] is not None:
            for color in item['colors']:
                handler.addQuickElement(u"g:color", color)

        if item['condition'] in self.CONDITIONS:
            handler.addQuickElement(u"g:condition", item['condition'])

        if item['ean'] is not None:
            handler.addQuickElement(u"g:ean", item['ean'])

        if item['features'] is not None:
            for feature in item['features']:
                handler.addQuickElement(u"g:feature", feature)

        # we don't want this since Django RSS feeds already have guid elements
        #handler.addQuickElement(u"g:id", item['id'])

        if item['image_links'] is not None:
            # 1st image is "image_link"
            # then up to 10 "additional_image_link"s maybe used
            key = u"g:image_link"
            for img in item['image_links']:
                handler.addQuickElement(key, img)
                key = u"g:additional_image_link"

        if item['made_in'] is not None:
            handler.addQuickElement(u"g:made_in", item['made_in'])

        if item['manufacturer'] is not None:
            handler.addQuickElement(u"g:manufacturer", item['manufacturer'])

        if item['materials'] is not None:
            for material in item['materials']:
                handler.addQuickElement(u"g:material", material)

        if item['model_number'] is not None:
            handler.addQuickElement(u"g:model_number", item['model_number'])

        if item['mpn'] is not None:
            handler.addQuickElement(u"g:mpn", item['mpn'])

        if item['online_only'] is not None and item['online_only'] in self.ONLINE_ONLY:
            handler.addQuickElement(u"g:online_only", item['online_only'])

        if item['payments_accepted'] is not None:
            for payment in item['payments_accepted']:
                if payment in self.PAYMENT_TYPES:
                    handler.addQuickElement(u"g:payment_accepted", payment)

        if item['payment_notes'] is not None:
            handler.addQuickElement(u"g:payment_notes", item['payment_notes'])

        handler.addQuickElement(u"g:price", '%(price)s %(currency)s' % item)

        if item['price_type'] is not None and item['price_type'] in self.PRICE_TYPES:
            handler.addQuickElement(u"g:price_type", item['price_type'])

        if item['product_types'] is not None:
            for type in item['product_types']:
                handler.addQuickElement(u"g:product_type", type)

        if item['quantity'] is not None:
            handler.addQuickElement(u"g:quantity", item['quantity'])

        if item['sizes'] is not None:
            for size in item['sizes']:
                handler.addQuickElement(u"g:size", size)

        if item['upc'] is not None:
            handler.addQuickElement(u"g:upc", item['upc'])

        if item['youtube_videos'] is not None:
            for video in item['youtube_videos']:
                handler.addQuickElement(u"g:youtube", video)

        handler.startElement(u'g:shipping', {})
        handler.addQuickElement(u"g:price", self.FREE_SHIPPING_PRICE)
        handler.endElement(u'g:shipping')
