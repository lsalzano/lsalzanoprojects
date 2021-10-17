#script per gestire il gioco di campo minato

import random, itertools
import tkinter as tk #libreria per creare la grafica
from tkinter import messagebox #libreria per mostrare i messaggi all'utente quando vince e quando perde


####################################################################################################################################################################################################
#costanti
const_numero_bomba = -1
const_numero_vuoto = 0
const_char_coperto = '#'
const_char_bomba = '*'
const_char_vuoto = ' '
const_char_sep_colonne = '' #carattere di separazione delle colonne nella rappresentazione dello schema su terminale

################################################################################################################################################################################################
#classi
class Casella:
	#classe per rappresentare la casella
	flag_mostrato = None #flag che indica se la casella e' stata mostrata
	numero = None #numero all'interno della casella

	def __init__(self, n):
		#metodo costruttore
		self.numero = n
		#inizializzo il flag alla casella nascosta
		self.flag_mostrato = False

class BottoneSchema(tk.Button):
	#classe che rappresenta un bottone nello schema
        #oltre agli attributi ha anche la riga e la colonna dello schema nel quale si trova
	r = None
	c= None
	#contiene anche l'attributo che fa riferimento allo schema al quale appartiene
	schema = None

	#il metodo costruttore e' uguale a quello padre
	#in piu ha un metodo apposta per popolare gli attributi che non ci sono nel padre
	def popola_attributi(self, r, c, schema):
		self.r=r
		self.c = c
		self.schema = schema
		#adesso vado a posizionare il padre nelle coordinare rispettive
		self.grid(row = self.r, column = self.c)
		#vado ad impostare il comando del click
		self.configure(command=self.scopri_bottone)

	#creo un metodo da chiamare al click del bottone
	def scopri_bottone(self):
		#chiamo la funzione di gestione del click dello schema
		self.schema.gestione_click_bottone(r=self.r, c=self.c)

