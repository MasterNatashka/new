import cv2
import numpy as np
from pynput import keyboard
import requests
from requests.auth import HTTPDigestAuth

rtsp_url = "rtsp://192.168.0.71:554/user=admin&password=MKL28200205As&channel=0&stream=1?.sdp"
cap = cv2.VideoCapture(rtsp_url)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Для камер с ONVIF (имитация SOAP через HTTP)
ptz_url = "http://192.168.0.71:8899/onvif/ptz_service"
headers = {'Content-Type': 'application/soap+xml'}
auth=HTTPDigestAuth('admin', 'MKL28200205As')

pan_speed = 0.5
tilt_speed = 0.5
zoom_speed = 0.3
current_pan = 0
current_tilt = 0
current_zoom = 0

def ptz_move(pan=0, tilt=0):
  return requests.post(
    ptz_url,
    headers=headers,
    auth=auth,
    timeout=5,
    data=f"""
      <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
        <soap:Body>
          <tptz:ContinuousMove xmlns:tptz="http://www.onvif.org/ver20/ptz/wsdl">
            <tptz:ProfileToken>Profile_1</tptz:ProfileToken>
            <tptz:Velocity>
              <tt:PanTilt x={pan} y={tilt} xmlns:tt="http://www.onvif.org/ver10/schema"/>
            </tptz:Velocity>
          </tptz:ContinuousMove>
        </soap:Body>
      </soap:Envelope>
    """
  )

def ptz_stop():
  return requests.post(
    ptz_url,
    headers=headers,
    auth=auth,
    timeout=5,
    data=f"""
      <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
        <soap:Body>
          <tptz:Stop xmlns:tptz="http://www.onvif.org/ver20/ptz/wsdl">
            <tptz:ProfileToken>Profile_1</tptz:ProfileToken>
            <tptz:PanTilt>true</tptz:PanTilt>
            <tptz:Zoom>true</tptz:Zoom>
          </tptz:Stop>
        </soap:Body>
      </soap:Envelope>
    """
  )

def on_press(key):
  global current_pan, current_tilt, current_zoom
  try:
    if key == keyboard.Key.up and current_tilt != -tilt_speed:
      current_tilt = -tilt_speed
      ptz_move(pan=current_pan, tilt=current_tilt)
    elif key == keyboard.Key.down and current_tilt != tilt_speed:
      current_tilt = tilt_speed
      ptz_move(pan=current_pan, tilt=current_tilt)
    elif key == keyboard.Key.left and current_pan != -pan_speed:
      current_pan = -pan_speed
      ptz_move(pan=current_pan, tilt=current_tilt)
    elif key == keyboard.Key.right and current_pan != pan_speed:
      current_pan = pan_speed
      ptz_move(pan=current_pan, tilt=current_tilt)
    elif key == keyboard.Key.page_up:
      current_zoom = zoom_speed
      print("Zoom In")
    elif key == keyboard.Key.page_down:
      current_zoom = -zoom_speed
      print("Zoom Out")
  except AttributeError:
    pass

def on_release(key):
  global current_pan, current_tilt, current_zoom
  if key in [keyboard.Key.up, keyboard.Key.down] and current_tilt != 0:
    current_tilt = 0
    ptz_stop()
  elif key in [keyboard.Key.left, keyboard.Key.right] and current_pan != 0:
    current_pan = 0
    ptz_stop()
  elif key in [keyboard.Key.page_up, keyboard.Key.page_down]:
    current_zoom = 0
  if key == keyboard.Key.esc:
      print("Exiting PTZ control")
      return False  # Stop listener

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

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

try:
  while listener.is_alive():
    # Here you would send the PTZ commands to your camera
    # For example:
    # ptz.send_ptz_command(pan=current_pan, tilt=current_tilt, zoom=current_zoom)
    ok, frame = cap.read()

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
                counter+=1
                cv2.line(frame, (900,count_line_position),(1200,count_line_position),(0,127,255),3)
                detected.remove((x,y))
                print("id" +str(counter))
    # вызываем метод с функцией отражения текста поверх потока
    cv2.putText(frame, "Количество: " +str(counter), (100, 70), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 5)#, cv2.LINE_AA)
    # создаём условие, которое будет отвечать за отображение и закрытие окна (прим.: frame)/выход из rtsp
    # левая часть - вызываем функцию отображения окна (прим.: frame) с прослушиванием нажатия клавиш 
    # функция может принять в качестве параметра время в милисекундах или можно проверять нажатие клавиш
    # присвоен параметр - 1, поскольку есть условие (примю: правая часть)
    # прим.: присвоив - 0, можно получать текущую картинку
    # правая часть - вызываем функцию возврата/перевода юникода с назначением исполняемой клавиши
    # x (прим.: например) -> в юникод, для функции waitKey
    cv2.imshow("video", frame)
    cv2.waitKey(1)
  cv2.destroyAllWindows()
  cap.release()
except KeyboardInterrupt:
  pass
finally:
  listener.stop()
  listener.join() 
