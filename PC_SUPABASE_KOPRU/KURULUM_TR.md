# SS OIL S21 — Supabase kurulum

1. Supabase Dashboard > SQL Editor > New query: `supabase.sql` dosyasını çalıştır.
2. Supabase Authentication > Users: çalışanların e-posta/şifre kullanıcılarını oluştur.
3. Telefonda Ayarlar: Project URL, anon/publishable key, kullanıcı e-postası ve şifresi gir; **Bulut Veri Girişini Test Et**.
4. PC'de ayrı bir klasörde `kopru.py` çalıştır. Windows PowerShell:

```powershell
$env:SSOIL_PC_URL='http://127.0.0.1:8767'
$env:SSOIL_PC_TOKEN='PC_TOKENIN'
$env:SSOIL_SUPABASE_URL='https://PROJE.supabase.co'
$env:SSOIL_SERVICE_ROLE_KEY='SUPABASE_SECRET_KEY'
python kopru.py
```

**Güvenlik:** service_role/secret anahtarını telefona, Codemagic'e veya paylaşılan ZIP'e yazmayın. PC'de saklayın.

**ÖNEMLİ SINIRLAR:** Mevcut PC sunucusu `/shared` üzerinde `orderUnits`, `barcodeErrors` ve bazı bölümleri kabul etmiyorsa, bu bölümler PC merkezine aktarılamaz. Köprü ayrı çalışır, çalışan sunucuyu değiştirmez. PC'deki stok ve kasa verileri yalnızca okuma amaçlı anlık görüntü olarak buluta aktarılır. Bu paket Flutter/Codemagic üzerinde derlenmedi ve uçtan uca test edilmedi. Her 3 saniyelik yenileme bulutta sorgu maliyeti oluşturur.
