# Swiss Federal Councillors — Autograph Card Ordering Tool

Order autograph cards from all 7 members of the Swiss Federal Council directly from their official department websites.

## Usage

```bash
python3 order.py
```

No dependencies beyond the Python standard library.

The script will ask for your delivery details once, then how many cards you want from each councillor, and submit the forms.

## Councillors covered

| Councillor | Department | Status |
|---|---|---|
| Albert Rösti | UVEK/DETEC | ✅ automated |
| Elisabeth Baume-Schneider | EDI/DFI | ✅ automated |
| Karin Keller-Sutter | EFD/DFF | ✅ automated |
| Beat Jans | EJPD/DFJP | ✅ automated |
| Martin Pfister | VBS/DDPS | ✅ automated |
| Guy Parmelin | WBF/DEFR | ✅ automated |
| Ignazio Cassis | EDA/DFAE | ⚠️ manual (Akamai blocks non-browser requests) |

For Cassis: [eda.admin.ch/fr/carte-dedicacee](https://www.eda.admin.ch/fr/carte-dedicacee)

## Notes

- Cards are free and shipped by post within Switzerland
- Some departments cap orders at 2–3 cards per submission
- Departments without a quantity field require one submission per card (handled automatically)