class Schema:
	#classe che contiene l'intero schema
	flag_completo  = None #flag che indica se lo schema e' completo ovvero se sono nascoste soltanto le bombe
	flag_perdente = None #flag che indica se si e' scoperta una bomba
	dim_v = None #dimensione verticale dello schema
	dim_o = None #dimensione orizzontale dello schema
	numero_bombe = None #numero delle bombe presenti nello schema
	schema = None #contiene lo schema di gioco con oggetti di tipo Casella
	#attributi utili per la parte grafica
	schema_bottoni = None #schema che contiene i bottoni per la parte grafica

	def __init__(self, dim_v, dim_o, n):
		#metodo costruttore
		self.dim_v = dim_v
		self.dim_o = dim_o
		self.numero_bombe = n
		#inizializzo i flag
		self.flag_completo = False
		self.flag_perdente = False
		#vado a popolare le caselle
		self.crea_schema_iniziale()
		

	#####################################################################################################################################################################################
	#metodi di utilita
	def adiacenti(self, r, c):
		#metodo che ritorna la lista delle celle adiacenti a quella data (le eventualmente 8 celle intorno ad essa)
		lista_celle = []
		#itero in modo da spostarmi di una casella in orizzontale
		for dr in (-1,0,1):
			#controllo di non andare fuori schema
			if 0 <= r + dr < self.dim_v:
				#itero per muovermi in verticale
				for dc in (-1,0,1):
					#evito di inserire la cella stessa
					if (0,0) != (dr, dc):
						#controllo per non andare fuori schema
						if 0 <= c + dc < self.dim_o:
							#aggiungo la nuova cella alla lista
							lista_celle.append( (r+dr, c+dc) )
		#al termine ritorno la lista ottenuta
		return lista_celle

	def verifica_completo(self):
		#metodo per verificare se uno schema e' completo( sono state scoperte tutte le caselle tranne quelle che contengono bombe) e ritornare true o false
		#scorro per tutte le caselle dello schema
		for r in range(self.dim_v):
			for c in range(self.dim_o):
				#verifico se la casella e' coperta e se non contiene una bomba
				if (self.schema[r][c].flag_mostrato ==False ) and (self.schema[r][c].numero != const_numero_bomba):
					#allora lo schema non e' completo
					return False
		#al termine se non ho trovato caselle coperte diverse dalle bombe allora posso dire che lo schema e' completo
		return True

	#######################################################################################################################################################################################################################
	#metodi per generare lo schema iniziale
	def crea_schema_iniziale(self):
		#metodo per popolare l'attributo schema con una matrice di oggetti Casella
		#prima ricorro a uno schema temporaneo con i numeri
		schema_numeri = [ [ const_numero_vuoto for c in range(self.dim_o) ] for r in range(self.dim_v) ]
		#lo schema e' completamente vuoto. Ora scelgo le caselle dove posizionare le bombe
		lista_tutte_caselle = [ (r,c) for r in range(self.dim_v) for c in range(self.dim_o) ]
		caselle_bombe = random.sample(lista_tutte_caselle, self.numero_bombe)
		#ora vado a posizionare le bombe nello schema dei numeri
		for (r,c) in caselle_bombe:
			schema_numeri[r][c] = const_numero_bomba
		#ora per ogni casella controllo quante bombe ha nelle vicinanze
		for (r,c) in lista_tutte_caselle:
			#se non e' una bomba modifico il suo numero
			if schema_numeri[r][c] != const_numero_bomba:
				#considero le sue celle adiacenti
				celle_adiacenti = self.adiacenti(r=r, c=c)
				#tra tutte le celle adiacenti considero solo quelle che hanno una bomba
				bombe_adiacenti = [ (r_a, c_a) for (r_a, c_a) in celle_adiacenti if schema_numeri[r_a][c_a] == const_numero_bomba ]
				#il numero da associare e' praticamente la lunghezza di questa lista
				schema_numeri[r][c] = len(bombe_adiacenti)
		#ora ho lo schema con tutti i numeri, mi basta solo generare gli oggetti di tipo Casella e mettere la matrice nello schema
		self.schema = []
		for r in range(self.dim_v):
			#creo la lista che rappresenta la riga
			riga = []
			for c in range(self.dim_o):
				#vado a creare la casella con il relativo numero
				oggetto_casella = Casella(schema_numeri[r][c])
				#la aggiungo alla riga
				riga.append(oggetto_casella)
			#al termine aggiungo la copia riga allo schema
			self.schema.append(riga[:])
		#a questo punto lo schema dovrebbe essere completo

	####################################################################################################################################################################################################################
	#metodi per scoprire una casella ed eventualmente utilizzare la ricerca in profondita per mostrare tutte le altre caselle sicuramente vuote
	def scopri_casella(self, r, c):
		#metodo per scoprire la casella in posizione r, c
		oggetto_casella = self.schema[r][c]
		#se la casella e' gia scoperta non faccio niente, procedo solamente se la casella non e' stata scoperta
		if oggetto_casella.flag_mostrato == False:
			#cambio il flag e scopro la casella
			oggetto_casella.flag_mostrato = True
			#verifico quale tipo di casella
			if oggetto_casella.numero == const_numero_bomba: 
				#si ferma e non continua a ricorsione perche' ha scoperto una bomba
				return None
			elif oggetto_casella.numero == 0:
				#se zero devo procedere a ricorsione tra le sue adiacenti in modo da espandere il piu possibile
				celle_adiacenti = self.adiacenti(r=r, c=c)
				#per ogni cella adiacente vado a ricorsione
				for (r_a, c_a) in celle_adiacenti:
					self.scopri_casella(r=r_a, c=c_a)
			else:
				#ho trovato un numero che non e' una bomba e neanche lo zero: mi fermo
				return None 

	def processo_click_casella(self, r, c):
		#metodo per gestire il processo di click nella casella r,c e la successiva verifica se lo schema e' completo
		#intanto scopro la casella
		self.scopri_casella(r=r, c=c)
		#adesso verifico se la casella scoperta era una bomba e quindi lo schema risulta perdente
		if self.schema[r][c].numero == const_numero_bomba:
			#schema perdente
			self.flag_perdente = True
		#verifico se lo schema risulta completo e quindi vincente
		elif self.verifica_completo():
			self.flag_completo = True

	################################################################################################################################################################################################
	#metodi per giocare attraverso il terminale 
	def calcola_schema_caratteri(self):
		#metodo per tornare la matrice dei caratteri da mostrare
		matrice_righe = []
		#scorro tutte le caselle
		for r in range(self.dim_v):
			#preparo la lista della riga
			lista_riga = []
			for c in range(self.dim_o):
				#vado a considerare la casella in posizione r,c
				casella_schema = self.schema[r][c]
				#verifico se e' scoperta o meno
				if casella_schema.flag_mostrato == True:
					#la casella e' mostrata
					#devo distinguere i casi se e' o meno un numero
					if casella_schema.numero == const_numero_bomba:
						#metto la bomba
						lista_riga.append(const_char_bomba)
					elif casella_schema.numero == 0:
						#inserisco uno spazio vuoto
						lista_riga.append(const_char_vuoto)
					else:
						#contiene un numero
						lista_riga.append(str(casella_schema.numero))
				else:
					#la casella non e' mostrata
					lista_riga.append( const_char_coperto)
			#al termine delle colonne aggiungo la copia della lista alla matrice
			matrice_righe.append(lista_riga[:])
		#al termine di tutto ritorno la matrice 
		return matrice_righe

	def crea_stringa_terminale(self, lista_nomi_righe, lista_nomi_colonne):
		#metodo per creare la stringa da rappresentare nel terminale 
		#prende come parametri la lista dei caratteri delle colonne e delle righe in modo da creare una sorta di battaglia navale
		#utilizzo il metodo rjust per far diventare tutte le stringhe della stessa lunghezza allineando a dx
		#creo inizialmente la matrice dei caratteri dello schema
		matrice_caratteri = self.calcola_schema_caratteri()
		#calcolo il massimo delle lunghezze delle colonne e delle righe
		max_len_col = max([ len(i) for i in lista_nomi_colonne ])
		max_len_righe = max( [ len(i) for i in lista_nomi_righe ] )
		#preparo la stringa dello schema
		stringa_schema = ''
		#inserisco l'intestazione con i nomi delle colonne
		stringa_schema += ' '*max_len_righe + ' ' + const_char_sep_colonne.join( [ i.rjust(max_len_col) for i in lista_nomi_colonne ] ) #+ ' ' + ' '*max_len_righe #questo se si vuole bilanciare completamente la stringa
		stringa_schema += '\n'
		#adesso scorro le righe e applico la stessa tecnica
		for r in range(self.dim_v):
			#inserisco il nome della riga
			stringa_schema += lista_nomi_righe[r].rjust(max_len_righe) + ' '
			#adesso devo inserire i caratteri dello schema
			stringa_schema += const_char_sep_colonne.join( [ i.rjust(max_len_col) for i in matrice_caratteri[r] ] )
			#adesso inserisco la fine della riga con il riferimento anche a destra
			stringa_schema += ' ' + lista_nomi_righe[r].rjust(max_len_righe) + '\n'
		#al termine devo inserire l'ultima riga uguale alla prima
		stringa_schema += ' '*max_len_righe + ' ' + const_char_sep_colonne.join( [ i.rjust(max_len_col) for i in lista_nomi_colonne ] ) #+ ' ' + ' '*max_len_righe #questo se si vuole bilanciare completamente la stringa
		#alla fine posso ritornare la stringa
		return stringa_schema

	def stampa_schema(self, lista_nomi_righe, lista_nomi_colonne):
		#metodo per stampare lo schema di gioco
		#informo l'utente su quante bombe ci sono
		print('Sono presenti %d bombe'%(self.numero_bombe))
		#stampo subito lo schema 
		print(self.crea_stringa_terminale(lista_nomi_righe=lista_nomi_righe, lista_nomi_colonne=lista_nomi_colonne))

	def scopri_tutte_caselle(self):
		#metodo per scoprire tutte le caselle dello schema e mostrarlo alla soluzione
		#itero lungo tutte le righe e poi per ogni cella metto il flag a True indipendentemente se sono gia state mostrate
		for riga in self.schema:
			for cella in riga:
				cella.flag_mostrato = True

	def gioca_partita_terminale(self):
		#metodo per giocare una partita dal terminale
		#utilizzo le lettere in orizzontale e i numeri in verticale
		#calcolo le etichette da mostrare 
		lista_etichette_colonne = crea_lista_lettere(elementi=self.dim_o)
		lista_etichette_righe = crea_lista_numeri(elementi=self.dim_v)
		#stampo lo schema
		self.stampa_schema(lista_nomi_righe=lista_etichette_righe, lista_nomi_colonne=lista_etichette_colonne)
		#adesso itero fino a quando uno dei 2 flag non e' verificato
		while (not(self.flag_completo)) and (not(self.flag_perdente)):
			#chiedo all'utente quale casella desidera scoprire
			#passo l'input dell'utente con il metodo strip e upper in modo da averceli gia' maiuscolo e senza spazi iniziali o finali
			stringa_casella_scoperta = input('Scegli quale casella scoprire (separare le coordinate da spazio del tipo A 1): ').strip().upper()
			#ricavo le coordinate 
			coordinate = stringa_casella_scoperta.split(' ')
			#adesso verifico che abbia inserito coordinate corrette
			if len(coordinate) != 2:
				#informo l'utente che non ha fatto una scelta valida
				print('Coordinata non corretta')
				#utilizzo l'istruzione continue per riprendere il ciclo da capo
				continue
			elif (coordinate[0] in lista_etichette_righe) and (coordinate[1] in lista_etichette_colonne):
				#questo caso va bene perche' la prima coordinata e' la riga, la seconda e' la colonna
				(coord_riga, coord_col) = coordinate
			elif (coordinate[0] in lista_etichette_colonne) and (coordinate[1] in lista_etichette_righe):
				#questo caso va bene perche la prima coordinata sono le colonne, la prima le righe
				(coord_col, coord_riga) = coordinate
			else:
				#l'utente ha inserito una combinazione non valida
				#informo l'utente che non ha fatto una scelta valida
				print('Coordinata non corretta')
				#utilizzo l'istruzione continue per riprendere il ciclo da capo
				continue
			#se arrivo qui significa che ho le coordinate corrette
			#ricavo il numero di colonna e riga da scoprire
			n_riga = lista_etichette_righe.index(coord_riga)
			n_col = lista_etichette_colonne.index(coord_col)
			#adesso scopro la cella
			self.processo_click_casella(r=n_riga, c=n_col)
			#infine stampo lo schema
			self.stampa_schema(lista_nomi_righe=lista_etichette_righe, lista_nomi_colonne=lista_etichette_colonne)
		#al termine del while signifca che ho terminato o perche' ha perso o perche' ha vinto
		if self.flag_perdente:
			#l'utente ha perso
			print('Hai Perso perchè hai trovato una bomba!! Ecco lo schema completo')
		else:
			#significa che l'utente ha vinto
			print('Complimenti!! Hai vinto!! Ecco lo schema completo.')
		#a questo punto scopro tutte le caselle e stampo lo schema finale
		self.scopri_tutte_caselle()
		self.stampa_schema(lista_nomi_righe=lista_etichette_righe, lista_nomi_colonne=lista_etichette_colonne)

	##########################################################################################################################################################################################################################
	#metodi per giocare attraverso la grafica
	def gestione_click_bottone(self, r, c):
		#processo che permette di gestire l'intero processo di click in un pulsante ovvero: 
		# 1) click del pulsante
		# 2) scoprire la casella
		# 3) verificare se lo schema è perdente o completo ed eventualmente completarlo e mostrare un messaggio all'utente
		#per prima cosa scopro lo casella
		self.processo_click_casella(r=r, c=c)
		#adesso verifico se ho vinto o perso
		if self.flag_perdente:
			#mostro un messaggio all'utente e completo tutto lo schema
			messagebox.showerror(title="Partita Persa", message="Hai Perso perchè hai trovato una bomba!!")
			#scopro tutto lo schema
			self.scopri_tutte_caselle()
		elif self.flag_completo:
			#l'utente ha vinto
			messagebox.showinfo(title="Partita Vinta", message="Complimenti!! Hai vinto!!")
			#scopro tutto lo schema
			self.scopri_tutte_caselle()
		#adesso aggiorno tutti i bottoni
		self.aggiorna_tutti_bottoni()

	def aggiorna_tutti_bottoni(self):
		#metodo per aggiornare tutti i bottoni ovvero cambiarne il testo di quelli scoperti e disattivarli se scoperti
		#per prima cosa mi calcolo lo schema con i caratteri
		schema_caratteri = self.calcola_schema_caratteri()
		for r in range(self.dim_v):
			for c in range(self.dim_o):
				#ricavo la casella
				casella = self.schema[r][c]
				#verifico se devo mostrarla
				if casella.flag_mostrato:
					#ricavo il bottone
					bottone = self.schema_bottoni[r][c]
					#verifico se e' gia disabilitato
					if bottone["state"] != "disabled":
						#se disabilitato adesso ci cambio la stringa mostrata con quella dello schema dei caratteri
						bottone.configure(text = schema_caratteri[r][c])
						bottone.configure(state = "disabled")

	def gioca_partita_grafica(self):
		#metodo per giocare la partita dalla grafica
		#creo il top della grafica
		top = tk.Tk()
		#inizializzo la matrice dei bottoni
		self.schema_bottoni = []
		#adesso vado ad inserire tutti i bottoni
		for r in range(self.dim_v):
			riga_bottoni = []
			for c in range(self.dim_o):
				#mi creo il bottone
				bottone = BottoneSchema(top, text=const_char_coperto)
				#adesso vado ad inserire le coordinate
				bottone.popola_attributi(r=r, c=c, schema=self)
				#aggiungo il bottone alla riga
				riga_bottoni.append(bottone)
			#al termine aggiungo la riga allo schema
			self.schema_bottoni.append(riga_bottoni[:])
		#adesso dovrei avere tutti i bottoni posizionati
		#posiziono la label
		label = tk.Label(top, text = "Numero di bombe presenti: %d"%(self.numero_bombe))
		label.grid(row = self.dim_v, column = 0, columnspan = self.dim_o)
		#mostro la grafica
		top.mainloop()
			
			

