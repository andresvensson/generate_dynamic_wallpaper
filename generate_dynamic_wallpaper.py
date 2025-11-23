#!/usr/bin/env python3
import requests
from datetime import datetime
import os
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom as minidom

# ----------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------

# URL to fetch sunrise / sunset JSON from your server
DAYLIGHT_API = "https://your-server.example.com/api/daylight"

# Directory where your wallpaper images live
IMAGE_DIR = "/usr/share/backgrounds/Dynamic_Wallpapers/Lakeside_modified"

# List of images in chronological order (dawn → day → sunset → night)
IMAGES = [
    "LakesideDeer-01.png",
    "LakesideDeer-02.png",
    "LakesideDeer-03.png",
    "LakesideDeer-04.png",
    "LakesideDeer-05.png",
    "LakesideDeer-06.png",
    "LakesideDeer-07.png",
    "LakesideDeer-08.png",
    "LakesideDeer-09.png",
    "LakesideDeer-10.png",
    "LakesideDeer-11.png",
    "LakesideDeer-12.png",
]

# Where GNOME expects the XML wallpaper file
#OUTPUT_XML = "/usr/share/backgrounds/Dynamic_Wallpapers/Lakeside_dynamic.xml"
OUTPUT_XML = "Lakeside_dynamic.xml"

# Transition time in seconds (e.g. 2 minutes = 120 sec)
TRANSITION_DURATION = 120

# ----------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------

def parse_hhmm(s):
    return datetime.strftime(s, "%H:%M")
    #s = str(s)
    #return s.time()
    #return datetime.strptime(s, "%H:%M")

def prettify(elem):
    """Return a pretty-printed XML string"""
    rough = tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="    ")

def seconds_between(t1, t2):
    print("T1", t1, "T2", t2)
    delta = (t2 - t1).total_seconds()
    while delta < 0:
        delta += 24 * 3600
    return delta

# ----------------------------------------------------------
# MAIN LOGIC
# ----------------------------------------------------------

def main():
    # 1. Fetch daylight info
    print("Fetching sunrise/sunset info...")
    data = get_data()
    # sunrise = parse_hhmm(data["sunrise"])
    # sunset  = parse_hhmm(data["sunset"])

    sunrise = data["sunrise"]
    sunset  = data["sunset"]

    # 2. Build XML structure
    background = Element("background")

    # Start at midnight
    starttime = SubElement(background, "starttime")
    for tag, val in [("year", 2025), ("month", 1), ("day", 1), ("hour", 0), ("minute", 0), ("second", 0)]:
        SubElement(starttime, tag).text = str(val)

    # Split images: dawn group → daytime group → dusk group → night group
    # Example: 12 images:
    #   0–2  : dawn
    #   3–7  : daytime
    #   8–9  : sunset
    #   10–11: night
    dawn_imgs   = IMAGES[0:3]
    day_imgs    = IMAGES[3:8]
    dusk_imgs   = IMAGES[8:10]
    night_imgs  = IMAGES[10:12]

    # added
    zero_ts = sunrise.replace(hour=0, minute=0)
    # -----

    segments = [
        #("dawn",   dawn_imgs,  0, sunrise),
        ("dawn", dawn_imgs, zero_ts, sunrise),
        ("day",    day_imgs,   sunrise, sunset),
        ("dusk",   dusk_imgs,  sunset, sunset.replace(hour=(sunset.hour+1)%24)),  # 1 hr after sunset
        ("night",  night_imgs, sunset.replace(hour=(sunset.hour+1)%24), sunrise.replace(hour=(sunrise.hour+24)%24)),
    ]

    print("SEGMENTS:", segments)

    # 3. Build XML sections for each segment
    current_time = datetime(2025, 1, 1, 0, 0, 0)  # start of slideshow

    for name, imgs, start, end in segments:

        # Calculate duration of segment
        duration = seconds_between(start, end)
        per_image = duration / len(imgs)

        print(f"Segment {name}: {len(imgs)} images, {per_image:.1f}s each")

        # Add images + transitions
        for i in range(len(imgs)):
            img = os.path.join(IMAGE_DIR, imgs[i])

            # STATIC BLOCK
            static = SubElement(background, "static")
            SubElement(static, "file").text = img
            SubElement(static, "duration").text = f"{per_image:.1f}"

            # TRANSITION BLOCK (to next)
            next_img = imgs[(i + 1) % len(imgs)]
            next_img_path = os.path.join(IMAGE_DIR, next_img)
            trans = SubElement(background, "transition", {"type": "overlay"})
            SubElement(trans, "duration").text = str(TRANSITION_DURATION)
            SubElement(trans, "from").text = img
            SubElement(trans, "to").text = next_img_path

    # 4. Save XML
    print("Writing:", OUTPUT_XML)
    xml_string = prettify(background)
    with open(OUTPUT_XML, "w") as f:
        f.write(xml_string)

    print("Done!")

def get_data() -> dict:
    print("Hej!")

    # raw = {"sunrise": "07:00", "sunset": "20:00"}
    #
    d = {}
    #
    today = datetime.today()
    d['sunrise'] = today.replace(hour=7, minute=0)
    d['sunset'] = today.replace(hour=20, minute=0)
    #
    # h1, m1 = map(int, raw["sunrise"].split(":"))
    # h2, m2 = map(int, raw["sunset"].split(":"))
    #
    # sunrise = today.replace(hour=h1, minute=m1, second=0)
    # sunset = today.replace(hour=h2, minute=m2, second=0)


    #d = {"sunrise": "07:00", "sunset": "20:00"}

    sr = "2025-11-22 08:00:00"
    ss = "2025-11-22 20:00:00"

    # d = datetime.today()
    # print("DATA:", d)
    # d = datetime.now()
    # d = d.hour
    # print("DATA:", d)
    # d = datetime.now().replace(hour=7, minute=0)
    print("DATA:", d)

    # initiate sqlite3
    # get from server
    # save/load to sqlite3

    return d


if __name__ == "__main__":
    main()
    #get_data()