import json
from socket import *
from threading import *
import sqlite3

# === Creation du base de données et des tables ===#
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''create table IF NOT EXISTS client(username TEXT primary key ,
                                                    password TEXT ,
                                                    firstname TEXT,
                                                    lastname TEXT
                                                    )'''
               )
conn.commit()
conn.close()
# Table des historiques
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('create table IF NOT EXISTS historique(user TEXT , contenu TEXT )')
conn.commit()
conn.close()

# Table des historiques precis entre uniquement entre deux utilisateurs
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('create table IF NOT EXISTS histprecis(emeteur TEXT , destinataire TEXT , content TEXT)')
conn.commit()
conn.close()

usernames = []  # une liste contenant les pseudo
clients = []  # celle ci contient les sockets de communications de chaque client
user_clients = []  # Et celle la contient un tuple de (username,client_socket)
salons = []  # Liste des noms des salons
clients_par_salon = {}  # Dictionnaire pour associer les clients à un salon spécifique
creator_salon = []  # Contient un tuples de createur avec son salon [(salon_name,creator_socket)]

# Fonction de diffusion
def diffusion(message):
    for c in clients:
        if c is not client:  # i.e envoie a tout le monde sauf moi
            c.send(f' {message}\n'.encode("utf-8"))


def diffusion1(message):
    for c in clients:
        c.send(f' {message}\n'.encode("utf-8"))


# Diffusion des messages dans un salon donne
def diffusion_salon(message, salon):  # Pour un salon donne, je vais envoyé le message aux clients de ce salon
    for c in clients_par_salon[salon]:
        c.send(f'{message}\n'.encode("utf-8"))


def diffusion_salon2(message, salon, client_socket):
    if client_socket in clients_par_salon[salon]:
        client_socket.send(f'{message}\n'.encode())


#diffusion uniquement dans la fenetre de celui qui a crée le salon
def diffusion_salon3(message, salon):  # creator_salon = [(salon_name,socket_creator)]
    for csalon in creator_salon:
        if csalon[0] == salon:
            csalon[1].send(f"{message}\n".encode())

def gestion_msg(client, addr):
    current_salon = None  # Salon actuel du client
    current_user = None
    while True:
        # =================== Recevoir des données d'inscripttion ===========================#
        message = client.recv(1024).decode("utf-8")
        data = message.split(',')  # Pour diviser les messages venant contenant des virgules en plusieurs  partie
        # et les mettre dans data sous forme de liste

        # === Pour les données de création du compte ===#
        if data[0] == "user_data":
            if data[1] == "" or data[2] == "" or data[3] == "" or data[4] == "":
                client.send("error".encode())
            else:
                client.send("confirm".encode())
                conn = sqlite3.connect("database.db")
                cursor = conn.cursor()
                cursor.execute("insert into client (username,password,firstname,lastname) values (?,?,?,?)",
                               (data[1], data[2], data[3], data[4]))
                conn.commit()
                conn.close()
                username = data[1]
                usernames.append(username)
                user_clients.append((username, client))

        # === Pour les données d'authentification ===#
        elif data[0] == "user_login":
            if data[1] == "" or data[2] == "":
                client.send("error".encode())
            else:
                conn = sqlite3.connect("database.db")
                cursor = conn.cursor()
                cursor.execute("select * from client where username=? and password=? ", (data[1], data[2]))
                result = cursor.fetchone()
                if result == None:
                    client.send("incorrect".encode())
                else:
                    client.send("confirm".encode())
                    user = data[1]
                    usernames.append(user)
                    user_clients.append((user, client))
                conn.commit()
                conn.close()
        # === Creation du salon === #
        elif data[0] == "create_salon":
            salon_name = data[1]
            if salon_name not in salons:
                salons.append(salon_name)
                clients_par_salon[salon_name] = [client]
                creator_salon.append((salon_name, client))  # [("gang","socket_oumar")]
                current_salon = salon_name
                index = clients.index(client)
                user = usernames[index]
                client.send(f"\n[INFO]: Vous avez crée le salon : ''{salon_name}''".encode())
                diffusion1(f"\n[INFO]: {user} a crée le salon ''{salon_name}'' ")
                # diffusion_salon(f"salon.salon {salon_name }crée par {user}.", current_salon)
            else:
                client.send(f" Le salon ''{salon_name}'' existe déjà.".encode())

        # === joindre un salon === #
        elif data[0] == "join_salon":
            salon_name = data[1]
            if salon_name in salons:
                clients_par_salon[salon_name].append(client)
                current_salon = salon_name
                index = clients.index(client)
                user = usernames[index]
                client.send(f" Vous avez rejoint le salon : ''{salon_name}''".encode())
                diffusion_salon(f"salon. {user} a rejoint le salon.", current_salon)
                # client.send(f"salon. {user} a rejoint le salon".encode())
            else:
                client.send(f" Le salon {salon_name} n'existe pas.".encode())

        # === Pour les messages destinés au salon === #
        elif data[0] == "salon_message":
            current_salon = data[3]
            if current_salon in clients_par_salon:
                sender = data[1]
                if client in clients_par_salon[current_salon]:
                    message_content = data[2]
                    salon_msg = f"salon.{sender} ({current_salon}): {message_content}"  # Format: username:message
                    diffusion_salon(salon_msg, current_salon)
                    # client.send(f"salon. {sender}({current_salon}): {message_content}".encode())
                else:
                    client.send(f"Vous ne faites pas parti de ce salon.".encode())
            else:
                # client.send("Vous n'êtes pas dans un salon.".encode())
                client.send(f"Le salon '{current_salon}' n'existe pas.".encode())


        # === Pour l'historique de tous les messages ===#
        elif data[0] == "historique":
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            #cursor.execute('select * from historique')
            index = clients.index(client)
            user = usernames[index]
            print(user)
            cursor.execute('SELECT * FROM histprecis')
            results = cursor.fetchall()
            if results:
                json_format = json.dumps(results)
                # essaie d'affichage ligne par ligne
                json_hist = json.loads(json_format)
                for message in json_hist:
                    client.send(f"{message[0]} => {message[1]}: {message[2]}\n".encode())
                client.send(f"\n----------------------------------------------------------------------".encode())
            else:
                client.send("Aucun message trouvé !".encode())
            # Conversion en JSON : La fonction json.dumps() est utilisée pour sérialiser(convertir) la liste de résultats en une chaîne JSON.
        # Cela permet de représenter les données de manière structurée et standardisée.

        # === message qui s'affiche quand un utilisateur quitte le chat
        elif data[0] == "left":
            diffusion1(f"({data[1]}) A quitté le chat !")
            current_user = data[1]
            clients.remove(client)
            usernames.remove(current_user)
            user_clients.remove((current_user, client))
            client.close()
        elif data[0] == "joinchat":
            # diffusion(f"{data[1]} A rejoint le chat !")
            # client.send(f"Vous avez rejoint le chat avec le username ({data[1]}) !".encode())
            client.send(f"Vous avez rejoint le chat !".encode())


        # === Pour les messages normaux ===#
        else:
            msg = message.split(':')  # ici je separe par le ":" car le format du message envoyé est username:{message}
            # len(msg) > 1 and (Pour verifier si on a au moins 1 elt dans la liste msg[split])


            # === Statut des utilisateurs connectés en envoyant "online"===#
            msg_online = message
            if msg_online == "online":  # msg[1] : 1 car dans msg on a : msg = ["username","message"]
                for pseudo in usernames:
                    client.send(f'{pseudo}\n'.encode())  # donc 1 pour indexer le message dans la liste msg
                client.send("\n------------------------------------------------------------------------".encode())

           # === Changement de pseudo et mise a jour dans la base de donnee === #

            elif len(msg) >1 and msg[1].startswith(" change_pseudo"):
                msg_pseudo = msg[1].split(',') # car message recu = ["user": " change_pseudo,old_pseudo,new_pseudo"]
                current_user = msg_pseudo[1]   # msg_pseudo = [" change_pseudo", "old_pseudo", "new_pseudo"]
                new_username = msg_pseudo[2]
                if new_username not in usernames:
                    index = usernames.index(current_user)
                    usernames[index] = new_username
                    user_clients.remove((current_user, client))
                    user_clients.append((new_username, client))
                   # Changer de pseudo dans la base de donnee aussi
                    conn = sqlite3.connect('database.db')
                    cursor = conn.cursor()
                   # cursor.execute('UPDATE histprecis SET (emeteur=? AND destinataire=?) WHERE (emeteur=? OR destinataire=?)',(current_user,current_user,current_user,current_user))
                    cursor.execute('UPDATE histprecis SET emeteur=? WHERE emeteur=?',(new_username, current_user))
                    cursor.execute('UPDATE histprecis SET destinataire=? WHERE destinataire=?',(new_username, current_user))
                    cursor.execute('UPDATE client SET username=? WHERE username=?',(new_username,current_user))
                    client.send(f"Vous avez changé de pseudo de {current_user} à {new_username}\n".encode())
                    conn.commit()
                else:
                    client.send(f"Le nom d'utilisateur {new_username} est déjà pris.\n".encode())

            # === pour historique entre deux clients donnees ! (emeteur et destinataire) === #
            elif len(msg) >1 and msg[1].startswith(" histprecis"): #car message = [ {user}: {content}]
                msg_hist = msg[1].split(',') #[" histprecis", "emeteur", "destinataire"]
                emeteur = msg_hist[1]
                destinataire = msg_hist[2]
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                #cursor.execute('select * from histprecis where emeteur=? ',(emeteur,)) #where emeteur=? AND destinataire=? ,
                cursor.execute('SELECT * FROM histprecis WHERE (emeteur = ? AND destinataire = ?) OR (emeteur = ? AND destinataire = ?)', (emeteur, destinataire,destinataire,emeteur))
                results2 = cursor.fetchall()
                print(results2)
                print(f"emeteur from database: {emeteur}")
                print(f"dest from database: {destinataire}")
                if results2:
                    json_format2 = json.dumps(results2)
                    # client.send(json_format.encode())
                    # essaie d'affichage ligne par ligne
                    json_hist2 = json.loads(json_format2)
                    client.send(f"\n------------------Historique de vos messages privés----------------".encode())
                    for message in json_hist2:
                        client.send(f"{message[0]} => {message[1]} : {message[2]}\n".encode())
                    client.send(f"\n---------------------------------------------------------------------------".encode())
                else:
                    client.send("Aucun message trouvé !".encode())

            # === Pour les messages privés ===#
            elif len(msg) > 1 and msg[1].startswith(" to"):  # message recu= " to@oumar. {message}"
                prv = msg[1].split('@')  # prv = ["to","oumar. {message}"]
                destinataire = prv[1].split(".")[0]  # destinataire = ["oumar","{message}"] d'ou le point (.)
                private_message = prv[1].split(".")[1]
                for user in user_clients:
                    if user[0] == destinataire:  # ("oumar","socket") si destinataire = oumar alors envoi lui le message
                        user[1].send(f"{msg[0]}(message privé):{private_message}\n".encode("utf-8"))
                    # elif user[0] == msg[0]:
                    # user[1].send(f"{msg[0]}: Message privée non reçu car {destinataire} non connecté !")
                index = clients.index(client)
                user = usernames[index]
                print(user)
                # === Enregistrer les messages privees dans la database === #
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute('insert into histprecis(emeteur,destinataire,content) values (?,?,?)', (user,destinataire,private_message))
                conn.commit()
                conn.close()

            # === Pour la diffusion des messages aux utilisateurs ===#
            else:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                #cursor.execute('insert into historique(user,contenu) values (?,?)', (msg[0], msg[1]))
                index = clients.index(client)
                user = usernames[index]
                cursor.execute('insert into histprecis(emeteur,destinataire,content) values (?,?,?)',(user, "all", msg[1]))
                conn.commit()
                conn.close()
                print(f"{addr}: " + message)
                message_s = message.split(':')[1]
                message_final = f"{user}: {message_s}"
                # Diffusion du message a tous les clients
                # diffusion(message)
                for c in clients:
                    if c is not client:  # i.e envoie a tout le monde sauf moi
                       # c.send(f'{message}\n'.encode("utf-8"))
                       c.send(f' {message_final}\n'.encode("utf-8"))
                if not message:  # si aucun message recu alors quitter la boucle while
                    break

    client.close()
    clients.remove(client)


host = '127.0.0.1'
port = 5555
server = socket(AF_INET, SOCK_STREAM)
server.bind((host, port))
server.listen()
print(f"[INFO] Serveur en ecoute sur le host {host} et le port {port}")
while True:
    client, addr = server.accept()
    print(f"Connecté avec {str(addr)}")
    clients.append(client)
    thread = Thread(target=gestion_msg, args=(client, addr,))
    thread.start()

# ========================================== FIN ==========================================#
