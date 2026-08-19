def must_change_password_context(request):
    if not request.user.is_authenticated:
        return {}
    member = getattr(request.user, "member", None)
    ctx = {}
    if member is not None:
        if member.must_change_password:
            ctx["show_password_modal"] = True
        if member.profile_image:
            ctx["profile_image"] = member.profile_image
    return ctx
