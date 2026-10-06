import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, LargeBinary
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date
import hashlib


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Lost & Found Matcher",
    page_icon="🔎",
    layout="wide"
)


# =========================================================
# DATABASE
# =========================================================

DATABASE_URL = "sqlite:///lost_found.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


# =========================================================
# DATABASE MODELS
# =========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(256), nullable=False)


class LostItem(Base):
    __tablename__ = "lost_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    item_name = Column(String(150), nullable=False)
    category = Column(String(100))
    color = Column(String(100))
    location = Column(String(200))
    date_lost = Column(Date)
    description = Column(Text)
    image = Column(LargeBinary)


class FoundItem(Base):
    __tablename__ = "found_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    item_name = Column(String(150), nullable=False)
    category = Column(String(100))
    color = Column(String(100))
    location = Column(String(200))
    date_found = Column(Date)
    description = Column(Text)
    image = Column(LargeBinary)


Base.metadata.create_all(engine)


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "selected_lost_id" not in st.session_state:
    st.session_state.selected_lost_id = None

if "selected_found_id" not in st.session_state:
    st.session_state.selected_found_id = None


def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()


# =========================================================
# PASSWORD HASHING
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# =========================================================
# LOGIN / REGISTER
# =========================================================

def login_page():

    st.title("🔐 AI Lost & Found Matcher")

    st.write(
        "Find and recover lost belongings using a smart lost and found system."
    )

    st.markdown("---")

    login_tab, register_tab = st.tabs(
        ["🔑 Login", "📝 Register"]
    )

    # =====================================================
    # LOGIN
    # =====================================================

    with login_tab:

        st.subheader("Login to your account")

        with st.form("login_form"):

            email = st.text_input(
                "Email",
                placeholder="Enter your email"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password"
            )

            login_button = st.form_submit_button(
                "Login",
                use_container_width=True
            )

        if login_button:

            email = email.strip()

            if email == "" or password == "":

                st.error("Please enter both email and password.")

            else:

                db = SessionLocal()

                user = db.query(User).filter(
                    User.email == email
                ).first()

                if user is None:

                    st.error(
                        "No account found with this email."
                    )

                    db.close()

                elif user.password != hash_password(password):

                    st.error(
                        "Incorrect password."
                    )

                    db.close()

                else:

                    st.session_state.logged_in = True
                    st.session_state.user_id = user.id
                    st.session_state.user_name = user.name
                    st.session_state.page = "Home"

                    db.close()

                    st.success("Login successful!")

                    st.rerun()

    # =====================================================
    # REGISTER
    # =====================================================

    with register_tab:

        st.subheader("Create a new account")

        with st.form("register_form"):

            name = st.text_input(
                "Full Name",
                placeholder="Enter your full name"
            )

            email = st.text_input(
                "Email Address",
                placeholder="example@gmail.com"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Create a password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter your password"
            )

            register_button = st.form_submit_button(
                "Create Account",
                use_container_width=True
            )

        if register_button:

            # Remove accidental spaces
            name = name.strip()
            email = email.strip()

            # Validation
            if (
                name == ""
                or email == ""
                or password == ""
                or confirm_password == ""
            ):

                st.error(
                    "Please fill in all fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(password) < 4:

                st.error(
                    "Password must contain at least 4 characters."
                )

            else:

                db = SessionLocal()

                existing_user = db.query(User).filter(
                    User.email == email
                ).first()

                if existing_user:

                    st.error(
                        "An account with this email already exists."
                    )

                    db.close()

                else:

                    new_user = User(
                        name=name,
                        email=email,
                        password=hash_password(password)
                    )

                    db.add(new_user)
                    db.commit()

                    db.close()

                    st.success(
                        "🎉 Account created successfully!"
                    )

                    st.info(
                        "Go to the Login tab and login with your new account."
                    )


# =========================================================
# SIDEBAR
# =========================================================

def sidebar():

    st.sidebar.title("🔎 AI Lost & Found")

    st.sidebar.write(
        f"Welcome, **{st.session_state.user_name}** 👋"
    )

    st.sidebar.markdown("---")

    pages = [
        "Home",
        "Report Lost Item",
        "Report Found Item",
        "Match Results",
        "Match Details",
        "My Reports"
    ]

    selected_page = st.sidebar.radio(
        "Navigation",
        pages,
        index=pages.index(st.session_state.page)
    )

    if selected_page != st.session_state.page:

        st.session_state.page = selected_page
        st.rerun()

    st.sidebar.markdown("---")

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = ""
        st.session_state.page = "Home"

        st.rerun()


# =========================================================
# HOME
# =========================================================

def home_page():

    st.title("🔎 AI Lost & Found Matcher")

    st.write(
        "A smart platform that helps people find their lost belongings "
        "by comparing lost and found item reports."
    )

    st.markdown("---")

    db = SessionLocal()

    lost_count = db.query(LostItem).count()
    found_count = db.query(FoundItem).count()

    my_lost_count = db.query(LostItem).filter(
        LostItem.user_id == st.session_state.user_id
    ).count()

    my_found_count = db.query(FoundItem).filter(
        FoundItem.user_id == st.session_state.user_id
    ).count()

    db.close()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Lost Items", lost_count)

    with col2:
        st.metric("Found Items", found_count)

    with col3:
        st.metric("My Lost Reports", my_lost_count)

    with col4:
        st.metric("My Found Reports", my_found_count)

    st.markdown("---")

    st.subheader("What would you like to do?")

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "📌 Report Lost Item",
            use_container_width=True
        ):
            go_to("Report Lost Item")

    with col2:

        if st.button(
            "📦 Report Found Item",
            use_container_width=True
        ):
            go_to("Report Found Item")

    with col3:

        if st.button(
            "🔎 View Possible Matches",
            use_container_width=True
        ):
            go_to("Match Results")

    st.markdown("---")

    st.subheader("How it works")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("### 1️⃣ Report")

        st.write(
            "Submit details about a lost or found item."
        )

    with col2:

        st.markdown("### 2️⃣ Match")

        st.write(
            "The system compares item information."
        )

    with col3:

        st.markdown("### 3️⃣ Recover")

        st.write(
            "Check possible matches and identify your item."
        )


