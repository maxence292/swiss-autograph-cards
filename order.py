#!/usr/bin/env python3
"""
Order autograph cards from all 7 Swiss Federal Councillors.
Each councillor's department runs the same SimpleForm CMS component,
so submissions go to /ne/simple-form-mail-dispatcher on each site.
"""

import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

COUNCILLORS = [
    {
        "name": "Albert Rösti",
        "dept": "uvek",
        "form_id": "4693",
        "container_id": "doc-1ivslr3a10",
        "fields": lambda d, n: {
            "Nbre cartes": str(n),
            "Titre": d["title"],
            "Nom": d["last_name"],
            "Prénom": d["first_name"],
            "Adresse": d["street"],
            "NPA": d["zip"],
            "Lieu": d["city"],
            "Pays (si ce n'est pas la Suisse)": d["country"],
            "E-Mail": d["email"],
        },
        "qty_field": True,
        "max_qty": 3,
    },
    {
        "name": "Elisabeth Baume-Schneider",
        "dept": "edi",
        "form_id": "398",
        "container_id": "doc-1i9r5d69p0",
        "fields": lambda d, n: {
            "Nbre cartes": f"{n} cartes" if n > 1 else "1 carte",
            "Civilité ": d["title"],
            "Prénom": d["first_name"],
            "Nom": d["last_name"],
            "Rue/n°": d["street"],
            "NPA": d["zip"],
            "Localité": d["city"],
            "Courriel": d["email"],
        },
        "qty_field": True,
        "max_qty": 2,
    },
    {
        "name": "Karin Keller-Sutter",
        "dept": "efd",
        "form_id": "805",
        "container_id": "doc-1i031bib70",
        "fields": lambda d, n: {
            "Titre": d["title"],
            "Nom": d["last_name"],
            "Prénom": d["first_name"],
            "Adresse": d["street"],
            "NPA": d["zip"],
            "Lieu": d["city"],
            "Pays": d["country"],
            "E-Mail": d["email"],
        },
        "qty_field": False,
        "max_qty": 1,
    },
    {
        "name": "Beat Jans",
        "dept": "ejpd",
        "form_id": "4135",
        "container_id": "doc-1jfalm92o0",
        "fields": lambda d, n: {
            "Nombre de cartes": str(n),
            "Nom": d["last_name"],
            "Prénom": d["first_name"],
            "Rue, N°": d["street"],
            "NPA": d["zip"],
            "Lieu": d["city"],
            "Pays": d["country"],
        },
        "qty_field": True,
        "max_qty": 3,
    },
    {
        "name": "Martin Pfister",
        "dept": "vbs",
        "form_id": "3853",
        "container_id": "doc-1hgi33ias0",
        "fields": lambda d, n: {
            "Appel": d["title"],
            "Prénom": d["first_name"],
            "Nom": d["last_name"],
            "Rue": d["street"],
            "NP": d["zip"],
            "Ville": d["city"],
            "E-mail": d["email"],
        },
        "qty_field": False,
        "max_qty": 1,
    },
    {
        "name": "Guy Parmelin",
        "dept": "wbf",
        "form_id": "1119",
        "container_id": "doc-1i96plpq20",
        "fields": lambda d, n: {
            "Quantité (3 max.)": str(n),
            "Genre": d["title"],
            "Prénom / Nom": f"{d['first_name']} {d['last_name']}",
            "Rue et numéro": d["street"],
            "Numéro postal et lieu": f"{d['zip']} {d['city']}",
        },
        "qty_field": True,
        "max_qty": 3,
    },
    {
        "name": "Ignazio Cassis",
        "dept": "eda",
        "form_id": None,  # fetch dynamically
        "container_id": None,
        "fields": None,
        "qty_field": None,
        "max_qty": None,
        "note": "May require browser — eda.admin.ch/fr/carte-dedicacee",
    },
]

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def ask(prompt, default=None):
    suffix = f" [{default}]" if default else ""
    val = input(f"{prompt}{suffix}: ").strip()
    return val if val else default


def collect_user_info():
    print("\n=== Your delivery details ===\n")
    title_raw = ask("Title (Monsieur/Madame)", "Monsieur")
    first = ask("First name")
    last = ask("Last name")
    street = ask("Street + number")
    zip_code = ask("Postal code (NPA)")
    city = ask("City")
    country = ask("Country (leave blank if Switzerland)", "")
    email = ask("Email")
    return {
        "title": title_raw,
        "first_name": first,
        "last_name": last,
        "street": street,
        "zip": zip_code,
        "city": city,
        "country": country,
        "email": email,
    }


def collect_quantities():
    print("\n=== Cards per councillor ===\n")
    qty = {}
    for c in COUNCILLORS:
        if c.get("note"):
            print(f"  {c['name']}: manual order required ({c['note']})")
            qty[c["name"]] = 0
            continue
        max_q = c["max_qty"] if c["qty_field"] else "?"
        n = ask(f"  {c['name']} (max {max_q} per order, 0 to skip)", "2")
        try:
            qty[c["name"]] = int(n)
        except ValueError:
            qty[c["name"]] = 0
    return qty


def submit(dept, payload):
    url = f"https://www.{dept}.admin.ch/ne/simple-form-mail-dispatcher"
    body = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (compatible)",
            "Referer": f"https://www.{dept}.admin.ch/",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as r:
            return r.status, r.read(200).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read(200).decode("utf-8", errors="replace")
    except Exception as e:
        return 0, str(e)


def order_councillor(councillor, user_data, qty):
    name = councillor["name"]
    n = qty.get(name, 0)
    if n == 0:
        return

    if councillor.get("note"):
        print(f"  ⚠  {name}: {councillor['note']}")
        return

    dept = councillor["dept"]
    submissions = 1

    if not councillor["qty_field"]:
        # No quantity field: submit once per card
        submissions = n
        n = 1

    for i in range(submissions):
        label = name if submissions == 1 else f"{name} [{i+1}/{submissions}]"
        fields = councillor["fields"](user_data, n)
        payload = {
            "LDFormId": councillor["form_id"],
            "LDFormContainerId": councillor["container_id"],
            **fields,
        }
        code, body = submit(dept, payload)
        ok = code == 200 and "successfully" in body.lower()
        status = "OK" if ok else f"FAIL (HTTP {code})"
        print(f"  {'✓' if ok else '✗'}  {label}: {status}")
        if submissions > 1 and i < submissions - 1:
            time.sleep(0.5)


def main():
    print("Swiss Federal Councillors — Autograph Card Ordering Tool")
    print("=" * 55)

    user_data = collect_user_info()
    quantities = collect_quantities()

    print("\n=== Submitting ===\n")
    for councillor in COUNCILLORS:
        order_councillor(councillor, user_data, quantities)

    print("\nDone.")


if __name__ == "__main__":
    main()
