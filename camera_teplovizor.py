### Программное обеспечение для получение видеопотока с камер:
### - Hikvision DS-2SE4C425MWG-E(14F0)
### - стреоскопической камеры
### Автор - Mathison
### mark - 0.0.2

### подключаем библиотеку openCV
import cv2
import numpy as np

# добавляем переменную и присваемваем rtsp ссылку
# rtsp - потоковый протокол реального времени
# инструкция состоит из:
# логнин - admin
# пароля - MKL28200205A
# ip адреса - 192.168.0.8
# камеры и потока
# - 1/2 - цветной видеопоток
# - 2/1 - тепловизорный поток

## Вариант 1
# создаём объект с методом из OpenCV, вызываем метод открытия потока с камеры с помощью rtsp и "захвата" видео
# передаём в переменную

url = "rtsp://admin:MKL28200205As@192.168.0.8:554/snl/live/1/2"
url2 = "rtsp://admin:MKL28200205As@192.168.0.8:554/snl/live/2/1"

camera = cv2.VideoCapture(url)
camera2 = cv2.VideoCapture(url2)

min_width_react = 80
min_hieght_react = 80
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
    # объявляем переменные и присваеиваем функцию чтения переданного rtsp
    ret, frame = camera.read()
    ret2, frame2 = camera2.read()

     # переворачиваем видеокадр
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    frame2 = cv2.rotate(frame2, cv2.ROTATE_180)

     # задаем размер кадра
    frame_size = (frame.shape[1], frame.shape[0])
    frame_resized = cv2.resize(frame, frame_size)
    frame2_resized = cv2.resize(frame2, frame_size)

    # объявление переменной и передаём вызов метода с функцией перевода кадров в чёрно-белую градацию
    grey = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    #grey2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
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
    #contours2,h2 = cv2.findContours(dilatada2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.line(frame, (900,count_line_position),(1200, count_line_position),(255,127,0),3)
    for(i,c) in enumerate(contours):
        (x,y,w,h) = cv2.boundingRect(c)
        validate_counter = (w>= min_width_react) and (h>= min_hieght_react)
        #
        if not validate_counter:
            continue
        # вызываем метод с функцией рисования прямоугольника на изображении из точек кортежа
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, "Объект: " +str(counter), (x, y-20), cv2.FONT_HERSHEY_COMPLEX, 1, (255,244,0), 2)
        center = center_handle(x,y,w,h)
        detected.append(center)
        cv2.circle(frame, center, 4, (0,0,255), -1)

        for (x,y) in detected:
            if y < (count_line_position + offset) and y > (count_line_position - offset):
                counter += 1
                cv2.line(frame, (900,count_line_position),(1200, count_line_position),(0,127,255),3)
                detected.remove((x,y))
                print("id" +str(counter))
    # вызываем метод с функцией отражения текста поверх потока
    cv2.putText(frame, "Количество: " +str(counter), (100, 70), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 5)

     #задаем размер кадра
    
    # создаём условие, которое будет отвечать за отображение и закрытие окна (прим.: frame)/выход из rtsp
    # левая часть - вызываем функцию отображения окна (прим.: frame) с прослушиванием нажатия клавиш 
    # функция может принять в качестве параметра время в милисекундах или можно проверять нажатие клавиш
    # присвоен параметр - 1, поскольку есть условие (примю: правая часть)
    # прим.: присвоив - 0, можно получать текущую картинку
    # правая часть - вызываем функцию возврата/перевода юникода с назначением исполняемой клавиши
    # x (прим.: например) -> в юникод, для функции waitKey
    if cv2.waitKey(1) == ord('x'):
        break
    
     #расположение кадров в окне по вертикали и горизонтали
    #col1 = np.vstack((frame_resized, frame2_resized))
    out = np.hstack((frame, frame2))#, frame3_resized))
    # вызываем метод отобюражения получаемых изображений в окне
    # окно подстравивается под изображение
    cv2.imshow("Hikvision",out)
# вызщываем метод с присвоением функции закрытия окна
cv2.destroyAllWindows()
  # вызываем метод и присваиваем функцию высвобождения программных и аппаратных мощностей
camera.release()
camera2.release()