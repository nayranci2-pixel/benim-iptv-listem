import urllib.request
import re

def icerik_cek(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    except:
        return None

def link_calisiyor_mu(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as response:
            return response.status == 200
    except:
        return False

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
        
    kanal_adi, grup, logo, kaynak = parcalar[0], parcalar[1], parcalar[2], parcalar[3]
    bulunan_link = None

    if kaynak.endswith(".m3u8"):
        if link_calisiyor_mu(kaynak):
            bulunan_link = kaynak
    elif kaynak.endswith(".m3u"):
        if kaynak not in onbellek:
            onbellek[kaynak] = icerik_cek(kaynak) or ""
        
        liste_icerigi = onbellek[kaynak].splitlines()
        for i, line in enumerate(liste_icerigi):
            if line.startswith("#EXTINF") and kanal_adi.lower() in line.lower():
                if i + 1 < len(liste_icerigi) and liste_icerigi[i+1].startswith("http"):
                    aday_link = liste_icerigi[i+1].strip()
                    if link_calisiyor_mu(aday_link):
                        bulunan_link = aday_link
                        break

    if bulunan_link:
        m3u_cikti.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{grup}",{kanal_adi}')
        m3u_cikti.append(bulunan_link)

with open("playlist.m3u", "w", encoding="utf-8") as out:
    out.write("\n".join(m3u_cikti))
