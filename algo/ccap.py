import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.colors as mcolors
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import sys

"""Allocation de comptoirs d'enregistrement.

Ce module vous fournit quelques classes qui vous faciliteront la lecture
et la manipulation des instances du problème.

#### Exemples d'utilisation
Création et manipulation d'instances du problème :
```python
# création d'une instance à partir d'un fichier
inst = Instance.from_file("instances/instance-2019-04-27.csv")

print(inst) # affiche les vols de l'instance
len(inst)   # renvoie le nombre de vols de l'instance

# On peut indexer et "trancher" les instances comme les listes Python :
inst[3] # récupération du 4ème vol (l'indexation commence à 0)
inst_small = inst[:10] # sélection des 10 premiers vols seulement

for flight in inst: # itération sur les vols d'une instance
    .....
```

Un exemple concret (et un peu plus complet et commenté) se trouve dans
 le fichier `example.py`.

#### Documentation des constantes et classes disponibles

La suite de cette page fournit une documentation des classes fournies,
détaillant notamment les attributs et méthodes disponibles.
"""

STEP = 5
"""Le pas de temps des données et de la résolution, en minutes."""

_ROWS = 16
_BOOTHS_PER_ROW = 12
_BOOTHS = _BOOTHS_PER_ROW * _ROWS

_OK = '\033[92m'
_WARNING = '\033[93m'
_ERROR = '\033[91m'
_END = '\033[0m'
_CHECK = _OK + '✔' + _END if sys.platform == 'linux' else 'OK  '
_WARN = _WARNING + '✖' + _END if sys.platform == 'linux' else 'WARN'
_FAIL = _ERROR + '✖' + _END if sys.platform == 'linux' else 'FAIL'
_LOGFILE = 'ccap.log'

