import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import anywidget
    import traitlets
    from datetime import datetime, timedelta
    import math

    return anywidget, datetime, mo, timedelta, traitlets


@app.cell
def _(anywidget, traitlets):
    # components
    # component
    class TimeInput(anywidget.AnyWidget):
        value = traitlets.Unicode("12:00").tag(sync=True)
        label = traitlets.Unicode("Saat Seçin").tag(sync=True)

        _esm = """
        function render({ model, el }) {
          const container = document.createElement("div");
          container.style.display = "inline-flex";
          container.style.alignItems = "center";
          container.style.gap = "8px";

          const label = document.createElement("label");
          label.textContent = model.get("label");
          label.style.fontSize = "14px";
          label.style.fontWeight = "500";

          const input = document.createElement("input");
          input.type = "time";
          input.value = model.get("value") || "12:00";
          input.style.padding = "4px 8px";
          input.style.borderRadius = "6px";
          input.style.border = "1px solid #ccc";
          input.style.fontFamily = "inherit";

          input.addEventListener("input", (e) => {
            model.set("value", e.target.value);
            model.save_changes();
          });

          model.on("change:value", () => {
            input.value = model.get("value");
          });

          container.appendChild(label);
          container.appendChild(input);
          el.appendChild(container);
        }
        export default { render };
        """

    return (TimeInput,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Soru 1 — Etkinlik Süresi Hesaplayıcı

    Soru: Kullanıcıdan bir etkinliğin başlangıç ve bi ş zamanını saat ve dakika olarak (dört ayrı input ile) alan ve etkinliğin süresini "X saat Y dakika"
    biçiminde yazdıran bir program yazın.
    İstenenler:
    - Saat 0–23, dakika 0–59 aralığında değilse "Hatalı saat girişi!" yazdırılmalıdır.
    - Etkinlik gece yarısını geçebilir (ör. 22:45 → 01:20). Bu durumda süre doğru hesaplanmalı ve "(Gece yarısı geçildi.)" mesajı da yazdırılmalıdır.
    - İpucu: Tüm zamanları dakikaya çevirin. Bir gün 1440 dakikadır; negatif farkı düzeltmek için % operatörünü kullanabilirsiniz.

    Örnek çalışmalar (programınız bu girdilerle aynı sonuçları vermelidir):
    ```
    Girdi: 22, 45, 1, 20
    Süre: 2 saat 35 dakika
    (Gece yarısı geçildi.)
    Girdi: 9, 15, 17, 40
    Süre: 8 saat 25 dakika
    Girdi: 25, 0, 1, 0
    Hatalı saat girişi!
    ```
    """)
    return


@app.cell
def _(TimeInput, mo):
    baslangic = mo.ui.anywidget(
        TimeInput(value="14:30", label="Toplantı Saati Başlangıcı:")
    )
    bitis = mo.ui.anywidget(
        TimeInput(value="14:50", label="Toplantı Saati Bitişi:")
    )
    mo.vstack([baslangic, bitis])
    return baslangic, bitis


@app.cell
def _(datetime, timedelta):
    def zaman_araligi(val1, val2):
        def _deger_al(v):
            if hasattr(v, "value"):
                v = v.value
            if isinstance(v, dict):
                return str(v.get("value", "12:00"))
            return str(v)

        s1 = _deger_al(val1)
        s2 = _deger_al(val2)
        fmt = "%H:%M"
        dt1 = datetime.strptime(s1.strip(), fmt)
        dt2 = datetime.strptime(s2.strip(), fmt)

        fark = dt2 - dt1
        if fark < timedelta(0):
            fark += timedelta(days=1)

        toplam_dakika = int(fark.total_seconds() // 60)
        saat = toplam_dakika // 60
        dakika = toplam_dakika % 60

        return saat, dakika, toplam_dakika

    return (zaman_araligi,)


@app.cell
def _(baslangic, bitis, mo, zaman_araligi):
    saat, dakika, toplam_dk = zaman_araligi(baslangic.value, bitis.value)

    mo.md(f"""
    - **Başlangıç:** `{baslangic.value}`
    - **Bitiş:** `{bitis.value}`
    - **Fark:** **{saat} saat {dakika} dakika** *(Toplam {toplam_dk} dk)*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Soru 2 — Palindrom ve Armstrong Sayısı

    Soru: Kullanıcıdan üç basamaklı bir tam sayı alan bir program yazın. Program sayının basamaklarını // ve % operatörleriyle ayırmalı ve aşağıdakileri yapmalıdır:

    İstenenler:
    - Sayı üç basamaklı değilse "Lütfen üç basamaklı bir sayı girin!" yazdırılmalıdır.
    - Sayının tersini hesaplayıp yazdırın (ör. 153 -> 351).
    - Metin (string) işlemleri kullanmayın, yalnızca aritmetrik operatörleri kullanın.
    - Sayı tersine eşitse palindrom olduğunu belir n.
    - Basamaklarının küpleri toplamı sayının kendisine eşitse Armstrong sayısı olduğunu belir n (ör. 1^3 + 5^3 + 3^3 = 153).

    Örnek çalışmalar (programınız bu girdilerle aynı sonuçları vermelidir):

    ```
    Girdi: 153
    Tersi: 351
    153 bir palindrom sayı değildir.
    153 bir Armstrong sayısıdır.
    ```
    """)
    return


@app.cell
def _():
    class Sayi:
        def __init__(self, sayi):
            self.sayi = sayi

        def is_palindrom(self):
            s = str(abs(self.sayi))
            # sayi == sayinin tersi mi?
            return s == s[::-1]

        def is_armstrong(self):
            s = str(abs(self.sayi))
            n = len(s)
            toplam = sum(int(basamak) ** n for basamak in s)
            return toplam == self.sayi

        def analiz(self):
            if not (100 <= abs(self.sayi) <= 999):
                print(f"Girdi: {self.sayi}")
                print("Lütfen üç basamaklı bir sayı girin!\n")
                return

            str_sayi = str(abs(self.sayi))
            tersi = str_sayi[::-1]

            print(f"Girdi: {self.sayi}")
            print(f"Tersi: {tersi}")

            if self.is_palindrom():
                print(f"{self.sayi} bir palindrom sayıdır.")
            else:
                print(f"{self.sayi} bir palindrom sayı değildir.")

            if self.is_armstrong():
                print(f"{self.sayi} bir Armstrong sayısıdır.")
            else:
                print(f"{self.sayi} bir Armstrong sayısı değildir.")

            print()

    s1 = Sayi(121)
    print(s1.analiz())

    s2 = Sayi(153)
    print(s2.analiz())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Soru 3 — Üçgen Analizi

    Soru: Kullanıcıdan üç kenar uzunluğu alan ve üçgeni analiz eden bir program yazın. İstenenler:
    - Kenarlardan biri 0 veya negatifse **Kenar uzunlukları pozitif olmalıdır!** yazdırılmalıdır.
    - Üçgen eşitsizliği sağlanmıyorsa (herhangi iki kenarın toplamı üçüncüden büyük değilse) "Bu kenarlarla üçgen oluşturulamaz." yazdırılmalıdır.
    - Üçgen geçerliyse türünü (eşkenar / ikizkenar / çeşitkenar) yazdırın. Dik üçgense bunu da belir n.
    - Çevreyi ve Heron formülüyle alanı (2 ondalık basamak) hesaplayın. Formül: u = (a+b+c)/2, Alan = √(u(u−a)(u−b)(u−c)).
    - İpucu: Karekök için ** 0.5, en uzun kenar için max() kullanılabilir.

    Örnek çalışmalar (programınız bu girdilerle aynı sonuçları vermelidir):

    ```
    Girdi: 3, 4, 5
    Çeşitkenar üçgen
    Dik üçgendir.
    Çevre: 12.0
    Alan: 6.0
    Girdi: 6, 6, 6
    Eşkenar üçgen
    Çevre: 18.0
    Alan: 15.59
    Girdi: 1, 2, 10
    Bu kenarlarla üçgen oluşturulamaz.
    ```
    """)
    return


