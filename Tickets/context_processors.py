def user_role(request):

    role = None

    if request.user.is_authenticated:

        group = request.user.groups.first()

        if group:

            role = group.name.lower()

    return {'role': role}