# =========================================================
# REPORT LOST ITEM
# =========================================================

def report_lost_page():

    st.title("📌 Report Lost Item")

    st.write(
        "Enter the details of the item you lost."
    )

    with st.form("lost_item_form"):

        item_name = st.text_input(
            "Item Name *",
            placeholder="Example: Black Water Bottle"
        )

        category = st.selectbox(
            "Category",
            [
                "Electronics",
                "Books",
                "Clothing",
                "Bags",
                "Accessories",
                "Documents",
                "Stationery",
                "Other"
            ]
        )

        color = st.text_input(
            "Color",
            placeholder="Example: Black"
        )

        location = st.text_input(
            "Location",
            placeholder="Example: College Library"
        )

        date_lost = st.date_input(
            "Date Lost",
            value=date.today()
        )

        description = st.text_area(
            "Description",
            placeholder="Describe the item..."
        )

        image = st.file_uploader(
            "Upload Item Image",
            type=["jpg", "jpeg", "png"]
        )

        submit = st.form_submit_button(
            "Submit Lost Report",
            use_container_width=True
        )

    if submit:

        item_name = item_name.strip()

        if item_name == "":

            st.error(
                "Please enter the item name."
            )

        else:

            image_bytes = None

            if image is not None:
                image_bytes = image.getvalue()

            db = SessionLocal()

            new_item = LostItem(
                user_id=st.session_state.user_id,
                item_name=item_name,
                category=category,
                color=color.strip(),
                location=location.strip(),
                date_lost=date_lost,
                description=description.strip(),
                image=image_bytes
            )

            db.add(new_item)
            db.commit()

            db.close()

            st.success(
                "✅ Lost item report submitted successfully!"
            )

            st.info(
                "Your report has been saved permanently."
            )


# =========================================================
# REPORT FOUND ITEM
# =========================================================

