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

where `book_url` is the book's page in a format like "https://archive.org/details/XXXXX". The default behavior assumes the book is Japanese (i.e. right-left), but for English (left-right) books you can pass in the `--eng` flag:

```
python3 pw.py output_name "book_url" --eng
```

The zip file `output_name.zip` is created, containing a correctly numbered list of the book's .jpg files.

### Disclaimer

By using this script to download "Borrow for 1 hour" books, it is your responsibility not to share them and to delete said files when you're hour is up! This is to be for personal use only.