############################################################################################################################################################################################################
#funzioni generali
def crea_lista_numeri(elementi):
	#funzione per creare la lista dei numeri in modo da etichettare righe o colonne
	return [str(i) for i in range(elementi)]

def crea_lista_lettere(elementi):
	#funzione per ritornare la lista delle lettere in modo da etichettare righe o colonne
	#calcolo la lista complessiva delle lettere
	lista_lettere = [ chr(i) for i in range( ord('A'), ord('Z') +1 ) ] #=A
	lista_etichette = []
	ripetizioni = 1
	#adesso itero fino a quando la lunghezza delle etichette supera il numero di elementi
	while len(lista_etichette) < elementi:
		#calcolo una nuova lista di etichette utilizzando itertools.product
                #itertools.product(lista_lettere, repeat=ripetizioni) = A^(ripetizioni)
		lista_etichette = [ ''.join(i) for i in itertools.product(lista_lettere, repeat=ripetizioni) ]
		ripetizioni += 1
	#al termine del ciclo ritorno solo gli elementi che mi servono
	return lista_etichette[:elementi]

def main():
	#funzione da eseguire nel caso del main
	#main per eseguire tutti i passaggi
	#per prima cosa chiedo all'utente i parametri di gioco
	n_righe = int(input("Scegliere il numero di righe: "))
	#prendo almeno una riga
	while n_righe <1:
		#informo l'utente che la scelta non e valida
		print("Numero di righe non valido")
		n_righe = int(input("Scegliere il numero di righe: "))
	n_col = int(input("Scegliere il numero di colonne: "))
	#analogo a quanto fatto per le righe
	while n_col <1:
		#informo l'utente che la scelta non e' valida
		print("Numero di colonne non valido")
		n_col = int(input("Scegliere il numero di colonne: "))
	#prendo un numero di bombe pari al massimo a righe*colonne -1
	n_max_bombe = n_righe * n_col -1
	n_bombe = int(input("Scegliere il numero di bombe (il numero deve essere compreso tra 1 e %d): "%(n_max_bombe)))
	while not( 1<= n_bombe <= n_max_bombe ):
		#informo l'utente che la scelta non e' consentita
		print("Numero di bombe non consentito")
		n_bombe = int(input("Scegliere il numero di bombe (il numero deve essere compreso tra 1 e %d): "%(n_max_bombe)))
	#ho tutti i parametri, posso creare l'oggetto di tipo schema
	oggetto_schema = Schema(dim_v=n_righe, dim_o=n_col, n=n_bombe)
	#chiedo quale modalita' vuole l'utente
	modalita = input('Scegliere la modalita di gioco. Inserire G per la grafica, T per il terminale: ').upper().strip()
	while modalita not in ('T', 'G'):
		#informo l'utente che ha scelto sbagliato
		print('Scelta non valida')
		modalita = input('Scegliere la modalita di gioco. Inserire G per la grafica, T per il terminale: ').upper().strip()
	#opero la scelta in base la modalita
	if modalita == 'T':
		#adesso eseguo la partita da terminale
		oggetto_schema.gioca_partita_terminale()
	else:
		#l'utente ha scelto di giocare con  la grafica
		oggetto_schema.gioca_partita_grafica()


#creo un flag per giocare piu' partite
flag_partita_successiva = True
while flag_partita_successiva:
	main()
	#chiedo all'utente se vuole giocare un altra partita
	stringa_prossima_partita = input("Se si desidera giocare un'altra partita inserire S: ").upper()
	flag_partita_successiva = stringa_prossima_partita == "S"
