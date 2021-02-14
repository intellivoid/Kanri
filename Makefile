format:
	echo "Formatting Haruka code in kanri/"
	black --skip-string-normalization kanri/
start:
	python3 -m pip install -r requirements.txt
	python3 -m kanri


