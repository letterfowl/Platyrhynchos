from unittest import TestCase
from bib import WORDS, Crossword


class TestBuild(TestCase):
    def test_build(self):
        self.assertEqual(
            list(Crossword.createFrom({"1": "abc", "2": "cdef", "3": "abcdefg"})),
            [
                Crossword(
                    letters={(0, 0): 'a', (1, 0): 'b', (2, 0): 'c'},
                    clueH={(0, 0): '1'},
                    clueV={},
                ),
                Crossword(
                    letters={(0, 0): 'c', (1, 0): 'd', (2, 0): 'e', (3, 0): 'f'},
                    clueH={(0, 0): '2'},
                    clueV={},
                ),
                Crossword(
                    letters={
                        (0, 0): 'a',
                        (1, 0): 'b',
                        (2, 0): 'c',
                        (3, 0): 'd',
                        (4, 0): 'e',
                        (5, 0): 'f',
                        (6, 0): 'g',
                    },
                    clueH={(0, 0): '3'},
                    clueV={},
                ),
            ],
        )


class TestBasic(TestCase):
    def setUp(self) -> None:
        self.words = Crossword.createFrom(
            {
                "Jak się nazywa rezultat odgórnie podjętych decyzji lub negocjacji": "rozstrzygnięcie",
                "Jak się nazywa nowotwór złośliwy skóry wywodzący się z komórek naskórka": "rak kolczystokomórkowy",
                "Jak się nazywa system dróg wokół miasta lub aglomeracji, składający się z głównych magistrali w ich obrębie": "rama komunikacyjna",
                "Jak się nazywa odwołanie kogoś z urzędu kościelnego lub z placówki zagranicznej": "rewokacja",
                "Jak się nazywa klasa pomocniczych wyrazów bądź morfemów będących obligatoryjnymi określeniami grupy imiennej, których główną funkcją jest sygnalizowanie jednoznaczności bądź wieloznaczności określanej grupy składniowej": "rodzajnik",
                "Jak się nazywa zróżnicowanie w obrębie jakiejś skali, całości, na którą składają się różne elementy": "rozstrzał",
                "Jak się nazywa RÓJKA": "rojenie",
                "Jak się nazywa listnik, Rajella fyllae - gatunek ryby chrzęstnoszkieletowej z rodziny rajowatych (Rajidae); raja listnik stanowi typowy gatunek rodzaju Rajella; płaszka ta występuje w północnym Atlantyk od Islandii do Gibraltaru": "raja listnik",
                "Jak się nazywa odpowiednio dostosowana ciupaga, pełniąca funkcję czekana": "rąbanica",
                "Jak się nazywa odmienność, inność, niejednakowość": "różność",
                "Jak się nazywa ruch opóźniony, w którym przyspieszenie ujemne (opóźnienie) ma stałą wartość": "ruch jednostajnie opóźniony",
                "Jak się nazywa cecha czynności, zachowań: to, że są nieprzyzwoite": "bezwstyd",
                "Jak się nazywa lichy, nieumiejętnie namalowany obraz": "bonseki",
                "Jak się nazywa przestępca, który podkłada ładunki wybuchowe lub wszczyna fałszywy alarm z powodu rzekomo podłożonej bomby": "bombiarz",
                "Jak się nazywa krótka kurtka lub bluza o luźnym kroju, która ma ściągacze u dołu i przy szyi, a także zwykle przy rękawach": "bomberka",
                "Jak się nazywa brodawka zlokalizowana na podeszwowej części stóp, mająca szorstką powierzchnię i kolor skóry, mogąca osiągać 1-2 cm wielkości; brodawka stóp może być dwojakiego rodzaju: rozsiana, głęboka (myrmecia) lub bardziej powierzchowna, wraz z pozostałymi brodawkami zlewająca się w skupiska tworzące tzw. brodawki mozaikowe (ang. mosaic warts)": "brodawka stóp",
                "Jak się nazywa kraina historyczna we Francji": "langwedocja",
                "Jak się nazywa świątynia żydowska": "bóżnica",
                "Jak się nazywa Lentinus - rodzaj grzybów z rodziny żagwiowatych; są to grzyby rozwijające się na drewnie, których owocniki posiadają kapelusze osadzone na centralnym lub bocznym trzonie": "twardziak",
                "Jak się nazywa Pleurocybella - rodzaj grzybów należący do rodziny twardzioszkowatych; w Polsce występuje jeden tylko gatunek": "bokówka",
                "Jak się nazywa wagon osobowy dawnej konstrukcji (do ok. 1925), przedziałowy, pozbawiony korytarza wewnętrznego, z osobnymi drzwiami zewnętrznymi do każdego przedziału i stopniami bocznymi na całej długości wagonu": "boczniak",
                "Jak się nazywa Panellus P. Karst. - rodzaj grzybów należący do rodziny grzybówkowatych (Mycenaceae)": "trzonowiec",
                "Jak się nazywa opancerzona podstawa wieży działowej na wojennym okręcie": "barbeta",
            }
        )
        return super().setUp()

    
