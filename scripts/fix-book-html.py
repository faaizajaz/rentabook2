import sys

from calibre.ebooks.oeb.polish.container import get_container
from calibre.ebooks.oeb.polish.pretty import fix_all_html

# Take string arg when running with calibre-debug
downloaded_file = str(sys.argv[1])

# Calibre stuff to fix html
container = get_container(downloaded_file, tweak_mode=True)
fix_all_html(container)
container.commit(keep_parsed=False)
