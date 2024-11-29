from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime
import csv
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Klucz do przechowywania sesji

# Strona główna formularza
@app.route('/')
def index():
    return render_template("form.html")

# Strona, która wyświetli listę promocji
@app.route('/promotions')
def promotions():
    promotions_list = get_promotions_from_file()
    return render_template("promotions.html", promotions=promotions_list)

# Obsługa formularza
@app.route('/submit', methods=['POST'])
def submit():
    promotion_name = request.form['promotion_name']
    barcode_plu = request.form['barcode_plu']
    net_price = float(request.form['net_price'])
    gross_price = float(request.form['gross_price'])
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    stores = request.form.getlist('stores')
    conditions = request.form['conditions']

    # Sprawdzanie, czy cena sprzedaży brutto nie jest mniejsza niż cena netto
    if gross_price <= net_price:
        send_email("Niepoprawna cena", f"Cena brutto jest mniejsza niż cena netto dla promocji {promotion_name}.")
        flash("Cena brutto jest mniejsza lub równa cenie netto, czy na pewno chcesz to wysłać?", 'danger')

    save_promotion(promotion_name, barcode_plu, net_price, gross_price, start_date, end_date, stores, conditions)

    return redirect(url_for('promotions'))

# Funkcja zapisująca promocję do pliku CSV
def save_promotion(promotion_name, barcode_plu, net_price, gross_price, start_date, end_date, stores, conditions):
    with open('promotions.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([promotion_name, barcode_plu, net_price, gross_price, start_date, end_date, ','.join(stores), conditions])

# Funkcja, która wysyła e-mail
def send_email(subject, body):
    sender = "your-email@example.com"
    recipient = "recipient@example.com"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    
    with smtplib.SMTP('smtp.example.com') as server:
        server.login("your-email@example.com", "your-password")
        server.sendmail(sender, recipient, msg.as_string())

# Funkcja do pobrania danych z pliku CSV
def get_promotions_from_file():
    promotions = []
    try:
        with open('promotions.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                promotions.append(row)
    except FileNotFoundError:
        pass  # Jeśli plik nie istnieje, to nie ma promocji
    return promotions

if __name__ == '__main__':
    app.run(debug=True)
