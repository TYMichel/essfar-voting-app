""" Pour ne pas rallonger l'application streamllit, cette librairie permmet de faire les traitements sur 
le jeu de données des votes et permet de tracer les graphiques nécéssaires

Les votes devront être éffectués dans le même mois"""
import pandas as pd 
import matplotlib.pyplot as plt 
import matplotlib.colors as mcolors 
import random as rd
from collections import ChainMap

#-----------------------------Transformation du jeu de données 

def minute_absolue(timestamp,ref):
    """applicable sur la colonne des timestamps
        ref : timestamp du premier vote 

        la fonction calcule la minute absolue sur 1 mois (a cause de la formule) d'un vote
        """
    # conversion 
    timestamp,ref = pd.to_datetime([timestamp,ref]) 
    # elements de reference 
    h_0 = ref.hour
    j_0 = ref.day
    # elements du vote
    h = timestamp.hour
    m_rel = timestamp.minute
    j = timestamp.day
    
    return m_rel + (h - h_0) * 60 + (j - j_0) * 24 * 60


def transformed_votes(votes : pd.DataFrame):
    """ Ajoute la colonne de la minute absolue au dataframe des votes """
    if "timestamp" not in votes.columns:
        print("Colonne timestamp manquante")
        return None
    df = votes
    ref = min(pd.to_datetime(votes["timestamp"]))
    df["minute_absolue"] = votes["timestamp"].apply(minute_absolue,args=(ref,))

    return df

def table_votes(t_votes):
    """ crées une table de contigence du nombre de vote de chaque candidat pour chaque minute"""
    # t_votes == transformed votes 
    grouped = t_votes.groupby(["vote","minute_absolue"])
    table = grouped.size().unstack(fill_value=0) # table de contingence minute-vote
    table = pd.DataFrame(table)
    print("Table transformée : ")
    print(table)
    print("index table transformée")
    print(table.index)
    
    table = table.cumsum(axis=1)
    return table 


#----------------------------graphique des votes en temps réels
def trace(tbl:pd.core.frame.DataFrame,matching={}):
    """ Prends en entrée la table avec les effectifs cumulés tels que transformés par les fonctions précédentes"""
    print(tbl)
    if type(tbl) != pd.core.frame.DataFrame: 
        print(" tbl pas une  dataframe...")
    candidats = tbl.index.to_list()
    print(f"candidats : {candidats}")
    colors = list(mcolors.BASE_COLORS.keys())
    print(f"colors {colors}")

    if  matching: # si le matching n'est pas vide
        print("le matching n'est pas vide.")
        
        if any([i not in candidats for i in list(matching.keys())] ):
            trace(tbl)
        to_remove = candidats.copy()
        for candidat in list(matching.keys()):
            to_remove.remove(candidat) # candidats qui ne sont pas dans le matching
    
    else:
        to_remove = candidats.copy()
        
    matching2 = {candidat : rd.choice(colors) for candidat in to_remove}
    matching = matching | matching2 
    print("Nous affichons le matching")
    print(matching)

    # minute absolue du premier vote 
    
    # trace les courbes
    fig,ax = plt.subplots(figsize=(15,8))
    for i in candidats:
        # pour avoir les minutes abolues
        ax.plot(tbl.loc[i].index - tbl.loc[i].index[0] , tbl.loc[i].values, label=i, marker='s', linestyle='-', color= matching[i]) 

    # mise en forme des graphiques
    print(type(ax))
    ax.set_title('📈 Nombre cumulé de votes par candidat  (par minute)', fontsize=16)
    ax.set_xlabel('minutes écoulées depuis le premier vote', fontsize=12)
    ax.set_ylabel('Nombre cumulé de votes', fontsize=12)
    ax.legend(title='Candidat', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.7)

    fig.tight_layout()
    return fig

 
#------------------------------Dénombrement des votes par candidats pour chaque minute




    