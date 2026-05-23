# ResQAI Chatbot Geliştirme Yol Haritası ve Yapılacaklar (TODO) Listesi

Bu dosya, ResQAI projesinin yerel makine öğrenmesi ve kural tabanlı hibrit yapısını geliştirmek için belirlenen adımları detaylandırmaktadır. Projeyi devralan herhangi bir geliştirici veya yapay zeka ajanı, bu listeyi takip ederek geliştirmeleri uygulayabilir.

---

## 📋 Genel Durum & Prensipler
*   **Kısıt:** Dışarıdan hazır büyük dil modelleri (LLM API'leri) veya derin öğrenme (LSTM, Transformer, YOLO vb.) kullanılması kesinlikle yasaktır.
*   **Yaklaşım:** Tamamen kendi hazırladığımız veri setleri ile yerel olarak eğitilmiş Scikit-learn modelleri + kural tabanlı (regex/keyword) algoritmalar kullanılacaktır.

---

## 🛠️ YAPILACAKLAR LİSTESİ (TODO)

### 🟩 [x] Adım 1: Türkçe Metin Ön İşleme (Preprocessing) Entegrasyonu
Türkçe sondan eklemeli bir dil olduğu için, kelimelerin ek almış hallerini normalize etmek modelin genelleme başarısını ciddi derecede artırır.
- [x] `src/resqai/preprocess.py` (veya `model.py` içinde) hafif ve kural tabanlı bir Türkçe ek temizleyici / kök bulucu (Lightweight Stemmer) geliştirilmesi.
- [x] Metinlerdeki noktalama işaretlerinin temizlenmesi, sayıların korunması ve gereksiz boşlukların atılması.
- [x] Bu ön işleme adımlarının model.py içindeki `TfidfVectorizer` parametrelerine `preprocessor` veya `tokenizer` olarak entegre edilmesi.
- [x] Yeni ön işleme yapısının birim testlerle doğrulanması.

---

### 🟩 [x] Adım 2: Güven Eşiği (Confidence Threshold) & Fallback Desteği
Modelin bilmediği/alakasız sorulara (örn: *"Bugün hava nasıl?"*) menüyle ilgili rastgele cevaplar vermesini engellemek için güven eşiği eklenmelidir.
- [x] `predict_intent` fonksiyonunun güncellenerek LogisticRegression modelinin `predict_proba()` olasılık skorlarının kontrol edilmesi.
- [x] En yüksek sınıf olasılığı belirlenen bir eşik değerinin (örn. `0.45` veya `0.50`) altındaysa niyetin otomatik olarak `fallback` olarak işaretlenmesi.
- [x] `responses.py` dosyasına `fallback` niyeti için açıklayıcı bir yanıt şablonu eklenmesi: *"Bunu tam anlayamadım. Size restoran menüsü, fiyatlar veya alerjen uyarıları hakkında yardımcı olabilirim."*

---

### 🟩 [x] Adım 3: Çoklu Model Seçimi ve Hiperparametre Optimizasyonu (AutoML)
Yalnızca Lojistik Regresyon ile sınırlı kalmayıp, diğer klasik ML algoritmalarını da denemek ve en başarılı olanı otomatik seçmek gerekir.
- [x] train.py dosyasının güncellenerek aşağıdaki modellerin cross-validation (çapraz doğrulama) ile eğitilmesi:
    *   `LogisticRegression`
    *   `LinearSVC`
    *   `MultinomialNB`
- [x] Bu modellerin hiperparametrelerinin (C değerleri, alpha değerleri vb.) optimize edilmesi.
- [x] En yüksek F1 skorunu (özellikle macro-average F1) veren en başarılı modelin otomatik olarak seçilerek `models/intent_model.joblib` olarak kaydedilmesi.
- [x] Seçilen modelin türünün ve eğitim parametrelerinin `training_logs/metrics.jsonl` dosyasına yazılması.

---

### 🟩 [x] Adım 4: Konuşma Hafızası (Dialogue Session Context) Desteği
Chatbot'un stateless (hafızasız) yapısını stateful (hafızalı) hale getirerek ardışık soruları anlamasını sağlamak.
- [x] FastAPI backend tarafında (`api.py`) bellek içi basit bir oturum (session-based context) yapısının tasarlanması.
- [x] Kullanıcının son sorduğu yemek kategorisini veya ürün adını hafızada (örn. `last_category`, `last_items`) tutması.
- [x] **Örnek Senaryo Desteği:**
    *   *Kullanıcı:* "Tatlılarda neyiniz var?" (intent: `menu_isteme`, category: `tatli`)
    *   *Kullanıcı:* "Peki fiyatları nedir?" (intent: `fiyat_sorma`, bot hafızadaki `tatli` kategorisini kullanarak tatlı fiyatlarını listeler).
- [x] Bu hafıza yapısının belli bir süre sonra veya yeni bir ana niyet algılandığında sıfırlanması/güncellenmesi.

---

### 🟩 [x] Adım 5: Veri Setini Temizleme ve Genişletme
Mevcut veri setindeki mükerrer kayıtların elenmesi ve yeni niyet sınıfları ile veri çeşitliliğinin artırılması.
- [x] dataset.csv içinde tespit edilen duplicate satırların temizlenmesi.
- [x] Aşağıdaki yeni niyet sınıfları için en az 40'ar adet Türkçe örnek cümle eklenmesi:
    *   `iletisim_saatler` (Adres, çalışma saatleri, telefon vb. sorular)
    *   `selamlasma_veda` (Merhaba, günaydın, iyi günler, hoşça kalın vb.)
    *   `siparis_isteme` (Sipariş verme adımları için yönlendirme istekleri)
- [x] Menü veritabanı olan menu.json dosyasının yeni ürünler, fiyatlar ve alerjen detaylarıyla güncellenmesi.

---

## 📈 Başarı Kriterleri
1.  **Doğruluk Skoru:** Intent sınıflandırma modelinin test setindeki F1 skorunun en az **%93** seviyesine ulaştırılması.
2.  **Güvenilirlik:** Alakasız/rastgele sorulara chatbot'un her zaman `fallback` yanıtı vermesi.
3.  **Kullanılabilirlik:** Sohbet arayüzünde bağlamsal soruların (örn. "Peki fiyatı ne?") hafıza yardımıyla doğru yanıtlanabilmesi.
