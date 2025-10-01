from page_index import index_page, SITE_DIR
from crowbar import Emitter
import shutil

def gen_site():
    SITE_OUT = SITE_DIR / "out"
    if SITE_OUT.exists():
        shutil.rmtree(SITE_OUT)
    SITE_OUT.mkdir()

    assets = ["logo.png"]
    for asset in assets:
        shutil.copy(SITE_DIR / asset, SITE_OUT)

    out = []
    emit = Emitter(writer=out.append)
    emit(index_page())
    with open(SITE_OUT / "index.html", mode="w") as fh:
        fh.write("".join(out))



if __name__ == "__main__":
    print("generating site...")
    gen_site()
