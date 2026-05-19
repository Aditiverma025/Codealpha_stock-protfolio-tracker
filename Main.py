import csv
from datetime import datetime
from pathlib import Path

PORTFOLIO_FILE = Path("portfolio.csv")
TRANSACTION_FILE = Path("transactions.csv")
REPORT_FILE = Path("portfolio_report.txt")

STOCK_PRICES = {
    "AAPL": 180,
    "TSLA": 250,
    "GOOGL": 140,
    "MSFT": 330,
    "AMZN": 145,
    "META": 320,
    "NFLX": 410,
    "NVDA": 875,
    "INFY": 18,
    "TCS": 45
}


def create_files():
    if not PORTFOLIO_FILE.exists():
        with open(PORTFOLIO_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Stock", "Quantity", "Average_Buy_Price"])

    if not TRANSACTION_FILE.exists():
        with open(TRANSACTION_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Type", "Stock", "Quantity", "Price", "Total_Value"])


def load_portfolio():
    portfolio = {}

    with open(PORTFOLIO_FILE, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["Stock"]:
                portfolio[row["Stock"]] = {
                    "quantity": int(row["Quantity"]),
                    "avg_buy_price": float(row["Average_Buy_Price"])
                }

    return portfolio


def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Stock", "Quantity", "Average_Buy_Price"])

        for stock, data in portfolio.items():
            writer.writerow([
                stock,
                data["quantity"],
                round(data["avg_buy_price"], 2)
            ])


def record_transaction(action, stock, quantity, price):
    total_value = quantity * price

    with open(TRANSACTION_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%d-%m-%Y %I:%M %p"),
            action,
            stock,
            quantity,
            price,
            total_value
        ])


def get_valid_stock():
    stock = input("Enter stock symbol: ").upper().strip()

    if stock not in STOCK_PRICES:
        print("Invalid stock symbol.")
        return None

    return stock


def get_valid_quantity(message="Enter quantity: "):
    try:
        quantity = int(input(message))

        if quantity <= 0:
            print("Quantity must be greater than zero.")
            return None

        return quantity

    except ValueError:
        print("Please enter a valid number.")
        return None


def show_available_stocks():
    print("\nAvailable Stocks")
    print("-" * 30)
    print(f"{'Symbol':<10}{'Price':>10}")
    print("-" * 30)

    for stock, price in STOCK_PRICES.items():
        print(f"{stock:<10}${price:>9}")

    print("-" * 30)


def buy_stock(portfolio):
    show_available_stocks()

    stock = get_valid_stock()
    if stock is None:
        return

    quantity = get_valid_quantity()
    if quantity is None:
        return

    price = STOCK_PRICES[stock]
    total_cost = quantity * price

    if stock in portfolio:
        old_quantity = portfolio[stock]["quantity"]
        old_avg_price = portfolio[stock]["avg_buy_price"]

        new_quantity = old_quantity + quantity
        new_avg_price = ((old_quantity * old_avg_price) + total_cost) / new_quantity

        portfolio[stock]["quantity"] = new_quantity
        portfolio[stock]["avg_buy_price"] = new_avg_price

    else:
        portfolio[stock] = {
            "quantity": quantity,
            "avg_buy_price": price
        }

    save_portfolio(portfolio)
    record_transaction("BUY", stock, quantity, price)

    print(f"\nBought {quantity} shares of {stock}.")
    print(f"Total Cost: ${total_cost:.2f}")


def sell_stock(portfolio):
    if not portfolio:
        print("\nPortfolio is empty. Buy stocks first.")
        return

    view_portfolio(portfolio)

    stock = input("\nEnter stock symbol to sell: ").upper().strip()

    if stock not in portfolio:
        print("You do not own this stock.")
        return

    quantity = get_valid_quantity("Enter quantity to sell: ")
    if quantity is None:
        return

    owned_quantity = portfolio[stock]["quantity"]

    if quantity > owned_quantity:
        print("You cannot sell more shares than you own.")
        return

    price = STOCK_PRICES[stock]
    sell_value = quantity * price

    portfolio[stock]["quantity"] -= quantity

    if portfolio[stock]["quantity"] == 0:
        del portfolio[stock]

    save_portfolio(portfolio)
    record_transaction("SELL", stock, quantity, price)

    print(f"\nSold {quantity} shares of {stock}.")
    print(f"Sell Value: ${sell_value:.2f}")


def view_portfolio(portfolio):
    if not portfolio:
        print("\nPortfolio is empty.")
        return

    print("\nPortfolio Summary")
    print("-" * 85)
    print(
        f"{'Stock':<8}"
        f"{'Qty':>6}"
        f"{'Avg Buy':>12}"
        f"{'Current':>12}"
        f"{'Invested':>13}"
        f"{'Value':>13}"
        f"{'P/L':>13}"
    )
    print("-" * 85)

    total_invested = 0
    total_value = 0

    for stock, data in portfolio.items():
        quantity = data["quantity"]
        avg_buy_price = data["avg_buy_price"]
        current_price = STOCK_PRICES[stock]

        invested = quantity * avg_buy_price
        current_value = quantity * current_price
        profit_loss = current_value - invested

        total_invested += invested
        total_value += current_value

        print(
            f"{stock:<8}"
            f"{quantity:>6}"
            f"${avg_buy_price:>11.2f}"
            f"${current_price:>11.2f}"
            f"${invested:>12.2f}"
            f"${current_value:>12.2f}"
            f"${profit_loss:>12.2f}"
        )

    print("-" * 85)
    print(f"Total Invested Value : ${total_invested:.2f}")
    print(f"Current Market Value : ${total_value:.2f}")
    print(f"Overall Profit/Loss  : ${total_value - total_invested:.2f}")


def view_transactions():
    if not TRANSACTION_FILE.exists():
        print("\nNo transactions found.")
        return

    with open(TRANSACTION_FILE, "r") as file:
        reader = csv.DictReader(file)
        transactions = list(reader)

    if not transactions:
        print("\nNo transactions found.")
        return

    print("\nTransaction History")
    print("-" * 80)
    print(
        f"{'Date':<20}"
        f"{'Type':<8}"
        f"{'Stock':<8}"
        f"{'Qty':>6}"
        f"{'Price':>12}"
        f"{'Total':>14}"
    )
    print("-" * 80)

    for row in transactions:
        print(
            f"{row['Date']:<20}"
            f"{row['Type']:<8}"
            f"{row['Stock']:<8}"
            f"{row['Quantity']:>6}"
            f"${float(row['Price']):>11.2f}"
            f"${float(row['Total_Value']):>13.2f}"
        )


def search_stock():
    stock = input("\nEnter stock symbol to search: ").upper().strip()

    if stock in STOCK_PRICES:
        print(f"{stock} current price is ${STOCK_PRICES[stock]:.2f}")
    else:
        print("Stock not found.")


def generate_report(portfolio):
    with open(REPORT_FILE, "w") as file:
        file.write("Advanced Stock Portfolio Tracker Report\n")
        file.write("=" * 45 + "\n")
        file.write("Developer: aditi verma\n")
        file.write("Internship: CodeAlpha Python Programming Internship\n")
        file.write(f"Generated On: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}\n\n")

        if not portfolio:
            file.write("Portfolio is empty.\n")
        else:
            total_invested = 0
            total_value = 0

            for stock, data in portfolio.items():
                quantity = data["quantity"]
                avg_buy_price = data["avg_buy_price"]
                current_price = STOCK_PRICES[stock]

                invested = quantity * avg_buy_price
                current_value = quantity * current_price
                profit_loss = current_value - invested

                total_invested += invested
                total_value += current_value

                file.write(f"Stock: {stock}\n")
                file.write(f"Quantity: {quantity}\n")
                file.write(f"Average Buy Price: ${avg_buy_price:.2f}\n")
                file.write(f"Current Price: ${current_price:.2f}\n")
                file.write(f"Invested Value: ${invested:.2f}\n")
                file.write(f"Current Value: ${current_value:.2f}\n")
                file.write(f"Profit/Loss: ${profit_loss:.2f}\n")
                file.write("-" * 45 + "\n")

            file.write(f"\nTotal Invested Value: ${total_invested:.2f}\n")
            file.write(f"Current Market Value: ${total_value:.2f}\n")
            file.write(f"Overall Profit/Loss: ${total_value - total_invested:.2f}\n")

    print(f"\nReport generated successfully: {REPORT_FILE}")


def show_menu():
    print("""
====================================================
        ADVANCED STOCK PORTFOLIO TRACKER
====================================================
Developer : aditi verma
Internship: CodeAlpha Python Programming Internship
----------------------------------------------------
1. View Available Stocks
2. Buy Stock
3. Sell Stock
4. View Portfolio Summary
5. View Transaction History
6. Search Stock Price
7. Generate Portfolio Report
8. Exit
====================================================
""")


def main():
    create_files()
    portfolio = load_portfolio()

    while True:
        show_menu()

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            show_available_stocks()

        elif choice == "2":
            buy_stock(portfolio)

        elif choice == "3":
            sell_stock(portfolio)

        elif choice == "4":
            view_portfolio(portfolio)

        elif choice == "5":
            view_transactions()

        elif choice == "6":
            search_stock()

        elif choice == "7":
            generate_report(portfolio)

        elif choice == "8":
            print("\nThank you for using Advanced Stock Portfolio Tracker.")
            break

        else:
            print("Invalid choice. Please select between 1 and 8.")


if __name__ == "__main__":
    main()
