 ### Программное обеспечение camera-2.0.0.0.py для получение видеопотока с камер:
 ### - PTZ и курсовой (прим.: совмещённой) камеры
 ### Автор - Mathison
 ### mark - 5.3.0.9

 ### подключаем библиотеку openCV
import cv2
import numpy as np

 # объявляем группу переменных и присваиваем параметры для сбора rtsp ссылки
# rtsp - потоковый протокол реального времени
# addr - ip адрес камеры
addr1 = '192.168.0.8'
addr2 = '192.168.0.8'
addr3 = '192.168.0.7'
# port - RTSP порт камеры
port = ':554'
# user = пользователь
user = 'admin'
# password = пароль
password_t = 'MKL28200205As'
password = '123Lisuin' #пароль китайской PTZ-камеры установленной на БЭК1000
# channel = канал
channel_t = '1' #цветное изображение
channel_tb= '2' #тепловизор-биспектральное изображение
channel = '0' #обзорная PTZ-камера
#channel = '1' #обзорная PTZ-камера

# stream = поток
stream_t = '2'
stream_tb = '2'
stream = '0.sdp?' #два потока китайской PTZ-камеры
#stream = '1.sdp?' #статичная камера с китайской PTZ-камеры
# url = адрес для web-камеры
# url = адресс, с префиксом f для форматирвоания и интерпритирования значения - строки 

 #Двуспектральная камера
#url1 = "rtsp://admin:MKL28200205As@192.168.0.8:554/snl/live/1/2"
#url1 = f"rtsp://user={user}:password={password_}@{addr1}{port}/snl/live/channel={channel_t}stream={stream_t}"
#url2 = "rtsp://admin:MKL28200205As@192.168.0.8:554/snl/live/2/2"
#url2 = f"rtsp://user={user}:password={password_}@{addr1}{port}/snl/live/channel={channel_tb}stream={stream_tb}"

 #Двуспектральная камера заводские настройки
#url = "rtsp://Admin:1234@192.168.0.250:554/snl/live/2/1"

 #Китайская PTZ-камера
url1 = "rtsp://192.168.0.71:554/user=admin&password=MKL28200205As&channel=0&stream=1.sdp?"
url2 = "rtsp://192.168.0.71:554/user=admin&password=MKL28200205As&channel=0&stream=1.sdp?"
url3 = "rtsp://192.168.0.71:554/user=admin&password=MKL28200205As&channel=0&stream=1.sdp?"
#url3 = f"rtsp://{addr3}{port}/user={user}&password={password}&channel={channel}&stream={stream}"

# создаём объект с методом из OpenCV, вызываем метод открытия потока с камеры с помощью rtsp и "захвата" видео
# передаём в переменную
#camera = cv2.VideoCapture(0)
camera1 = cv2.VideoCapture(url1)
camera2 = cv2.VideoCapture(url2)
camera3 = cv2.VideoCapture(url3)

min_width_react = 90
min_hieght_react = 90
count_line_position = 170
algo = cv2.createBackgroundSubtractorMOG2()
def center_handle(x,y,w,h):
    x1 = int(w/2)
    y1 = int(h/2)
    cx = x+x1
    cy = y+y1
    return cx,cy

detected = []
offset = 6
counter = 0

while True:
     # объявляем переменные и присваеиваем функцию чтения переданного rtsp-ссылки
    #ret, frame = camera.read()
    ret1, frame1 = camera1.read()
    ret2, frame2 = camera2.read()
    ret3, frame3 = camera3.read()
    #if not ret1, or not ret2, or not ret3:
    #    print("Нет соединения с камерой")
    #    break

     # Поворот изображения, получаемого от камеры
    frame3 = cv2.rotate(frame3, cv2.ROTATE_180)

     # задаем размер кадра
    frame_size = (frame1.shape[1], frame1.shape[0])
    frame1_resized = cv2.resize(frame1, frame_size)
    frame2_resized = cv2.resize(frame2, frame_size)
    frame3_resized = cv2.resize(frame3, frame_size)

     # объявление переменной и передаём вызов метода с функцией перевода кадров в чёрно-белую градацию
    grey = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
     # объявляем переменную и передаём вызов с функцией фильтрации (прим.: используем метод Гаусса, фильтры Гаусса)
     # для отсеивания лишних контуров
    blur = cv2.GaussianBlur(grey,(3,3),5)
    img_sub = algo.apply(blur)
     # объявляем и передаём в переменную вызов метода с функцией дилатации, расширения изображения
     # расширяем выделенную область определённую на шаге выше данного алгоритма
    dilate = cv2.dilate(img_sub, np.ones((5,5)))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    dilatada = cv2.morphologyEx(dilate, cv2.MORPH_CLOSE, kernel)
    dilatada = cv2.morphologyEx(dilatada, cv2.MORPH_CLOSE, kernel)
     # объявляем и передаём в переменную вызов метода с функцией поиска контуров
    contours,h = cv2.findContours(dilatada, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.line(frame1, (900,count_line_position),(1200, count_line_position),(255,127,0),3)
    for(i,c) in enumerate(contours):
        (x,y,w,h) = cv2.boundingRect(c)
        validate_counter = (w>= min_width_react) and (h>= min_hieght_react)
        #
        if not validate_counter:
            continue
         # вызываем метод с функцией рисования прямоугольника на изображении из точек кортежа
        cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame1, "Объект: " +str(counter), (x, y-20), cv2.FONT_HERSHEY_COMPLEX, 1, (255,244,0), 2)
        center = center_handle(x,y,w,h)
        detected.append(center)
        cv2.circle(frame1, center, 4, (0,0,255), -1)

        for (x,y) in detected:
            if y < (count_line_position + offset) and y > (count_line_position - offset):
                counter+=1
                cv2.line(frame1, (900,count_line_position),(1200,count_line_position),(0,127,255),3)
                detected.remove((x,y))
                print("id" +str(counter))
     # вызываем метод с функцией отражения текста поверх потока
    cv2.putText(frame1, "Количество: " +str(counter), (100, 70), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 5)#, cv2.LINE_AA)
     # создаём условие, которое будет отвечать за отображение и закрытие окна (прим.: frame)/выход из rtsp
     # левая часть - вызываем функцию отображения окна (прим.: frame) с прослушиванием нажатия клавиш 
     # функция может принять в качестве параметра время в милисекундах или можно проверять нажатие клавиш
     # присвоен параметр - 1, поскольку есть условие (примю: правая часть)
     # прим.: присвоив - 0, можно получать текущую картинку
     # правая часть - вызываем функцию возврата/перевода юникода с назначением исполняемой клавиши
     # x (прим.: например) -> в юникод, для функции waitKey
    if cv2.waitKey(1) == ord('x'):
        break

     # вызываем метод отобюражения получаемых изображений в окне
     # окно подстравивается под изображение
    col1 = np.vstack((frame1_resized, frame2_resized))
    out = np.hstack((frame1_resized, frame2_resized, frame3_resized))

    #cv2.imshow("Windows Video", frame1_resized)
    cv2.imshow('test', out)
    
 # вызщываем метод с присвоением функции закрытия окна
cv2.destroyAllWindows()
 # вызываем метод и присваиваем функцию высвобождения программных и аппаратных мощностей
#camera.release()
camera1.release()
camera2.release()
camera3.release()
