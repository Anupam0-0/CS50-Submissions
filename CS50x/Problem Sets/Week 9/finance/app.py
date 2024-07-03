import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Necesito lista de dicts {symbol, name, shares, price, total} para mandar a index.html

    # Obtener rows de portfolios que pertenezcan a usuario
    # Con JOIN se obtiene symbol, name y shares - ¡En orden alfabético por symbol!
    user_portfolio = db.execute(
        "SELECT * FROM portfolios JOIN stocks ON portfolios.stock_id = stocks.id WHERE portfolios.user_id = ? ORDER BY stocks.symbol;",
        session["user_id"],
    )
    # return "{}".format(user_portfolio) # DEBUG

    # Inicializar gran total en 0
    grand_total = float(0)

    # Loop en user_portfolio para hacer lookup de price y calcular row_total
    for portfolio_row in user_portfolio:

        # Obtener info desde IEX, chequear si existe respuesta
        info = lookup(portfolio_row["symbol"])
        if not info:
            return apology("internal server error", 400)
        # return "{}".format(info) # DEBUG

        # Obtener price, calcular total del row
        row_price = float(info["price"])
        row_total = row_price * portfolio_row["shares"]

        # row_price = float(lookup(portfolio_row["symbol"])["price"])

        # Agregar nuevos valores a diccionario portfolio_row
        portfolio_row["price"] = row_price
        portfolio_row["total"] = row_total

        # Actualizar gran total
        grand_total += row_total

        # Calcular outflow_balance de cada row
        transacciones = db.execute(
            "SELECT * FROM transacciones WHERE stock_id IN (SELECT id FROM stocks WHERE symbol=?) AND user_id=?;",
            portfolio_row["symbol"],
            session["user_id"],
        )
        outflow_balance = 0
        for row in transacciones:
            outflow_balance += row["price"] * row["shares"]
        portfolio_row["outflow_balance"] = outflow_balance

    # Test si outflow_balance está saliendo
    # return "{}".format(user_portfolio) # OK!!

    # Obtener cash de usuario y gran total
    cash = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])[0]["cash"]
    grand_total += cash

    # Render index.html, pasar: user_portfolio, cash, grand_total
    return render_template(
        "index.html", user_portfolio=user_portfolio, cash=cash, grand_total=grand_total
    )
    # return "{}, {}, {}".format(portfolio_list, fg_total, fcash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":

        # Tomar input de usuario: symbol y shares
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        if not symbol or not shares:
            return apology("missing symbol or shares", 400)

        # INTENTAR CONVERTIR EN FLOAT (Para descubrir si contiene characters inválidos)
        try:
            shares = float(shares)
        except:
            return apology("must be numeric!", 400)

        # HANDLE FRACTIONAL AND NEGATIVE VALUES
        if shares % 1 != 0:
            return apology("no fraction!", 400)
        if shares <= 0:
            return apology("no negative! (float)", 400)

        # Hacer lookup de symbol y chequear si es válido
        business_info = lookup(symbol)
        if not business_info:
            return apology("invalid symbol", 400)

        # Variables importantes: symbol, name, price, cash, shares, spending, datetime
        # symbol OK (arriba)
        name = business_info["name"]
        price = float(
            business_info["price"]
        )  # Convertido en float porque viene como string de lookup... creo...
        user_info = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])
        cash = user_info[0]["cash"]
        # shares OK (arriba)
        spending = price * shares
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Chequear si hay suficiente cash para realizar la compra
        if spending > cash:
            return apology("not enough cash", 400)

        # REALIZAR LA COMPRA
        # INSERT en stocks, INSERT o UPDATE en portfolios, INSERT en transacciones

        # Buscar symbol en stocks.
        stored_stock = db.execute("SELECT * FROM stocks WHERE symbol=?;", symbol)

        # Si no existe, insertar symbol y name en stocks, insertar shares en portfolios, insertar info en transacciones
        if not stored_stock:
            stock_id = db.execute(
                "INSERT INTO stocks(symbol, name) VALUES(?, ?);", symbol, name
            )
            db.execute(
                "INSERT INTO portfolios(user_id, stock_id, shares) VALUES(?, ?, ?);",
                session["user_id"],
                stock_id,
                shares,
            )
            db.execute(
                "INSERT INTO transacciones(user_id, stock_id, shares, price, p_datetime) VALUES(?, ?, ?, ?, ?);",
                session["user_id"],
                stock_id,
                shares,
                price,
                dt,
            )
        # Si ya existe symbol en stocks, debo chequear si user tiene shares en portfolio. No tiene: INSERT. Si tiene: UPDATE.
        else:
            stock_id = stored_stock[0]["id"]
            owned_stock = db.execute(
                "SELECT * FROM portfolios WHERE user_id=? AND stock_id=?;",
                session["user_id"],
                stock_id,
            )
            # User NO TIENE shares
            if not owned_stock:
                db.execute(
                    "INSERT INTO portfolios(user_id, stock_id, shares) VALUES(?, ?, ?);",
                    session["user_id"],
                    stock_id,
                    shares,
                )
                # db.execute("INSERT INTO transacciones(user_id, stock_id, shares, price, p_datetime) VALUES(?, ?, ?, ?, ?);", session["user_id"], stock_id, shares, price, dt)
            # User SI TIENE shares
            else:
                # Averiguar cuántos shares ya tiene, sumarle nuevos shares comprados, UPDATE total_shares en porftolios
                owned_shares = owned_stock[0]["shares"]
                total_shares = owned_shares + shares
                db.execute(
                    "UPDATE portfolios SET shares=? WHERE user_id=? AND stock_id=?;",
                    total_shares,
                    session["user_id"],
                    stock_id,
                )

            db.execute(
                "INSERT INTO transacciones(user_id, stock_id, shares, price, p_datetime) VALUES(?, ?, ?, ?, ?);",
                session["user_id"],
                stock_id,
                shares,
                price,
                dt,
            )

        # Actualizar cash de usuario
        cash = cash - spending
        db.execute("UPDATE users SET cash=? WHERE id=?;", cash, session["user_id"])

        # Redirigir a index
        flash("Bought!", "message")
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Obtener rows de TABLE transacciones que pertenecen al usuario
    user_history = db.execute(
        "SELECT * FROM transacciones WHERE user_id=?;", session["user_id"]
    )

    # Hacer loop para agregar symbol a cada row (dict) de user_history
    for row in user_history:
        row["symbol"] = db.execute("SELECT * FROM stocks WHERE id=?;", row["stock_id"])[
            0
        ]["symbol"]

    return render_template("history.html", user_history=user_history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")

        # Retorna diccionario con información de empresa. Ej. {'name': 'Apple Inc', 'price': 172.17, 'symbol': 'AAPL'}
        info = lookup(symbol)

        # Error check input de symbol
        if not info:
            return apology("Invalid Symbol", 400)

        # Se llama a sí misma pero avisa que info existe -- foo=True
        return render_template("quote.html", info=info, foo=True)

        # return "{}".format(info)

    else:
        return render_template("quote.html", foo=False)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        passConf = request.form.get("confirmation")

        if not username:
            return apology("missing username", 400)
        if not password:
            return apology("missing password", 400)
        if not passConf:
            return apology("missing password confirmation", 400)
        if password != passConf:
            return apology("invalid password confirmation", 400)

        # Chequear si username está disponible
        foo = db.execute("SELECT * FROM users WHERE username=?;", username)
        if len(foo) == 1:
            return apology("username unavailable", 400)

        db.execute(
            "INSERT INTO users(username, hash) VALUES(?, ?);",
            username,
            generate_password_hash(password),
        )
        # return "REGISTERED!"
        # return render_template("not-alone.html", username=username, password=password, passConf=passConf)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Remember which user has logged in -- saca id de rows y lo guarda en session
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Registered!", "message")
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":

        # Obtener symbol y shares que se quieren vender
        selling_symbol = request.form.get("symbol")
        selling_shares = int(request.form.get("shares"))

        # Chequear si existe input
        if not selling_symbol or not selling_shares:
            return apology("missing symbol or shares", 400)

        # Chequear si existe el symbol en stocks
        stored_stock = db.execute(
            "SELECT * FROM stocks WHERE symbol=?;", selling_symbol
        )
        if not stored_stock:
            return apology("no stocks to sell", 400)

        # Chequear si existe stock en portfolio de user
        owned_stock = db.execute(
            "SELECT * FROM portfolios WHERE user_id=? AND stock_id=?;",
            session["user_id"],
            stored_stock[0]["id"],
        )
        if not owned_stock:
            return apology("no stocks to sell", 400)

        # Chequear si existen suficientes shares para realizar la venta
        available_shares = int(owned_stock[0]["shares"])
        if available_shares < selling_shares:
            return apology("insufficient shares to sell", 400)

        # Calcular nuevo total de available shares
        total_shares = available_shares - selling_shares

        # Actualizar shares en portfolio de usuario (table portfolios)

        # Si nuevo total es mayor a 0, actualizar table
        if total_shares > 0:
            db.execute(
                "UPDATE portfolios SET shares=? WHERE user_id=? AND stock_id=?;",
                total_shares,
                session["user_id"],
                stored_stock[0]["id"],
            )
        # Pero si nuevo total es cero shares, eliminar row de portfolio de usuario
        else:
            db.execute(
                "DELETE FROM portfolios WHERE user_id=? AND stock_id=?;",
                session["user_id"],
                stored_stock[0]["id"],
            )

        # Sumar fondos de venta a cash de usuario (table users)
        current_price = float(lookup(selling_symbol)["price"])
        # stock_info = lookup(selling_symbol)
        # current_price = float(stock_info["price"])
        income = current_price * selling_shares
        user_info = db.execute("SELECT * FROM users WHERE id=?;", session["user_id"])
        total_cash = user_info[0]["cash"] + income
        db.execute(
            "UPDATE users SET cash=? WHERE id=?;", total_cash, session["user_id"]
        )

        db.execute(
            "INSERT INTO transacciones(user_id, stock_id, shares, price, p_datetime) VALUES(?, ?, ?, ?, ?);",
            session["user_id"],
            stored_stock[0]["id"],
            selling_shares * -1,
            current_price,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        # Redirigir a index
        flash("Sold!", "message")
        return redirect("/")

    else:
        user_portfolio = db.execute(
            "SELECT * FROM stocks WHERE id IN (SELECT stock_id FROM portfolios WHERE user_id=?);",
            session["user_id"],
        )
        return render_template("sell.html", user_portfolio=user_portfolio)


@app.route("/changePassword", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":

        # Chequear si existe input
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        new_password_confirmation = request.form.get("new_password_confirmation")
        if not current_password or not new_password or not new_password_confirmation:
            return apology("missing input", 403)

        # Chequear si current password es correcto
        hash = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])[0][
            "hash"
        ]
        if not check_password_hash(hash, current_password):
            return apology("invalid password", 403)

        # Chequear si confirmación es correcta
        if new_password != new_password_confirmation:
            return apology("invalid confirmation", 403)

        # Chequear si nuevo password es igual al anterior
        if check_password_hash(hash, new_password):
            return apology("must provide different password", 403)

        # Actualizar password
        new_hash = generate_password_hash(new_password)
        db.execute("UPDATE users SET hash=? WHERE id=?;", new_hash, session["user_id"])

        flash("Password Changed!", "message")
        return redirect("/")

    else:
        return render_template("changePassword.html")
