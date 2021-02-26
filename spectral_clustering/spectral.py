"""
Modul spectral.
Modul zawiera implementacje funkcji Mnn(), Mnn_graph(), Laplacian_eigen(), spectral_clustering() 
"""

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from sklearn.cluster import KMeans


def Mnn(X, M):
    """
    Funkcja wyznacza macierz najbliższych sąsiadów 
    dla zadanej macierzy X oraz liczby naturalnej M. 
    ------------------
    param:
    X - dwuwymiarowa macierz o wymiarach (n,d) i elementach rzeczywistych
    N - liczba naturalna oznaczająca drugi wymiar macierzy wyjściowej
    ------------------
    return value:
    S - dwuwymiarow macierz o wymiarach (n,M) i elementach rzeczywistych, 
    taka że S[i,j] jest indeksem j-tego najbliższego sąsiada X[i] względem metryki euklidesowej
    """
    
    # Sprawdzenie poprawności argumentów wejściowych
    if type(M) != int:
        raise TypeError("Argument M był {0} a powinien być typu {1}".format(type(n), int))
       
    if type(X) != np.ndarray:
        raise TypeError("Argument X był {0} a powinien być typu {1}".format(type(X), np.ndarray))
    elif X.ndim != 2:
        raise ValueError("Podana macierz X nie jest dwuwymiarowa.")
    
    # Sprawdzenie czy wartość M > ilość wierszy macierzy X odjąć 1
    if M > X.shape[0] - 1:
        raise ValueError("Ilość sąsiadów M = {0} jest większa niż ilość możliwych sąsiadów n = {1}.".format(M, X.shape[0]-1))
    
    # Sprawdzenie typu wartości macierzy X i ewentualna konwersja na float    
    if X.dtype != np.float:
        X = X.astype(np.float)
    
    n, d = X.shape
    S = np.zeros((n, M), dtype=np.int)
    # Stworzenie macierzy pomocniczej gdzie P[i,j] = ||x[i] - x[j]||
    P = np.zeros((n, n))
    for i in range(n):
        P[i, i] = np.inf
        for j in range(i+1, n):
            dist = np.linalg.norm(X[i] - X[j])
            P[i, j] = dist
            P[j, i] = dist
    
    # Uzupełnienie macierzy S poprzez posortowanie kolejnych wierszy macierzy P
    # i wybranie pierwszych M elementów każdego wiersza
    for i in range(n):
        S[i] = np.argsort(P[i])[0:M]
     
    # Zwrócenie wynikowej macierzy z konwersją wartośći indeksów na int
    return S


def Mnn_graph(S):
    """
    Funkcja wyznacza macierz sąsiedztwa dla przyjmowanej macierzy S. 
    Dwa punkty i,j są uznawane za sąsiadów, jeśli istnieje takie u, 
    że S[i,u] = j lub S[j,u] = 1.
    Jeśli graf reprezentowany przez tą macierz sąsiedztwa jest niespójny, 
    to zostaje on uspójony poprzez dodanie p-1 krawędzi, gdzie p to liczba 
    spójnych składowych grafu.
    ------------------
    param:
    S - dwuwymiarowa macierz o wymiarach (n,m) i elementach naturalnych
    ------------------
    return value:
    G - dwuwymiarow macierz o wymiarach (n,n) i elementach ze zbioru {0,1}, 
    reprezentująca macierz sąsiedztwa grafu nieskierowanego o n wierzchołkach
    """
    
    # Sprawdzenie poprawności danych wejściowych
    if type(S) != np.ndarray:
        raise TypeError("Argument S był {0} a powinien być typu {1}".format(type(S), np.ndarray))
    elif S.ndim != 2:
        raise ValueError("Podana macierz S nie jest dwuwymiarowa.")
    elif S.dtype != np.int:
        raise TypeError("Wartości S są typu {0} a powinny być typu {1}".format(S.dtype, np.int))
    
    n, m = S.shape
    G = np.zeros((n, n), dtype=np.int)
    
    # Wypełenienie macierzy sąsiedztwa G
    for i in range(n):
        for j in range(i+1, n):
            if np.any(S[i, :] == j) or np.any(S[j, :] == i):
                G[i, j] = 1
                G[j, i] = 1
    
    # Sprawdzenie czy graf G jest spójny
    # Źródło: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.connected_components.html
    n_components, labels = connected_components(csgraph=csr_matrix(G), directed=False, return_labels=True)
    
    if n_components == 1:
        return G
    else:
        # Uspójnienie grafu G
        # Odczytanie największej etykiety, czyli ilości składowych do uspójnienia
        last_label = np.max(labels)      
        
        # Dla każdej etykiety łączymy ostatni wierzchołek o tej etykiecie 
        # z  pierwszym wierzchołkiem kolejnej etykiety
        for label in range(0, last_label):
            j = np.argmax(labels > label)
            i = j - 1
            G[i, j] = 1
            G[j, i] = 1
            
        return G


