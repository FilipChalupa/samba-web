# samba-web

Docker image, který vystaví obsah Samba share jako statický HTTP server s directory listingem. Přístup na Samba probíhá on-demand — při každém requestu se přímo dotáže SMB serveru.

## Použití

```bash
cp .env.example .env
# vyplnit .env
docker compose up --build
```

Server běží na [http://localhost:8080](http://localhost:8080).

## Env proměnné

| Proměnná | Popis | Výchozí |
|---|---|---|
| `SMB_HOST` | IP nebo hostname Samba serveru | **povinné** |
| `SMB_SHARE` | Název share | **povinné** |
| `SMB_USER` | Uživatelské jméno (`guest` = bez hesla) | `guest` |
| `SMB_PASSWORD` | Heslo | prázdné |
| `SMB_DOMAIN` | Doména / workgroup | prázdné |
| `SMB_PATH` | Podsložka uvnitř share | `/` (root) |
| `PORT` | Port HTTP serveru uvnitř kontejneru | `80` |

## Nasazení přes Coolify

Nasadit jako **Docker image** nebo **Dockerfile**. Env proměnné nastavit v Coolify UI. Port kontejneru: `80`.

## Chování

- **Složka** → HTML directory listing (načte se ze Samby při každém requestu)
- **Soubor** → streamuje se přímo ze Samby do HTTP response (64 KB bloky)
- Žádný lokální cache, žádný sync — vždy aktuální obsah
- HTTP 404 pro neexistující cesty, HTTP 503 při výpadku SMB serveru
