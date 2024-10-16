from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector as ms
import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# MySQL connection setup
mycon = ms.connect(host="localhost", user="root", passwd="your_new_password", database="don")
mycur = mycon.cursor()

# Create tables if not exist
mycur.execute("""
    CREATE TABLE IF NOT EXISTS Bank(
        AccNo INT PRIMARY KEY AUTO_INCREMENT,
        AccountName VARCHAR(20),
        Age INT,
        Gender CHAR(1),
        Balance INT,
        DOC DATETIME,
        LastLogin DATETIME
    )
""")
mycon.commit()

# Home page with options
@app.route('/')
def index():
    return render_template('index.html')

# Route for creating an account
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        account_name = request.form['accountName']
        age = int(request.form['age'])
        gender = request.form['gender']
        balance = int(request.form['balance'])

        # Insert data into the Bank table
        now = datetime.datetime.now()
        mycur.execute("""
            INSERT INTO Bank (AccountName, Age, Gender, Balance, DOC)
            VALUES (%s, %s, %s, %s, %s)
        """, (account_name, age, gender, balance, now))
        mycon.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('create_account.html')

# Route for depositing money
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        acc_no = int(request.form['accNo'])
        deposit_amount = int(request.form['amount'])

        # Update the balance in the Bank table
        mycur.execute("UPDATE Bank SET Balance = Balance + %s WHERE AccNo = %s", (deposit_amount, acc_no))
        mycon.commit()

        flash('Deposit successful!', 'success')
        return redirect(url_for('index'))

    return render_template('deposit.html')

# Route for withdrawing money
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        acc_no = int(request.form['accNo'])
        withdraw_amount = int(request.form['amount'])

        # Check if balance is sufficient
        mycur.execute("SELECT Balance FROM Bank WHERE AccNo = %s", (acc_no,))
        balance = mycur.fetchone()[0]
        if balance >= withdraw_amount:
            # Update the balance
            mycur.execute("UPDATE Bank SET Balance = Balance - %s WHERE AccNo = %s", (withdraw_amount, acc_no))
            mycon.commit()

            flash('Withdrawal successful!', 'success')
        else:
            flash('Insufficient balance!', 'danger')

        return redirect(url_for('index'))

    return render_template('withdraw.html')

# Route for checking balance
@app.route('/check_balance', methods=['GET', 'POST'])
def check_balance():
    if request.method == 'POST':
        acc_no = int(request.form['accNo'])

        # Retrieve the balance
        mycur.execute("SELECT Balance FROM Bank WHERE AccNo = %s", (acc_no,))
        balance = mycur.fetchone()

        if balance:
            return render_template('check_balance.html', balance=balance[0])
        else:
            flash('Account not found!', 'danger')

    return render_template('check_balance.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
