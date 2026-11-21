"""Extract supplied Gilroy faces for local rendering without distributing the font."""
from pathlib import Path
import sys
from zipfile import ZipFile

directory = Path(__file__).resolve().parents[2] / '.local' / 'redesign' / 'gilroy'
directory.mkdir(parents=True, exist_ok=True)
with ZipFile(Path(sys.argv[1])) as archive:
    for name in ('Gilroy-Light.otf', 'Gilroy-ExtraBold.otf'):
        (directory / name).write_bytes(archive.read(f'Gilroy-FREE/{name}'))
