from .models import Notification

def user_role(request):

    role = None

    if request.user.is_authenticated:

        group = request.user.groups.first()

        if group:

            role = group.name

    return {"role": role}


def notifications(request):

    if not request.user.is_authenticated:

        return {
            "notifications": [],
            "unread_notifications_count": 0,}

    user_notifications = Notification.objects.filter(user=request.user).order_by("-created_at")[:5]

    unread_count = Notification.objects.filter(user=request.user,is_read=False).count()

    return {
        "notifications": user_notifications,
        "unread_notifications_count": unread_count,}
