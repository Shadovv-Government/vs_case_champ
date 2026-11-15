import nbformat, sys
from nbclient import NotebookClient
p = sys.argv[1]
nb = nbformat.read(open(p, encoding="utf-8"), as_version=4)
NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": "."}}).execute()
nbformat.write(nb, open(p, "w", encoding="utf-8"))
print("ok")
