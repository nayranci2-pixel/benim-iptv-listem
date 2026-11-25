import urllib.request
import urllib.error
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': '*/*'
}

def icerik_cek(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
            return response.read().decode('utf-8', errors='ignore')
    except:
        return None

def gercek_yayin_mi(url, referer=""):
    if "youtube.com" in url or "youtu.be" in url:
        return False
    try:
        istek_basliklari = HEADERS.copy()
        if referer:
            istek_basliklari['Referer'] = referer
        req = urllib.request.Request(url, headers=istek_basliklari)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            if response.status != 200:
                return False
            baslangic = response.read(200).decode('utf-8', errors='ignore').strip()
            return baslangic.startswith("#EXTM3U")
    except urllib.error.HTTPError as e:
        return e.code == 403
    except:
        return False

def metin_temizle(metin):
    degisim = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    return metin.translate(degisim).lower().replace(" hd", "").replace(" tv", "").strip()

m3u_cikti = ["#EXTM3U"]
onbellek = {}

with open("kanallar.txt", "r", encoding="utf-8") as f:
    satirlar = f.readlines()

for satir in satirlar:
    satir = satir.strip()
    if not satir or satir.startswith("#"):
        continue
    
    parcalar = [p.strip() for p in satir.split("|")]
    if len(parcalar) < 4:
        continue
        
    kanal_adi = parcalar[0]
    grup = parcalar[1]
    logo = parcalar[2]
    kaynak = parcalar[3]
    ozel_referer = parcalar[4] if len(parcalar) > 4 else ""
    
    bulunan_link = None
    ekstra_satirlar = []

    if ".m3u8" in kaynak and not kaynak.endswith("playlist.m3u8"):
        if gercek_yayin_mi(kaynak, ozel_referer):
            bulunan_link = kaynak
            if ozel_referer:
                ekstra_satirlar.append(f"#EXTVLCOPT:http-referrer={ozel_referer}")
    else:
        if kaynak not in onbellek:
            onbellek[kaynak] = icerik_cek(kaynak) or ""
        
        liste_icerigi = onbellek[kaynak].splitlines()
        aranan_temiz = metin_temizle(kanal_adi)
        
        for i, line in enumerate(liste_icerigi):
            if line.startswith("#EXTINF"):
                satir_kanal_adi = line.split(",")[-1]
                satir_temiz = metin_temizle(satir_kanal_adi)
                
                if aranan_temiz == satir_temiz or (len(aranan_temiz) > 3 and aranan_temiz in satir_temiz):
                    gecici_opt = []
                    aday_link = None
                    for j in range(i + 1, min(i + 6, len(liste_icerigi))):
                        alt_satir = liste_icerigi[j].strip()
                        if alt_satir.startswith("#EXTVLCOPT:"):
                            gecici_opt.append(alt_satir)
                        elif alt_satir.startswith("http"):
                            aday_link = alt_satir
                            break
                    
                    if aday_link and gercek_yayin_mi(aday_link):
                        bulunan_link = aday_link
                        ekstra_satirlar = gecici_opt
                        break

    if bulunan_link:
        m3u_cikti.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{grup}",{kanal_adi}')
        m3u_cikti.extend(ekstra_satirlar)
        m3u_cikti.append(bulunan_link)

with open("playlist.m3u", "w", encoding="utf-8") as out:
    out.write("\n".join(m3u_cikti))
