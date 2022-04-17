from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from base import views as base
from restaurant import views as restaurant

router = routers.DefaultRouter()
router.register('account', base.AccountViewSet)
router.register('restaurant', restaurant.RestaurantViewSet)
router.register('menu', restaurant.MenuViewSet)
router.register('vote', restaurant.VoteViewSet)
router.register('vote_result', restaurant.VoteResultViewSet, basename='vote_result')

urlpatterns = [
    path('v1/api/', include(router.urls), name='api'),
    path('v1/api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
    path('', RedirectView.as_view(url='/v1/api/', permanent=False), name='index')
]
