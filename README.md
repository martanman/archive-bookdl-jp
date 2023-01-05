### Installation

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
cp sample_config.py config.py
```

### Usage

Edit `config.py` with your email and password for your archive.org account. Then run

```
python3 pw.py output_name "book_url"
```

The zip file `output_name.zip` is created, containing a correctly numbered (hopefully) list of the book's .jpg files. `book_url` is in the format `https://archive.org/details/XXXX`

### Disclaimer

By using this script to download "Borrow for 1 hour" books, it is your responsibility not to share them and to delete said files when you're hour is up! This should be for personal use only; you must not use this to commit copyright infringements!
