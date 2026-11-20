"""Silnik wnioskujący — uzupełniony (TODO 1–4) i podpięty pod własną bazę wiedzy."""
import json
import operator
from pathlib import Path

OPERATORY = {
    "==": operator.eq, "!=": operator.ne,
    ">": operator.gt, ">=": operator.ge,
    "<": operator.lt, "<=": operator.le,
}


def wczytaj_baze(sciezka):
    return json.loads(Path(sciezka).read_text(encoding="utf-8"))


def warunek_spelniony(warunek, fakty):
    """warunek to lista [atrybut, operator, wartość], np. ["sredni_wiek", ">=", 18]."""
    atrybut, op, wartosc = warunek
    return atrybut in fakty and fakty[atrybut] is not None and OPERATORY[op](fakty[atrybut], wartosc)


def regula_spelniona(regula, fakty):
    # TODO 1: zwróć True, jeśli WSZYSTKIE warunki z regula["jesli"] są spełnione.
    return all(warunek_spelniony(warunek, fakty) for warunek in regula["jesli"])


def wnioskuj_w_przod(baza, fakty):
    """Zwraca (fakty po wnioskowaniu, lista id odpalonych reguł)."""
    fakty = dict(fakty)
    slad = []
    zmiana = True
    while zmiana:
        zmiana = False
        for regula in baza["reguly"]:
            atrybut, wartosc = regula["to"]
            # TODO 2: dopisz fakt, ślad i ustaw zmiana = True
            if atrybut not in fakty and regula_spelniona(regula, fakty):
                fakty[atrybut] = wartosc
                slad.append(regula["id"])
                zmiana = True
    return fakty, slad


def wnioskuj_wstecz(baza, cel, fakty, zapytaj, slad=None, powod=None):
    """Ustala wartość atrybutu `cel`. Brakujące dane pobiera funkcją zapytaj(atrybut, powod)."""
    if slad is None:
        slad = []
    if cel in fakty:                                   # już wiemy — nie pytamy drugi raz
        return fakty[cel]
    if cel not in baza["atrybuty"]:
        raise ValueError(f"Niezadeklarowany atrybut: {cel}")

    reguly = [r for r in baza["reguly"] if r["to"][0] == cel]

    # Wniosek bez reguł to luka w bazie: nie pytamy użytkownika o gotową decyzję.
    if not reguly and baza["atrybuty"][cel]["typ"] == "wniosek":
        fakty[cel] = None
        return None

    # TODO 3: jeśli nie ma reguł (cel to dana wejściowa), zapytaj użytkownika i zapamiętaj
    if not reguly:
        fakty[cel] = zapytaj(cel, powod)
        return fakty[cel]

    for regula in reguly:
        spelniona = True
        for atrybut, op, wartosc in regula["jesli"]:
            # TODO 4: ustal atrybut rekurencyjnie
            znana = wnioskuj_wstecz(baza, atrybut, fakty, zapytaj, slad, regula)
            if znana is None or not warunek_spelniony([atrybut, op, wartosc], fakty):
                spelniona = False
                break

        if spelniona:
            fakty[cel] = regula["to"][1]
            slad.append(regula["id"])
            return fakty[cel]

    fakty[cel] = None
    return None


def zapytaj_konsola(baza):
    """Pytanie w konsoli. Sprawdza odpowiedź, bo literówka dałaby ciche None."""
    def zapytaj(atrybut, powod):
        opis = baza["atrybuty"].get(atrybut, {})
        podpowiedz = f" ({'/'.join(opis['wartosci'])})" if "wartosci" in opis else ""
        while True:
            odp = input(f"{opis.get('pytanie', atrybut)}{podpowiedz} ").strip()
            if opis.get("typ") == "liczba":
                try:
                    return float(odp.replace(",", "."))
                except ValueError:
                    print("   Podaj liczbę.")
                    continue
            if "wartosci" in opis and odp not in opis["wartosci"]:
                print("   Dozwolone:", ", ".join(opis["wartosci"]))
                continue
            return odp
    return zapytaj


if __name__ == "__main__":
    # Zadanie 4: własna baza wiedzy i przykładowe fakty
    PLIK_BAZY = Path(__file__).parent.parent / "wiedza" / "moja_dziedzina.json"
    FAKTY = {"klimat": "horror", "sredni_wiek": 22, "mechanika": "srednia", "walka": "tak"}

    baza = wczytaj_baze(PLIK_BAZY)
    cel = baza["cel"]

    print("=== Wnioskowanie w przód ===")
    fakty, slad = wnioskuj_w_przod(baza, FAKTY)
    print("Wynik:", fakty.get(cel), "| reguły:", " -> ".join(slad))

    print("\n=== Wnioskowanie wstecz ===")
    slad = []
    print("Polecam:", wnioskuj_wstecz(baza, cel, {}, zapytaj_konsola(baza), slad))
    print("Reguły:", " -> ".join(slad))