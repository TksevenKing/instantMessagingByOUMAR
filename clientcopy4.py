from socket import *
from threading import *
from tkinter import *
from tkinter import messagebox,simpledialog
from tkinter import PhotoImage
host = '127.0.0.1'
port = 5555

client = socket(AF_INET, SOCK_STREAM)
client.connect((host, port))

# ==== Pour changer le fond et la police facilement ==== #
DARK_GREY = '#121212'
MEDIUM_GREY = '#1F1B24'
OCEAN_BLUE = '#464EB8'
WHITE = "white"
FONT = ("Helvetica", 14)
BUTTON_FONT = ("Helvetica", 13)
SMALL_FONT = ("Helvetica", 13)


# === Fonction de creation de salon === #
def creer_salon():
    room_name = simpledialog.askstring("Créer un salon", "Entrez le nom du salon:")
    if room_name:
        message = f"create_salon,{room_name}"
        client.send(message.encode())

# === Rejoindre un salon === #
def rejoindre_salon():
    room_name = simpledialog.askstring("Rejoindre un salon", "Entrez le nom du salon:")
    if room_name:
        #user_joining = username_entry.get()
        message = f"join_salon,{room_name},quelqu'un"
        client.send(message.encode())



# ========= Creation de la fenetre d'inscription =========#
def fen_registre1():

    # === Envoyer au serveur les données entrées par le client lors de création du compte ==#
    def user_data():
        nom = nom_entry.get()
        prenom = prenom_entry.get()
        username = username_entry.get()
        password = password_entry.get()

        data = f"user_data,{username},{password},{prenom},{nom}"
        client.send(data.encode())

    # === Confirmation d'existence d'un champ vide ===#
    def conf_registre():
        info = client.recv(1024).decode()
        if info == "error":
            messagebox.showerror("error", "Remplissez tous les champs !")
        else:
            username = username_entry.get()
            client.send(f"joinchat".encode())
            fen_registre.destroy()  # to destroy the fen_registre window
            chat(username)  # Cette fonction est appelée après l'inscription de l'utilisateur avec succès..

    # === Fonction du boutton Créer un compte ==#
    def send_data():
        user_data()
        conf_registre()

    # === Fenetre d'inscription === #
    fen_registre = Tk()
    fen_registre.title("Instant Messaging : Inscription")  # Donner un titre
    fen_registre.geometry("400x450")  # Controler le largeur et la longuer
    fen_registre.resizable(False, False)  # Refuser l'acces au changement des longuer du fenetre
    fen_registre.config(background=OCEAN_BLUE)  # Changer la couleur du background
    fen_registre.iconbitmap("img/icon.ico")  # Changer l'incone du fenetre

    titre_registre = Label(fen_registre, text="INSCRIPTION", fg=WHITE, bg=DARK_GREY, font=FONT)
    titre_registre.place(x=140, y=10)  # Insérer le texte

    titre_label = Label(fen_registre, text='BIENVENUE \n SUR\n INSTANT MESSAGING !',fg=WHITE, bg=OCEAN_BLUE, font=FONT)
    titre_label.place(x=90, y=80)

    nom_label = Label(fen_registre, text='Nom: ', fg=WHITE, bg=OCEAN_BLUE, font=FONT)
    nom_label.place(x=20, y=214)
    nom_entry = Entry(fen_registre, width=15, font=FONT, bg=MEDIUM_GREY, fg=WHITE)
    nom_entry.place(x=142, y=214)  # Insérer la zone de texte

    prenom_label = Label(fen_registre, text='Prénom: ', fg=WHITE, bg=OCEAN_BLUE, font=FONT)
    prenom_label.place(x=20, y=260)
    prenom_entry = Entry(fen_registre, width=15, font=FONT, bg=MEDIUM_GREY, fg=WHITE)
    prenom_entry.place(x=142, y=260)

    username_label = Label(fen_registre, text='USERNAME: ', fg=WHITE, bg=OCEAN_BLUE, font=FONT)
    username_label.place(x=20, y=314)
    username_entry = Entry(fen_registre, width=15, font=FONT, bg=MEDIUM_GREY, fg=WHITE)
    username_entry.place(x=142, y=314)

    password_label = Label(fen_registre, text='PASSWORD: ', fg=WHITE, bg=OCEAN_BLUE, font=FONT)
    password_label.place(x=20, y=364)
    password_entry = Entry(fen_registre, width=15, font=FONT, bg=MEDIUM_GREY, fg=WHITE)
    password_entry.place(x=142, y=364)

    creer_compte_bt = Button(fen_registre, text='Créer un compte', font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, width=15,
                             justify='center', command=send_data)
    creer_compte_bt.place(x=130, y=400)  # Ajouter une boutton

    fen_registre.mainloop()  # Lancer la fenetre d'inscription



