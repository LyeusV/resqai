# ResQAI Chatbot Geliştirme Yol Haritası ve Yapılacaklar (TODO) Listesi

Bu dosya, ResQAI projesinin yerel makine öğrenmesi ve kural tabanlı hibrit yapısını geliştirmek için belirlenen adımları detaylandırmaktadır. Projeyi devralan herhangi bir geliştirici veya yapay zeka ajanı, bu listeyi takip ederek geliştirmeleri uygulayabilir.

---

## 📋 Genel Durum & Prensipler
*   **Kısıt:** Dışarıdan hazır büyük dil modelleri (LLM API'leri) veya derin öğrenme (LSTM, Transformer, YOLO vb.) kullanılması kesinlikle yasaktır.
*   **Yaklaşım:** Tamamen kendi hazırladığımız veri setleri ile yerel olarak eğitilmiş Scikit-learn modelleri + kural tabanlı (regex/keyword) algoritmalar kullanılacaktır.

---

## 🛠️ YAPILACAKLAR LİSTESİ (TODO)

### 🟩 [ ] Adım 1: Türkçe Metin Ön İşleme (Preprocessing) Entegrasyonu
Türkçe sondan eklemeli bir dil olduğu için, kelimelerin ek almış hallerini normalize etmek modelin genelleme başarısını ciddi derecede artırır.
- [ ] `src/resqai/preprocess.py` (veya `model.py` içinde) hafif ve kural tabanlı bir Türkçe ek temizleyici / kök bulucu (Lightweight Stemmer) geliştirilmesi.
- [ ] Metinlerdeki noktalama işaretlerinin temizlenmesi, sayıların korunması ve gereksiz boşlukların atılması.
- [ ] Bu ön işleme adımlarının [model.py](file:///c:/Users/MSI/VSCode/resqai/src/resqai/model.py) içindeki `TfidfVectorizer` parametrelerine `preprocessor` veya `tokenizer` olarak entegre edilmesi.
- [ ] Yeni ön işleme yapısının birim testlerle doğrulanması.

---

### 🟩 [ ] Adım 2: Güven Eşiği (Confidence Threshold) & Fallback Desteği
Modelin bilmediği/alakasız sorulara (örn: *"Bugün hava nasıl?"*) menüyle ilgili rastgele cevaplar vermesini engellemek için güven eşiği eklenmelidir.
- [ ] `predict_intent` fonksiyonunun güncellenerek [LogisticRegression](file:///c:/Users/MSI/VSCode/resqai/src/resqai/model.py#L8) modelinin `predict_proba()` olasılık skorlarının kontrol edilmesi.
- [ ] En yüksek sınıf olasılığı belirlenen bir eşik değerinin (örn. `0.45` veya `0.50`) altındaysa niyetin otomatik olarak `fallback` olarak işaretlenmesi.
- [ ] `responses.py` dosyasına `fallback` niyeti için açıklayıcı bir yanıt şablonu eklenmesi: *"Bunu tam anlayamadım. Size restoran menüsü, fiyatlar veya alerjen uyarıları hakkında yardımcı olabilirim."*

---

### 🟩 [ ] Adım 3: Çoklu Model Seçimi ve Hiperparametre Optimizasyonu (AutoML)
Yalnızca Lojistik Regresyon ile sınırlı kalmayıp, diğer klasik ML algoritmalarını da denemek ve en başarılı olanı otomatik seçmek gerekir.
- [ ] [train.py](file:///c:/Users/MSI/VSCode/resqai/src/resqai/train.py) dosyasının güncellenerek aşağıdaki modellerin cross-validation (çapraz doğrulama) ile eğitilmesi:
    *   `LogisticRegression`
    *   `LinearSVC`
    *   `MultinomialNB`
- [ ] Bu modellerin hiperparametrelerinin (C değerleri, alpha değerleri vb.) optimize edilmesi.
- [ ] En yüksek F1 skorunu (özellikle macro-average F1) veren en başarılı modelin otomatik olarak seçilerek `models/intent_model.joblib` olarak kaydedilmesi.
- [ ] Seçilen modelin türünün ve eğitim parametrelerinin `training_logs/metrics.jsonl` dosyasına yazılması.

---

### 🟩 [ ] Adım 4: Konuşma Hafızası (Dialogue Session Context) Desteği
Chatbot'un stateless (hafızasız) yapısını stateful (hafızalı) hale getirerek ardışık soruları anlamasını sağlamak.
- [ ] FastAPI backend tarafında (`api.py`) bellek içi basit bir oturum (session-based context) yapısının tasarlanması.
- [ ] Kullanıcının son sorduğu yemek kategorisini veya ürün adını hafızada (örn. `last_category`, `last_items`) tutması.
- [ ] **Örnek Senaryo Desteği:**
    *   *Kullanıcı:* "Tatlılarda neyiniz var?" (intent: `menu_isteme`, category: `tatli`)
    *   *Kullanıcı:* "Peki fiyatları nedir?" (intent: `fiyat_sorma`, bot hafızadaki `tatli` kategorisini kullanarak tatlı fiyatlarını listeler).
- [ ] Bu hafıza yapısının belli bir süre sonra veya yeni bir ana niyet algılandığında sıfırlanması/güncellenmesi.

---

### 🟩 [ ] Adım 5: Veri Setini Temizleme ve Genişletme
Mevcut veri setindeki mükerrer kayıtların elenmesi ve yeni niyet sınıfları ile veri çeşitliliğinin artırılması.
- [ ] [dataset.csv](file:///c:/Users/MSI/VSCode/dataset/dataset.csv) içinde tespit edilen duplicate satırların temizlenmesi.
- [ ] Aşağıdaki yeni niyet sınıfları için en az 40'ar adet Türkçe örnek cümle eklenmesi:
    *   `iletisim_saatler` (Adres, çalışma saatleri, telefon vb. sorular)
    *   `selamlasma_veda` (Merhaba, günaydın, iyi günler, hoşça kalın vb.)
    *   `siparis_isteme` (Sipariş verme adımları için yönlendirme istekleri)
- [ ] Menü veritabanı olan [menu.json](file:///c:/Users/MSI/VSCode/data/menu.json) dosyasının yeni ürünler, fiyatlar ve alerjen detaylarıyla güncellenmesi.

---

## 📈 Başarı Kriterleri
1.  **Doğruluk Skoru:** Intent sınıflandırma modelinin test setindeki F1 skorunun en az **%93** seviyesine ulaştırılması.
2.  **Güvenilirlik:** Alakasız/rastgele sorulara chatbot'un her zaman `fallback` yanıtı vermesi.
3.  **Kullanılabilirlik:** Sohbet arayüzünde bağlamsal soruların (örn. "Peki fiyatı ne?") hafıza yardımıyla doğru yanıtlanabilmesi.
