from rest_framework.permissions import BasePermission


class TicketPermission(BasePermission):

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        is_admin = user.groups.filter(
            name="Admin"
        ).exists()

        is_engineer = user.groups.filter(
            name="Support Engineer"
        ).exists()

        is_customer = user.groups.filter(
            name="Customer"
        ).exists()

        # View
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return (
                is_admin
                or is_engineer
                or is_customer
            )

        # Create
        if request.method == "POST":
            return (
                is_admin
                or is_engineer
                or is_customer
            )

        # Update
        if request.method in ["PUT", "PATCH"]:
            return (
                is_admin
                or is_engineer
            )

        # Delete
        if request.method == "DELETE":
            return is_admin

        return False

    def has_object_permission(self, request, view, obj):

        user = request.user

        # Admin → full access
        if user.groups.filter(
            name="Admin"
        ).exists():
            return True

        # Engineer
        if user.groups.filter(
            name="Support Engineer"
        ).exists():

            # Engineer can VIEW:
            # own tickets + assigned tickets
            if request.method in [
                "GET",
                "HEAD",
                "OPTIONS"
            ]:
                return (
                    obj.created_by == user
                    or obj.assigned_to == user
                )

            # Engineer can UPDATE:
            # assigned tickets only
            if request.method in [
                "PUT",
                "PATCH"
            ]:
                return obj.assigned_to == user

            # Engineer cannot delete
            return False

        # Customer
        if user.groups.filter(
            name="Customer"
        ).exists():

            # Customer can VIEW own tickets only
            if request.method in [
                "GET",
                "HEAD",
                "OPTIONS"
            ]:
                return obj.created_by == user

            return False

        return False

class CommentPermission(BasePermission):

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Admin → full comment access
        if user.groups.filter(
            name="Admin"
        ).exists():
            return True

        # Engineer → can create comments
        if user.groups.filter(
            name="Support Engineer"
        ).exists():

            if request.method == "POST":
                return True

        # Customer → cannot comment
        return False

    def has_object_permission(self, request, view, obj):

        user = request.user

        # Admin → full access
        if user.groups.filter(
            name="Admin"
        ).exists():
            return True

        # Engineer → only comments belonging
        # to tickets they can work on
        if user.groups.filter(
            name="Support Engineer"
        ).exists():

            if request.method in ["GET", "HEAD", "OPTIONS"]:
                return (
                    obj.ticket.assigned_to == user
                    or obj.ticket.created_by == user
                )

            if request.method == "DELETE":
                return False

            if request.method in ["PUT", "PATCH"]:
                return False

        return False