# === Creation de la fenetre de chat ===#
def chat(user):
    # == Demande d'hitorique des messages ==#
    def historique():
        add_message("---------------------Historique des Conversations----------------------")
        client.send(f"historique,{user}".encode())

    # == Demande de la liste des clients connectés == #
    def online():
        add_message("-----------------------Utilisateurs en lignes:--------------------------")
        client.send(f'online'.encode('utf-8'))

    # ------- adding_message to the interface----- #
    def add_message(msg):
        txtMessages.configure(state=NORMAL)
        txtMessages.insert(END, msg + '\n')
        txtMessages.configure(state=DISABLED)

    # == Envoie des messages ==#
    def Send_Msg():
        client_msg = ecrire_msg_entry.get()
        if client_msg:
            msg = f' {user}: {client_msg}'
            own_msg = f" Vous: {client_msg}"
            add_message(own_msg)
            client.send(msg.encode())
            ecrire_msg_entry.delete(0, "end")
        else:
            messagebox.showerror("Error", "saisissez un message avant d'envoyer")

    # == Recevoir les données du serveur ==#
    def Recv_Msg():
        while True:
            server_msg = client.recv(1024).decode("utf-8")
            print(server_msg)
            if server_msg.startswith(f"salon."):
                svr_msg = server_msg.split(".")[1]
                add_room_message(svr_msg)
            else:
                add_message(server_msg)


    # Se deconnecter en fermant la connexion
    def deconnexion():
        chat.destroy()
        client.send(f"left,{user}".encode())
        print("vous vous etes deconnectés")
        # client.close()
# ==== Fenetre Principale ==== #
    chat = Tk()
    fen_authentification.destroy()  # Destroying the authentification window
    chat.title('Instant Messaging')
    chat.geometry('500x570')
    chat.config(background=DARK_GREY)
    chat.resizable(False, False)
    chat.iconbitmap("img/icon.ico")

    txtMessages = Text(chat, width=53, height=22, font=SMALL_FONT, bg=MEDIUM_GREY, fg=WHITE)
    txtMessages.configure(state='disabled')
    txtMessages.place(x=10, y=10)

    ecrire_msg_label = Label(chat, text='Votre Message ', fg='black', bg='Azure', font=FONT)
    ecrire_msg_label.place(x=165, y=446)
    ecrire_msg_entry = Entry(chat, width=35, font=FONT, bg=MEDIUM_GREY, fg=WHITE)
    ecrire_msg_entry.place(x=10, y=470)

    envoyer_button = Button(chat, text='Envoyer', command=Send_Msg, font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE,
                            justify='center')
    envoyer_button.place(x=420, y=465)

    historique_bt = Button(chat, text='Historique', font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, width=15,
                           justify='center', command=historique)
    historique_bt.place(x=350, y=500)

    online_button = Button(chat, text='En ligne', command=online, font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, width=15,
                           justify='center')
    online_button.place(x=190, y=500)

    deconnecter_bt = Button(chat, text='Déconnecter', command=deconnexion, font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE,
                            width=15, justify='center')
    deconnecter_bt.place(x=30, y=500)

    # bouton lies aux salons
    creer_salon_button = Button(chat, text='Créer un salon', command=creer_salon, font=BUTTON_FONT, bg=OCEAN_BLUE,
                                fg=WHITE, width=15, justify='center')
    creer_salon_button.place(x=30, y=535)

    rejoindre_salon_button = Button(chat, text='Rejoindre un salon', command=rejoindre_salon, font=BUTTON_FONT,
                                    bg=OCEAN_BLUE, fg=WHITE, width=15, justify='center')
    rejoindre_salon_button.place(x=190, y=535)

    # Fonction pour ajouter un message à la fenêtre des messages du salon
    def add_room_message(message):
        salon_messages_text.configure(state='normal')
        salon_messages_text.insert(END, message + '\n')
        salon_messages_text.configure(state='disabled')

    # Création de la fenêtre des messages du salon
    salon_window = Toplevel(chat)
    salon_window.title(f"Messages du Salon")
    salon_window.geometry("400x300")
    salon_window.iconbitmap("img/icon.ico")

    # Ajout du widget Text pour afficher les messages du salon
    salon_messages_text = Text(salon_window, width=60, height=15, font=SMALL_FONT, bg=MEDIUM_GREY, fg=WHITE)
    salon_messages_text.pack()

    # Fonction d'envoi du message au salon
    def envoyer_salon_message():
        room_name = simpledialog.askstring("Envoyer un message", "Entrez le nom du salon:")
        if room_name:
                message_content = simpledialog.askstring("Envoyer un message", "Entrez votre message:")
                if message_content:
                    message = f"salon_message,{user},{message_content},{room_name}"
                    client.send(message.encode())
                else:
                    messagebox.showerror("Error", "Saisissez un message avant d'envoyer.")
        else:
            messagebox.showerror("Error", "Saisissez le nom du Salon.")

    envoyer_salon_button = Button(chat, text='Envoyer au salon', command=envoyer_salon_message, font=BUTTON_FONT,
                                  bg=OCEAN_BLUE, fg=WHITE, justify='center')
    envoyer_salon_button.place(x=350, y=535)

    recvThread = Thread(target=Recv_Msg)
    recvThread.start()

    chat.mainloop()


