from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, DashboardAPIView, TicketCommentViewSet, TicketHistoryViewSet
from django.urls import path,include


router = DefaultRouter()

router.register("tickets", TicketViewSet, basename="ticket")
router.register("comments",TicketCommentViewSet,basename="comments")
router.register("history",TicketHistoryViewSet,basename="history")

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/",DashboardAPIView.as_view(),name="dashboard_api"),
]