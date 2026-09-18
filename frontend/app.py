import httpx
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="AI Decision Assistant",
    page_icon="🤖",
    layout="centered",
)


if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = None


def api_request(method: str, endpoint: str, **kwargs):
    headers = kwargs.pop("headers", {})

    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"

    try:
        response = httpx.request(
            method,
            f"{API_URL}{endpoint}",
            headers=headers,
            timeout=60.0,
            **kwargs,
        )
        return response
    except httpx.RequestError as exc:
        st.error(f"Could not connect to backend: {exc}")
        return None


def login():
    st.title("🤖 AI Decision Assistant")
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login", type="primary"):
        if not email or not password:
            st.warning("Please enter your email and password.")
            return

        response = api_request(
            "POST",
            "/login",
            json={
                "email": email,
                "password": password,
            },
        )

        if response is None:
            return

        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]

            me_response = api_request("GET", "/me")

            if me_response and me_response.status_code == 200:
                st.session_state.user = me_response.json()

            st.rerun()

        else:
            try:
                detail = response.json().get("detail", "Login failed.")
            except Exception:
                detail = "Login failed."

            st.error(detail)


def register():
    st.title("🤖 AI Decision Assistant")
    st.subheader("Create Account")

    email = st.text_input("Email", key="register_email")
    password = st.text_input(
        "Password",
        type="password",
        key="register_password",
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
    )

    if st.button("Register", type="primary"):
        if not email or not password:
            st.warning("Please fill in all fields.")
            return

        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        response = api_request(
            "POST",
            "/register",
            json={
                "email": email,
                "password": password,
            },
        )

        if response is None:
            return

        if response.status_code == 201:
            st.success("Registration successful. You can now log in.")
        else:
            try:
                detail = response.json().get(
                    "detail",
                    "Registration failed.",
                )
            except Exception:
                detail = "Registration failed."

            st.error(detail)


def new_decision():
    st.header("New Decision")

    message = st.text_area(
        "Customer support ticket",
        placeholder=(
            "Example: My package arrived damaged yesterday "
            "and the order value was ₹3500."
        ),
        height=160,
    )

    if st.button("Get AI Decision", type="primary"):
        if not message.strip():
            st.warning("Please enter a support ticket.")
            return

        response = api_request(
            "POST",
            "/tickets",
            json={
                "message": message.strip(),
            },
        )

        if response is None:
            return

        if response.status_code == 201:
            data = response.json()
            decision = data["decision"]

            st.success("Decision generated successfully.")

            st.subheader("Decision")

            st.metric(
                "Recommended Action",
                decision["action"],
            )

            st.write(
                f"**Confidence:** "
                f"{decision['confidence']:.0%}"
            )

            st.write("**Reason:**")
            st.info(decision["reason"])

            st.write("**Policy Sources:**")

            for source in decision.get("sources", []):
                st.code(source)

        else:
            try:
                detail = response.json().get(
                    "detail",
                    "Unable to generate decision.",
                )
            except Exception:
                detail = "Unable to generate decision."

            st.error(detail)


def history():
    st.header("Decision History")

    response = api_request("GET", "/tickets")

    if response is None:
        return

    if response.status_code != 200:
        st.error("Unable to load ticket history.")
        return

    tickets = response.json()

    if not tickets:
        st.info("No decisions yet.")
        return

    for ticket in tickets:
        decision = ticket.get("decision")

        with st.expander(
            f"Ticket #{ticket['id']} — "
            f"{ticket['message'][:70]}"
        ):
            st.write(f"**Message:** {ticket['message']}")
            st.write(
                f"**Created:** {ticket['created_at']}"
            )

            if decision:
                st.write(
                    f"**Action:** `{decision['action']}`"
                )

                st.write(
                    f"**Confidence:** "
                    f"{decision['confidence']:.0%}"
                )

                st.write(
                    f"**Reason:** {decision['reason']}"
                )

                st.write("**Sources:**")

                for source in decision.get("sources", []):
                    st.code(source)


def dashboard():
    user_email = (
        st.session_state.user["email"]
        if st.session_state.user
        else "User"
    )

    with st.sidebar:
        st.title("AI Decision Assistant")

        st.write(f"Logged in as:")
        st.write(f"**{user_email}**")

        page = st.radio(
            "Navigation",
            [
                "New Decision",
                "History",
            ],
        )

        st.divider()

        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()

    if page == "New Decision":
        new_decision()
    else:
        history()


if st.session_state.token:
    dashboard()
else:
    tab_login, tab_register = st.tabs(
        ["Login", "Register"]
    )

    with tab_login:
        login()

    with tab_register:
        register()