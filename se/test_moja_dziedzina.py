"""Testy własnej bazy wiedzy (Zadanie Z2). Uruchom: python se/test_moja_dziedzina.py"""
from pathlib import Path

from silnik import wczytaj_baze, wnioskuj_w_przod, wnioskuj_wstecz

baza = wczytaj_baze(Path(__file__).parent.parent / "wiedza" / "moja_dziedzina.json")
cel = baza["cel"]

PRZYPADKI = [
    # T1: typowy (horror, dorośli, średnia mechanika, walka)
    ({"klimat": "horror", "sredni_wiek": 22, "mechanika": "srednia", "walka": "tak"}, "Hunter_The_Reckoning_5e", "typowy"),
    # T2: typowy (sci-fi, średnia mechanika, bez walki)
    ({"klimat": "sci-fi", "sredni_wiek": 21, "mechanika": "srednia", "walka": "nie"}, "Obcy_Gra_Fabularna", "typowy"),
    # T3: granica przedziału (sredni_wiek == 18 -> dorosli)
    ({"klimat": "fantasy", "sredni_wiek": 18, "mechanika": "srednia", "walka": "tak"}, "Warhammer_FRP_4e", "granica"),
    # T4: brak wyniku (sredni_wiek == 10 -> poniżej progu 12 lat)
    ({"klimat": "fantasy", "sredni_wiek": 10, "mechanika": "srednia", "walka": "tak"}, None, "brak wyniku"),
    # T5: konflikt reguł (R11 przed R13 -> wygrywa Monster_of_the_Week zamiast Zew_Cthulhu)
    ({"klimat": "horror", "sredni_wiek": 15, "mechanika": "wysoka", "walka": "nie"}, "Monster_of_the_Week", "konflikt"),
]

ok = 0
for wejscie, oczekiwane, rodzaj in PRZYPADKI:
    fakty, slad = wnioskuj_w_przod(baza, wejscie)
    w_przod_ok = fakty.get(cel) == oczekiwane

    zadane = []
    def zapytaj(atrybut, powod):
        zadane.append(atrybut)
        return wejscie[atrybut]

    wstecz = wnioskuj_wstecz(baza, cel, {}, zapytaj, [])
    wstecz_ok = wstecz == oczekiwane and len(zadane) == len(set(zadane))

    status = "OK " if w_przod_ok and wstecz_ok else "BŁĄD"
    ok += w_przod_ok and wstecz_ok
    print(f"[{status}] ({rodzaj}) -> w przód: {fakty.get(cel)}, wstecz: {wstecz}, pytań: {len(zadane)}")

print(f"\nZaliczone przypadki: {ok}/{len(PRZYPADKI)}")