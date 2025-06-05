import cv2
from pynput import keyboard
import requests
from requests.auth import HTTPDigestAuth
import time

rtsp_url = "rtsp://192.168.0.241:554/user=admin&password=MKL28200205As&channel=0&stream=1?.sdp"
cap = cv2.VideoCapture(rtsp_url)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Для камер с ONVIF (имитация SOAP через HTTP)
ptz_url = "http://192.168.0.241:8899/onvif/ptz_service"
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

try:
  while listener.is_alive():
    # Here you would send the PTZ commands to your camera
    # For example:
    # ptz.send_ptz_command(pan=current_pan, tilt=current_tilt, zoom=current_zoom)
    ok, frame = cap.read()
    cv2.imshow("video", frame)
    cv2.waitKey(1)
  cv2.destroyAllWindows()
  cap.release()
except KeyboardInterrupt:
  pass
finally:
  listener.stop()
  listener.join() 
