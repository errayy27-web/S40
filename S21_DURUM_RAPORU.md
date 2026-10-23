# S21 kontrol
- Yerel PC / Supabase seçimi: kaynakta eklendi; cihazda test edilmedi.
- Supabase e-posta/şifre oturumu: eklendi; Supabase Auth kullanıcı hesabı gerekir.
- 3 saniyelik yenileme: mevcut timer korundu.
- Bulut paylaşılan olay okuma/yazma: kaynakta eklendi; RLS authenticated politikası gerekir.
- PC snapshot -> Supabase: bağımsız köprüye eklendi; çalıştırılmadı.
- PC sunucusunun kabul etmediği bölümler: halen eksik.
- Çatışma çözümü, tam offline kuyruk, güvenilir silme: üretim testi yok.
- Codemagic derleme: test edilmedi.
- Kasa/etiket UI: kaynak kodda bu sürümde değiştirilmedi.
