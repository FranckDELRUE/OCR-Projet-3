import pandas as pd
import numpy as np

def sommeSerie(df, annee, element1, code1, text = 0, mul = 1, element2 = 0, code2 = 0):
    """
        Permet de faire la somme d'une série, à partir d'une Data frame, en choissisant l'année, la colonne (element1) 
        et le type d'information de la colonne (code1).
        Text permet de choisir de retourner un string (1) ou non (0)
        mul est le multiplicateur appliqué à la somme pour la convertion des unités
        element2 et code 2 sont les élements d'un filtre supplementaire à faire sur le Data Frame. code2 peut-etre une liste
        retourne soit un string soit un float
    """
    if (code2 == 0) & (element2 == 0):
        filt = 1
    elif isinstance(code2, int):
        filt = (df[element2] == code2)
    else:
        filt = (df[element2].isin(code2))
        
    somme = df[(df[element1] == code1) & (df['Année'] == annee) & (filt)].Valeur.sum() * mul
    if text != 0:
        return f'En {annee}, {text[0]} {somme} {text[1]}'
    else:
        return somme
    
def differencePopulation(df, annee, element1, code1, element2, code2, code3, multiplicateur = 1000):
    """
        Prend un Data Frame et une année, deux colonnes (element1 et element2) et leurs types d'informations dans la colonne
        (code1 et code2). 
        Le premier element-code est pour choisir la population, le deuxième element-code est pour choisir le pays.
        code3 est une liste pour une liste de pays pour faire la comparaison multiplicateur permet la conversion d'unité, 
        ici de milliers de personnes à 1 personne retourne un string
    """
    somme1 = sommeSerie(df, annee, element1, code1, 0, multiplicateur, element2, code2)
    somme2 = sommeSerie(df, annee, element1, code1, 0, multiplicateur, element2, code3)
    diff = somme1 - somme2
    text = ('La différence entre la population de la Chine et des autres pays contenant le mot Chine est de', "Il n'y a pas de différence")
    return f"{text[0]} {abs(diff)} habitants" if diff else f'{text[1]}'

def calculPopulation(df, annee, text = 0):
    """
        permet de calculer la population en utilisant la fonction sommeSérie
        texte permet de choisir de retourne soit un text (=1) ou un float (=0) 
    """
    if ~text:
        return sommeSerie(df, annee, 'Code Élément', 511, 0, 1000)
    elif text:
        return sommeSerie(df, annee, 'Code Élément', 511, ('la population mondiale est de','habitants'), 1000)

def retourneLigne(df, annee, parametre):
    """
        permet de retourner une ligne de la data Frame passée en argument avec l'année
        Prends un dictionnaire pour passer les parametres de selection
        Retourne une ou des lignes
    """
    filt = (df['Année'] == annee)
    
    for k,v in parametre.items() :
        filt &= (df[k] == v)
        
    return df[filt]

def retourneValeur(df, annee, parametre, valeur):
    """
        permet de retourner une valeur d'une ligne d'une Data Frame. Prend le Data Frame et l'année
        Parametre est un dictionnaire pour la selection de la ligne de la Data Frame et une colonne (valeur) pour retourner sa
        valeur
    """
    return retourneLigne(df, annee, parametre)[valeur].values

def retourneValeurs(df, annee, parametre, element, codes, valeur):
    """
        permet de retourner plusieurs valeurs de differentes lignes ayant des éléments en commun.
        parametre est un dictionnaire. element selectionne la colonne et codes selectionne les lignes 
        valeur retourne les valeurs de la colonne selectionnée
        Retourne un tuple, avec les valeurs
    """
    val = []
    dico = {}
    for v in codes:
        dico = parametre.copy()
        dico[element] = v
        val.append(retourneValeur(df, annee, dico, valeur)[0])
        
    return tuple(val)
        
