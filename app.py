from flask import Flask, render_template, request, jsonify, redirect, session
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
load_dotenv()
import random
from datetime import date
from decimal import Decimal, InvalidOperation


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

CORS(app)

app.secret_key = "simplebank-secret-key"

# Session configuration
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "simplebank")
    )


# =========================================================
# LOGIN CHECK
# =========================================================

def is_logged_in():

    return "user_id" in session


# =========================================================
# MONEY HELPER
# =========================================================

def parse_amount(value):

    try:

        amount = Decimal(str(value))

        if amount <= 0:
            return None

        return amount.quantize(Decimal("0.01"))

    except (InvalidOperation, ValueError, TypeError):

        return None


# =========================================================
# GET USER ACCOUNT
# =========================================================

def get_user_account(cursor, user_id):

    cursor.execute(
        """
        SELECT
            id,
            account_number,
            balance
        FROM accounts
        WHERE user_id = %s
        LIMIT 1
        """,
        (user_id,)
    )

    return cursor.fetchone()


# =========================================================
# CALCULATE ACCOUNT BALANCE
# =========================================================

def calculate_balance(cursor, account_id):

    cursor.execute(
        """
        SELECT
            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = 'credit'
                            THEN amount

                        WHEN transaction_type = 'debit'
                            THEN -amount

                        ELSE 0
                    END
                ),
                0
            ) AS current_balance
        FROM transactions
        WHERE account_id = %s
        """,
        (account_id,)
    )

    result = cursor.fetchone()

    return Decimal(str(
        result["current_balance"] or 0
    ))


# =========================================================
# UPDATE ACCOUNT BALANCE
# =========================================================