def report_found_page():

    st.title("📦 Report Found Item")

    st.write(
        "Enter the details of the item you found."
    )

    with st.form("found_item_form"):

        item_name = st.text_input(
            "Item Name *",
            placeholder="Example: Black Wallet"
        )

        category = st.selectbox(
            "Category",
            [
                "Electronics",
                "Books",
                "Clothing",
                "Bags",
                "Accessories",
                "Documents",
                "Stationery",
                "Other"
            ]
        )

        color = st.text_input(
            "Color",
            placeholder="Example: Black"
        )

        location = st.text_input(
            "Location",
            placeholder="Example: College Library"
        )

        date_found = st.date_input(
            "Date Found",
            value=date.today()
        )

        description = st.text_area(
            "Description",
            placeholder="Describe the item..."
        )

        image = st.file_uploader(
            "Upload Item Image",
            type=["jpg", "jpeg", "png"]
        )

        submit = st.form_submit_button(
            "Submit Found Report",
            use_container_width=True
        )

    if submit:

        item_name = item_name.strip()

        if item_name == "":

            st.error(
                "Please enter the item name."
            )

        else:

            image_bytes = None

            if image is not None:
                image_bytes = image.getvalue()

            db = SessionLocal()

            new_item = FoundItem(
                user_id=st.session_state.user_id,
                item_name=item_name,
                category=category,
                color=color.strip(),
                location=location.strip(),
                date_found=date_found,
                description=description.strip(),
                image=image_bytes
            )

            db.add(new_item)
            db.commit()

            db.close()

            st.success(
                "✅ Found item report submitted successfully!"
            )

            st.info(
                "Your report has been saved permanently."
            )


# =========================================================
# MATCH CALCULATION
# =========================================================

def calculate_match(lost, found):

    score = 0
    reasons = []

    if (
        lost.category
        and found.category
        and lost.category.lower() == found.category.lower()
    ):

        score += 30
        reasons.append("Category matches")

    if (
        lost.color
        and found.color
        and lost.color.lower() == found.color.lower()
    ):

        score += 25
        reasons.append("Color matches")

    if (
        lost.location
        and found.location
        and (
            lost.location.lower() in found.location.lower()
            or found.location.lower() in lost.location.lower()
        )
    ):

        score += 25
        reasons.append("Location is similar")

    lost_name = lost.item_name.lower()
    found_name = found.item_name.lower()

    if (
        lost_name in found_name
        or found_name in lost_name
    ):

        score += 20
        reasons.append("Item name is similar")

    return score, reasons


# =========================================================
# MATCH RESULTS
# =========================================================

def match_results_page():

    st.title("🔎 Match Results")

    st.write(
        "Possible matches between your lost item reports "
        "and found item reports."
    )

    db = SessionLocal()

    lost_items = db.query(LostItem).filter(
        LostItem.user_id == st.session_state.user_id
    ).all()

    found_items = db.query(FoundItem).all()

    if not lost_items:

        st.info(
            "You haven't reported any lost items yet."
        )

        db.close()
        return

    if not found_items:

        st.info(
            "There are no found-item reports available yet."
        )

        db.close()
        return

    match_found = False

    for lost in lost_items:

        st.markdown("---")

        st.subheader(
            f"Lost Item: {lost.item_name}"
        )

        for found in found_items:

            score, reasons = calculate_match(
                lost,
                found
            )

            if score >= 40:

                match_found = True

                col1, col2 = st.columns(2)

                with col1:

                    st.markdown(
                        f"**Found Item:** {found.item_name}"
                    )

                    st.write(
                        f"Category: {found.category}"
                    )

                    st.write(
                        f"Color: {found.color}"
                    )

                    st.write(
                        f"Location: {found.location}"
                    )

                with col2:

                    st.metric(
                        "Match Score",
                        f"{score}%"
                    )

                    if reasons:

                        st.write(
                            "Why this may be a match:"
                        )

                        for reason in reasons:

                            st.write(
                                f"✓ {reason}"
                            )

                if st.button(
                    "View Match Details",
                    key=f"match_{lost.id}_{found.id}"
                ):

                    st.session_state.selected_lost_id = lost.id
                    st.session_state.selected_found_id = found.id

                    go_to("Match Details")

    if not match_found:

        st.warning(
            "No strong matches found yet."
        )

    db.close()


# =========================================================
# MATCH DETAILS
# =========================================================