def ajoutLigne(df, element, code, nouveauElement, nouveauCode, nouveauUnite, colonne, multiplicateur = 1, avec = 'Zone', comment = 'left', operation = 'multiplication'):
    """
        Permet de rajouter des lignes à la Data Frame. La valeur provient d'une opération entre les valeurs deux deux autres
        lignes
        Cette fonction merge deux colonnes, fais une operation entre les deux valeurs mergées, et retourne la Data Frame avec
        les nouvelles
        lignes
        Cette fonction prend une Data Frame
    """
    filt1 = df[element] == code[0]
    filt2 = df[element] == code[1]
    
    df2 = pd.merge(df[filt1], df.loc[filt2, colonne], how = comment, on = avec)
    if operation == 'multiplication':
        df2['Valeur_x'] = df2['Valeur_x'] * df2['Valeur_y'] * multiplicateur
    elif operation == 'division':
        df2['Valeur_x'] = df2['Valeur_x'] / df2['Valeur_y'] * multiplicateur
    elif operation == 'add':
        df2['Valeur_x'] = (df2['Valeur_x'] + df2['Valeur_y']) * multiplicateur
    
    df2['Code Élément'] = nouveauCode
    df2['Élément'] = nouveauElement
    df2['Unité'] = nouveauUnite
    df2['Description du Symbole'] = 'Donnée calculée'
    
    df2.rename(columns={'Valeur_x': 'Valeur'}, inplace=True)
    df2.drop(['Valeur_y'], axis=1, inplace=True)
    df2.replace(np.inf, 0, inplace=True)
    return pd.concat([df, df2], ignore_index=True, sort=False).fillna(0)

def calculNourriturePersonne(df, annee, element, veg = 0, jour = 0):
    """
        Permet de retourner un string contenant les pourcentages de population mondiale nourri par rapport à l'element passés en 
        argument. il prend une dataFrame, une année. 
        veg permet de prendre en compte que les végétaux dans la dataFrame
        jour permet de signaler que l'élément à une unité journalier et non annuelle
    """
    liste = (2720, 0.056)
    personne = []
    typeProduit = []
    
    pop = calculPopulation(df, annee, 0)
    
    if veg:
        element2 = '_calc_Vegetaux'
        code2 = 1     
    else:
        element2 = 0
        code2 = 0
        
    if jour:
        mulJour = 1
    else:
        mulJour = 365

    for i in range(2):
        typeProduit.append(df.loc[df['Code Élément'] == element[i], 'Élément'].iloc[0])
        som = sommeSerie(df, annee, 'Code Élément', element[i], 0, 1, element2, code2)
        personne.append(som / (liste[i] * mulJour))

    return f'En {annee}, la {typeProduit[0]}, permet de nourrir {personne[0]} personnes en Kcal soit {(personne[0] / pop) * 100} % de la population mondiale. Et, la {typeProduit[1]}, permet de nourrir {personne[1]} personnes en Kg de Protéines soit {(personne[1] / pop) * 100} % de la population mondiale'
        
