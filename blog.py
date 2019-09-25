from flask import Flask,render_template

app=Flask(__name__)
@app.route("/")  #localhost sayfasında hemen alttaki fonksiyonu çalıştırır.
def fonksiyon():
    sayi=10
    sozluk=dict()
    sozluk["kelime1"]="ilker"
    sozluk["kelime2"]="mustafa"
    sozluk["kelime3"]="aykut"
    return render_template("layout.html",deger=sayi,giden=sozluk) #deger anahtar kelimesiyle sayi değişkenini html e yollama.Virgülle başka parametrelerde yollanabilir.

@app.route("/diger") #localhost:5000/diger
def digereGit():
    return "Diğer Sayfa"
   

if __name__== "__main__":
    app.run(debug=True)