@app.cell
def _():
    class Ucgen:
        def __init__(self, k1, k2, k3):
            self.k1 = k1
            self.k2 = k2
            self.k3 = k3

        def cevre(self):
            return self.k1 + self.k2 + self.k3

        def alan(self):
            u = (self.k1 + self.k2 + self.k3) / 2
            alan = (u * (u - self.k1) * (u - self.k2) * (u - self.k3)) ** 0.5
            return alan

        def hangi_ucgen(self):

            kenarlar = sorted([self.k1, self.k2, self.k3])
            tur = ""
            if round(kenarlar[0] ** 2 + kenarlar[1] ** 2, 2) == round(
                kenarlar[2] ** 2, 2
            ):
                tur += "Dik "
            if self.k1 == self.k2 == self.k3:
                tur += "Eşkenar"
            elif (
                self.k1 == self.k2 or self.k1 == self.k3 or self.k2 == self.k3
            ):
                tur += "İkizkenar"
            else:
                tur += "Çeşitkenar"

            return tur

        def analiz(self):
            print(f"Kenarlar: {self.k1}, {self.k2}, {self.k3}")
            if not (
                self.k1 + self.k2 > self.k3
                and self.k1 + self.k3 > self.k2
                and self.k2 + self.k3 > self.k1
            ):
                print("Bu kenarlarla üçgen oluşturulamaz.\n")
                return
            else:
                print(f"Tür: {self.hangi_ucgen()} Üçgen")
                print(f"Çevre: {self.cevre():.2f}")
                print(f"Alan: {self.alan():.2f}\n")

    Ucgen(3, 4, 5).analiz()
    Ucgen(6, 6, 6).analiz()
    Ucgen(1, 2, 10).analiz()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Soru 4 — Ders Başarı Notu Hesaplama

    Soru: Kullanıcıdan vize, ödev ve final notlarını alan ve öğrencinin ortalamasını, harf notunu ve geçme durumunu belirleyen bir program yazın.
    İstenenler:
    - Ağırlıklar: vize %30, ödev %20, final %50. Ortalama 2 ondalık basamakla yazdırılmalıdır.
    - Notlardan biri 0–100 aralığında değilse "Notlar 0-100 arasında olmalıdır!" yazdırılmalıdır.
    - Final barajı: Final notu 45'in al ndaysa ortalama ne olursa olsun harf notu FF olmalıdır.
    - Harf notu tablosu: 90+ AA, 85+ BA, 75+ BB, 65+ CB, 55+ CC, 50+ DC, 45+ DD, al FF.
    - Durum: FF ise "Kaldı", DC veya DD ise "Şartlı geç ", diğerleri "Geç ".

    Örnek çalışmalar (programınız bu girdilerle aynı sonuçları vermelidir):

    ```
    Girdi: 60, 80, 70
    Ortalama: 69.0
    Harf notu: CB
    Durum: Geçti

    Girdi: 95, 100, 40
    Ortalama: 68.5
    Final barajı (45) aşılamadı.
    Harf notu: FF
    Durum: Kaldı

    Girdi: 40, 50, 48
    Ortalama: 46.0
    Harf notu: DD
    Durum: Şartlı geçti
    ```
    """)
    return


@app.cell
def _():
    class Not:
        def __init__(self, v, o, f):
            self.v = v
            self.o = o
            self.f = f

        def ortalama(self):
            return 0.30 * self.v + 0.20 * self.o + 0.50 * self.f

        def harf_notu(self):
            ort = self.ortalama()
            if ort >= 90: return "AA"
            elif ort >= 85: return "BA"
            elif ort >= 75: return "BB"
            elif ort >= 65: return "CB"
            elif ort >= 55: return "CC"
            elif ort >= 50: return "DC"
            elif ort >= 45: return "DD"
            else: return "FF"

        def durum(self):
            harf = self.harf_notu()
            if harf == "FF":
                return "Kaldı"
            elif harf in ("DC", "DD"):
                return "Şartlı Geçti"
            else:
                return "Geçti"

        def analiz(self):
            v, o, f = self.v, self.o, self.f
            if not all(0 <= x <= 100 for x in (v, o, f)):
                print("Notlar 0-100 arasında olmalıdır!")

            ort = self.ortalama()
            harf = self.harf_notu()
            durum_metni = self.durum()

            print(f"Vize: {v} | Ödev: {o} | Final: {f}")
            print(f"Ağırlıklı Ortalama: {ort:.2f}")
            print(f"Harf Notu: {harf} ({durum_metni})\n")

    Not(100, 2, 100).analiz()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Soru 5 — Kredi Taksit Hesaplayıcı

    Soru: Kullanıcıdan kredi tutarını, yıllık faiz oranını (%) ve vadeyi (ay) alan ve eşit taksitli kredinin ödeme planını özetleyen bir program yazın. İstenenler:
    - Aylık faiz oranı: i = yıllık faiz / 12 / 100
    - Aylık taksit formülü: Taksit = P × i × (1 + i)ⁿ / ((1 + i)ⁿ − 1) (P: kredi tutarı, n: vade)
    - Aylık taksi , toplam geri ödemeyi, toplam faizi ve faizin anaparaya oranını (%) 2 ondalık basamakla yazdırın.
    - Faiz oranı 0 girilirse formül sı ra bölme hatası verir. Bu durumda taksit = P / n olarak hesaplanmalıdır.
    - Kredi tutarı veya vade 0 ya da nega fse, faiz oranı nega fse "Geçersiz giriş!" yazdırılmalıdır.

    Örnek çalışmalar (programınız bu girdilerle aynı sonuçları vermelidir):

    ```
    Girdi: 100000, 36, 12
    Aylık taksit: 10046.21 TL
    Toplam geri ödeme: 120554.5 TL
    Toplam faiz: 20554.5 TL
    Faizin anaparaya oranı: % 20.55
    Girdi: 12000, 0, 6
    Aylık taksit: 2000.0 TL
    Toplam geri ödeme: 12000.0 TL
    Toplam faiz: 0.0 TL
    Faizin anaparaya oranı: % 0.0
    ```
    """)
    return


@app.cell
def _():
    class Taksit:
        def __init__(self, anapara, yillik_faiz, vade):
            self.P = anapara
            self.yillik_faiz = yillik_faiz
            self.n = vade

        def hesap(self):
            if self.P <= 0 or self.n <= 0 or self.yillik_faiz < 0:
                print("Geçersiz giriş!")
                return

            if self.yillik_faiz == 0:
                aylik_taksit = self.P / self.n
            else:
                i = self.yillik_faiz / 12 / 100  # Aylık faiz oranı
                aylik_taksit = self.P * i * ((1 + i) ** self.n) / (((1 + i) ** self.n) - 1)

            toplam_geri_odeme = aylik_taksit * self.n
            toplam_faiz = toplam_geri_odeme - self.P
            faiz_anapara_orani = (toplam_faiz / self.P) * 100

            print(f"Aylık Taksit: {aylik_taksit:.2f} TL")
            print(f"Toplam Geri Ödeme: {toplam_geri_odeme:.2f} TL")
            print(f"Toplam Faiz: {toplam_faiz:.2f} TL")
            print(f"Faizin Anaparaya Oranı: %{faiz_anapara_orani:.2f}\n")

    Taksit(100_000, 36, 12).hesap()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
