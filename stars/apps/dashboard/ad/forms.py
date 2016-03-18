from django import forms

from oscar.core.loading import get_model

RollingAd = get_model('ad', 'RollingAd')


def _attr_image_field(attribute):
    return forms.ImageField(
        label=attribute.name, required=attribute.required)

class RollingAdForm(forms.ModelForm):
    FIELD_FACTORIES = {
        "image": _attr_image_field,
    }
    class Meta:
        model = RollingAd
        fields = ['title', 'image', 'position', 'link_url', 'description', 'order_num', 'valid']


    def get_attribute_field(self, attribute):
        """
        Gets the correct form field for a given attribute type.
        """
        return self.FIELD_FACTORIES[attribute.type](attribute)
