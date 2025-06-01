### Программное обеспечение для получение видеопотока с камер:
### - PTZ и курсовой (прим.: совмещённой) камеры
### Автор - Mathison
### mark - 5.3.0.9

### подключаем библиотеку openCV
import cv2
import numpy as np

# объявляем группу переменных и присваиваем параметры для сбора rtsp ссылки
# rtsp - потоковый протокол реального времени
# ipport_cam = ip адрес и порт камеры
ipport_cam = '192.168.0.7:554'
# user = пользователь
user = 'admin'
# password = пароль
password = 'MKL28200205As'
# channel = канал
channel = '1'
# stream = поток
stream = '1'
# url = адрес для web-камеры
# url = 0
# url = адресс, с префиксом f для форматирвоания и нтерпритирвоания значения - строки 
url = f"rtsp://{ipport_cam}/user={user}&password={password}&channel={channel}&stream={stream}.sdp?"

# создаём объект с методом из OpenCV, вызываем метод открытия потока с камеры с помощью rtsp и "захвата" видео
# передаём в переменную
camera = cv2.VideoCapture(0)
min_width_react = 80
min_hieght_react = 80
count_line_position = 450
algo = cv2.createBackgroundSubtractorMOG2()
def center_handle(x,y,w,h):
    x1 = int(w/2)
    y1 = int(h/2)
    cx = x+x1
    cy = y+y1
    return cx,cy

detected = []
offset = 6
contours = 0

while True:
    # объявляем переменные и присваеиваем функцию чтения переданного rtsp
    ret, frame = camera.read()
    # Поворот изображения, получаемого от камеры
    frame2 = cv2.rotate(frame, cv2.ROTATE_180)
    # объявление переменной и передаём вызов метода с функцией перевода кадров в чёрно-белую градацию
    grey = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
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
    cv2.line(frame,(25,count_line_position),(1200, count_line_position),(255,127,0),2)
    for(i,c) in enumerate(contours):
        (x,y,w,h) = cv2.boundingRect(c)
        validate_counter = (w>= min_width_react) and (h>= min_hieght_react)
        #
        if not validate_counter:
            continue
        # вызываем метод с функцией рисования прямоугольника на изображении из точек кортежа
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, "Объект: " +str(contours), (x, y-20), cv2.FONT_HERSHEY_COMPLEX, 1, (255,254,0), 2)
        center = center_handle(x,y,w,h)
        detected.append(center)
        cv2.circle(frame, center, 4, (0,0,255), -1)

        for (x,y) in detected:
            if y < (count_line_position + offset) and y > (count_line_position + offset):
                contours+=1
                cv2.line(frame,(25,count_line_position),(1200, count_line_position),(0,127,255),2)
                detected.remove(x,y)
                print("" +str(contours))
    # вызываем метод с функцией отражения текста поверх потока
    cv2.putText(frame, "Количество: " +str(contours), (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5, cv2.LINE_AA)
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
    cv2.imshow("Windows Hikvision",frame)
# вызщываем метод с присвоением функции закрытия окна
cv2.destroyAllWindows()
# вызываем метод и присваиваем функцию высвобождения программных и аппаратных мощностей
camera.release()