def sync_account_balance(cursor, account_id):

    balance = calculate_balance(
        cursor,
        account_id
    )

    cursor.execute(
        """
        UPDATE accounts
        SET balance = %s
        WHERE id = %s
        """,
        (
            balance,
            account_id
        )
    )

    return balance


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if is_logged_in():

        return redirect("/dashboard")

    return render_template("login.html")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if not is_logged_in():

        return redirect("/")

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # -------------------------------------------------
        # ACCOUNT
        # -------------------------------------------------

        account = get_user_account(
            cursor,
            session["user_id"]
        )

        if not account:

            return "Bank account not found.", 404

        account_id = account["id"]

        # -------------------------------------------------
        # INCOME
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                COALESCE(
                    SUM(amount),
                    0
                ) AS total_income
            FROM transactions
            WHERE account_id = %s
            AND transaction_type = 'credit'
            """,
            (account_id,)
        )

        total_income = cursor.fetchone()[
            "total_income"
        ]

        # -------------------------------------------------
        # EXPENSES
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                COALESCE(
                    SUM(amount),
                    0
                ) AS total_expenses
            FROM transactions
            WHERE account_id = %s
            AND transaction_type = 'debit'
            """,
            (account_id,)
        )

        total_expenses = cursor.fetchone()[
            "total_expenses"
        ]

        total_income = Decimal(
            str(total_income or 0)
        )

        total_expenses = Decimal(
            str(total_expenses or 0)
        )

        # -------------------------------------------------
        # CURRENT BALANCE
        # -------------------------------------------------

        total_savings = (
            total_income -
            total_expenses
        )

        # Keep accounts.balance synchronized
        cursor.execute(
            """
            UPDATE accounts
            SET balance = %s
            WHERE id = %s
            """,
            (
                total_savings,
                account_id
            )
        )

        connection.commit()

        account["balance"] = float(
            total_savings
        )

        # -------------------------------------------------
        # RECENT TRANSACTIONS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                transaction_type,
                amount,
                description,
                transaction_date
            FROM transactions
            WHERE account_id = %s
            ORDER BY transaction_date DESC, id DESC
            LIMIT 5
            """,
            (account_id,)
        )

        transactions = cursor.fetchall()

        for transaction in transactions:

            transaction["amount"] = float(
                transaction["amount"] or 0
            )

        # -------------------------------------------------
        # RENDER
        # -------------------------------------------------

        return render_template(

            "dashboard.html",

            user_name=session["user_name"],

            user_email=session["user_email"],

            account=account,

            transactions=transactions,

            income=float(total_income),

            expenses=float(total_expenses),

            savings=float(total_savings),

            total_income=float(total_income),

            total_expenses=float(total_expenses),

            total_savings=float(total_savings)

        )

    except Exception as error:

        print(
            "DASHBOARD ERROR:",
            error
        )

        return (
            "Unable to load dashboard.",
            500
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()



# =========================================================
# DASHBOARD SPENDING OVERVIEW API
# =========================================================

@app.route("/api/dashboard-chart")
def dashboard_chart():

    # -----------------------------------------------------
    # CHECK LOGIN
    # -----------------------------------------------------

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    connection = None
    cursor = None

    try:

        # -------------------------------------------------
        # GET USER ID
        # -------------------------------------------------

        user_id = session["user_id"]

        # -------------------------------------------------
        # GET PERIOD
        # -------------------------------------------------

        period = request.args.get(
            "period",
            "this_month"
        )

        # -------------------------------------------------
        # CONNECT DATABASE
        # -------------------------------------------------

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # -------------------------------------------------
        # THIS MONTH
        # -------------------------------------------------

        if period == "this_month":

            cursor.execute("""
                SELECT
                    DATE(transaction_date) AS transaction_day,

                    SUM(
                        CASE
                            WHEN transaction_type = 'credit'
                            THEN amount
                            ELSE 0
                        END
                    ) AS income,

                    SUM(
                        CASE
                            WHEN transaction_type = 'debit'
                            THEN amount
                            ELSE 0
                        END
                    ) AS expenses

                FROM transactions

                WHERE user_id = %s

                AND transaction_date >=
                    DATE_FORMAT(
                        CURDATE(),
                        '%Y-%m-01'
                    )

                AND transaction_date <
                    DATE_ADD(
                        DATE_FORMAT(
                            CURDATE(),
                            '%Y-%m-01'
                        ),
                        INTERVAL 1 MONTH
                    )

                GROUP BY DATE(transaction_date)

                ORDER BY DATE(transaction_date)
            """, (user_id,))

            rows = cursor.fetchall()

            # -------------------------------------------------
            # CREATE FULL MONTH RANGE
            # -------------------------------------------------

            from datetime import date, timedelta

            today = date.today()

            first_day = today.replace(day=1)

            chart_dates = []

            current_day = first_day

            while current_day <= today:

                chart_dates.append(
                    current_day
                )

                current_day += timedelta(
                    days=1
                )

            # -------------------------------------------------
            # CONVERT DATABASE DATA INTO DICTIONARY
            # -------------------------------------------------

            transaction_data = {}

            for row in rows:

                transaction_date = row[
                    "transaction_day"
                ]

                if hasattr(
                    transaction_date,
                    "date"
                ):
                    transaction_date = (
                        transaction_date.date()
                    )

                transaction_data[
                    transaction_date
                ] = {
                    "income": float(
                        row["income"] or 0
                    ),
                    "expenses": float(
                        row["expenses"] or 0
                    )
                }

            # -------------------------------------------------
            # BUILD CHART DATA
            # -------------------------------------------------

            labels = []
            income = []
            expenses = []

            for chart_date in chart_dates:

                labels.append(
                    chart_date.strftime("%d")
                )

                day_data = transaction_data.get(
                    chart_date,
                    {
                        "income": 0,
                        "expenses": 0
                    }
                )

                income.append(
                    day_data["income"]
                )

                expenses.append(
                    day_data["expenses"]
                )

        # -------------------------------------------------
        # LAST MONTH
        # -------------------------------------------------

        elif period == "last_month":

            cursor.execute("""
                SELECT
                    DATE(transaction_date) AS transaction_day,

                    SUM(
                        CASE
                            WHEN transaction_type = 'credit'
                            THEN amount
                            ELSE 0
                        END
                    ) AS income,

                    SUM(
                        CASE
                            WHEN transaction_type = 'debit'
                            THEN amount
                            ELSE 0
                        END
                    ) AS expenses

                FROM transactions

                WHERE user_id = %s

                AND transaction_date >=
                    DATE_FORMAT(
                        CURDATE() - INTERVAL 1 MONTH,
                        '%Y-%m-01'
                    )

                AND transaction_date <
                    DATE_FORMAT(
                        CURDATE(),
                        '%Y-%m-01'
                    )

                GROUP BY DATE(transaction_date)

                ORDER BY DATE(transaction_date)
            """, (user_id,))

            rows = cursor.fetchall()

            from datetime import date, timedelta

            today = date.today()

            current_month_first = today.replace(
                day=1
            )

            last_month_last = (
                current_month_first
                - timedelta(days=1)
            )

            last_month_first = (
                last_month_last.replace(day=1)
            )

            chart_dates = []

            current_day = last_month_first

            while current_day <= last_month_last:

                chart_dates.append(
                    current_day
                )

                current_day += timedelta(
                    days=1
                )

            # -------------------------------------------------
            # DATABASE DATA
            # -------------------------------------------------

            transaction_data = {}

            for row in rows:

                transaction_date = row[
                    "transaction_day"
                ]

                if hasattr(
                    transaction_date,
                    "date"
                ):
                    transaction_date = (
                        transaction_date.date()
                    )

                transaction_data[
                    transaction_date
                ] = {
                    "income": float(
                        row["income"] or 0
                    ),
                    "expenses": float(
                        row["expenses"] or 0
                    )
                }

            # -------------------------------------------------
            # BUILD CHART
            # -------------------------------------------------

            labels = []
            income = []
            expenses = []

            for chart_date in chart_dates:

                labels.append(
                    chart_date.strftime("%d")
                )

                day_data = transaction_data.get(
                    chart_date,
                    {
                        "income": 0,
                        "expenses": 0
                    }
                )

                income.append(
                    day_data["income"]
                )

                expenses.append(
                    day_data["expenses"]
                )

        # -------------------------------------------------
        # LAST 6 MONTHS
        # -------------------------------------------------

        elif period == "6_months":

            cursor.execute("""
                SELECT
                    DATE_FORMAT(
                        transaction_date,
                        '%Y-%m'
                    ) AS transaction_month,

                    SUM(
                        CASE
                            WHEN transaction_type = 'credit'
                            THEN amount
                            ELSE 0
                        END
                    ) AS income,

                    SUM(
                        CASE
                            WHEN transaction_type = 'debit'
                            THEN amount
                            ELSE 0
                        END
                    ) AS expenses

                FROM transactions

                WHERE user_id = %s

                AND transaction_date >=
                    DATE_FORMAT(
                        CURDATE() - INTERVAL 5 MONTH,
                        '%Y-%m-01'
                    )

                GROUP BY
                    DATE_FORMAT(
                        transaction_date,
                        '%Y-%m'
                    )

                ORDER BY transaction_month
            """, (user_id,))

            rows = cursor.fetchall()

            from datetime import date

            # -------------------------------------------------
            # CREATE LAST 6 MONTHS
            # -------------------------------------------------

            today = date.today()

            months = []

            year = today.year
            month = today.month

            for i in range(5, -1, -1):

                calculated_month = month - i
                calculated_year = year

                while calculated_month <= 0:

                    calculated_month += 12
                    calculated_year -= 1

                months.append(
                    (
                        calculated_year,
                        calculated_month
                    )
                )

            # -------------------------------------------------
            # DATABASE DATA
            # -------------------------------------------------

            transaction_data = {}

            for row in rows:

                month_key = row[
                    "transaction_month"
                ]

                transaction_data[
                    month_key
                ] = {
                    "income": float(
                        row["income"] or 0
                    ),
                    "expenses": float(
                        row["expenses"] or 0
                    )
                }

            # -------------------------------------------------
            # BUILD CHART
            # -------------------------------------------------

            labels = []
            income = []
            expenses = []

            month_names = [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec"
            ]

            for chart_year, chart_month in months:

                month_key = (
                    f"{chart_year}-"
                    f"{chart_month:02d}"
                )

                labels.append(
                    month_names[
                        chart_month - 1
                    ]
                )

                day_data = transaction_data.get(
                    month_key,
                    {
                        "income": 0,
                        "expenses": 0
                    }
                )

                income.append(
                    day_data["income"]
                )

                expenses.append(
                    day_data["expenses"]
                )

        # -------------------------------------------------
        # INVALID PERIOD
        # -------------------------------------------------

        else:

            return jsonify({
                "success": False,
                "message": "Invalid period."
            }), 400

        # -----------------------------------------------------
        # RETURN CHART DATA
        # -----------------------------------------------------

        return jsonify({

            "success": True,

            "period": period,

            "labels": labels,

            "income": income,

            "expenses": expenses

        })

    # ---------------------------------------------------------
    # ERROR HANDLING
    # ---------------------------------------------------------

    except Exception as e:

        print(
            "DASHBOARD CHART ERROR:",
            str(e)
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to load spending overview."

        }), 500

    # ---------------------------------------------------------
    # CLOSE DATABASE
    # ---------------------------------------------------------

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# ADD MONEY
# =========================================================

@app.route(
    "/api/add-money",
    methods=["POST"]
)
def add_money():

    if not is_logged_in():

        return jsonify({

            "success": False,

            "message":
                "Please login first."

        }), 401

    data = request.get_json() or {}

    amount = parse_amount(
        data.get("amount")
    )

    description = str(
        data.get(
            "description",
            ""
        )
    ).strip()

    if amount is None:

        return jsonify({

            "success": False,

            "message":
                "Please enter a valid amount."

        }), 400

    if amount > Decimal("1000000"):

        return jsonify({

            "success": False,

            "message":
                "Maximum amount is ₹10,00,000."

        }), 400

    if not description:

        description = (
            "Money added to account"
        )

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # -------------------------------------------------
        # ACCOUNT
        # -------------------------------------------------

        account = get_user_account(
            cursor,
            session["user_id"]
        )

        if not account:

            return jsonify({

                "success": False,

                "message":
                    "Bank account not found."

            }), 404

        account_id = account["id"]

        # -------------------------------------------------
        # INSERT CREDIT TRANSACTION
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO transactions
            (
                account_id,
                transaction_type,
                amount,
                description
            )
            VALUES
            (
                %s,
                'credit',
                %s,
                %s
            )
            """,
            (
                account_id,
                amount,
                description
            )
        )

        # -------------------------------------------------
        # SYNC BALANCE
        # -------------------------------------------------

        new_balance = sync_account_balance(
            cursor,
            account_id
        )

        connection.commit()

        return jsonify({

            "success": True,

            "message":
                f"₹{amount:,.2f} added successfully.",

            "balance":
                float(new_balance)

        }), 200

    except Exception as error:

        if connection:
            connection.rollback()

        print(
            "ADD MONEY ERROR:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to add money."

        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# MY CARDS
# =========================================================

@app.route("/cards")
def cards():

    if not is_logged_in():

        return redirect("/")

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        account = get_user_account(
            cursor,
            session["user_id"]
        )

        if not account:

            return "Bank account not found.", 404

        account_id = account["id"]

        # -------------------------------------------------
        # CURRENT BALANCE
        # -------------------------------------------------

        current_balance = calculate_balance(
            cursor,
            account_id
        )

        account["balance"] = float(
            current_balance
        )

        # -------------------------------------------------
        # CARDS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                card_number,
                card_type,
                card_network,
                expiry_date,
                card_holder,
                status
            FROM cards
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (session["user_id"],)
        )

        user_cards = cursor.fetchall()

        return render_template(

            "cards.html",

            user_name=session["user_name"],

            user_email=session["user_email"],

            account=account,

            cards=user_cards

        )

    except Exception as error:

        print(
            "CARDS PAGE ERROR:",
            error
        )

        return (
            "Unable to load cards.",
            500
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# CREATE CARD
# =========================================================

@app.route(
    "/api/cards/create",
    methods=["POST"]
)
def create_card():

    if not is_logged_in():

        return jsonify({

            "success": False,

            "message":
                "Please login first."

        }), 401

    data = request.get_json() or {}

    card_type = str(
        data.get(
            "card_type",
            "Debit Card"
        )
    ).strip()

    card_network = str(
        data.get(
            "card_network",
            "VISA"
        )
    ).strip()

    card_holder = str(
        data.get(
            "card_holder",
            session["user_name"]
        )
    ).strip()

    if not card_holder:

        return jsonify({

            "success": False,

            "message":
                "Card holder name is required."

        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # -------------------------------------------------
        # CHECK ACTIVE CARD
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM cards
            WHERE user_id = %s
            AND status = 'Active'
            LIMIT 1
            """,
            (session["user_id"],)
        )

        existing_card = cursor.fetchone()

        if existing_card:

            return jsonify({

                "success": False,

                "message":
                    "You already have an active card."

            }), 409

        # -------------------------------------------------
        # GENERATE CARD NUMBER
        # -------------------------------------------------

        card_number = None

        for _ in range(20):

            generated_number = "".join(

                str(random.randint(0, 9))

                for _ in range(16)

            )

            cursor.execute(
                """
                SELECT id
                FROM cards
                WHERE card_number = %s
                LIMIT 1
                """,
                (generated_number,)
            )

            if not cursor.fetchone():

                card_number = (
                    generated_number
                )

                break

        if not card_number:

            return jsonify({

                "success": False,

                "message":
                    "Unable to generate card number."

            }), 500

        # -------------------------------------------------
        # EXPIRY
        # -------------------------------------------------

        today = date.today()

        expiry_year = today.year + 3

        expiry_date = (
            f"{today.month:02d}/"
            f"{str(expiry_year)[-2:]}"
        )

        # -------------------------------------------------
        # INSERT CARD
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO cards
            (
                user_id,
                card_number,
                card_type,
                card_network,
                expiry_date,
                card_holder,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'Active'
            )
            """,
            (
                session["user_id"],
                card_number,
                card_type,
                card_network,
                expiry_date,
                card_holder
            )
        )

        connection.commit()

        return jsonify({

            "success": True,

            "message":
                "Your new debit card has been added successfully."

        }), 201

    except Exception as error:

        if connection:
            connection.rollback()

        print(
            "CREATE CARD ERROR:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to create new card."

        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# ADD CARD ALIAS
# =========================================================

@app.route(
    "/api/cards/add",
    methods=["POST"]
)
def add_card():

    return create_card()


# =========================================================
# TOGGLE CARD FREEZE
# =========================================================

@app.route(
    "/api/cards/toggle-freeze",
    methods=["POST"]
)
def toggle_card_freeze():

    if not is_logged_in():

        return jsonify({

            "success": False,

            "message":
                "Please login first."

        }), 401

    data = request.get_json() or {}

    card_id = data.get("card_id")

    if not card_id:

        return jsonify({

            "success": False,

            "message":
                "Card information is missing."

        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
                status
            FROM cards
            WHERE id = %s
            AND user_id = %s
            LIMIT 1
            """,
            (
                card_id,
                session["user_id"]
            )
        )

        card = cursor.fetchone()

        if not card:

            return jsonify({

                "success": False,

                "message":
                    "Card not found."

            }), 404

        if card["status"] == "Frozen":

            new_status = "Active"

            message = (
                "Your card has been unfrozen successfully."
            )

        else:

            new_status = "Frozen"

            message = (
                "Your card has been frozen successfully."
            )

        cursor.execute(
            """
            UPDATE cards
            SET status = %s
            WHERE id = %s
            AND user_id = %s
            """,
            (
                new_status,
                card_id,
                session["user_id"]
            )
        )

        connection.commit()

        return jsonify({

            "success": True,

            "message": message,

            "status": new_status

        })

    except Exception as error:

        if connection:
            connection.rollback()

        print(
            "TOGGLE CARD ERROR:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to update card status."

        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# CARD STATUS API
# =========================================================

@app.route(
    "/api/cards/<int:card_id>/status",
    methods=["POST"]
)
def change_card_status(card_id):

    if not is_logged_in():

        return jsonify({

            "success": False,

            "message":
                "Please login first."

        }), 401

    data = request.get_json() or {}

    requested_status = data.get(
        "status"
    )

    if requested_status not in [
        "Active",
        "Frozen"
    ]:

        return jsonify({

            "success": False,

            "message":
                "Invalid card status."

        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE cards
            SET status = %s
            WHERE id = %s
            AND user_id = %s
            """,
            (
                requested_status,
                card_id,
                session["user_id"]
            )
        )

        if cursor.rowcount == 0:

            connection.rollback()

            return jsonify({

                "success": False,

                "message":
                    "Card not found."

            }), 404

        connection.commit()

        if requested_status == "Frozen":

            message = (
                "Your card has been frozen successfully."
            )

        else:

            message = (
                "Your card has been unfrozen successfully."
            )

        return jsonify({

            "success": True,

            "message": message,

            "status":
                requested_status

        })

    except Exception as error:

        if connection:
            connection.rollback()

        print(
            "CARD STATUS ERROR:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to update card status."

        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# CARD DETAILS
# =========================================================

@app.route(
    "/api/cards/<int:card_id>",
    methods=["GET"]
)
def get_card_details(card_id):

    if not is_logged_in():

        return jsonify({

            "success": False,

            "message":
                "Please login first."

        }), 401

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
                card_number,
                card_type,
                card_network,
                expiry_date,
                card_holder,
                status
            FROM cards
            WHERE id = %s
            AND user_id = %s
            LIMIT 1
            """,
            (
                card_id,
                session["user_id"]
            )
        )

        card = cursor.fetchone()

        if not card:

            return jsonify({

                "success": False,

                "message":
                    "Card not found."

            }), 404

        return jsonify({

            "success": True,

            "card": card

        })

    except Exception as error:

        print(
            "CARD DETAILS ERROR:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to load card details."

        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# TRANSACTIONS
# =========================================================

@app.route("/transactions")
def transactions():

    if not is_logged_in():

        return redirect("/")

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        account = get_user_account(
            cursor,
            session["user_id"]
        )

        if not account:

            return "Bank account not found.", 404

        account_id = account["id"]

        # -------------------------------------------------
        # TRANSACTION LIST
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                transaction_type,
                amount,
                description,
                transaction_date
            FROM transactions
            WHERE account_id = %s
            ORDER BY transaction_date DESC, id DESC
            """,
            (account_id,)
        )

        transaction_list = cursor.fetchall()

        for transaction in transaction_list:

            transaction["amount"] = float(
                transaction["amount"] or 0
            )

        # -------------------------------------------------
        # CURRENT BALANCE
        # -------------------------------------------------

        current_balance = calculate_balance(
            cursor,
            account_id
        )

        account["balance"] = float(
            current_balance
        )

        return render_template(

            "transactions.html",

            user_name=session["user_name"],

            user_email=session["user_email"],

            account=account,

            transactions=transaction_list

        )

    except Exception as error:

        print(
            "TRANSACTIONS ERROR:",
            error
        )

        return (
            "Unable to load transactions.",
            500
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# ANALYTICS
# =========================================================

@app.route("/analytics")
def analytics():

    if not is_logged_in():

        return redirect("/")

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        selected_period = request.args.get(
            "period",
            "all"
        )

        allowed_periods = [

            "all",

            "this_month",

            "last_month",

            "6_months"

        ]

        if selected_period not in allowed_periods:

            selected_period = "all"

        # -------------------------------------------------
        # ACCOUNT
        # -------------------------------------------------

        account = get_user_account(
            cursor,
            session["user_id"]
        )

        if not account:

            return "Bank account not found.", 404

        account_id = account["id"]

        # -------------------------------------------------
        # DATE CONDITION
        # -------------------------------------------------

        date_condition = ""

        if selected_period == "this_month":

            date_condition = """
                AND YEAR(transaction_date)
                    = YEAR(CURRENT_DATE())

                AND MONTH(transaction_date)
                    = MONTH(CURRENT_DATE())
            """

        elif selected_period == "last_month":

            date_condition = """
                AND YEAR(transaction_date)
                    = YEAR(
                        DATE_SUB(
                            CURRENT_DATE(),
                            INTERVAL 1 MONTH
                        )
                    )

                AND MONTH(transaction_date)
                    = MONTH(
                        DATE_SUB(
                            CURRENT_DATE(),
                            INTERVAL 1 MONTH
                        )
                    )
            """

        elif selected_period == "6_months":

            date_condition = """
                AND transaction_date >=
                    DATE_SUB(
                        CURRENT_DATE(),
                        INTERVAL 6 MONTH
                    )
            """

        # -------------------------------------------------
        # INCOME
        # -------------------------------------------------

        cursor.execute(

            f"""
            SELECT
                COALESCE(
                    SUM(amount),
                    0
                ) AS total_income
            FROM transactions
            WHERE account_id = %s
            AND transaction_type = 'credit'
            {date_condition}
            """,

            (account_id,)

        )

        income = cursor.fetchone()[
            "total_income"
        ]

        # -------------------------------------------------
        # EXPENSES
        # -------------------------------------------------

        cursor.execute(

            f"""
            SELECT
                COALESCE(
                    SUM(amount),
                    0
                ) AS total_expenses
            FROM transactions
            WHERE account_id = %s
            AND transaction_type = 'debit'
            {date_condition}
            """,

            (account_id,)

        )

        expenses = cursor.fetchone()[
            "total_expenses"
        ]

        income = Decimal(
            str(income or 0)
        )

        expenses = Decimal(
            str(expenses or 0)
        )

        savings = (
            income -
            expenses
        )

        # -------------------------------------------------
        # CURRENT BALANCE
        # -------------------------------------------------

        current_balance = calculate_balance(
            cursor,
            account_id
        )

        account["balance"] = float(
            current_balance
        )

        # -------------------------------------------------
        # MONTHLY DATA
        # -------------------------------------------------

        cursor.execute(

            f"""
            SELECT

                DATE_FORMAT(
                    transaction_date,
                    '%Y-%m'
                ) AS month,

                COALESCE(
                    SUM(
                        CASE

                            WHEN transaction_type =
                                'credit'

                            THEN amount

                            ELSE 0

                        END
                    ),
                    0
                ) AS income,

                COALESCE(
                    SUM(
                        CASE

                            WHEN transaction_type =
                                'debit'

                            THEN amount

                            ELSE 0

                        END
                    ),
                    0
                ) AS expenses

            FROM transactions

            WHERE account_id = %s

            {date_condition}

            GROUP BY
                DATE_FORMAT(
                    transaction_date,
                    '%Y-%m'
                )

            ORDER BY month ASC
            """,

            (account_id,)

        )

        monthly_data = cursor.fetchall()

        for month in monthly_data:

            month["income"] = float(
                month["income"] or 0
            )

            month["expenses"] = float(
                month["expenses"] or 0
            )

        # -------------------------------------------------
        # RECENT TRANSACTIONS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                transaction_type,
                amount,
                description,
                transaction_date
            FROM transactions
            WHERE account_id = %s
            ORDER BY transaction_date DESC, id DESC
            LIMIT 5
            """,
            (account_id,)
        )

        recent_transactions = cursor.fetchall()

        for transaction in recent_transactions:

            transaction["amount"] = float(
                transaction["amount"] or 0
            )

        return render_template(

            "analytics.html",

            user_name=session["user_name"],

            user_email=session["user_email"],

            account=account,

            income=float(income),

            expenses=float(expenses),

            savings=float(savings),

            monthly_data=monthly_data,

            recent_transactions=
                recent_transactions,

            selected_period=
                selected_period

        )

    except Exception as error:

        print(
            "ANALYTICS ERROR:",
            error
        )

        return (
            "Unable to load analytics.",
            500
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# TRANSFER PAGE
# =========================================================

@app.route("/transfer")
def transfer():

    if not is_logged_in():

        return redirect("/")

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        account = get_user_account(
            cursor,
            session["user_id"]
        )

        if not account:

            return "Bank account not found.", 404

        account_id = account["id"]

        current_balance = calculate_balance(
            cursor,
            account_id
        )

        account["balance"] = float(
            current_balance
        )

        return render_template(

            "transfer.html",

            user_name=session["user_name"],

            user_email=session["user_email"],

            account=account

        )

    except Exception as error:

        print(
            "TRANSFER PAGE ERROR:",
            error
        )

        return (
            "Unable to load transfer page.",
            500
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# CHECK RECIPIENT
# =========================================================

@app.route(
    "/api/check-recipient",
    methods=["POST"]
)
def check_recipient():

    if not is_logged_in():

        return jsonify({

            "success": False,

            "message":
                "Please login first."

        }), 401

    data = request.get_json() or {}

    mobile_number = str(
        data.get(
            "mobile_number",
            ""
        )
    ).strip()

    if not mobile_number:

        return jsonify({

            "success": False,

            "message":
                "Mobile number is required."

        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
                name
            FROM users
            WHERE mobile_number = %s
            LIMIT 1
            """,
            (mobile_number,)
        )

        user = cursor.fetchone()

        if not user:

            return jsonify({

                "success": False,

                "message":
                    "No user found with this mobile number."

            }), 404

        if user["id"] == session["user_id"]:

            return jsonify({

                "success": False,

                "message":
                    "You cannot transfer money to yourself."

            }), 400

        return jsonify({

            "success": True,

            "message":
                f"Recipient found: {user['name']}",

            "recipient": {

                "id":
                    user["id"],

                "name":
                    user["name"]

            }

        })

    except Exception as error:

        print(
            "RECIPIENT CHECK ERROR:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to check recipient."

        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# MONEY TRANSFER
# =========================================================

@app.route(
    "/api/transfer",
    methods=["POST"]
)
def transfer_money():

    if not is_logged_in():

        return jsonify({

            "success": False,

            "message":
                "Please login first."

        }), 401

    data = request.get_json() or {}

    recipient_mobile = str(
        data.get(
            "recipient_mobile",
            ""
        )
    ).strip()

    amount = parse_amount(
        data.get("amount")
    )

    description = str(
        data.get(
            "description",
            ""
        )
    ).strip()

    if not recipient_mobile:

        return jsonify({

            "success": False,

            "message":
                "Recipient mobile number is required."

        }), 400

    if amount is None:

        return jsonify({

            "success": False,

            "message":
                "Invalid transfer amount."

        }), 400

    if amount > Decimal("1000000"):

        return jsonify({

            "success": False,

            "message":
                "Maximum transfer amount is ₹10,00,000."

        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # -------------------------------------------------
        # SENDER
        # -------------------------------------------------

        sender_account = get_user_account(
            cursor,
            session["user_id"]
        )

        if not sender_account:

            return jsonify({

                "success": False,

                "message":
                    "Sender account not found."

            }), 404

        sender_account_id = (
            sender_account["id"]
        )

        # -------------------------------------------------
        # SENDER BALANCE
        # -------------------------------------------------

        sender_balance = calculate_balance(
            cursor,
            sender_account_id
        )

        if sender_balance < amount:

            return jsonify({

                "success": False,

                "message":
                    "Insufficient balance."

            }), 400

        # -------------------------------------------------
        # RECIPIENT
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name
            FROM users
            WHERE mobile_number = %s
            LIMIT 1
            """,
            (recipient_mobile,)
        )

        recipient_user = cursor.fetchone()

        if not recipient_user:

            return jsonify({

                "success": False,

                "message":
                    "Recipient not found."

            }), 404

        if recipient_user["id"] == session["user_id"]:

            return jsonify({

                "success": False,

                "message":
                    "You cannot transfer money to yourself."

            }), 400

        # -------------------------------------------------
        # RECIPIENT ACCOUNT
        # -------------------------------------------------

        recipient_account = get_user_account(
            cursor,
            recipient_user["id"]
        )

        if not recipient_account:

            return jsonify({

                "success": False,

                "message":
                    "Recipient account not found."

            }), 404

        recipient_account_id = (
            recipient_account["id"]
        )

        # -------------------------------------------------
        # SENDER TRANSACTION
        # -------------------------------------------------

        sender_description = (
            description
            if description
            else
            f"Transfer to {recipient_user['name']}"
        )

        cursor.execute(
            """
            INSERT INTO transactions
            (
                account_id,
                transaction_type,
                amount,
                description
            )
            VALUES
            (
                %s,
                'debit',
                %s,
                %s
            )
            """,
            (
                sender_account_id,
                amount,
                sender_description
            )
        )

        # -------------------------------------------------
        # RECIPIENT TRANSACTION
        # -------------------------------------------------

        recipient_description = (
            description
            if description
            else
            "Money received"
        )

        cursor.execute(
            """
            INSERT INTO transactions
            (
                account_id,
                transaction_type,
                amount,
                description
            )
            VALUES
            (
                %s,
                'credit',
                %s,
                %s
            )
            """,
            (
                recipient_account_id,
                amount,
                recipient_description
            )
        )

        # -------------------------------------------------
        # SYNC SENDER BALANCE
        # -------------------------------------------------

        new_sender_balance = (
            sync_account_balance(
                cursor,
                sender_account_id
            )
        )

        # -------------------------------------------------
        # SYNC RECIPIENT BALANCE
        # -------------------------------------------------

        sync_account_balance(
            cursor,
            recipient_account_id
        )

        connection.commit()

        return jsonify({

            "success": True,

            "message":
                f"₹{amount:,.2f} sent successfully to "
                f"{recipient_user['name']}.",

            "balance":
                float(new_sender_balance)

        })

    except Exception as error:

        if connection:
            connection.rollback()

        print(
            "TRANSFER ERROR:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Transfer failed. Please try again."

        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# SETTINGS PAGE
# =========================================================

@app.route("/settings")
def settings():

    if not is_logged_in():

        return redirect("/")

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # -------------------------------------------------
        # USER
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                mobile_number
            FROM users
            WHERE id = %s
            LIMIT 1
            """,
            (session["user_id"],)
        )

        user = cursor.fetchone()

        if not user:

            session.clear()

            return redirect("/")

        # -------------------------------------------------
        # ACCOUNT
        # -------------------------------------------------

        account = get_user_account(
            cursor,
            session["user_id"]
        )

        if not account:

            return "Bank account not found.", 404

        return render_template(

            "settings.html",

            user_name=user["name"],

            user_email=user["email"],

            user_mobile=user["mobile_number"],

            account=account

        )

    except Exception as error:

        print(
            "SETTINGS PAGE ERROR:",
            error
        )

        return (
            "Unable to load settings.",
            500
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# UPDATE PROFILE
# =========================================================

@app.route(
    "/api/settings/profile",
    methods=["POST"]
)
def update_profile():

    if not is_logged_in():

        return jsonify({

            "success": False,

            "message":
                "Please login first."

        }), 401

    data = request.get_json() or {}

    name = str(
        data.get(
            "name",
            ""
        )
    ).strip()

    email = str(
        data.get(
            "email",
            ""
        )
    ).strip()

    mobile = str(
        data.get(
            "mobile_number",
            ""
        )
    ).strip()

    if not name or not email:

        return jsonify({

            "success": False,

            "message":
                "Name and email are required."

        }), 400

    if mobile and not mobile.isdigit():

        return jsonify({

            "success": False,

            "message":
                "Mobile number must contain only digits."

        }), 400

    if mobile and len(mobile) != 10:

        return jsonify({

            "success": False,

            "message":
                "Mobile number must contain 10 digits."

        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # -------------------------------------------------
        # EMAIL CHECK
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            AND id != %s
            LIMIT 1
            """,
            (
                email,
                session["user_id"]
            )
        )

        if cursor.fetchone():

            return jsonify({

                "success": False,

                "message":
                    "That email address is already in use."

            }), 409

        # -------------------------------------------------
        # MOBILE CHECK
        # -------------------------------------------------

        if mobile:

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE mobile_number = %s
                AND id != %s
                LIMIT 1
                """,
                (
                    mobile,
                    session["user_id"]
                )
            )

            if cursor.fetchone():

                return jsonify({

                    "success": False,

                    "message":
                        "That mobile number is already registered."

                }), 409

        # -------------------------------------------------
        # UPDATE USER
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE users

            SET
                name = %s,
                email = %s,
                mobile_number = %s

            WHERE id = %s
            """,
            (
                name,
                email,
                mobile or None,
                session["user_id"]
            )
        )

        connection.commit()

        # -------------------------------------------------
        # UPDATE SESSION
        # -------------------------------------------------

        session["user_name"] = name

        session["user_email"] = email

        return jsonify({

            "success": True,

            "message":
                "Profile updated successfully.",

            "user": {

                "name":
                    name,

                "email":
                    email,

                "mobile_number":
                    mobile

            }

        })

    except mysql.connector.Error as error:

        if connection:
            connection.rollback()

        print(
            "PROFILE DATABASE ERROR:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to update profile."

        }), 500

    except Exception as error:

        if connection:
            connection.rollback()

        print(
            "PROFILE UPDATE ERROR:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to update profile."

        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# CHANGE PASSWORD
# =========================================================

@app.route(
    "/api/settings/change-password",
    methods=["POST"]
)
def change_password():

    if not is_logged_in():

        return jsonify({

            "success": False,

            "message":
                "Please login first."

        }), 401

    data = request.get_json() or {}

    current_password = data.get(
        "current_password"
    )

    new_password = data.get(
        "new_password"
    )

    if not current_password or not new_password:

        return jsonify({

            "success": False,

            "message":
                "All password fields are required."

        }), 400

    if len(new_password) < 6:

        return jsonify({

            "success": False,

            "message":
                "Password must contain at least 6 characters."

        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT password
            FROM users
            WHERE id = %s
            LIMIT 1
            """,
            (session["user_id"],)
        )

        user = cursor.fetchone()

        if not user:

            return jsonify({

                "success": False,

                "message":
                    "User account not found."

            }), 404

        if not check_password_hash(

            user["password"],

            current_password

        ):

            return jsonify({

                "success": False,

                "message":
                    "Current password is incorrect."

            }), 401

        hashed_password = (
            generate_password_hash(
                new_password
            )
        )

        cursor.execute(
            """
            UPDATE users
            SET password = %s
            WHERE id = %s
            """,
            (
                hashed_password,
                session["user_id"]
            )
        )

        connection.commit()

        return jsonify({

            "success": True,

            "message":
                "Password changed successfully."

        })

    except Exception as error:

        if connection:
            connection.rollback()

        print(
            "CHANGE PASSWORD ERROR:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to change password."

        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# TEST DATABASE
# =========================================================

@app.route("/test-db")
def test_db():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            "SELECT DATABASE()"
        )

        result = cursor.fetchone()

        return (
            f"Connected to database: "
            f"{result[0]}"
        )

    except Exception as error:

        print(
            "DATABASE ERROR:",
            error
        )

        return (
            "Database connection failed.",
            500
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/api/register",
    methods=["POST"]
)
def register():

    data = request.get_json() or {}

    name = str(
        data.get(
            "name",
            ""
        )
    ).strip()

    email = str(
        data.get(
            "email",
            ""
        )
    ).strip()

    password = data.get(
        "password"
    )

    mobile = str(
        data.get(
            "mobile_number",
            ""
        )
    ).strip()

    if not name or not email or not password:

        return jsonify({

            "success": False,

            "message":
                "All fields are required."

        }), 400

    if len(password) < 6:

        return jsonify({

            "success": False,

            "message":
                "Password must contain at least 6 characters."

        }), 400

    if mobile:

        if not mobile.isdigit():

            return jsonify({

                "success": False,

                "message":
                    "Mobile number must contain only digits."

            }), 400

        if len(mobile) != 10:

            return jsonify({

                "success": False,

                "message":
                    "Mobile number must contain 10 digits."

            }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # -------------------------------------------------
        # EMAIL
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            LIMIT 1
            """,
            (email,)
        )

        if cursor.fetchone():

            return jsonify({

                "success": False,

                "message":
                    "Email already registered."

            }), 409

        # -------------------------------------------------
        # MOBILE
        # -------------------------------------------------

        if mobile:

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE mobile_number = %s
                LIMIT 1
                """,
                (mobile,)
            )

            if cursor.fetchone():

                return jsonify({

                    "success": False,

                    "message":
                        "Mobile number already registered."

                }), 409

        # -------------------------------------------------
        # HASH PASSWORD
        # -------------------------------------------------

        hashed_password = (
            generate_password_hash(
                password
            )
        )

        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                mobile_number,
                password
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                name,
                email,
                mobile or None,
                hashed_password
            )
        )

        user_id = cursor.lastrowid

        # -------------------------------------------------
        # GENERATE ACCOUNT NUMBER
        # -------------------------------------------------

        account_number = None

        for _ in range(20):

            generated_account = "".join(

                str(random.randint(0, 9))

                for _ in range(12)

            )

            cursor.execute(
                """
                SELECT id
                FROM accounts
                WHERE account_number = %s
                LIMIT 1
                """,
                (generated_account,)
            )

            if not cursor.fetchone():

                account_number = (
                    generated_account
                )

                break

        if not account_number:

            connection.rollback()

            return jsonify({

                "success": False,

                "message":
                    "Unable to create bank account."

            }), 500

        # -------------------------------------------------
        # CREATE ACCOUNT
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO accounts
            (
                user_id,
                account_number,
                balance
            )
            VALUES
            (
                %s,
                %s,
                0
            )
            """,
            (
                user_id,
                account_number
            )
        )

        connection.commit()

        return jsonify({

            "success": True,

            "message":
                "Registration successful.",

            "account_number":
                account_number

        }), 201

    except Exception as error:

        if connection:
            connection.rollback()

        print(
            "REGISTRATION ERROR:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Registration failed."

        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/api/login",
    methods=["POST"]
)
def login():

    data = request.get_json() or {}

    email = str(
        data.get(
            "email",
            ""
        )
    ).strip()

    password = data.get(
        "password"
    )

    if not email or not password:

        return jsonify({

            "success": False,

            "message":
                "Email and password are required."

        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                password
            FROM users
            WHERE email = %s
            LIMIT 1
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:

            return jsonify({

                "success": False,

                "message":
                    "Invalid email or password."

            }), 401

        if not check_password_hash(

            user["password"],

            password

        ):

            return jsonify({

                "success": False,

                "message":
                    "Invalid email or password."

            }), 401

        # -------------------------------------------------
        # SESSION
        # -------------------------------------------------

        session.clear()

        session["user_id"] = user["id"]

        session["user_name"] = user["name"]

        session["user_email"] = user["email"]

        return jsonify({

            "success": True,

            "message":
                "Login successful.",

            "redirect":
                "/dashboard",

            "user": {

                "id":
                    user["id"],

                "name":
                    user["name"],

                "email":
                    user["email"]

            }

        })

    except Exception as error:

        print(
            "LOGIN ERROR:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Login failed."

        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )