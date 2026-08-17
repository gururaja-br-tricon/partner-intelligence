import os
import uuid

import bcrypt
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from app.auth.user_store import (
    VALID_DOMAINS,
    create_user,
    delete_user,
    get_user_by_email,
    list_all_users,
    update_user_password,
    update_user_roles,
)

ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

st.set_page_config(page_title="Partner Intelligence — Admin", layout="wide")

if "admin_authed" not in st.session_state:
    st.session_state["admin_authed"] = False

if not st.session_state["admin_authed"]:
    st.title("Admin Login")
    with st.form("admin_login_form"):
        password = st.text_input("Admin password", type="password")
        submitted = st.form_submit_button("Log in")
        if submitted:
            if password == ADMIN_PASSWORD:
                st.session_state["admin_authed"] = True
                st.rerun()
            else:
                st.error("Incorrect admin password.")
    st.stop()

st.title("User Admin")

if st.button("Log out"):
    st.session_state["admin_authed"] = False
    st.rerun()

st.divider()
st.subheader("Create user")

with st.form("create_user_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    roles = st.multiselect("Roles", sorted(VALID_DOMAINS))
    submitted = st.form_submit_button("Create user")

    if submitted:
        if not email or not password:
            st.error("Email and password are required.")
        elif not roles:
            st.error("Select at least one role.")
        elif get_user_by_email(email) is not None:
            st.error(f"A user with email '{email}' already exists.")
        else:
            password_hash = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            user_id = str(uuid.uuid4())
            try:
                create_user(
                    user_id=user_id,
                    email=email,
                    password_hash=password_hash,
                    roles=roles,
                )
                st.success(
                    f"Created user {email} with roles: {', '.join(sorted(roles))}"
                )
                st.rerun()
            except Exception as e:
                st.error(f"Failed to create user: {e}")

st.divider()
st.subheader("Existing users")
st.caption(
    "Note: deleting a user or changing roles does not revoke an already-issued "
    "JWT — the change takes effect the next time that person logs in, not "
    "immediately. There is no session-kill mechanism yet."
)

users = list_all_users()

if not users:
    st.info("No users yet.")
else:
    for user in users:
        with st.expander(
            f"{user.email}  —  roles: {', '.join(sorted(user.roles)) or '(none)'}"
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Update roles**")
                new_roles = st.multiselect(
                    "Roles",
                    sorted(VALID_DOMAINS),
                    default=sorted(user.roles),
                    key=f"roles_{user.user_id}",
                )
                if st.button("Save roles", key=f"save_roles_{user.user_id}"):
                    try:
                        update_user_roles(user.user_id, new_roles)
                        st.success("Roles updated.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to update roles: {e}")

            with col2:
                st.markdown("**Reset password**")
                new_password = st.text_input(
                    "New password", type="password", key=f"pw_{user.user_id}"
                )
                if st.button("Save password", key=f"save_pw_{user.user_id}"):
                    if not new_password:
                        st.error("Enter a new password.")
                    else:
                        new_hash = bcrypt.hashpw(
                            new_password.encode("utf-8"), bcrypt.gensalt()
                        ).decode("utf-8")
                        try:
                            update_user_password(user.user_id, new_hash)
                            st.success("Password updated.")
                        except Exception as e:
                            st.error(f"Failed to update password: {e}")

            st.divider()
            confirm = st.checkbox(
                f"Confirm delete {user.email}", key=f"confirm_del_{user.user_id}"
            )
            if st.button(
                "Delete user", key=f"del_{user.user_id}", disabled=not confirm
            ):
                try:
                    delete_user(user.user_id)
                    st.success(f"Deleted {user.email}.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete user: {e}")
