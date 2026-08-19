from functools import wraps

from flask import session, redirect, url_for, flash, abort


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(view):

    @wraps(view)
    def wrapped_view(*args, **kwargs):

        if "user_id" not in session:
            flash(
                "Please log in to access this page.",
                "warning"
            )

            return redirect(
                url_for("login")
            )

        return view(*args, **kwargs)

    return wrapped_view


# =========================================================
# ROLE REQUIRED
# =========================================================

def role_required(*allowed_roles):

    def decorator(view):

        @wraps(view)
        def wrapped_view(*args, **kwargs):

            # User must be logged in
            if "user_id" not in session:

                flash(
                    "Please log in to access this page.",
                    "warning"
                )

                return redirect(
                    url_for("login")
                )


            # Get current user's role
            user_role = session.get("role")


            # Check permission
            if user_role not in allowed_roles:

                abort(403)


            return view(*args, **kwargs)

        return wrapped_view

    return decorator