import re
import os

font_selector = re.compile(r"[{;]\s*font-family\s*:[^;}]*;")
font_replace = re.compile(r"[{;}]\s*font-family\s*:")

def analyse_css(dir) -> dict:
    result = {}
    
    for file in os.listdir(dir):
        with open(os.path.join(dir,file),"r",encoding="utf-8") as f:
            css = f.read()
            fonts = font_selector.findall(css,re.I)
            fonts_processed = []
            for ff in fonts:
                ff = ff[:-1]
                for font in font_replace.sub("",ff).split(","):
                    fonts_processed.append(font.strip("""'" """).lower().replace("!important",""))
            fonts_processed = list(set(fonts_processed))

            for font in fonts_processed:
                if font in result.keys():
                    result[font] += 1
                else:
                    result[font] = 1
    
    to_del = [] # Store outliers as you can't resize a dict while iterating through it
    for k in result.keys():
        if result[k] <= 5:
            to_del.append(k)
    
    for outlier in to_del:
        del result[outlier]

    return result