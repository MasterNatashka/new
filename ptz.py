from time import sleep
from onvif import ONVIFCamera
 
XMAX = 1
XMIN = -1
YMAX = 1
YMIN = -1
 
def perform_move(ptz, request, timeout):
    # объявялем метод непрериывного движения
    ptz.ContinuousMove(request)
    # вызываем функцию ожидания
    sleep(timeout)
    # объявляем метод остановки движения
    ptz.Stop({'ProfileToken': request.ProfileToken})
 
def move_up(ptz, request, timeout=1):
    print ('движение вверх...')
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMAX
    perform_move(ptz, request, timeout)
 
def move_down(ptz, request, timeout=1):
    print ('движение вниз...')
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMIN
    perform_move(ptz, request, timeout)
 
def move_right(ptz, request, timeout=1):
    print ('движение направо...')
    request.Velocity.PanTilt._x = XMAX
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)
 
def move_left(ptz, request, timeout=1):
    print ('дыижение налево...')
    request.Velocity.PanTilt._x = XMIN
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)
 
def continuous_move():
    mycam = ONVIFCamera('192.168.0.8', 80, 'admin', '123Lisuin')
    # объявляем переменную и создаём объект медиаслужбы
    media = mycam.create_media_service()
    # объявляем переменную и создаём объект службы ptz
    ptz = mycam.create_ptz_service()
 
    # объявляем переменную и создаём объект получение целевого профиля
    media_profile = media.GetProfiles()[0];
 
    # объявляем переменную и создаём объекn получения профиля цели
    request = ptz.create_type('GetConfigurationOptions')
    # объявление объекта и присвоение параметров конфигурации PTZ для получения диапазона непрерывного перемещения
    request.ConfigurationToken = media_profile.PTZConfiguration._token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)
 
    request = ptz.create_type('ContinuousMove')
    request.ProfileToken = media_profile._token
 
    ptz.Stop({'ProfileToken': media_profile._token})
 
    # объявляем переменные и создаём диапазон панорамирования и наклона
    # NOTE: X и Y вектор скорости
    global XMAX, XMIN, YMAX, YMIN
    XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
    XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
    YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
    YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min
 
    # движение направо
    move_right(ptz, request)
 
    # движение налево
    move_left(ptz, request)
 
    # движение вверх
    move_up(ptz, request)
 
    # дыижение вниз
    move_down(ptz, request)
 
if __name__ == '__main__':
    continuous_move()