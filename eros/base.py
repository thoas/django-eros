class ErosModelBase(object):
    author_field = None

    def get_author(self, obj):
        if self.author_field:
            return getattr(obj, self.author_field, None)

        return None
