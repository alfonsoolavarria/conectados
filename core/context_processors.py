def must_change_password_context(request):
    if not request.user.is_authenticated:
        return {}
    member = getattr(request.user, "member", None)
    if member is not None and member.must_change_password:
        return {"show_password_modal": True}
    return {}
