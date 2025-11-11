import streamlit as st
import pandas as pd
import os
from datetime import datetime, timezone
from streamlit_image_select import image_select

# ai_app.py
# GitHub Copilot
# Application Streamlit pour récupérer des votes avec vérification d'identifiants autorisés.
# Placez ce fichier dans /home/mike/MyPython/essfar-election/ai_app.py
# Utilisation: streamlit run ai_app.py
#* Tous les fichier seront en csv

st.set_page_config(page_title="Système de vote", layout="centered",initial_sidebar_state="collapsed")

#----------------------------------------- Nom de l'application ICI (modifiable à souhait) --------------------------------
st.title("🗳️ Élections présidentielles AGES 2025-2026")
#------------------------------------------------------------------------------------------------------------------------



st.image("./images/Essfar_logo.png")

# --- Sidebar: fichiers / options ---

# Autorized voters file uploader or path

# fichier de clé prédéfini 
keys_path = "fake_keys.csv" # les clés pour le vote (fake or real)
try:
    uploaded_auth = open(keys_path,"r")
except Exception as e:
    st.error(f"Impossible d'avoir les voteurs autorisés: {e}")
    

# Votes storage file path
votes_path =  "votes.csv"

#*  Chargements des candidats 
# En supposant qu'un fichier excel contient les noms des candidats

candidats = pd.read_excel("candidats.xlsx",header=0)
candidats = candidats.fillna(" ")

if candidats.empty:
    st.error(" Il n'y a aucun candidat dans le fichier excel des candidats. Bien vouloir en ajouter")

liste_candidats = [str(nom) +" "+ str(prenom) for nom, prenom in zip(candidats["nom"], candidats["prenom"])] 
if not liste_candidats:
    liste_candidats = ["Option 1", "Option 2", "Option 3"] 
    

# --- Charger la liste des identifiants autorisés ---
def load_authorized(uploaded_file):
    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded_file, dtype=str, header=0, names=["identifiant"])
            else:
                df = pd.read_excel(uploaded_file, dtype=str)
            return df.fillna("").astype(str)
        except Exception as e:
            st.error(f"Erreur lecture fichier uploadé: {e}")
            return None
    st.warning("Aucun fichier des identifiants autorisés fourni. Chargez un fichier ou placez-le au chemin indiqué.")
    return None

authorized_df = load_authorized(uploaded_auth)

# If loaded, ask which column contains the identifier
id_column = "identifiant" # le fichier contiendra une seule colonne (en théorie)
if isinstance(authorized_df, pd.DataFrame):
    authorized_ids = set(authorized_df[id_column].astype(str).str.strip())
else:
    authorized_ids = set()

# --- Charger/initialiser fichier des votes ---
def load_votes(path):
    """Trouve un fichier contenant les votes et le charge en
    dataframe, ou alors crées le fichier en question """
    if os.path.exists(path):
        try:
            df = pd.read_csv(path, dtype=str)
            return df.fillna("").astype(str)
        except Exception as e: #* Au cas où le fichier est vide.
            return pd.DataFrame(columns=["identifiant", "vote", "timestamp"])
    else:
        # create empty dataframe
        return pd.DataFrame(columns=["identifiant", "vote", "timestamp"])

votes_df = load_votes(votes_path)

# --- Formulaire de vote ---
st.header("Formulaire de vote")
def format_choice(chemin): 
        """ les choix sont des chemins vers des images, il faut 
        faire correspondre chaque image à un candidat. Le tout 
        en fonction du nom de l'image. """
        global liste_candidats
        st.write(liste_candidats)
        name = os.path.split(chemin)[1].split(".")[0]
        st.write(f" name : {name}")
        for i in liste_candidats:
            if name == i.split(" ")[0].lower(): 
                return i
        
        st.error("Il semblerait que les noms des images ne correspondent pas aux noms des candidats.")
with st.form("vote_form"):
    voter_id_raw = st.text_input(" 👤 Identifiant du votant (tel que dans la liste autorisée)", value="")
    # Choice selector
    
    #* Images des candidats
    # choice = st.selectbox("✉️  Choix du vote", options=default_choices)
    images = os.listdir("./images/candidats") # toutes les images 
    images = ["images/candidats/" + i  for i in images]
    
    if images == []: # si pas d'images
        st.error("Il n'y aucune image de candidats dans le dossier 'candidats'")
        
    choice = image_select("✉️  Choix du vote", images)
    # correspondance image et candidats
    if choice:
        choice = format_choice(choice)
    submit = st.form_submit_button("Valider le vote", type="primary", use_container_width=True )
    
if submit:
    voter_id = str(voter_id_raw).strip()
    if voter_id == "":
        st.error("Identifiant vide — le vote n'est pas pris en compte.")
    else:
        # Check authorization
        if voter_id not in authorized_ids:
            st.error("Identifiant non autorisé — le vote n'est pas pris en compte.")
        else:
            # Check if already voted
            already = False
            if not votes_df.empty:
                # compare after stripping
                already = any(votes_df["identifiant"].astype(str).str.strip() == voter_id)
            if already:
                st.warning("Cet identifiant a déjà été enregistré — nouveau vote non pris en compte.")
            else:
                # Record vote
                ts = datetime.now(timezone.utc).isoformat()
                new_row = {"identifiant": voter_id, "vote": choice, "timestamp": ts}
                votes_df = pd.concat([votes_df, pd.DataFrame([new_row])], ignore_index=True) # ajoutes le nouveau vote  au dataFrame
                try:
                    # save to CSV
                    votes_df.to_csv(votes_path, index=False)
                    st.success("Vote enregistré avec succès.")
                except Exception as e:
                    st.error(f"Erreur lors de l'enregistrement du vote: {e}")

# --- Section Administrateur pour le téléchargement ---
st.sidebar.header("Section Administrateur")
admin_password = st.sidebar.text_input("Mot de passe administrateur", type="password")

if admin_password == "admin": # Remplacez "admin" par un mot de passe plus sécurisé
    
    #* Suppresion des votes
    @st.dialog("Suppression des votes")
    def supp_votes():
        st.error("Voulez-vous vraiment supprimez tous les votes ? sinon quittez !")
        if st.button("Supprimer"):
            votes_df = pd.DataFrame(columns=["identifiant", "vote", "timestamp"])
            votes_df.to_csv(votes_path, index=False)
            st.rerun()
    
    
    erase = st.button("Effacer les votes")
    if erase:
        supp_votes()
    #     votes_df = pd.DataFrame(columns=["identifiant", "vote", "timestamp"])
    #     votes_df.to_csv(votes_path, index=False)
        
    
    st.header("Résultats des votes")
    st.dataframe(votes_df)

    # Convertir le DataFrame en CSV pour le téléchargement
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv_data = convert_df_to_csv(votes_df)
    

    st.download_button(
       label="📥 Télécharger les votes en CSV",
       data=csv_data,
       file_name='votes.csv',
       mime='text/csv',
    )
