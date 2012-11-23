pep8:
	flake8 eros --ignore=E501,E127,E128,E124

test:
	coverage run --branch --source=eros manage.py test -s -x eros
	coverage report --omit=eros/test*

release:
	python setup.py sdist register upload -s
