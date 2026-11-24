# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.7
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import fastai
import pandas as pd, numpy as np, matplotlib.pyplot as plt, math

# %%
l = [math.log2(v) for v in range(10, 100, 5)]
print(l)
n = np.arange(500, 710, 12)
print(n)

# %%
plt.scatter(l, n)

# %%
urls = search_images('bird photos', max_results=10)
urls[0]

# %%
# ============================================
# SOLUZIONE 1: Codice Aggiornato per il Notebook
# ============================================
# Sostituisci il vecchio codice con questo nel tuo notebook

from duckduckgo_search import DDGS
from fastcore.all import *

def search_images(keywords, max_results=200):
    """
    Cerca immagini usando DuckDuckGo Search (API aggiornata)
    
    Args:
        keywords: termini di ricerca
        max_results: numero massimo di risultati
    
    Returns:
        L (lista estesa fastai) di URL immagini
    """
    with DDGS() as ddgs:
        # NOTA: L'API restituisce un generatore
        results = ddgs.images(keywords=keywords, max_results=max_results)
        # Estrai gli URL dalle immagini
        image_urls = [result.get("image") for result in results]
    
    return L(image_urls)

# Esempio d'uso:
# urls = search_images('bird photos', max_results=100)
# print(f"Trovate {len(urls)} immagini")


# ============================================
# SOLUZIONE ALTERNATIVA (per compatibilità con vecchio codice)
# ============================================
# Se vuoi mantenere il nome del modulo "ddgs" per retrocompatibilità

import sys
from duckduckgo_search import DDGS

# Crea un alias del modulo
class DDGSModule:
    def __init__(self):
        self.DDGS = DDGS

sys.modules['ddgs'] = DDGSModule()

# Ora puoi usare: from ddgs import DDGS

# %%
n = 25
remainders = []
while n != 0: 
    print(n % 2)
    remainders.append(str(n % 2 ))
    n = n // 2
print("".join(remainders)[::-1])


# %%
print("Ciao")


# %%
