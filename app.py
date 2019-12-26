import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.secret_key = "Çok gizli bir key"

# veri tabanı bağlantısı
uri = os.getenv('MONGO_ATLAS_URI')
client = MongoClient(uri)
# tododb: veri tabanı adı, todos ve user: collection ismi
todo = client.tododb.todos
user = client.tododb.user
# artık todos ve user ile veri tabanında her şeyi yapabilirsin


@app.route('/')
def anasayfa():
     # veri tabanından kayıtları çek, bir listeye al
    yapilacaklar = []
    for yap in todo.find():
        yapilacaklar.append({
            "_id": str(yap.get("_id")),
            "filmad": yap.get("filmad"),
            "filmk": yap.get("filmk"),
            "filmr": yap.get("filmr")
        })
    # index.html'e bu listeyi gönder
    return render_template('anasayfa.html', yapilacaklar=yapilacaklar)
        


@app.route('/son')
def son():
    return render_template('son.html')
@app.route('/eniyi')
def eniyi():
    return render_template('eniyi.html')


@app.route('/kayit', methods=['GET','POST'])
def kayit():
    if request.method == 'GET':
        return render_template('kayit.html')
    # POST
    # formdan gelen bilgileri al
    eposta = request.form.get("eposta")
    sifre = request.form.get("sifre")
    #veri tabanına kaydet
    u = user.find_one({'eposta':eposta})
    
    if u is None :
        user.insert_one({'eposta': eposta, 'sifre': sifre})
    else:
        flash(f"{eposta} eposta adresi daha önceden sistemde kayıtlı")
        return redirect('/kayit')
    return redirect('/')    


@app.route('/giris', methods=['GET','POST'])
def giris():
    if request.method == 'GET':
        return render_template('giris.html')
    # POST
    # formdan gelen bilgileri al
    eposta = request.form.get("eposta")
    sifre = request.form.get("sifre")
    #veri tabanında kayıt var mı?
    u = user.find_one({'eposta':eposta})
    # kullanıcı epostası var mı?
    
    if u is not None:
        # epostaya ait olan kullanıcı var
        if sifre == u.get('sifre'):
            # şifre de eşleşiyorsa giriş başarılıdır
            # kullanıcının epostasını session içine al
            session['eposta'] = eposta
            # todo ekleyebileceği sayfaya yönlendiriyoruz.
            return redirect('/istek')
        else:
            flash("Hatalı şifre girdiniz")
            return redirect('/giris')
    else:
        flash(f"Sistemde {eposta} eposta adresi bulunamadı. Lütfen kayıt olun.")
        return redirect('/giris')
    


@app.route('/kapat')
def kapat():
    session.pop('eposta', None)
    return redirect('/')


@app.route('/istek')
def istek():
    # yetkisiz kullanıcılar giremesin
    if 'eposta' not in session:
        flash("Film isteğinde bulunmak için giriş yapmalısınız!")
        return redirect('/giris')

    # veri tabanından kayıtları çek, bir listeye al
    yapilacaklar = []
    for yap in todo.find():
        yapilacaklar.append({
            "_id": str(yap.get("_id")),
            "filmad": yap.get("filmad"),
            "filmk": yap.get("filmk"),
            "filmr": yap.get("filmr")
        })
        
    # index.html'e bu listeyi gönder
    return render_template('istek.html', yapilacaklar=yapilacaklar)




@app.route('/sil/<id>')
def sil(id):
    # id'si gelen kaydı sil
    todo.find_one_and_delete({'_id': ObjectId(id)})
    # ana sayfaya gönder
    return redirect('/istek')


@app.route('/ekle', methods=['POST'])
def ekle():
    # Kullanıcıdan sadece isim aldık
    # durumu default olarak False kabul ediyoruz
    filmad = request.form.get('filmad')
    filmk = request.form.get('filmk')
    filmr = request.form.get('filmr')
    todo.insert_one({'filmad': filmad, 'filmk': filmk, 'filmr' : filmr})
    # ana sayfaya yönlendir
    return redirect('/istek')

# hatalı ya da olmayan bir url isteği gelirse
# hata vermesin, ana sayfaya yönlendirelim
@app.errorhandler(404)
def hatali_url(e):
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
