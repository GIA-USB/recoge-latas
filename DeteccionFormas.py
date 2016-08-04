# Deteccion de formas
# import the necessary packages
import numpy as np
import argparse
import cv2

##--------------------------------------------------------------##
#	Función que permite aumentar o disminuir el brillo de 		 #
#	una imagen. La idea es poder usarlo para disminuir la  	 	 #
#	luz que puede afectar la detección de los colores. 			 #
#																 #
#	Parámetros:												     #
#		image: imagen a la que se le quiere modificar el brillo. #
#		gamma: = 1 es la imagen original, > 1 aumenta el brillo, #
#				< 1 lo disminuye. 								 #
#	Retorna: la imagen con el brillo modificado. 				 #
##--------------------------------------------------------------##
def ajustarBrillo(image, gamma=1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
 
	# apply gamma correction using the lookup table
	return cv2.LUT(image, table)


##--------------------------------------------------------------##
#	Función utilizada para detectar la presencia de un color en  #
#	una imagen. Para ser más precisos se utiliza un rango donde	 #
#	se encuentra el color buscado. 								 #
#																 #
#	Parámetros:												     #
#		image: imagen donde se buscará el color.  				 #
#		lower: color en HSV que corresponde al límite inferior   #
#				del rango del color buscado. 					 #
#		upper: color en HSV que corresponde al límete superior	 #
#				del rango del color buscado. 					 #
#	Retorna: la máscara resultante de la búsqueda del rango 	 #
#			 de colores en image,								 #
##--------------------------------------------------------------##
def detectarColor(image, lower, upper):
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	hsv = cv2.GaussianBlur(hsv, (5, 5), 7)	# Blur utilizado para disminuir ruido
	mascara = cv2.inRange(hsv, lower, upper)	
	return mascara


##--------------------------------------------------------------##
#	Función utilizada para detectar la presencia de un color en  #
#	una imagen. Se descartarán aquellas figuras que tengan un    #
#	área pequeña, porque corresponden a ruido u objetos no 		 # 
#	deseados. 													 #
#																 #
#	Parámetros:												     #
#		image: imagen donde se buscará el color.  				 #
#		mascara: color en HSV que corresponde al límite inferior   #
#				del rango del color buscado. 					 #
#		error: color en HSV que corresponde al límete superior	 #
#				del rango del color buscado. 					 #
#	Retorna: la máscara resultante de la búsqueda del rango 	 #
#			 de colores en image,								 #
##--------------------------------------------------------------##
def detectarForma(image, mascara,error):
	##---- Encuentra los contornos en la máscara. CHAIN_APPROX_SIMPLE sirve para ahorrar memoria ----##
	##---- porque te retorna solo los vértices de la figura. 									 ----##
	im2, cnts, hierarchy = cv2.findContours(mascara, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)	

	##---- Recorremos los contornos encontrados ----##
	for cnt in cnts:
		peri = cv2.arcLength(cnt, True)					# Perímetro del contorno
		aprox = cv2.approxPolyDP(cnt,error*peri,True) 	# Aproxima las curvas poligonales de un contorno
		area = cv2.contourArea(cnt)
		if area >= 1000:
			print area
			if 3<=len(aprox) <6:
				cv2.drawContours(image,[cnt],0,(0,0,255),1)		# Dibuja el contorno encontado en la img original
				return "Cuadrado"
			elif 6<=len(aprox) :
				cv2.drawContours(image,[cnt],0,(255,255,0),1)	
				return "Circulo"
		

##---- Main function ----##
if __name__ == "__main__":

	cap = cv2.VideoCapture(1)
	error = 0.0213

	while(True):
		# Leer la imagen
		ret1, image = cap.read()
		# Rango para la imagen.
		lower = np.array([0, 0, 0])			# 0, 0, 0
		upper = np.array([180, 255, 50])	# 180 255 50
		image1 = ajustarBrillo(image,1)
		filtroColor = detectarColor(image1,lower,upper)
		filtroForma = detectarForma(image1,filtroColor,error)
		image2 = ajustarBrillo(image,1.30)
		filtroColor = detectarColor(image2,lower,upper)
		filtroForma = detectarForma(image2,filtroColor,error)
		cv2.imshow("Image1", image1)
		cv2.imshow("Image2", image2)	
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()