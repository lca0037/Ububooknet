# -*- coding: utf-8 -*-
from src.Modelo import Personaje as p
from src.Lexers import CreaDict as cd
from src.Lexers import PosPersonajes as pp
from src.LecturaFicheros import Lectorcsv
from src.LecturaFicheros import LecturaEpub
import matplotlib.pyplot as plt
import collections
import numpy as np
import networkx as nx
import urllib
import json
from bs4 import BeautifulSoup
import zipfile
from threading import Thread



class Modelo:
    """
    Clase que contiene la lógica de la aplicación
    
    Args:
        
    """ 

    def __init__(self):
        """
        Clase que contiene la lógica de la aplicación
        
        Args:
            Constructor de la clase
        """ 
        self.__csv = Lectorcsv.Lectorcsv(self)
        self.__texto = list()
        self.personajes= dict()
        self.numpers = 0
        self.__fincaps = list()
        self.__G = None
            
    def crearDict(self):
        """
        Método para crear un diccionario automaticamente
        
        Args:
            
        """ 
        creard = cd.CreaDict(self)
        txt = ''
        for i in self.__texto:
            txt += i
        d = Thread(target=creard.crearDict,args=(txt,))
        d.start()
        d.join()
    
    def obtenerPosPers(self):
        """
        Método para obtener las posiciones de los personajes
        
        Args:
            
        """ 
        self.pos = list()
        self.fin = list()
        posper = pp.PosPersonajes(self)
        pers = self.getDictParsear()
        self.__fincaps = list() 
        posiciones = list()
        txt = ''
        for f in self.__texto:
            txt = txt + f + "+ ---CAPITULO--- +"
        posper.obtenerPos(txt, pers)
        posiciones = self.pos
        self.__fincaps = self.fin
        for i in self.personajes.keys():
            self.personajes[i].lennombres = dict()
            pers = self.personajes[i].getPersonaje()
            self.personajes[i].resNumApariciones(self.personajes[i].getNumApariciones()[0])
            for n in pers.keys():
                c = 1
                apar = 0
                for posc in posiciones:
                    if(n in posc.keys()):
                        pers[n][c] = posc[n]
                        apar+=len(posc[n])
                    c+=1
                self.personajes[i].lennombres[n]=apar
                self.personajes[i].sumNumApariciones(apar)
        
    def getDictParsear(self):
        """
        Función que genera una lista de nombres para obtener su posición en el texto
    
        Args:
            
        Return:
            Set con los todos los nombres de personajes
        """
        l = list()
        for i in self.personajes.keys():
            for n in self.personajes[i].getPersonaje():
                if(n not in l):
                    l.append(n)
        return l

    def getPersonajes(self):
        """
        Función que devuelve el diccionario de personajes
    
        Args:
            
        Return:
            diccionario de personajes
        """
        return self.personajes

    def vaciarDiccionario(self):
        """
        Método que limpia el diccionario de personajes
    
        Args:
            
        """
        self.personajes = dict()
        self.numpers = 0

    def anadirPersonaje(self, idpers, pers):
        """
        Método para añadir un personaje al diccionario de personajes
    
        Args:
            idpers: id del nuevo personaje
            pers: nombre del personaje
        Return:
            string que dice si está aadido o no
        """
        if(idpers not in self.personajes):
            self.personajes[idpers] = p.Personaje()
            self.personajes[idpers].getPersonaje()[pers] = dict()
            self.numpers+=1
            return 'Personaje añadido correctamente'
        return 'La id de personaje ya existe'

    def __eliminarPersonaje(self, idPersonaje):
        """
        Método para eliminar personajes
    
        Args:
            idPersonaje: id del personaje a eliminar
        """
        if(idPersonaje in self.personajes):
            del self.personajes[idPersonaje]

    def eliminarListPersonajes(self, personajes):
        """
        Método para eliminar una lista de personajes
    
        Args:
            idPersonaje: id del personaje a eliminar
        """
        for idp in personajes:
            self.__eliminarPersonaje(idp)
    
    def __juntarPersonajes(self, idPersonaje1, idPersonaje2):
        """
        Método para juntar personajes
    
        Args:
            idPersonaje1: id del primer personaje a juntar
            idPersonaje2: id del primer personaje a juntar
        """
        if(idPersonaje1 in self.personajes and idPersonaje2 in self.personajes):
            pers1 = self.personajes[idPersonaje1].getPersonaje()
            pers2 = self.personajes[idPersonaje2].getPersonaje()
            apar1 = self.personajes[idPersonaje1].lennombres
            apar2 = self.personajes[idPersonaje2].lennombres
            for k in pers2.keys():
                if k not in pers1.keys():
                    pers1[k]=pers2[k]
                    if(k in apar2.keys()):
                        apar1[k] = apar2[k]
                        self.personajes[idPersonaje1].sumNumApariciones(apar2[k])
            self.__eliminarPersonaje(idPersonaje2)

    def juntarListPersonajes(self,lista):
        """
        Método para juntar una lista de personajes
    
        Args:
            lista: lista de personajes a juntar
        """
        for i in range(1,len(lista)):
            self.__juntarPersonajes(lista[0],lista[i])
    
    def anadirReferenciaPersonaje(self,idp,ref):
        """
        Método para añadir una referencia a un personaje
    
        Args:
            idp: id del personaje
            ref: nueva referencia
        """
        self.personajes[idp].getPersonaje()[ref]= dict()
    
    def __eliminarReferenciaPersonaje(self,idp,ref):
        """
        Método para eliminar una referencia a un personaje
    
        Args:
            idp: id del personaje
            ref: referencia a eliminar
        """
        if(idp in self.personajes.keys()):
            p = self.personajes[idp].getPersonaje()
            if(ref in p.keys()):
                if (len(p)>1):
                    del p[ref]
                    if(ref in self.personajes[idp].lennombres):
                        self.personajes[idp].resNumApariciones(self.personajes[idp].lennombres[ref])
                        del self.personajes[idp].lennombres[ref]
                else:
                    del self.personajes[idp]
    
    def eliminarListRefs(self,lista):
        """
        Método para eliminar una lista de referencias
    
        Args:
            lista: lista de referencias a eliminar
        """
        for l in lista:
            self.__eliminarReferenciaPersonaje(l[0],l[1])

    def modificarIdPersonaje(self,idact,newid):
        """
        Método para modificar los id de los personajes
    
        Args:
            idact: id a cambiar
            newid: nueva id
        """
        self.personajes[newid] = self.personajes.pop(idact)

    def juntarPosiciones(self):
        """
        Método para juntar los posiciones de las referencias de un personaje
    
        Args:
            
        """
        for i in self.personajes.keys():
            pers = self.personajes[i].getPersonaje()
            pos = {}
            for n in pers.keys():
                    for caps in pers[n].keys():
                        cont = 0
                        if(caps not in pos.keys()):
                            pos[caps]=list()
                        for j in pers[n][caps]:
                            while(cont<len(pos[caps]) and pos[caps][cont]<j):
                                cont+=1
                            pos[caps].insert(cont,j)
            self.personajes[i].setPosicionPers(pos)
       
    def prepararRed(self):
        """
        Método que obtiene las posiciones de los personajes y las junta
    
        Args:
            
        """
        d = Thread(target=self.obtenerPosPers)
        d.start()
        d.join()
        self.juntarPosiciones()
        
    def getMatrizAdyacencia(self):
        """
        Método que devuelve la matriz de adyacencia de la red
    
        Args:
            
        Return:
            Matriz de adyacencia
        """
        return nx.adjacency_matrix(self.__G).todense()

    def generarGrafo(self,rango,minapar,caps):
        """
        Método para generar un grafo a partir de las relaciones de los personajes
    
        Args:
            rango: rango de palabras
            minapar: numero minimo de apariciones
            caps: si se tienen en cuenta los capitulos
        """
        persk = list(self.personajes.keys())
        tam = len(persk)
        self.__G = nx.Graph()
        for i in range(tam):
            #Se comprueba que se cumple con el requisito mínimo de apariciones
            if(self.personajes[persk[i]].getNumApariciones()[0]>=minapar):
                #La red es no dirigida sin autoenlaces así que no hace falta medir el peso 2 veces ni consigo mismo
                for j in range(i+1,tam):
                    #Se comprueba que cumple el requisito mínimo de apariciones
                    if(self.personajes[persk[j]].getNumApariciones()[0]>=minapar):
                        peso=0
                        #Se recorren los capítulos
                        for cap in self.personajes[persk[i]].getPosicionPers().keys():
                            #Se obtienene las posiciones del personaje en el capítulo correspondiente
                            for posi in self.personajes[persk[i]].getPosicionPers()[cap]:
                                prev = False
                                post = False
                                #Si no se tienen en cuenta los capítulos
                                if(not caps):
                                    aux = posi-rango
                                    capaux = cap
                                    #Si aux negativo se ha pasado al capítulo anterior capaux minimo de 2 para no salirnos de la lista
                                    while(aux<0 and capaux>1):
                                        prev = True
                                        capaux-=1
                                        aux = self.__fincaps[capaux-1] + aux
                                        #Si aux menor que 0 nos hemos saltado más de un capítulo
                                        if(aux<0):
                                            #Como nos hemos saltado el capítulo entero consideramos todas las posiciones que tiene el 
                                            #segundo personaje en ese capítulo como relación
                                            peso+=len(self.personajes[persk[j]].getPosicionPers()[capaux])
                                        else:
                                            #Comprobamos todas las palabras del capítulo previo que no nos hemos saltado por completo y añadimos
                                            #las que se encuentren en el rango
                                            for posj in self.personajes[persk[j]].getPosicionPers()[capaux]:
                                                if(posj>=aux):
                                                    peso+=1
                                    #Se repite el proceso anterior pero para capítulos posteriores
                                    aux = posi + rango - self.__fincaps[cap-1]
                                    capaux = cap
                                    while(aux>0 and capaux<len(self.__fincaps)):
                                        capaux+=1
                                        post=True
                                        if(aux>self.__fincaps[capaux-1]):
                                            aux = aux - self.__fincaps[capaux-1]
                                            peso+=len(self.personajes[persk[j]].getPosicionPers()[capaux])
                                        else:
                                            for posj in self.personajes[persk[j]].getPosicionPers()[capaux]:
                                                if(posj<=aux):
                                                    peso+=1
                                                else:
                                                    break
                                #Si se ha pasado al capítulo previo y al posterior se añaden directamente todas las posiciones del actual
                                if(not caps and prev and post):
                                    peso+=len(self.personajes[persk[j]].getPosicionPers()[cap])
                                else:
                                    #Se comprueba en el capítulo actual las palabras que entran en el rango
                                    for posj in self.personajes[persk[j]].getPosicionPers()[cap]:
                                        if(posj>=(posi-rango)):
                                            if(posj<=(posi+rango)):
                                                peso+=1
                                            else:
                                                break
                        if(peso>0):
                            self.__G.add_edge(persk[i],persk[j],weight=peso)
    
    def visualizar(self):
        """
        Método para mandar a d3 la información para visualizar la red
    
        Args:
            
        """
        return json.dumps(nx.json_graph.node_link_data(self.__G))

    def scrapeWiki(self,url):
        """
        Método para obtener un diccionario de personajes haciendo web scraping
    
        Args:
            url: url donde hacer web scraping
        """
        web = urllib.request.urlopen(url)
        html = BeautifulSoup(web.read(), "html.parser")
        for pers in html.find_all("a", {"class": "category-page__member-link"}):
            pn = pers.get('title')
            self.anadirPersonaje(pn,pn)

    def importDict(self, fichero):
        """
        Método para importar un diccionario de personajes desde un fichero csv
    
        Args:
            fichero: ruta al fichero
        """
        self.__csv.importDict(fichero)
    
    def exportDict(self, fichero):
        """
        Método para exportar el diccionario de personajes a un fichero csv
    
        Args:
            fichero: ruta del nuevo fichero
        """
        self.__csv.exportDict(fichero)
         
    '''
    
    '''
    def obtTextoEpub(self, fich):
        """
        Método para obtener el texto del epub del que se quiere obtener la red de 
        personajes
        
        Args:
            fich: ruta al archivo epub
        """
        l = LecturaEpub.LecturaEpub(fich)
        self.__texto = list()
        for f in l.siguienteArchivo():
            self.__texto.append(". " + f)

    @staticmethod
    def esEpub(fich):
        """
        Método para comprobar si un archivo es un epub
        
        Args:
            fich: ruta al archivo epub
        """
        if(not zipfile.is_zipfile(fich)):
            return False
        x = zipfile.ZipFile(fich)
        try:
            x.read('META-INF/container.xml')
        except:
            return False
        else:
            return True

    def exportGML(self,filename):
        """
        Método exportar la red a formato GML
        
        Args:
            filename: ruta del nuevo fichero
        """
        self.writeFile(filename,nx.generate_gml(self.__G))
        
    def exportGEXF(self,filename):
        """
        Método exportar la red a formato GEXF
        
        Args:
            filename: ruta del nuevo fichero
        """
        self.writeFile(filename,nx.generate_gexf(self.__G))
    
    def exportPajek(self,filename):
        """
        Método exportar la red a formato GML
        
        Args:
            filename: ruta del nuevo fichero
        """
        nx.write_pajek(self.__G, filename)
        
    def writeFile(self,filename,text):
        """
        Método escribir un fichero
        
        Args:
            filename: ruta del nuevo fichero
            text: texto para generar el archivo
        """
        file = open(filename,"w")
        for r in text:
            file.write(r)
            
    def generarInforme(self, solicitud):
        """
        Método que maneja las solicitudes de informes
        
        Args:
            solicitud: lista con las metricas
        """
        switch = {'cbx cbx-nnod': self.nNodos, 'cbx cbx-nenl': self.nEnl, 'cbx cbx-nint': self.nInt, 'cbx cbx-gradosin': self.gSin, 'cbx cbx-gradocon': self.gCon, 'cbx cbx-distsin': self.dSin, 'cbx cbx-distcon': self.dCon, 'cbx cbx-dens': self.dens, 'cbx cbx-concomp': self.conComp, 'cbx cbx-exc': self.exc, 'cbx cbx-dia': self.diam, 'cbx cbx-rad': self.rad, 'cbx cbx-longmed': self.longMed, 'cbx cbx-locclust': self.locClust, 'cbx cbx-clust': self.clust, 'cbx cbx-trans': self.trans, 'cbx cbx-centg': self.centG, 'cbx cbx-centc': self.centC, 'cbx cbx-centi': self.centI, 'cbx cbx-ranwal': self.ranWal, 'cbx cbx-centv': self.centV,'cbx cbx-para': self.paRa, 'cbx cbx-kcliperc': self.kCliPerc, 'cbx cbx-girnew': self.girNew, 'cbx cbx-roles': self.roles}
        valkcliqper =  solicitud['valkcliqper']
        del solicitud['valkcliqper']
        self.informe = dict()
        for s in solicitud.keys():
            if('cbx cbx-kcliperc' == s):
                self.informe[s] = switch[s](valkcliqper)
            else:
                self.informe[s] = switch[s]()
        
    def nNodos(self):
        """
        Método que devuelve el numero de nodos
        
        Args:
            
        Return:
            Numero de nodos
        """
        return nx.number_of_nodes(self.__G)
        
    def nEnl(self):
        """
        Método que devuelve el numero de enlaces
        
        Args:
            
        Return:
            Numero de enlaces
        """
        return nx.number_of_edges(self.__G)
        
    def nInt(self):
        """
        Método que devuelve el numero de interacciones
        
        Args:
            
        Return:
            Numero de interacciones
        """
        return self.__G.size(weight='weight')
    
    def gSin(self):
        """
        Método que devuelve el grado sin tener en cuenta el peso
        
        Args:
            
        Return:
            Grado sin el peso
        """
        return nx.degree(self.__G)
        
    def gCon(self):
        """
        Método que devuelve el grado teniendo en cuenta el peso
        
        Args:
            
        Return:
            Grado con el peso
        """
        return nx.degree(self.__G,weight='weight')
        
    def dSin(self):
        """
        Método que devuelve la distribución de grado sin tener en cuenta el peso
        
        Args:
            
        Return:
            Distribucion de grado sin el peso
        """
        degree_sequence = sorted([d for n, d in self.__G.degree()], reverse=True)  # degree sequence
        # print "Degree sequence", degree_sequence
        print(degree_sequence)
        degreeCount = collections.Counter(degree_sequence)
        print(degreeCount)
        return degreeCount
    
    def dCon(self):
        """
        Método que devuelve la distribución de grado teniendo en cuenta el peso
        
        Args:
            
        Return:
            Distribucion de grado con el peso
        """
        degree_sequence = sorted([d for n, d in self.__G.degree(weight='weight')], reverse=True)
        degreeCount = collections.Counter(degree_sequence)
        return degreeCount
        
    def dens(self):
        """
        Método que devuelve la densidad de la red
        
        Args:
            
        Return:
            Densidad de la red
        """
        return nx.density(self.__G)
        
    def conComp(self):
        """
        Método que devuelve todos los componentes conectados
        
        Args:
            
        Return:
            lista de cada componente conectado
        """
        l = list()
        for x in nx.connected_components(self.__G):
            l.append(x)
        return l
        
    def exc(self):
        """
        Método que devuelve la excentricidad de la red
        
        Args:
            
        Return:
            excentricidad de la red
        """
        return nx.eccentricity(self.__G)
    
    def diam(self):
        """
        Método que devuelve el diametro de la red
        
        Args:
            
        Return:
            diametro de la red
        """
        return nx.diameter(self.__G)
        
    def rad(self):
        """
        Método que devuelve el radio de la red
        
        Args:
            
        Return:
            radio de la red
        """
        return nx.radius(self.__G)
        
    def longMed(self):
        """
        Método que devuelve la distancia media de la red
        
        Args:
            
        Return:
            distancia media de la red
        """
        return nx.average_shortest_path_length(self.__G)
        
    def locClust(self):
        """
        Método que devuelve el clustering de cada nodo
        
        Args:
            
        Return:
            clustering de cada nodo
        """
        return nx.clustering(self.__G)
        
    def clust(self):
        """
        Método que devuelve el clustering global de la red
        
        Args:
            
        Return:
            clustering global
        """
        return nx.average_clustering(self.__G)
        
    def trans(self):
        """
        Método que devuelve la transitividad de la red
        
        Args:
            
        Return:
            transitividad de la red
        """
        return nx.transitivity(self.__G)
        
    def centG(self):
        """
        Método que devuelve la centralidad de grado
        
        Args:
            
        Return:
            centralidad de grado
        """
        return nx.degree_centrality(self.__G)
        
    def centC(self):
        """
        Método que devuelve la centralidad de cercania
        
        Args:
            
        Return:
            centralidad de cercania
        """
        return nx.closeness_centrality(self.__G)
        
    def centI(self):
        """
        Método que devuelve la centralidad de intermediacion
        
        Args:
            
        Return:
            centralidad de intermediacion
        """
        return nx.betweenness_centrality(self.__G)
        
    def ranWal(self):
        """
        Método que devuelve la centralidad de intermediacion random walker
        
        Args:
            
        Return:
            centralidad de intermediacion random walker
        """
        return nx.current_flow_betweenness_centrality(self.__G)
        
    def centV(self):
        """
        Método que devuelve la centralidad de valor propio
        
        Args:
            
        Return:
            centralidad de valor propio
        """
        return nx.eigenvector_centrality(self.__G)
        
    def paRa(self):
        """
        Método que devuelve la centralidad de pagerank
        
        Args:
            
        Return:
            centralidad de pagerank
        """
        return nx.pagerank(self.__G)
        
    def kCliPerc(self, k):
        """
        Método que devuelve las comunidades de k-clique
        
        Args:
            k: valor k del k-clique
        Return:
            comunidades de k-clique
        """
        l = list()
        for x in nx.algorithms.community.k_clique_communities(self.__G, int(k)):
            l.append(x)
        return l
        
    def girNew(self):
        """
        Método que devuelve las comunidades de girvan-newman
        
        Args:
            
        Return:
            comunidades de girvan-newman
        """
        l = list()
        resul,mod,npart = self.girvan_newman(self.__G.copy())
        for c in nx.connected_components(resul):
            l.append(c)
        return l
        
    def roles(self):
        """
        Método para detectar roles en comunidades de girvan-newman
        
        Args:
            
        Return:
            roles en comunidades de girvan-newman
        """
        z = self.obtenerZ(self.__G)
        p = self.obtenerP(self.__G)
        pesos = self.__G.degree(weight='weight')
        hubp = list()
        hubc = list()
        hubk = list()
        nhubu = list()
        nhubp = list()
        nhubc = list()
        nhubk = list()
        for t in pesos:
            k = t[0]
            pesoaux = list()
            aux = t[1]*12
            pesoaux.append(aux)
            nodo = list()
            nodo.append(k)
            if z[k] >= 2.5:
                if(p[k] < 0.32):
                    hubp.append(k)
                elif(p[k] < 0.75):
                    hubc.append(k)
                else:
                    hubk.append(k)
            else:
                if(p[k] > -0.02 and p[k] < 0.02):
                    nhubu.append(k)
                elif(p[k] < 0.625):
                    nhubp.append(k)
                elif(p[k] < 0.8):
                    nhubc.append(k)
                else:
                    nhubk.append(k)
        roles = {'hubp':hubp,'hubc':hubc,'hubk':hubk,'nhubu':nhubu,'nhubp':nhubp,'nhubc':nhubc,'nhubk':nhubk}
        return roles

        
    def obtenerZ(self, grafo):
        """
        Método para calcular el grado de la comunidad de cada nodo
        
        Args:
            grafo: red de personajes
        Return:
            grado de la comunidad de cada nodo
        """
        zi = dict()
        resul,mod,npart = self.girvan_newman(grafo.copy())
        for c in nx.connected_components(resul):
            subgrafo = grafo.subgraph(c)
            pesos = subgrafo.degree()
            n = subgrafo.number_of_nodes()
            medksi = 0
            for peso in pesos:
                medksi = medksi + peso[1]/n
            desvksi = 0
            for peso in pesos:
                desvksi = desvksi + (peso[1]-medksi)**2
            desvksi = desvksi/n
            desvksi = desvksi**0.5
            if(desvksi == 0):
                for peso in pesos:
                    zi[peso[0]] = 0
            else:
                for peso in pesos:
                    zi[peso[0]] = (peso[1]-medksi)/desvksi
        return zi
    
    def obtenerP(self, grafo):
        """
        Método para calcular el coeficiente de participacion de cada nodo
        
        Args:
            grafo: red de personajes
        Return:
            coeficiente de participacion de cada nodo
        """
        pi = dict()
        pesos = grafo.degree()
        for peso in pesos:
            ki = peso[1]
            piaux = 0
            resul,mod,npart = self.girvan_newman(grafo.copy())
            for c in nx.connected_components(resul):
                c.add(peso[0])
                sub = grafo.subgraph(c)
                pesosaux = sub.degree()
                ksi = pesosaux[peso[0]]
                piaux = piaux + (ksi/ki)**2 
            pi[peso[0]] = 1 - piaux
        return pi
    
    def modularidad(self,grafo, particion):
        """
        Método para calcular la modularidad
        
        Args:
            grafo: red de personajes
            particion: particion de nodos de la red
        Return:
            coeficiente de participacion de cada nodo
        """
        m = nx.number_of_edges(grafo)
        nodos = list(particion.keys())
        tot = 0
        for i in range(0,len(nodos)):
            for j in range(0,len(nodos)):
                if(particion[nodos[i]]==particion[nodos[j]]):
                    aux = (grafo.degree[nodos[i]]*grafo.degree[nodos[j]]/(2*m))
                    A = grafo.number_of_edges(nodos[i],nodos[j])
                    tot += A-aux
        return tot/(2*m)
    
    def girvan_newman(self,grafo):
        """
        Método para calcular la mejor comunidad por girvan-newman
        
        Args:
            grafo: red de personajes
        Return:
            mejor partincion
            modularidad
            numero de particiones
        """
        inicial = grafo.copy()
        mod = list()
        npart = list()
        part = dict()
        i=0
        for c in nx.connected_components(grafo):
            for j in c:
                part[j]=i
            i+=1
        npart.append(i)
        ultnpar = i
        modu = self.modularidad(inicial,part)
        mod.append(modu)
        mejormod = modu
        mejor = grafo.copy()
        while(nx.number_of_edges(grafo)>0):
            btwn = list(nx.edge_betweenness_centrality(grafo).items())
            mini = -1
            for i in btwn:
                if i[1]>mini:
                    enlaces = i[0]
                    mini=i[1]
            grafo.remove_edge(*enlaces)
            i=0
            part = dict()
            for c in nx.connected_components(grafo):
                for j in c:
                    part[j]=i
                i+=1
            if(i>ultnpar):
                ultnpar = i
                npart.append(i)
                modu = self.modularidad(inicial,part)
                mod.append(modu)
                if(modu>mejormod):
                    mejormod=modu
                    mejor = grafo.copy()
        return mejor,mod,npart