def match_details_page():

    st.title("📄 Match Details")

    db = SessionLocal()

    lost = None
    found = None

    if (
        st.session_state.selected_lost_id
        and st.session_state.selected_found_id
    ):

        lost = db.query(LostItem).filter(
            LostItem.id == st.session_state.selected_lost_id
        ).first()

        found = db.query(FoundItem).filter(
            FoundItem.id == st.session_state.selected_found_id
        ).first()

    else:

        lost = db.query(LostItem).filter(
            LostItem.user_id == st.session_state.user_id
        ).first()

        found = db.query(FoundItem).first()

    if not lost or not found:

        st.info(
            "No match details are available yet."
        )

        db.close()
        return

    score, reasons = calculate_match(
        lost,
        found
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📌 Lost Item")

        st.write(
            f"**Name:** {lost.item_name}"
        )

        st.write(
            f"**Category:** {lost.category}"
        )

        st.write(
            f"**Color:** {lost.color}"
        )

        st.write(
            f"**Location:** {lost.location}"
        )

        st.write(
            f"**Description:** {lost.description}"
        )

    with col2:

        st.subheader("📦 Found Item")

        st.write(
            f"**Name:** {found.item_name}"
        )

        st.write(
            f"**Category:** {found.category}"
        )

        st.write(
            f"**Color:** {found.color}"
        )

        st.write(
            f"**Location:** {found.location}"
        )

        st.write(
            f"**Description:** {found.description}"
        )

    st.markdown("---")

    st.subheader("📊 Match Analysis")

    st.metric(
        "Overall Match Score",
        f"{score}%"
    )

    for reason in reasons:

        st.write(
            f"✓ {reason}"
        )

    st.markdown("---")

    if score >= 70:

        st.success(
            "This looks like a strong possible match."
        )

    elif score >= 40:

        st.warning(
            "This may be a possible match. Check the details carefully."
        )

    else:

        st.info(
            "This is a weak match."
        )

    if st.button(
        "✅ Confirm This Match",
        use_container_width=True
    ):

        st.success(
            "Match confirmed successfully!"
        )

    db.close()


# =========================================================
# MY REPORTS
# =========================================================

def my_reports_page():

    st.title("📋 My Reports")

    db = SessionLocal()

    lost_items = db.query(LostItem).filter(
        LostItem.user_id == st.session_state.user_id
    ).all()

    found_items = db.query(FoundItem).filter(
        FoundItem.user_id == st.session_state.user_id
    ).all()

    lost_tab, found_tab = st.tabs(
        ["📌 Lost Items", "📦 Found Items"]
    )

    # =====================================================
    # LOST REPORTS
    # =====================================================

    with lost_tab:

        if not lost_items:

            st.info(
                "You have not reported any lost items."
            )

        else:

            for item in lost_items:

                st.subheader(
                    item.item_name
                )

                st.write(
                    f"**Category:** {item.category}"
                )

                st.write(
                    f"**Color:** {item.color}"
                )

                st.write(
                    f"**Location:** {item.location}"
                )

                st.write(
                    f"**Date Lost:** {item.date_lost}"
                )

                st.write(
                    f"**Description:** {item.description}"
                )

                if item.image:

                    st.image(
                        item.image,
                        width=250
                    )

                st.markdown("---")

    # =====================================================
    # FOUND REPORTS
    # =====================================================

    with found_tab:

        if not found_items:

            st.info(
                "You have not reported any found items."
            )

        else:

            for item in found_items:

                st.subheader(
                    item.item_name
                )

                st.write(
                    f"**Category:** {item.category}"
                )

                st.write(
                    f"**Color:** {item.color}"
                )

                st.write(
                    f"**Location:** {item.location}"
                )

                st.write(
                    f"**Date Found:** {item.date_found}"
                )

                st.write(
                    f"**Description:** {item.description}"
                )

                if item.image:

                    st.image(
                        item.image,
                        width=250
                    )

                st.markdown("---")

    db.close()


# =========================================================
# MAIN
# =========================================================

if not st.session_state.logged_in:

    login_page()

else:

    sidebar()

    if st.session_state.page == "Home":

        home_page()

    elif st.session_state.page == "Report Lost Item":

        report_lost_page()

    elif st.session_state.page == "Report Found Item":

        report_found_page()

    elif st.session_state.page == "Match Results":

        match_results_page()

    elif st.session_state.page == "Match Details":

        match_details_page()

    elif st.session_state.page == "My Reports":

        my_reports_page()