# == Envoyer au serveur les données entrées par le client lors d'authentification ==#
def login():
    user = username_entry.get()
    passw = password_entry.get()
    data = f"user_login,{user},{passw}"
    client.send(data.encode())


# === Confirmation de sing up ===#
def confirmation():
    info = client.recv(1024).decode()
    if info == "error":
        messagebox.showerror("error", "Remplissez tous les champs !")
    elif info == "incorrect":
        messagebox.showerror("error", "username ou password incorrect !")
    else:
        msg_entry = username_entry.get()
        client.send(f"joinchat,{msg_entry}".encode())
        chat(username_entry.get())  # Cette fonction est appelée après l'authentification de l'utilisateur avec succès.
        # j'appelle la fonction chat() avec le username pour que le serveur sache a qui
        # client.send("Join the chat")# envoye la demande de l'historique et aussi de la liste des onlines


# === Fonction du boutton Se connecter ==#
def se_connecter():
    login()
    confirmation()


# Fenetre d'authentification

fen_authentification = Tk()
fen_authentification.title("Instant Messaging : Authentification")
fen_authentification.geometry("400x500")
fen_authentification.resizable(False, False)
fen_authentification.config(background=OCEAN_BLUE)
fen_authentification.iconbitmap("img/icon.ico")

titre_auth = Label(fen_authentification, text="Authentification", fg='white', bg=DARK_GREY, font=FONT)
titre_auth.place(x=130, y=10)

img_auth = PhotoImage(file="img/login4.png")  # pour ajouter l'image
img_auth_label = Label(fen_authentification, image=img_auth)
img_auth_label.place(x=70, y=60)

username_label = Label(fen_authentification, text="USERNAME: ", fg='white', bg=OCEAN_BLUE, font=FONT)  # bg='gray'
username_label.place(x=30, y=300)
username_entry = Entry(fen_authentification, width=15, font=FONT, bg=MEDIUM_GREY, fg=WHITE)
username_entry.place(x=152, y=300)  # x=134, y=305

password_label = Label(fen_authentification, text="PASSWORD: ", fg='white', bg=OCEAN_BLUE, font=FONT)
password_label.place(x=30, y=340)
password_entry = Entry(fen_authentification, width=15, show='*', font=FONT, bg=MEDIUM_GREY, fg=WHITE)
password_entry.place(x=152, y=340)  # x=134, y=305

seconnecter_bt = Button(fen_authentification, text="Se Connecter", command=se_connecter, font=BUTTON_FONT,
                        bg=OCEAN_BLUE, fg=WHITE, width=15, justify='center')
seconnecter_bt.place(x=132, y=390)

passage_registre_label = Label(fen_authentification, text="Pas encore inscrit?", fg='white', bg='gray',
                               font=("Helvetica", 11))
passage_registre_label.place(x=80, y=460)
passage_registre_bt = Button(fen_authentification, text="Créer un compte", command=fen_registre1, fg='black',
                             bg='white')
passage_registre_bt.place(x=235, y=460)

fen_authentification.mainloop()

# ========================================== FIN ==========================================#
