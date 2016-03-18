# -*- coding: utf-8 -*-
import json
from django.core.exceptions import (
    ObjectDoesNotExist,  PermissionDenied)
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import (View, FormView)
from rest_framework.views import APIView

from oscar.core.loading import get_class, get_classes, get_model
from oscar.core.utils import redirect_to_referrer

WishList = get_model('wishlists', 'WishList')
WishLine = get_model('wishlists', 'Line')
Product = get_model('catalogue', 'Product')
WishListForm, LineFormset = get_classes('wishlists.forms',
                                        ['WishListForm', 'LineFormset'])
PageTitleMixin = get_class('customer.mixins', 'PageTitleMixin')

wishlist_title = u'我的关注'

class MyFavListView(APIView):

    def get(self, request, *args, **kwargs):
        user = request.user
        tpl = 'customer/wishlists/myfav.html'

        wishlist = WishList.objects.filter(owner__pk=user.pk).first()
        if not wishlist:
            wishlist = WishList(owner=user)
            wishlist.save()
            myfav = []
        else:
            myfav = WishLine.objects.filter(wishlist=wishlist,
                                            product__is_on_shelves=True,
                                            )

        m = {
             'frame_id': 'myfav',
            'myfav': myfav,
             }
        return render(request, tpl, m)

    def get_or_create_wishlist(self, user):
        myfav = WishList.objects.filter(owner__pk=user.pk).first()
        if not myfav:
            myfav = WishList(owner=user)
            myfav.save()
        return myfav

# class MyFavListView(PageTitleMixin, FormView):
#     """
#     This view acts as a DetailView for a wish list and allows updating the
#     quantities of products.
#
#     It is implemented as FormView because it's easier to adapt a FormView to
#     display a product then adapt a DetailView to handle form validation.
#     """
#     template_name = 'customer/wishlists/myfav.html'
#     active_tab = "myfav"
#     form_class = LineFormset
#
#     def dispatch(self, request, *args, **kwargs):
#         self.object = self.get_or_create_wishlist(request.user)
#         return super(self.__class__, self).dispatch(request, *args,  **kwargs)
#
#     def get_or_create_wishlist(self, user):
#         myfav = WishList.objects.filter(owner__pk=user.pk).first()
#         if not myfav:
#             myfav = WishList(owner=user)
#             myfav.save()
#         return myfav
#
#
#     def get_page_title(self):
#         # return self.object.name
#         return wishlist_title
#
#     def get_form_kwargs(self):
#         kwargs = super(self.__class__, self).get_form_kwargs()
#         kwargs['instance'] = self.object
#         return kwargs
#
#     def get_context_data(self, **kwargs):
#         ctx = super(self.__class__, self).get_context_data(**kwargs)
#         ctx['myfav'] = self.object.lines
#         ctx['frame_id'] = 'myfav'
#         # other_wishlists = self.request.user.wishlists.exclude(
#         #     pk=self.object.pk)
#
#         return ctx


class MyFavAddProduct(View):
    """
    Adds a product to a wish list.

    - If the user doesn't already have a wishlist then it will be created for
      them.
    - If the product is already in the wish list, its quantity is increased.
    """

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=kwargs['product_pk'])
        self.wishlist = self.get_or_create_wishlist(request, *args, **kwargs)
        return super(self.__class__, self).dispatch(request)

    def get_or_create_wishlist(self, request, *args, **kwargs):

        try:
            wishlist = WishList.objects.get(owner=self.request.user)
        except ObjectDoesNotExist:
            return request.user.wishlists.create()

        if not wishlist.is_allowed_to_edit(request.user):
            raise PermissionDenied
        return wishlist

    def get(self, request, *args, **kwargs):
        # This is nasty as we shouldn't be performing write operations on a GET
        # request.  It's only included as the UI of the product detail page
        # allows a wishlist to be selected from a dropdown.
        return self.add_product()

    def post(self, request, *args, **kwargs):
        return self.add_product()

    def add_product(self):
        self.wishlist.add(self.product)
        # msg = _("'%s' was added to your wish list.") % self.product.get_title()
        # messages.success(self.request, msg)
        return redirect_to_referrer(
            self.request, self.product.get_absolute_url())


class MyFavRemoveProduct(View):

    def post(self, request, *args, **kwargs):
        WishLine.objects.filter(wishlist__owner=request.user, product__pk=kwargs['product_pk']).delete()

        return HttpResponseRedirect(reverse('customer:myfav-list'))

    def get(self, request, *args, **kwargs):
        WishLine.objects.filter(wishlist__owner=request.user, product__pk=kwargs['product_pk']).delete()
        # return HttpResponse("")

        return HttpResponseRedirect(reverse('customer:myfav-list'))


class MyFavRemoveProductListView(APIView):

    def post(self, request, *args, **kwargs):
        data = request.data
        s = data.get('params')
        if s:
            params = json.loads(s)
            for p in params:
                WishLine.objects.filter(wishlist__owner=request.user, product__pk=p['id']).delete()

        return HttpResponseRedirect(reverse('customer:myfav-list'))

    def get(self, request, *args, **kwargs):
        WishLine.objects.filter(wishlist__owner=request.user, product__pk=kwargs['product_pk']).delete()
        # return HttpResponse("")

        return HttpResponseRedirect(reverse('customer:myfav-list'))
# class FavLineMixin(object):
#     """
#     Handles fetching both a wish list and a product
#     Views using this mixin must be passed two keyword arguments:
#
#     * line_pk: The primary key of the wish list line
#
#     or
#
#     * product_pk: The primary key of the product
#     """
#
#     def fetch_line(self, user, line_pk=None, product_pk=None):
#         self.wishlist = WishList._default_manager.get(
#             owner=user)
#         if line_pk is not None:
#             self.line = self.wishlist.lines.get(pk=line_pk)
#         else:
#             self.line = self.wishlist.lines.get(product_id=product_pk)
#         self.product = self.line.product

# class MyFavRemoveProduct(FavLineMixin, DeleteView):
# # class MyFavRemoveProduct(FavLineMixin, PageTitleMixin, View):
#     # template_name = 'customer/wishlists/myfav_delete_product.html'
#     # template_name = 'customer/wishlists/myfav_list.html'
#     # active_tab = "myfav"
#
#     # def get_page_title(self):
#     #     return _(u'Remove %s') % self.object.get_title()
#
#     def get_object(self, queryset=None):
#         self.fetch_line(
#             self.request.user,
#             product_pk=self.kwargs.get('product_pk'))
#         return self.line
#
#     # def get_context_data(self, **kwargs):
#     #     ctx = super(self.__class__, self).get_context_data(**kwargs)
#     #     ctx['myfav'] = self.wishlist
#     #     ctx['product'] = self.product
#     #     return ctx
#
#     def get_success_url(self):
#         # msg = _(u"'%(title)s' 从 我的关注 中删除") % {
#         #     'title': self.line.get_title()}
#         # messages.success(self.request, msg)
#
#         # # We post directly to this view on product pages; and should send the
#         # # user back there if that was the case
#         # referrer = safe_referrer(self.request, '')
#         # if (referrer and self.product and
#         #         self.product.get_absolute_url() in referrer):
#         #     return referrer
#         # else:
#         return reverse('customer:myfav-list')