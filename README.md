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
