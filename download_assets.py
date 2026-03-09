"""
Download IPL Team Logos and Stadium Ground Images (with throttling)
"""
import urllib.request, os, time

os.makedirs("docs/assets/logos", exist_ok=True)
os.makedirs("docs/assets/grounds", exist_ok=True)

HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Referer": "https://en.wikipedia.org/",
}

def download(url, path, delay=1.5):
    try:
        time.sleep(delay)
        req = urllib.request.Request(url, headers=HDR)
        with urllib.request.urlopen(req, timeout=20) as r, open(path, "wb") as f:
            data = r.read()
            f.write(data)
        print(f"  ✅ {os.path.basename(path)} ({len(data)//1024}KB)")
        return True
    except Exception as e:
        print(f"  ⚠️  {os.path.basename(path)}: {e}")
        return False

# ─── Team Logos — use thumb PNG variants (more reliable) ─────────────
logos = {
    "csk.png":  "https://upload.wikimedia.org/wikipedia/en/thumb/2/2b/Chennai_Super_Kings_Logo.svg/200px-Chennai_Super_Kings_Logo.svg.png",
    "mi.png":   "https://upload.wikimedia.org/wikipedia/en/thumb/c/cd/Mumbai_Indians_Logo.svg/200px-Mumbai_Indians_Logo.svg.png",
    "rcb.png":  "https://upload.wikimedia.org/wikipedia/en/thumb/2/2a/Royal_Challengers_Bengaluru_2025.svg/200px-Royal_Challengers_Bengaluru_2025.svg.png",
    "kkr.png":  "https://upload.wikimedia.org/wikipedia/en/thumb/4/4c/Kolkata_Knight_Riders_Logo.svg/200px-Kolkata_Knight_Riders_Logo.svg.png",
    "srh.png":  "https://upload.wikimedia.org/wikipedia/en/thumb/8/81/Sunrisers_Hyderabad.svg/200px-Sunrisers_Hyderabad.svg.png",
    "dc.png":   "https://upload.wikimedia.org/wikipedia/en/thumb/2/2f/Delhi_Capitals_%282020%29.svg/200px-Delhi_Capitals_%282020%29.svg.png",
    "rr.png":   "https://upload.wikimedia.org/wikipedia/en/thumb/6/60/Rajasthan_Royals_Logo.svg/200px-Rajasthan_Royals_Logo.svg.png",
    "pbks.png": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a5/Punjab_Kings_Logo.svg/200px-Punjab_Kings_Logo.svg.png",
    "gt.png":   "https://upload.wikimedia.org/wikipedia/en/thumb/0/09/Gujarat_Titans_Logo.svg/200px-Gujarat_Titans_Logo.svg.png",
    "lsg.png":  "https://upload.wikimedia.org/wikipedia/en/thumb/l/lb/Lucknow_Super_Giants_Logo.svg/200px-Lucknow_Super_Giants_Logo.svg.png",
    "dd.png":   "https://upload.wikimedia.org/wikipedia/en/thumb/5/5d/Delhi_Daredevils_Logo.svg/200px-Delhi_Daredevils_Logo.svg.png",
    "dc_old.png":"https://upload.wikimedia.org/wikipedia/en/thumb/f/f5/Deccan_Chargers_Logo.svg/200px-Deccan_Chargers_Logo.svg.png",
    "rps.png":  "https://upload.wikimedia.org/wikipedia/en/thumb/b/b5/Logo_of_Rising_Pune_Supergiants.png/200px-Logo_of_Rising_Pune_Supergiants.png",
    "ipl.png":  "https://upload.wikimedia.org/wikipedia/en/thumb/8/84/Indian_Premier_League_Official_Logo.svg/200px-Indian_Premier_League_Official_Logo.svg.png",
    "ktk.png":  "https://upload.wikimedia.org/wikipedia/en/thumb/5/5c/Kochi_Tuskers_Kerala_Logo.svg/200px-Kochi_Tuskers_Kerala_Logo.svg.png",
    "pw.png":   "https://upload.wikimedia.org/wikipedia/en/thumb/d/da/Pune_Warriors_India_Logo.svg/200px-Pune_Warriors_India_Logo.svg.png",
}

print("Downloading team logos ...")
done = set()
for fname, url in logos.items():
    path = f"docs/assets/logos/{fname}"
    if os.path.exists(path) and os.path.getsize(path) > 2000:
        print(f"  ⏭️  {fname} (already exists)")
        done.add(fname)
        continue
    if download(url, path, delay=2):
        done.add(fname)

# ─── Stadium Images ───────────────────────────────────────────────────
grounds = {
    "wankhede.jpg":       "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Wankhede_stadium.jpg/640px-Wankhede_stadium.jpg",
    "eden_gardens.jpg":   "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Eden_Gardens_during_IPL.jpg/640px-Eden_Gardens_during_IPL.jpg",
    "chinnaswamy.jpg":    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Chinnaswamy_Stadium%2C_Bengaluru.jpg/640px-Chinnaswamy_Stadium%2C_Bengaluru.jpg",
    "chepauk.jpg":        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/MA_Chidambaram_Stadium.jpg/640px-MA_Chidambaram_Stadium.jpg",
    "kotla.jpg":          "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Feroz_Shah_Kotla_Grounds.jpg/640px-Feroz_Shah_Kotla_Grounds.jpg",
    "mohali.jpg":         "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Punjab_Cricket_Association_Stadium.jpg/640px-Punjab_Cricket_Association_Stadium.jpg",
    "rajiv_gandhi.jpg":   "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Rajiv_Gandhi_International_Cricket_Stadium.jpg/640px-Rajiv_Gandhi_International_Cricket_Stadium.jpg",
    "sawai_mansingh.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Sawai_Mansingh_Stadium.jpg/640px-Sawai_Mansingh_Stadium.jpg",
    "narendra_modi.jpg":  "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Narendra_Modi_Stadium.jpg/640px-Narendra_Modi_Stadium.jpg",
    "brabourne.jpg":      "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Brabourne_Stadium.jpg/640px-Brabourne_Stadium.jpg",
    "ekana.jpg":          "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Bharat_Ratna_Shri_Atal_Bihari_Vajpayee_Ekana_Cricket_Stadium.jpg/640px-Bharat_Ratna_Shri_Atal_Bihari_Vajpayee_Ekana_Cricket_Stadium.jpg",
    "dharamsala.jpg":     "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/HPCA_Cricket_Stadium%2C_Dharamsala.jpg/640px-HPCA_Cricket_Stadium%2C_Dharamsala.jpg",
    "vizag.jpg":          "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Dr._Y.S._Rajasekhara_Reddy_ACA-VDCA_Cricket_Stadium.jpg/640px-Dr._Y.S._Rajasekhara_Reddy_ACA-VDCA_Cricket_Stadium.jpg",
    "mca.jpg":            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/MCA_Stadium.jpg/640px-MCA_Stadium.jpg",
}

print("\nDownloading ground/stadium images ...")
for fname, url in grounds.items():
    path = f"docs/assets/grounds/{fname}"
    if os.path.exists(path) and os.path.getsize(path) > 10000:
        print(f"  ⏭️  {fname} (already exists)")
        continue
    download(url, path, delay=2)

print("\n✅ Done!")
