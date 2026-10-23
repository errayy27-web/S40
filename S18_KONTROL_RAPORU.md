# S18 — Dürüst kontrol raporu

Temel: S16 Barkod Hataları Görünür.
Değiştirilen tek mevcut dosya: lib/main.dart.

YAPILAN: Açılışta ve 3 saniyede bir mevcut /kasa endpointinden salt-okunur Kasa yenilemesi. Mevcut syncShared zaten 3 saniyede bir çalışıyordu ve aynen korundu. API yerel PC'yi önce, mevcut alternatif URL'yi sonra deniyor.

DEĞİŞTİRİLMEYEN: codemagic.yaml, pubspec.yaml, pc_server/*, ekranlar, stok başlangıçları, Kasa hesapları.

EKSİK: Supabase'i gerçek veri deposu olarak kullanma; PC-Supabase köprüsü; buluttan bütün kayıtların 3 saniyede eşitlenmesi; merkezi silme garantisi. Bunlar bu ZIP'te tamamlanmış değildir.

Flutter/Codemagic derlemesi ve telefon testi yapılamadı. Çalışan APK'nın üzerine kurmadan önce Codemagic test edin.
