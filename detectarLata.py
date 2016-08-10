# Deteccion de formas
# import the necessary packages
import numpy as np
import argparse
import cv2
import imutils
global boxmax
boxmax = -1
global boxmin
boxmin = 10000000
global maximo 
maximo = -1
global minimo 
minimo = 10000000000
##--------------------------------------------------------------##
#	Funcion que permite aumentar o disminuir el brillo de 		 #
#	una imagen. La idea es poder usarlo para disminuir la  	 	 #
#	luz que puede afectar la deteccion de los colores. 			 #
#																 #
#	Parametros:												     #
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
#	Funcion utilizada para detectar la presencia de un color en  #
#	una imagen. Para ser mas precisos se utiliza un rango donde	 #
#	se encuentra el color buscado. 								 #
#																 #
#	Parametros:												     #
#		image: imagen donde se buscara el color.  				 #
#		lower: color en HSV que corresponde al limite inferior   #
#				del rango del color buscado. 					 #
#		upper: color en HSV que corresponde al limite superior	 #
#				del rango del color buscado. 					 #
#	Retorna: la mascara resultante de la busqueda del rango 	 #
#			 de colores en image,								 #
##--------------------------------------------------------------##
def detectarColor(image, lower, upper):
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	hsv = cv2.GaussianBlur(hsv, (5, 5), 7)	# Blur utilizado para disminuir ruido
	mascara = cv2.inRange(hsv, lower, upper)	
	return mascara


