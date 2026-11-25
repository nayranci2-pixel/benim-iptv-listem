import urllib.request
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

def gercek_yayin_mi(url):
    if "youtube.com" in url or "youtu.be" in url:
        return False
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            if response.status != 200:
                return False
            baslangic = response.read(200).decode('utf-8', errors='ignore').strip()
            return baslangic.startswith("#EXTM3U")
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
    bulunan_link = None

    if ".m3u8" in kaynak and not kaynak.endswith("playlist.m3u8"):
        if gercek_yayin_mi(kaynak):
            bulunan_link = kaynak
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
                    if i + 1 < len(liste_icerigi) and liste_icerigi[i+1].startswith("http"):
                        aday_link = liste_icerigi[i+1].strip()
                        if gercek_yayin_mi(aday_link):
                            bulunan_link = aday_link
                            break

    if bulunan_link:
        m3u_cikti.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{grup}",{kanal_adi}')
        m3u_cikti.append(bulunan_link)

with open("playlist.m3u", "w", encoding="utf-8") as out:
    out.write("\n".join(m3u_cikti))