class Instance:
    """ Créer et manipuler des instances du problème d'allocation
    de comptoirs d'enregistrement.

    Les objets de la classe `Instance` se comportent à peu près comme des
    listes de vols. Vous pouvez notamment :
    - calculer le nombre de vol avec la fonction `len`
    - récupérer un vol en connaissant sa position
    - prendre une \"tranche\" de l'instance
    - itérer sur les vols à l'aide d'une boucle `for`
    - concaténer des instances avec l'opérateur `+`
    """

    def __init__(self, flights, booths, rows):
        """Crée une instance.

        Paramètres :
        - flights (Flight list) : liste des vols
        - booths (int) : nombre de comptoirs dans l'aérogare
        - rows (int) : nombre de rangées de comptoirs
        """
        self._flights = flights
        self.booths = booths
        """Nombre de comptoirs disponibles."""
        self.rows = rows
        """Nombre de rangées de comptoirs."""
        self.booths_per_row = booths // rows
        """Nombre de comptoirs par rangée."""
        for i, fi in enumerate(self._flights): fi._index = i
        self.cost = [[f._cost_bin(row) for row in range(self.rows)]
                     for f in self._flights]
        """Le coût d'affectation : matrice indexée par les vols puis les numéros
        rangée. Par exemple, pour avoir le coût du vol `f` sur la rangée `r` :
        `inst.cost[f][r]`."""
        self._solution = False

    @property
    def flights(self):
        """Liste des vols."""
        return self._flights.copy()

    @staticmethod
    def from_file(filename):
        """Crée une nouvelle instance à partir du fichier `filename`."""
        with open(filename) as f:
            booths, rows = map(int, f.readline().strip('# \t\n').split())
            return Instance([Flight(line) for line in f], booths, rows)

    def __repr__(self): return f'{self.__class__.__name__}({self.flights})'
    def __str__(self): return '\n'.join(str(f) for f in self.flights)
    def __len__(self): return len(self.flights)
    def __iter__(self): return iter(self.flights)

    def __getitem__(self, key):
        if isinstance(key, int): return self.flights[key]
        elif isinstance(key, slice):
            return Instance(self.flights[key], booths=self.booths, rows=self.rows)

    def __add__(self, other):
        return Instance(self.flights + other.flights,
                        booths=self.booths, rows=self.rows)

    def _to_file(self, filename):
        with open(filename, 'w') as f:
            print('#', self.booths, self.rows, file=f)
            for flight in self.flights:
                print(flight._to_csv(), file=f)

    def solution(self, first, last_minute=None):
        """Implémente une solution pour l'instance, afin de pouvoir la valider
        et la dessiner.

        - `first` : liste des premiers comptoirs
        - `last_minute` (optionnel) : liste des comptoirs restants ouvert dans les dernières 45 minutes

        Attention ! Les comptoirs sont numérotés à partir de 0, donc les indices des comptoirs sont entre `0` et `.booths - 1` !
        """
        err_msg = 'Solution incorrecte : certaines valeurs sont négatives'
        for c in first:
            if c < 0: raise ValueError(err_msg)
        self._solution = True
        for f, ff in zip(self.flights, first): f._first = ff
        if last_minute is not None:
            for c in last_minute:
                if c < 0: raise ValueError(err_msg)
            for f, lm in zip(self.flights, last_minute):
                f._last_minute = lm
        # Calcul de dépassements
        self._overflow = [f for f in self.flights if self.booths < f._first + f.booths]
        # Calcul des conflits
        steps = 24 * (60 // STEP)
        occ = [[None] * steps for _ in range(self.booths)]
        self._conflicts = _Conflicts()
        for f in self.flights:
            for t in range(f.opening.t, f.closing.t):
                for b in range(f._first, f._first + f.booths):
                    if occ[b][t] is None:
                        occ[b][t] = [f]
                    else:
                        for of in occ[b][t]: self._conflicts.add(of, f, t, b)
                        occ[b][t].append(f)
            for t in range(f.closing, f.tko):
                b = f._last_minute
                if b is not None:
                    if occ[b][t] is None:
                        occ[b][t] = [f]
                    else:
                        for of in occ[b][t]: self._conflicts.add(of, f, t, b)
                        occ[b][t].append(f)
        # Calculs sur dernier comptoir
        self._no_last = [f for f in self.flights if f._last_minute is None]
        self._last_outside = [f for f in self.flights
                              if f._last_minute is not None
                              and f._last_minute not in range(f._first, f._first + f.booths)]
        # Calculs sur les rangées
        l = [(f._first // self.booths_per_row,
              (f._first + f.booths - 1) // self.booths_per_row,
              f) for f in self.flights]
        self._row_issues = [(rf, rl, f) for rf, rl, f in l if rf != rl]

    def overflow(self):
        """Renvoie le nombre de vols causant un dépassement du nombre de comptoirs disponibles."""
        return len(self._overflow)

    def conflicts(self):
        """Renvoie le nombre de conflits entre vols sur un même comptoir."""
        return None

    def last_booth_conflict(self):
        """Renvoie le nombre de vols dont le comptoir pour le dernières 45 minutes est pris en dehors de précédents."""
        return len(self._last_outside)

    def row_conflicts(self):
        """Renvoie le nombre de vols qui ont des comptoirs sur plusieurs rangées."""
        return len(self._row_issues)

    def _validate_overflow(self):
        if self._overflow == []:
            print(_CHECK, 'Pas de dépassement du nombre de comptoirs disponibles')
        else:
            print(_FAIL, 'Dépassement du nombre de comptoirs disponibles')
            with open(_LOGFILE, 'a') as log:
                print('\nDépassements du nombre de comptoirs :', file=log)
                print(f'{"Vol":<7} -- Comptoirs utilisés', file=log)
                for f in self._overflow:
                    print(f'{f.callsign} -- {f._first}-{f._first + f.booths - 1}', file=log)

    def _validate_conflicts(self):
        if not self._conflicts.is_empty():
            print(_FAIL, 'Il y a des conflits entre vols sur certains comptoirs')
            self._conflicts.edit()
        else:
            print(_CHECK, 'Pas de conflits entre vols')

    def _validate_last(self):
        if self._no_last != []:
            print(_WARN, 'Certains vols n\'ont pas de comptoir pour les dernières 45min.')
            with open(_LOGFILE, 'a') as log:
                print('\nVols sans comptoir pour les dernières 45min :', file=log)
                for f in self._no_last:
                    print(f'{f.callsign}', file=log)
        elif self._last_outside == []:
            print(_CHECK, 'Dernier comptoir OK')
        else:
            print(_FAIL, 'Dernier comptoir pris en dehors des comptoirs précédents')
            with open(_LOGFILE, 'a') as log:
                print('\nDernier comptoir en dehors des précédents :', file=log)
                print(f'{"Vol":<7} -- Comptoirs utilisés -- Dernier comptoir', file=log)
                for f in self._last_outside:
                    print(f'{f.callsign:<7} -- {f._first}-{f._first + f.booths - 1} -- {f._last_minute}', file=log)

    def _validate_rows(self):
        if self._row_issues == []:
            print(_CHECK, 'Comptoirs d\'un même vol sur rangée unique')
        else:
            print(_FAIL, 'Certains vols ont des comptoirs sur plusieurs rangées')
            with open(_LOGFILE, 'a') as log:
                print('\nVols à cheval sur plusieurs rangées:', file=log)
                for rf, rl, f in self._row_issues:
                    print(f'{f.callsign:<7} -- rangées {rf} et {rl}', file=log)

    def cost_booths(self):
        """Renvoie le nombre de comptoirs et le nombre de rangées utilisés par la solution."""
        used_booths = [False] * self.booths
        used_rows = [False] * self.rows
        for f in self.flights:
            for b in range(f._first, f._first + f.booths):
                used_booths[b] = True
                used_rows[b // self.booths_per_row] = True
        return (sum(1 for b in used_booths if b), sum(1 for r in used_rows if r))

    def _validate_cost_booths(self):
        ub, ur = self.cost_booths()
        print(f'Comptoirs utilisés : {ub}/{self.booths}')
        print(f'Rangées utilisés : {ur}/{self.rows}')

    def cost_preferences(self):
        """Calcule le coût de la solution implémentée."""
        if self.rows > 1:
            return sum(self.cost[f][f._first // self.booths_per_row]
                       for f in self.flights)
        else: return 0

    def _validate_cost(self): print(f'Coût de la solution : {self.cost_preferences()}')

    def validate(self):
        """Permet de vérifier la validité d'une solution implémentée par la méthode
        `.solution`.

        Cette méthode vérifie les points suivants :
        - on n'utilise pas plus de comptoirs que ceux disponibles dans l'aérogare
        - il n'y a pas de conflit entre vols sur un même comptoir
        - le comptoir pour les dernières 45 minutes est pris parmi les précédents
        - les comptoirs pour un vol sont tous dans la même rangée

        Elle calcule également :
        - le nombre de comptoirs utilisés
        - le coût vis-à-vis des préférences des compagnies
        """
        if self._solution:
            with open(_LOGFILE, 'w') as log:
                print('Instance :', file=log)
                print(str(self), file=log)
            self._validate_overflow()
            self._validate_conflicts()
            self._validate_last()
            self._validate_rows()
            self._validate_cost_booths()
            self._validate_cost()
        else:
            print('Pas de solution à valider')

    def draw(self, filename=None):
        """Dessine la solution implémentée.

        Si un nom de fichier est fourni, la figure sera enregistrée dans le
        fichier plutôt que dessinée dans une fenêtre Matplotlib.
        Exemple :

        `inst.draw('/home/cyril/rota/instance-4vols-v1.png')`"""
        if self._solution:
            times = [f.opening for f in self.flights] + [f.tko for f in self.flights]
            min_t = int(min(times))
            max_t = int(max(times))
            # usedCounters = max([f._first + f.booths - 1 for f in self.flights])

            palette = mcolors.TABLEAU_COLORS
            colors = list(palette.keys()) # gets the list of color names
            fig, ax = plt.subplots()
            for i, f in enumerate(self.flights):
                color = palette[colors[i % len(colors)]]
                text_color = _darken(color, amount=1.3)
                alpha = 0.7
                plt.text(3 + f.opening, f._first + 0.4, f.callsign, color=text_color)
                ax.add_patch(
                    Rectangle(
                        (f.opening, f._first), f.closing - f.opening, f.booths,
                        color=color, alpha=alpha))
                if f._last_minute is not None:
                    ax.add_patch(
                        Rectangle(
                            (f.closing, f._last_minute), f.tko - f.closing, 1,
                            color=color, alpha=alpha))

            plt.xlabel("Time")
            plt.xlim(min_t, max_t)
            xs = range(min_t, max_t + 1, 60 // STEP)
            plt.xticks(xs, [Time(t) for t in xs])
            ax.xaxis.set_minor_locator(MultipleLocator(1))

            plt.ylabel("Counters")
            plt.ylim(0, self.booths)
            plt.yticks(range(0, self.booths + 1, self.booths_per_row))
            ax.yaxis.set_minor_locator(MultipleLocator(1))

            plt.grid(visible=True)
            plt.grid(visible=True, which='minor', color='lightgray', linewidth=0.3)
            plt.title("Used counters per flight")
            if filename is None: plt.show()
            else: plt.savefig(filename)


class Flight:
    """Informations sur les vols.

    Outre les attributs décrits ci-après, les vols peuvent être comparés (`f1 < f2`)
    selon leur identifiant unique (pour retrouver l'ordre d'origine des instances,
    par exemple).
    """

    def __init__(self, line):
        """Crée un nouveau vol (vous ne devriez pas avoir besoin de ce constructeur).
        """
        data = line.strip().split(',')
        self.uid = int(data[0])
        """Un identifiant unique (int)."""
        self.callsign = data[1]
        """L'identifiant commercial du vol (str)."""
        self.tko = Time(data[2])
        """L'heure de décollage (Time)."""
        self.opening = self.tko - _OPENING
        """Heure d'ouverture des comptoirs (Time)."""
        self.closing = self.tko - _CLOSING
        """Heure de fermeture des comptoirs -- sauf 1 qui reste ouvert (Time)."""
        self.booths = int(data[3])
        """Le nombre de comptoirs requis pour le vol (int)."""
        self.preferences = [int(r) for r in data[4].split()]
        """Les rangées préférées par la compagnie aérienne (int list)."""
        self._index = None # position dans l'instance
        self._first = None
        """Le premier comptoir alloué au vol -- les autres sont en suivant (int)."""
        self._last_minute = None
        """Le comptoir restant ouvert pour les 45 dernières minutes (int)."""

    def __repr__(self):
        return f'{self.__class__.__name__}({self.uid}, {self.callsign}, {self.tko}, {self.booths}, {self.preferences})'

    def __str__(self):
        return f'{self.uid:4d} {self.callsign:<7} {str(self.tko)} {self.booths:2d} {",".join(str(r) for r in self.preferences)}'

    def _to_csv(self):
        return f'{self.uid},{self.callsign},{str(self.tko)},{self.booths},{" ".join(str(r) for r in self.preferences)}'

    def __lt__(self, other): return self.uid < other.uid
    def __index__(self): return self._index

    def _cost_bin(self, row):
        if self.preferences == [] or row in map(int, self.preferences): return 0
        else: return 1


class Time:
    """Manipulation d'heures.

    Exemple d'utilisation :
    ```python
    t1 = Time(11, 35) # création à partir d'heures et minutes
    dt = Time(7)      # création à partir d'un nombre de pas de temps
    print(t)          # affiche le temps sous la forme "hh:mm"
    t2 = t1 + dt      # on peut additioner et soustraire des temps
    t1 < t2           # comparaison de deux temps
    ```
    """

    def __init__(self, *time):
        """
        Plusieurs possibilités pour créer un temps :
        ```python
        t = Time("18:45") # à partir d'une chaîne de caractères de la forme "hh:mm"
        t = Time(18, 45)  # à partir des heures et minutes données en entiers
        t = Time(225)     # à partir d'un nombre de pas de temps
        ```
        Lève `ValueError` si le format n'est pas correct.
        """
        if len(time) == 1 and isinstance(time[0], int):
            t = time[0]
        elif len(time) == 1 and isinstance(time[0], str):
            h, m = time[0].split(':')
            t = (int(h) * 60 + int(m)) // STEP
        elif len(time) == 2:
            t = (int(time[0]) * 60 + int(time[1])) // STEP
        else: raise ValueError(f'Unsupported format for Time: {time}')
        self.t = t
        """Le temps en pas de temps."""
        self.tm = self.t * STEP
        r"""Le temps en minutes (`self.tm` $=$ `self.t` $\times$ `STEP`)."""

    def __repr__(self): return f'{self.__class__.__name__}({str(self)})'
    def __str__(self): return f'{self.tm // 60:02d}:{self.tm % 60:02d}'
    def __lt__(self, other): return self.t < other.t
    def __add__(self, other): return Time(self.t + other.t)
    def __sub__(self, other): return Time(self.t - other.t)
    def __index__(self): return self.t
    def __int__(self): return self.t
    def __radd__(self, i): return Time(self.t + i)


_OPENING = Time(2, 30)
_CLOSING = Time(0, 45)


class _Conflicts(dict):

    def __init__(self): super().__init__()

    def is_empty(self): return self == {}

    def add(self, f1, f2, t, b):
        if (f1, f2) in self:
            times, booths = self[(f1, f2)]
            times.append(t)
            booths.append(b)
        else:
            self[(f1, f2)] = ([t], [b])

    def edit(self):
        l = sorted(self.items())
        with open(_LOGFILE, 'a') as log:
            print('\nConflits :', file=log)
            print(f'{"Vols impliqués":<15} -- {"Période":<11} -- Comptoirs concernés', file=log)
            for (f1, f2), (times, booths) in l:
                min_t = Time(min(times))
                max_t = Time(max(times) + 1) # pour inclure la durée du dernier pas de temps
                print(f'{f1.callsign:>7} {f2.callsign:>7} -- {str(min_t)}-{str(max_t)} -- {list(set(booths))}', file=log)


def _darken(color, amount=1.5):
    import colorsys
    try:
        c = mcolors.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mcolors.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])

