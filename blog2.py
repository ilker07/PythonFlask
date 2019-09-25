
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from passlib.handlers.sha2_crypt import sha256_crypt
from functools import wraps
#Decorator kullanımı fonksiyona girilip girilmeyeceğini belirler.

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
         if "logged_in" in session:
            return f(*args, **kwargs)
         else:
            flash("Giriş yap buryı görmek için.","danger")
            return redirect(url_for("baslangic"))  
    return decorated_function



#Kullanıcı kayıt Formu 

class kullaniciKayit(Form):
 isim=StringField("İsim Soyisim",validators=[validators.Length(min=4,max=25)])
 kullaniciismi=StringField("Kullanici Adi",validators=[validators.Length(min=5,max=35)])
 email=StringField("E-Mail",validators=[validators.Email(message="Geçerli bir adres gir.")])
 sifre=PasswordField("Parola ",validators=[validators.DataRequired(message="Parola gir.."),validators.EqualTo(fieldname="confirm",message="Parola uyuşmuyor.")])
 confirm=PasswordField("Parola Doğrula",validators=[validators.EqualTo(fieldname="sifre",message="Parola uyuşmuyor.")])

class kullaniciGiris(Form):
  kullaniciadi=StringField("Kullanıcı Adı:")
  kullaniciSifre=PasswordField("Parola:") 
app=Flask(__name__)
app.secret_key="ilker"

app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="udemypython"
app.config["MYSQL_CURSORCLASS"]="DictCursor"

mysql=MySQL(app)



@app.route("/")
def baslangic():
    
    sayilar=[10,22,13,65,72]
    return render_template("indexYeni.html",islem=1,dizi=sayilar) #islem ifadesi gonderildi.Gönderilmek zorunda değil. 
                                                                  #Dizi ifadesi de sonradan eklendi.

@app.route("/about")
def hakkinda():

    return render_template("about.html")
@app.route("/register",methods=["GET","POST"])
def kayit():
    form=kullaniciKayit(request.form)

    if request.method=="POST" and form.validate():

        alinan_isim=form.isim.data
        alinan_kullanici_ismi=form.kullaniciismi.data
        alinan_email=form.email.data
        alinan_sifre=sha256_crypt.encrypt(form.sifre.data)

        cursor=mysql.connection.cursor()

        sorgu="Insert into users (isim,email,kullaniciadi,sifre) VALUES(%s,%s,%s,%s)"

        cursor.execute(sorgu,(alinan_isim,alinan_kullanici_ismi,alinan_email,alinan_sifre))
        mysql.connection.commit()
        cursor.close()
        flash("Başarıyla kayıt oldunuz..","success")
        return redirect(url_for("girisYap"))
    else:

      return render_template("register.html",form=form)

@app.route("/article/<string:veriIdsi>")
def detay(veriIdsi):
    #return "Id: "+ veriIdsi
    cursor=mysql.connection.cursor()
    sorgu="Select * from articles where id=%s"
    result=cursor.execute(sorgu,(veriIdsi,))

    if result>0:
      article=cursor.fetchone()
      return render_template("article.html",article=article)
       

    else:
      return render_template("article.html")  



@app.route("/login",methods=["GET","POST"])
def girisYap():

  form=kullaniciGiris(request.form)
  if request.method=="POST":
    gelenKullaniciismi=form.kullaniciadi.data
    gelenSifre=form.kullaniciSifre.data

    cursor=mysql.connection.cursor()

    sorgu="Select * from  users where  kullaniciadi =  %s"
    sonuc=cursor.execute(sorgu,(gelenKullaniciismi,))

    if sonuc > 0:
      data=cursor.fetchone()
      veriTabanindangelenSifre=data["sifre"]
      if(sha256_crypt.verify(gelenSifre,veriTabanindangelenSifre)):
        flash("Başarıyla giriş yapıldı","success")

        session["logged_in"]=True
        session["username"]=gelenKullaniciismi

        return redirect(url_for("baslangic"))
      else:
        flash("Parola yanlışş...","danger")
        return redirect(url_for("girisYap"))  
    else:
      flash("Kayıt bulunamadı...","danger")
      return redirect(url_for("girisYap"))
  return render_template("login.html",form=form)
