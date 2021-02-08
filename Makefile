format:
	echo "Formatting Haruka code in haruka/"
	black --skip-string-normalization haruka/
start:
	python3 -m pip install -r requirements.txt
	python3 -m haruka