def calculNourriture(df, annee):
    """
        Permet de calculer le résultat de la question 8 en additionnant les 3 composants Food, Feed et Waste
        Il renvoie un string formaté comprenant les réponses. Il s'appuie sur la fonction calculNourriturePersonne pour le
        renvoyer.
    """
    codeElementFood = 5142
    codeElementFeed = 5521
    codeElementWaste = 5123
    
    colonne = ['Zone', 'Valeur', 'Produit', 'Année']
    avec = ['Zone', 'Année', 'Produit']

    codeAddFoodFeed = (codeElementFood, codeElementFeed)
    
    nouveauElementFoodFeed = 'FeedFood (Milliers de Kg)'
    nouveauUniteFoodFeed = 'Milliers de Kg'
    nouveauCodeFoodFeed = 9142
    
    df = ajoutLigne(df, 'Code Élément', codeAddFoodFeed, nouveauElementFoodFeed, nouveauCodeFoodFeed, nouveauUniteFoodFeed, colonne, 1000, avec, 'left', 'add')
    
    codeAddFoodFeedWaste = (nouveauCodeFoodFeed, codeElementWaste)

    nouveauElementFoodFeedWaste = 'Disponibilité Alimentaire (Food/Feed/Waste) (Kg)'
    nouveauUniteFoodFeedWaste = 'Milliers de Kg'
    nouveauCodeFoodFeedWaste = 9143

    multiplicateurFoodFeedWaste = 1000
    
    df = ajoutLigne(df, 'Code Élément', codeAddFoodFeedWaste, nouveauElementFoodFeedWaste, nouveauCodeFoodFeedWaste, nouveauUniteFoodFeedWaste, colonne, multiplicateurFoodFeedWaste, avec, 'left', 'add')
    
    df = df[df['Code Élément'] != nouveauCodeFoodFeed]
    
    energieFoodFeedWaste = ('Disponibilité Alimentaire (Food/Feed/Waste) (Kcal)', 9145)
    proteineFoodFeedWaste = ('Disponibilité Alimentaire de protéines en quantité (Food/Feed/Waste) (Kg)', 9155)
    
    df = creatLigneRatio(df, nouveauCodeFoodFeedWaste, energieFoodFeedWaste, proteineFoodFeedWaste)
        
    df = df[df['Code Élément'] != nouveauCodeFoodFeedWaste]
    
    codeFoodFeedWaste = (9145, 9155)
    
    return calculNourriturePersonne(df, annee, (9145, 9155), 1)

def creatLigneRatio(df, code, energie, proteine, multiplicateur = 1):
    """
         Permet de créer deux lignes ratio pour calculer selon une ligne donnée les ratios Energie 9684 et Proteine 9694
         Il retourne la data Frame avec les nouvelles lignes de ratios
    """
    codeElementRatioEnergie = 9684
    codeElementRatioProteine = 9694

    codeRatioEnergie = (code, codeElementRatioEnergie)
    codeRatioProteine = (code, codeElementRatioProteine)

    nouveauElementEnergie = energie[0]
    nouveauUniteEnergie = 'KCal'
    nouveauCodeEnergie = energie[1]

    nouveauElementProteine = proteine[0]
    nouveauUniteProteine = 'Kg'
    nouveauCodeProteine = proteine[1]

    colonne = ['Zone', 'Valeur', 'Produit', 'Année']
    avec = ['Zone', 'Année', 'Produit']
    
    df = ajoutLigne(df, 'Code Élément', codeRatioEnergie, energie[0], energie[1], 'KCal', colonne, multiplicateur, avec)
    df = ajoutLigne(df, 'Code Élément', codeRatioProteine, proteine[0], proteine[1], 'Kg', colonne, multiplicateur, avec)
    
    return df

def ligneToColonne(df, dicCode):
    """
        Prends une data frame et un dictionnaire. Permet de mettre des éléments du dictionnaire, présentés en ligne, en colonne.
        Les colonnes "Code Élément", "Élément" et "Valeur" sont supprimées
        Retourne la data Frame avec les colonnes. Les lignes sont supprimées.
    """
    colonne = ['Valeur', 'Code zone', 'Année', 'Code Produit']
    avec = ['Code zone', 'Année', 'Code Produit']

    for k,v in dicCode.items():
        filt1 = (df['Code Élément'] == k)
        df = df.merge(df.loc[filt1, colonne], how = 'left', on = avec).fillna(0)
        df.rename(columns={'Valeur_x': 'Valeur', 'Valeur_y': v}, inplace=True)
    
    df.rename(columns={'Code zone': 'code_pays', 'Zone': 'pays', 'Code Produit' : 'code_produit', 'Produit' : 'produit', 'Année': 'annee'}, inplace=True)
    return df.drop(["Code Élément", "Élément", 'Valeur'], axis=1).drop_duplicates()

    