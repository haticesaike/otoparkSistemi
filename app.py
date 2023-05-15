from flask import Flask, render_template, flash, redirect, url_for, session, logging, request

import pyodbc

cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=DESKTOP-TFQCHFC;"
                      "Database=otoparkSistemi;"
                      "Trusted_Connection=yes;")

cursor = cnxn.cursor()

app = Flask(__name__)
app.secret_key = "Hatice-Oznur"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":
        otoparkAdi = request.form["name"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        sorgu = "Select * From Otopark where username = ?"
        cursor.execute(sorgu, username)
        otoparklar = cursor.fetchall()

        print(otoparklar)
        if len(otoparklar) > 0:
            flash("Böyle bir kullanıcı bulunmaktadır. Lüften farklı bir kullanıcı adıyla kayıt olunuz.", "red")
            return redirect(url_for("register"))

        sorgu = "INSERT INTO Otopark (otopark_adi, username, password, email) values (?,?,?,?)"
        cursor.execute(sorgu, otoparkAdi, username, password, email)
        cnxn.commit()

        flash("Başarıyla kayıt oldunuz.", "green")
        return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sorgu = "Select * From Otopark where username = ?"
        cursor.execute(sorgu, username)
        otopark = cursor.fetchone()

        if not otopark:
            flash("Kullanıcı adınız yanlış.", "red")
            return redirect(url_for("login"))

        if otopark[3] != password:
            flash("Şifreniz yanlış.", "red")
            return redirect(url_for("login"))

        session["logged_in"] = True
        session["otopark_id"] = otopark[0]
        session["otopark_adi"] = otopark[1]

        flash("Sisteme başarıyla giriş yaptınız.", "green")
        return redirect(url_for("index"))


##########################
######## PERSONEL ########
##########################
@app.route("/personel", methods=["GET", "POST"])
def personel():
    if request.method == "GET":
        return render_template("personel.html")


@app.route("/personellerim", methods=["GET", "POST"])
def personellerim():
    if request.method == "GET":
        sorgu = "Select * From Personel where otopark_id = ?"
        cursor.execute(sorgu, session["otopark_id"])
        db_personeller = cursor.fetchall()

        return render_template("personellerim.html", liste_uzunluk=len(db_personeller), otoparkAdi=session["otopark_adi"], personeller=db_personeller)


@app.route("/personel_ekle", methods=["GET", "POST"])
def personel_ekle():
    if request.method == "GET":
        return render_template("personel_ekle.html")

    elif request.method == "POST":
        personel_adi = request.form["name"]
        personel_soyadi = request.form["surname"]
        telefonNumarasi = request.form["telNo"]
        mesai = request.form["mesai"]
        try:
            mesai = int(mesai)
        except:
            flash("Haftalık çalışma süresi olarak integer tipinde değer giriniz.", "red")
            return redirect(url_for("personel_ekle"))

        sorgu = "INSERT INTO Personel (otopark_id, isim, soyisim, tel_no, haftalik_calisma_suresi) values (?,?,?,?,?)"
        cursor.execute(sorgu, session["otopark_id"], personel_adi, personel_soyadi, telefonNumarasi, mesai)
        cnxn.commit()
        flash("Başarıyla personel eklediniz.", "green")
        return redirect(url_for("personel"))


@app.route("/personel_cikar", methods=["GET", "POST"])
def personel_cikart():
    if request.method == "GET":
        return render_template("personel_cikart.html")

    elif request.method == "POST":
        personel_adi = request.form["name"]
        personel_soyadi = request.form["surname"]

        sorgu = "DELETE FROM Personel where isim = ? AND soyisim = ?"
        cursor.execute(sorgu, personel_adi, personel_soyadi)
        cnxn.commit()

        flash("Başarıyla personeli kaldırdınız.", "green")
        return redirect(url_for("personel"))


##########################
####### PARK KATI ########
##########################
@app.route("/park_alani", methods=["GET"])
def park_alani():
    if request.method == "GET":
        return render_template("park_alani.html")


@app.route("/park_alanlari", methods=["GET"])
def park_alanlari():
    if request.method == "GET":
        sorgu = "Select * From Park_Alani where otopark_id = ?"
        cursor.execute(sorgu, session["otopark_id"])
        db_parklar = cursor.fetchall()
        return render_template("park_alanlari.html", otoparkAdi=session["otopark_adi"], liste_uzunluk=len(db_parklar), parklar=db_parklar)


@app.route("/park_alani_ekle", methods=["GET", "POST"])
def park_alani_ekle():
    if request.method == "GET":
        return render_template("park_alani_ekle.html")

    elif request.method == "POST":
        park_kati_adi = request.form["name"]
        parktaki_alan = request.form["yer"]

        try:
            parktaki_alan = int(parktaki_alan)
        except:
            flash("Parktaki toplam yer miktarı olarak integer tipinde değer giriniz.", "red")
            return redirect(url_for("park_alani_ekle"))

        sorgu = "INSERT INTO Park_Alani (otopark_id, adi, bos_alan, dolu_alan) values (?,?,?,?)"
        cursor.execute(sorgu, session["otopark_id"], park_kati_adi, parktaki_alan, 0)
        cnxn.commit()

        flash("Başarıyla park alanı oluşturdunuz.", "green")
        return redirect(url_for("park_alani"))


@app.route("/park_alani_cikar", methods=["GET", "POST"])
def park_alani_cikar():
    if request.method == "GET":
        return render_template("park_alani_cikar.html")

    elif request.method == "POST":
        park_kati_adi = request.form["name"]

        sorgu = "DELETE FROM Park_Alani where otopark_id = ? AND adi = ?"
        cursor.execute(sorgu, session["otopark_id"], park_kati_adi)
        cnxn.commit()

        flash("Başarıyla park alanını sildiniz.", "green")
        return redirect(url_for("park_alani"))


@app.route("/parka_arac_ekle", methods=["GET", "POST"])
def parka_arac_ekle():
    if request.method == "GET":
        return render_template("parka_arac_ekle.html")

    elif request.method == "POST":
        park_kati_adi = request.form["name"]
        giren_arac = request.form["sayi"]

        try:
            giren_arac = int(giren_arac)
        except:
            flash("Giriş yapan araç sayısını integer tipinde değer giriniz.", "red")
            return redirect(url_for("park_alani_ekle"))

        sorgu = "Select * From Park_Alani where otopark_id = ? AND adi = ?"
        cursor.execute(sorgu, session["otopark_id"], park_kati_adi)
        db_park = cursor.fetchone()

        if db_park[3] < giren_arac:
            flash("Otoparkta yeterli yer yok.", "red")
            return redirect(url_for("parka_arac_ekle"))

        bos_alan = db_park[3] - giren_arac
        dolu_alan = db_park[4] + giren_arac

        sorgu = "UPDATE Park_Alani SET bos_alan = ?, dolu_alan = ? WHERE otopark_id = ? AND adi = ?"

        cursor.execute(sorgu, bos_alan, dolu_alan, session["otopark_id"], park_kati_adi)
        cnxn.commit()

        flash("Otoparka araçlar başarıyla girdi.", "green")
        return redirect(url_for("park_alani"))


@app.route("/parka_arac_cikar", methods=["GET", "POST"])
def parka_arac_cikar():
    if request.method == "GET":
        return render_template("parka_arac_cikar.html")

    elif request.method == "POST":
        park_kati_adi = request.form["name"]
        cikan_arac = request.form["sayi"]

        try:
            cikan_arac = int(cikan_arac)
        except:
            flash("Çıkan yapan araç sayısını integer tipinde değer giriniz.", "red")
            return redirect(url_for("park_alani_ekle"))

        sorgu = "Select * From Park_Alani where otopark_id = ? AND adi = ?"
        cursor.execute(sorgu, session["otopark_id"], park_kati_adi)
        db_park = cursor.fetchone()

        if db_park[3] > cikan_arac:
            flash("Otoparkta yeterli araç yok.", "red")
            return redirect(url_for("parka_arac_cikar"))

        bos_alan = db_park[3] + cikan_arac
        dolu_alan = db_park[4] - cikan_arac

        sorgu = "UPDATE Park_Alani SET bos_alan = ?, dolu_alan = ? WHERE otopark_id = ? AND adi = ?"

        cursor.execute(sorgu, bos_alan, dolu_alan, session["otopark_id"], park_kati_adi)
        cnxn.commit()

        flash("Otoparktan araçlar başarıyla çıktı.", "green")
        return redirect(url_for("park_alani"))


##########################
###### MUSTERİLER ########
##########################
@app.route("/musteriler", methods=["GET"])
def musteriler():
    if request.method == "GET":
        return render_template("musteriler.html")

@app.route("/musterilerim", methods=["GET"])
def musterilerim():
    if request.method == "GET":

        sorgu = "Select * From Musteri where otopark_id = ?"
        cursor.execute(sorgu, session["otopark_id"])
        db_musteriler = cursor.fetchall()

        return render_template("musterilerim.html", otoparkAdi=session["otopark_adi"], liste_uzunluk=len(db_musteriler), musteriler=db_musteriler)

@app.route("/musteri_ekle", methods=["GET", "POST"])
def musteri_ekle():
    if request.method == "GET":
        return render_template("musteri_ekle.html")

    elif request.method == "POST":
        musteri_adi = request.form["name"]
        musteri_soyadi = request.form["surname"]
        musteri_telno = request.form["telno"]

        sorgu = "INSERT INTO Musteri (otopark_id,isim, soyisim, tel_no) values (?,?,?,?)"
        cursor.execute(sorgu, session["otopark_id"], musteri_adi, musteri_soyadi, musteri_telno)
        cnxn.commit()


        sorgu = "Select * From Musteri where tel_no = ?"
        cursor.execute(sorgu, musteri_telno)
        musteri = cursor.fetchone()
        session["musteri"] = musteri[0]

        flash("Başarıyla müşteri oluşturdunuz.", "green")
        return redirect(url_for("arac_ekle"))

@app.route("/arac_ekle", methods=["GET", "POST"])
def arac_ekle():
    if request.method == "GET":
        return render_template("arac_ekle.html")

    elif request.method == "POST":
        plaka = request.form["plaka"]
        marka = request.form["marka"]
        model = request.form["model"]
        rengi = request.form["rengi"]

        sorgu = "INSERT INTO Arac (musteri_id,plaka, marka, model, renk) values (?,?,?,?,?)"
        cursor.execute(sorgu, session["musteri"], plaka, marka, model, rengi)
        cnxn.commit()

        flash("Başarıyla aracı oluşturdunuz.", "green")
        return redirect(url_for("musteriler"))

@app.route("/musteri_cikar", methods=["GET", "POST"])
def musteri_cikar():
    if request.method == "GET":
        return render_template("musteri_cikar.html")

    elif request.method == "POST":
        musteri_adi = request.form["name"]
        musteri_soyadi = request.form["surname"]


        sorgu = "DELETE FROM Musteri where otopark_id = ? AND isim = ? AND soyisim = ?"
        cursor.execute(sorgu, session["otopark_id"], musteri_adi, musteri_soyadi)
        cnxn.commit()


        flash("Başarıyla müşteri oluşturdunuz.", "green")
        return redirect(url_for("musteriler"))


##########################
####### UCRETLER #########
##########################
@app.route("/ucret", methods=["GET"])
def ucret():
    if request.method == "GET":
        return render_template("ucret.html")


@app.route("/ucretlerim", methods=["GET"])
def ucretlerim():
    if request.method == "GET":
        sorgu = "Select * From Ucretler where otopark_id = ?"
        cursor.execute(sorgu, session["otopark_id"])
        db_ucretler = cursor.fetchall()
        return render_template("ucretlerim.html", otoparkAdi=session["otopark_adi"], liste_uzunluk=len(db_ucretler), tarifeler=db_ucretler)


@app.route("/ucret_ekle", methods=["GET", "POST"])
def ucret_ekle():
    if request.method == "GET":
        return render_template("ucret_ekle.html")

    elif request.method == "POST":
        ucret_adi = request.form["name"]
        sure = request.form["sure"]
        ucreti = request.form["ucreti"]

        sorgu = "INSERT INTO Ucretler (otopark_id, adi, sure, ucret) values (?,?,?,?)"
        cursor.execute(sorgu, session["otopark_id"], ucret_adi, sure, ucreti)
        cnxn.commit()

        flash("Tarife başarıyla eklendi.", "green")
        return redirect(url_for("ucret"))


@app.route("/ucret_cikar", methods=["GET", "POST"])
def ucret_cikar():
    if request.method == "GET":
        return render_template("ucret_cikar.html")

    elif request.method == "POST":
        ucret_adi = request.form["name"]

        sorgu = "DELETE FROM Ucretler where otopark_id = ? AND adi = ?"
        cursor.execute(sorgu, session["otopark_id"], ucret_adi)
        cnxn.commit()

        flash("Tarife başarıyla silindi.", "green")
        return redirect(url_for("ucret"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


app.run(debug=True)