##--------------------------------------------------------------##
#	Funcion utilizada para detectar la presencia de un color en  #
#	una imagen. Se descartaran aquellas figuras que tengan un    #
#	area pequena, porque corresponden a ruido u objetos no 		 # 
#	deseados. 													 #
#																 #
#	Parametros:												     #
#		image: imagen donde se buscara el color.  				 #
#		mascara: color en HSV que corresponde al limite inferior   #
#				del rango del color buscado. 					 #
#		error: color en HSV que corresponde al limete superior	 #
#				del rango del color buscado. 					 #
#	Retorna: la mascara resultante de la busqueda del rango 	 #
#			 de colores en image,								 #
##--------------------------------------------------------------##
def detectarForma(image, mascara,error):
	##---- Encuentra los contornos en la mascara. CHAIN_APPROX_SIMPLE sirve para ahorrar memoria ----##
	##---- porque te retorna solo los vertices de la figura. 									 ----##
	im2, cnts, hierarchy = cv2.findContours(mascara, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

	
	 

	##---- Recorremos los contornos encontrados ----##
	for cnt in cnts:
		peri = cv2.arcLength(cnt, True)					# Perimetro del contorno
		aprox = cv2.approxPolyDP(cnt,error*peri,True) 	# Aproxima las curvas poligonales de un contorno
		area = cv2.contourArea(cnt)
		if area >= 1000:
			print area
			if 3<=len(aprox) <6:
				cv2.drawContours(image,[cnt],0,(0,0,255),7)		# Dibuja el contorno encontado en la img original
				return "Cuadrado"
			elif 6<=len(aprox) :
				cv2.drawContours(image,[cnt],0,(255,255,0),7)	
				return "Circulo"



def distance_to_camera(knownWidth, focalLength, perWidth):
	return (knownWidth * focalLength) / perWidth


def distancia(image,src, focalLength , kdist, kwidth):
	global minimo
	global maximo
	global boxmin
	global boxmax
	#ref1 = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
	src = cv2.threshold(src, 60, 255, cv2.THRESH_BINARY)[1]
	im2, contours, hierarchy = cv2.findContours(src.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	try:
		c = max(contours, key = cv2.contourArea)
		M = cv2.moments(c)
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])
	# draw the contour and center of the shape on the image
		cv2.drawContours(image1, [c], -1, (0, 255, 0), 2)
		cv2.circle(image1, (cX, cY), 7, (255, 255, 255), -1)
		cv2.putText(image1, "center", (cX - 20, cY - 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
	except:
		return -1
	marker = cv2.minAreaRect(c)
	inches = distance_to_camera(kwidth, focalLength, marker[1][0])
	box = np.int0(cv2.boxPoints(marker))
	if inches < minimo:
		minimo = inches
		boxmin = box
	elif inches > maximo:
		maximo = inches
		boxmax = box

	if inches < 25:
		cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
		cv2.putText(image, "%.2fcm" % (inches),
		(image.shape[1] - 200, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX,
		2.0, (0, 255, 0), 3)
	else:
		cv2.drawContours(image, [box], -1, (0, 0, 255), 2)
		cv2.putText(image, "%.2fcm" % (inches),
		(image.shape[1] - 200, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX,
		2.0, (0, 0 , 255), 3)	
	try:
		cv2.drawContours(image, [boxmin], -1, (255, 0, 255), 2)
		cv2.drawContours(image, [boxmax], -1, (0, 0,0), 2)
	except: 
		pass
	return image.copy()

def calibrarDist(ref, kdist, kwidth):
	ref1 = cv2.cvtColor(ref.copy(), cv2.COLOR_BGR2GRAY)
	ref1 = cv2.GaussianBlur(ref1, (5, 5), 0)
	ref1 = cv2.Canny(ref1, 35, 125)
	edged = cv2.Canny(ref, 35, 125)
	im2, contours, hierarchy = cv2.findContours(edged,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	c = max(contours, key = cv2.contourArea)
	marker = cv2.minAreaRect(c)
	focalLength = (marker[1][0] * kdist) / kwidth
	#cv2.imshow("im2",im2)
	return focalLength	

def dibujarGrid(image1,numFil,numCol):
 
	for i in range(1,numFil):
		cv2.line(image1,(0,(480/numFil)*i),(640,(480/numFil)*i),(255,0,0),5)
	for i in range(1,numCol):
		cv2.line(image1,((640/numCol)*i,0),((640/numCol)*i,480),(255,0,0),5)	

##---- Main function ----##
if __name__ == "__main__":
	"""
	kDist = 24
	kWidth = 6.5
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
	"""
	kernel = np.ones((5,5),np.uint8)
	PATH = "latita.jpg"
	refer = cv2.imread(PATH)
	kDist = 24
	kWidth = 6.5
	cap = cv2.VideoCapture(0)
	F = calibrarDist(refer,kDist,kWidth)
	while(True):
		error = 0.0220						#0.0213
		# Leer la imagen
		ret1, image = cap.read()
		#image = image & mask_rbg
		# Rango para la imagen.
		lower = np.array([0, 0, 0])			# 0, 0, 0
		upper = np.array([180, 255, 50])	# 180 255 50
		image1 = ajustarBrillo(image,0.99)		# Ajustamos el brillo de la imagen
		# Aplicamos el filtro de color que nos devuelve una mascara.
		filtroColor = detectarColor(image1.copy(),lower,upper)
		filtroCBlur = cv2.GaussianBlur(filtroColor, (23, 23), 0)
		filtroCCan = cv2.Canny(filtroCBlur.copy(),0,255)
		filtroCCan = cv2.morphologyEx(filtroCCan.copy(), cv2.MORPH_CLOSE, kernel)
		filtroForma = detectarForma(filtroCCan,filtroColor.copy(),error)
		distancia(image1,filtroCCan.copy(),F,kDist,kWidth)
		dibujarGrid(image1,2,3)

	# find contours in the thresholded image
		#cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		#cv2.CHAIN_APPROX_SIMPLE)
		#cnts = cnts[0] if imutils.is_cv2() else cnts[1]

		

		#cv2.imshow("blur", filtroCBlur)
		#cv2.imshow("filtroColor",filtroColor)
		cv2.imshow("Original", image1)
		#cv2.imshow("Can", filtroCCan)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()