@app.route("/logout")
def cikisYap():
  session.clear()
  return redirect(url_for("baslangic"))

@app.route("/dashboard")
@login_required    #Giriş yapıldıysa burası çalışsın.
def kontrolPanel():

  cursor=mysql.connection.cursor()
  sorgu="Select * from articles where author= %s"
  result=cursor.execute(sorgu,(session["username"],))

  if result>0:
    articles=cursor.fetchall()
    return render_template("dashboard.html",articles=articles)

  else:
    return render_template("dashboard.html")
#Makale gosterme


@app.route("/showArticles")
def makaleGoster():
  cursor=mysql.connection.cursor()

  sorgu="Select * from articles"

  sonuc=cursor.execute(sorgu)

  if sonuc>0:

    articles=cursor.fetchall()

    return render_template("showArticles.html",articles=articles)
  else:
    return render_template("showArticles.html")  

#Makale Silme
@app.route("/delete/<string:id>")
@login_required
def sil(id):
  cursor=mysql.connection.cursor()

  sorgu="Select * from articles where author=%s and id=%s"
  result=cursor.execute(sorgu,(session["username"],id))

  if result>0:
    sorgu2="Delete from articles where id=%s"
    cursor.execute(sorgu2,(id,))
    mysql.connection.commit()
    return redirect(url_for("kontrolPanel"))

  else:
    flash("Böyle bir makale yok veya bu işleme yetkiniz yok..","danger")
    return redirect(url_for("baslangic"))

#Makale Güncelleme
@app.route("/edit/<string:id>",methods=["GET","POST"])
@login_required
def guncelle(id):

  if request.method=="GET":
    cursor=mysql.connection.cursor()

    sorgu="Select * from articles where id=%s and author=%s"
    result=cursor.execute(sorgu,(id,session["username"]))

    if result==0:

       flash("Böyle bir makale yok ya bu işleme yetliniz yok!!","danger")
       return redirect(url_for("baslangic"))
    else:

      article=cursor.fetchone()
      form=ArticleForm()

      form.title.data=article["title"]
      form.content.data=article["content"]

      return render_template("update.html",form=form)





  else:
    form=ArticleForm(request.form)

    yeniBaslik=form.title.data
    yeniIcerik=form.content.data

    sorgu2="Update articles set title=%s,content=%s where id=%s"
    cursor=mysql.connection.cursor()
    cursor.execute(sorgu2,(yeniBaslik,yeniIcerik,id))
    mysql.connection.commit()
    flash("Makale başarıyla güncellendi","success")
    return redirect(url_for("kontrolPanel"))

#Arama

@app.route("/search",methods=["GET","POST"])
def ara():

  if request.method=="GET":
    return redirect(url_for("baslangic"))
  else:

    keyword=request.form.get("keyword")
    cursor=mysql.connection.cursor()
    sorgu="Select * from articles where title like '%"+keyword+"%'"
    result=cursor.execute(sorgu)

    if result==0:
      flash("Makale bulunamadı..","danger")
      return redirect(url_for("makaleGoster"))

    else:
      articles=cursor.fetchall()
      return render_template("showArticles.html",articles=articles)



#Makale ekleme.
@app.route("/articles",methods=["GET","POST"])
def makaleEkle():
  form=ArticleForm(request.form)
  if request.method=="POST" and form.validate():
    title=form.title.data
    content=form.content.data

    cursor=mysql.connection.cursor()

    sorgu="Insert into articles(title,author,content) VALUES(%s,%s,%s) "
    cursor.execute(sorgu,(title,session["username"],content))
    mysql.connection.commit()
    cursor.close()
    flash("Makale Eklendi","success")
    return redirect(url_for("kontrolPanel"))
  return render_template("addarticle.html",form=form)




#Makale Form
# 
class ArticleForm(Form):
  title=StringField("Makale Başlığı",validators=[validators.length(min=5,max=20)])
  content=TextAreaField("İçerik",validators=[validators.length(min=10)])  
if __name__== "__main__":
    app.run(debug=True)