def Laplacian_eigen(G, k):
    """
    Funkcja wyznacza laplasjan L grafu reprezentowanego przez macierz G.
    Zwraca macierz, której kolumny składają się z wektorów własnych
    macierzy L odpowiadających 2., 3., ..., (k+1) najmniejszej wartości własnej L.
    ------------------
    param:
    G - dwuwymiarowa macierz o wymiarach (n,n) i elementach ze zbioru {0,1}
    k - drugi wymiar zwracanej macierzy (ilość zwracanych wektorów własnych) 
    ------------------
    return value:
    E - dwuwymiarow macierz o wymiarach (n,k) której kolumny to kolejne wektory własne 
    laplasjanu macierzy G.
    """  
    
    # Sprawdzenie poprawności danych wejściowych
    if type(G) != np.ndarray:
        raise TypeError("Argument G był {0} a powinien być typu {1}".format(type(G), np.ndarray))
    elif G.ndim != 2:
        raise ValueError("Podana macierz G nie jest dwuwymiarowa.")
        
    if type(k) != int:
        raise TypeError("Argument k był {0} a powinien być typu {1}".format(type(k), int))  
    

    # Wyznaczenie wektora takiego, że d[i] = stopień i-tego wierzchołka G
    d = G.sum(axis=1)
    # Wyznaczenie laplasjanu grafu G
    L = np.diag(d) - G

    # Obliczenie wartości i wektorów własnych
    w, v = np.linalg.eig(L) 
    
    # Posortowanie wyników po wartościach własnych i wybranie 
    # odpowiednich wektorów własnych z posortowanej tablicy
    E = v[:, np.argsort(w)][:, 1:(k+1)]
    
    return E


def spectral_clustering(X, k, M):
    """
    Funkcja implementująca algorymt spectralny, 
    polegający na zastosowaniu procedury k-średnich 
    dla odpowiednio przekształconej macierzy X.
    ------------------
    param:
    X - dwuwymiarowa macierz o wymiarach (n,d) i elementach ze zbioru liczb rzeczywistych
    k - parametr ilości skupień
    M - parametr ilości najbliższych sąsiadów
    ------------------
    return value:
    z - tablica określająca przynależność kolejnych punktów Xi do jednego z k skupień
	Jeśli podczas wykonywania funckji wystąpił wyjątek, to zwracana tablica jest pusta.
    """
    
    try:
        # Sprawdzenie poprawności danych wejściowych
        if type(X) != np.ndarray:
            raise TypeError("Argument G był {0} a powinien być typu {1}".format(type(X), np.ndarray))
        elif X.ndim != 2:
            raise ValueError("Podana macierz X nie jest dwuwymiarowa.")
        if type(k) != int:
            raise TypeError("Argument k był {0} a powinien być typu {1}".format(type(k), int))     
        if type(M) != int:
            raise TypeError("Argument M był {0} a powinien być typu {1}".format(type(M), int))

        # Sprawdzenie, czy jest możliwy podział na zadaną ilość skupień
        if k > X.shape[0]:
            raise ValueError("Podana ilość skupień {0} jest większa niż ilość obserwacji {1}.".format(k, X.shape[0]))
        if k <= 0:
            raise ValueError("Podana ilość skupień musi być jest większa niż 0.")

        # Wyznaczenie macierzy M-najbliższych sąsiadów
        S = Mnn(X, M)
        
        # Wyznaczenie macierzy sąsiedztwa
        G = Mnn_graph(S)
        
        # Wyznaczenie laplasjanu i jego wektorów własnych
        E = Laplacian_eigen(G, k)
        
        # Zastosowanie algorytmu k-średnich
        kmeans = KMeans(n_clusters=k, random_state=0).fit(E)
        
        # Odczytanie ciągu takiego, że wartość z[i] oznacza do którego z k skupień należy punkt Xi
        z = kmeans.labels_
        
        return z
    
    except Exception as e:
        print(e)
        return []
