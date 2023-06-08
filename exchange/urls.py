from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("exch/", views.display, name="display"),
    path("vkurse/", views.vkurse, name="vkurse"),
    path("currencyapi/", views.currencyapi, name="currencyapi"),
    path("nbu/", views.nbu, name="nbu"),
    path("privat/", views.privat, name="privat"),
    path("monobank/", views.monobank, name="monobank"),
]
