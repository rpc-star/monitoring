dev:
\tpip install -r requirements.txt

up:
\tdocker compose up -d

down:
\tdocker compose down

logs:
\tdocker compose logs -f --tail=200

test:
\tpytest -q