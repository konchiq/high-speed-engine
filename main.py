from vpython import *
import numpy as np
import easygui

# Создание всплывающего окна для ввода параметров
msg = "Введите параметры симуляции"
title = "Настройка релятивистской симуляции"
field_names = ["Масса покоя объекта (кг):", "Длина объекта (м):", "Начальная скорость (доля от c):"]
field_values = easygui.multenterbox(msg, title, field_names, ["100000", "1e10", "0.5"])

# Обработка ввода и установка значений по умолчанию
try:
    m0 = float(field_values[0]) if field_values[0] else 100000
    L0 = float(field_values[1]) if field_values[1] else 1e10
    v0 = float(field_values[2]) if field_values[2] else 0.9
except (ValueError, TypeError):
    easygui.msgbox("Ошибка ввода! Используются значения по умолчанию.", "Ошибка")
    m0, L0, v0 = 100000, 1e10, 0.9

# КОНСТАНТЫ И НАСТРОЙКИ
c = 3e8  # Скорость света (м/с)
FPS = 60
SIMULATION_TIME = 100
INITIAL_RANGE = 2.5e10  # Начальный масштаб сцены

# НАСТРОЙКА СЦЕНЫ
scene = canvas(
    title='<title>Релятивистское движение</title>',
    width=1920,
    height=1080,
    align='left'
)
scene.range = INITIAL_RANGE
scene.forward = vector(-0.3, -0.2, -1)
scene.autoscale = False

# Коэффициент для масштабирования меток
current_scale = 1.0


def update_scale():
    global current_scale
    current_scale = scene.range / INITIAL_RANGE


# ОБЪЕКТ С ПРИВЯЗАННОЙ МЕТКОЙ
class LabeledObject:
    def __init__(self, obj_type, m0, L0, pos, obj_color, label_offset_y, label_yoffset):
        self.obj_type = obj_type
        self.m0 = m0
        self.L0 = L0
        self.pos = pos
        self.obj_color = obj_color
        self.label_offset_y = label_offset_y
        self.label_yoffset = label_yoffset

        # Основной объект
        self.obj = box(
            pos=self.pos,
            size=vector(L0, L0 / 10, L0 / 10),
            color=self.obj_color,
            make_trail=True,
            trail_type="points",
            interval=10,
            retain=100
        )

        # Метка
        self.label_pos = vector(pos.x, pos.y + label_offset_y, pos.z)
        self.create_label()

        # Соединительная линия
        self.connector = curve(color=color.white, radius=1e7)
        self.update_connector()

    def create_label(self):
        if self.obj_type == 'relativistic':
            # Начальные значения для релятивистского объекта
            gamma = 1.0
            p = self.m0 * 0 * gamma
            E_kin = 0
            text = (f"Релятивистский объект\n"
                    f"L = {self.L0:.2e} м\n"
                    f"γ = {gamma:.2f}\n"
                    f"p = {p:.2e} кг·м/с\n"
                    f"E_kin = {E_kin:.2e} Дж")
        else:
            # Начальные значения для классического объекта
            p = self.m0 * 0
            E_kin = 0
            text = (f"Классический объект\n"
                    f"L = {self.L0:.2e} м\n"
                    f"p = {p:.2e} кг·м/с\n"
                    f"E_kin = {E_kin:.2e} Дж")

        self.label = label(
            pos=self.label_pos,
            text=text,
            xoffset=20,
            yoffset=self.label_yoffset,
            height=16,
            border=4,
            font='sans',
            box=True
        )

    def update_connector(self):
        # Обновление соединительной линии
        self.connector.clear()
        if self.label_yoffset > 0:  # Метка снизу
            self.connector.append(
                self.label_pos + vec(0, 40, 0),
                vec(self.obj.pos.x, self.obj.pos.y - self.obj.size.y / 2, 0)
            )
        else:  # Метка сверху
            self.connector.append(
                self.label_pos + vec(0, -40, 0),
                vec(self.obj.pos.x, self.obj.pos.y + self.obj.size.y / 2, 0)
            )

    def update(self, velocity, t):
        # Обновление позиции объекта
        self.obj.pos.x = velocity * t

        # Обновление позиции метки (сохранение вертикального смещения)
        self.label_pos.x = velocity * t
        self.label.pos = self.label_pos

        # Обновление соединительной линии
        self.update_connector()

        # Обновление параметров в зависимости от типа объекта
        if self.obj_type == 'relativistic':
            v_fraction = velocity / c
            gamma = 1 / np.sqrt(1 - v_fraction ** 2)
            p = self.m0 * velocity * gamma  # Релятивистский импульс
            E_kin = (gamma - 1) * self.m0 * c ** 2  # Релятивистская кинетическая энергия

            self.obj.length = self.L0 * np.sqrt(1 - v_fraction ** 2)
            self.label.text = (f"Релятивистский объект\n"
                               f"L = {self.L0 * np.sqrt(1 - v_fraction ** 2):.2e} м\n"
                               f"γ = {gamma:.2f}\n"
                               f"p = {p:.2e} кг·м/с\n"
                               f"Eк = {E_kin:.2e} Дж")
        else:
            # Классические формулы для импульса и энергии
            p = self.m0 * velocity
            E_kin = 0.5 * self.m0 * velocity ** 2
            self.label.text = (f"Классический объект\n"
                               f"L = {self.L0:.2e} м\n"
                               f"p = {p:.2e} кг·м/с\n"
                               f"Eк = {E_kin:.2e} Дж")


# ИНТЕРАКТИВНОЕ УПРАВЛЕНИЕ
def setup_controls(velocity_handler, reset_handler):
    # Очистка предыдущих элементов управления
    scene.caption = ""

    # Создание элементов управления под сценой
    scene.append_to_caption("\n\nСкорость (доля от c): ")
    speed_slider = slider(min=0.01, max=0.99, value=0.5, length=400,
                          bind=lambda s: velocity_handler(s.value))

    scene.append_to_caption("\n\n")
    button(bind=lambda: set_v(0.1, speed_slider, velocity_handler), text="10% c")
    button(bind=lambda: set_v(0.3, speed_slider, velocity_handler), text="30% c")
    button(bind=lambda: set_v(0.5, speed_slider, velocity_handler), text="50% c")
    button(bind=lambda: set_v(0.7, speed_slider, velocity_handler), text="70% c")
    button(bind=lambda: set_v(0.9, speed_slider, velocity_handler), text="90% c")
    button(bind=lambda: set_v(0.99, speed_slider, velocity_handler), text="99% c")

    scene.append_to_caption("\n\n")
    button(bind=reset_handler, text="Перезапуск симуляции")


def set_v(v, slider, handler):
    slider.value = v
    handler(v)


def reset_simulation():
    global t_lab, rel_obj, cls_obj, current_velocity, current_v_fraction

    # Сброс времени
    t_lab = 0

    # Удаление старых объектов
    rel_obj.obj.visible = False
    cls_obj.obj.visible = False
    rel_obj.label.visible = False
    cls_obj.label.visible = False
    rel_obj.connector.visible = False
    cls_obj.connector.visible = False

    # Создание новых объектов
    rel_obj = LabeledObject('relativistic', m0, L0, vector(0, 0, 0), color.red, -L0 - 2e9, 80)
    cls_obj = LabeledObject('classical', m0, L0, vector(0, L0, 0), color.blue, L0 + 2e9, -80)

    # Сброс скорости
    current_velocity = v0 * c
    current_v_fraction = v0


# ОСНОВНАЯ ПРОГРАММА
# Координатные оси
axis_x = cylinder(pos=vec(-1.5e11, 0, 0), axis=vec(3e11, 0, 0), radius=5e6, color=color.white)
axis_y = cylinder(pos=vec(0, -1.5e11, 0), axis=vec(0, 3e11, 0), radius=5e6, color=color.white)

# Создание объектов
rel_obj = LabeledObject('relativistic', m0, L0, vector(0, 0, 0), color.red, -L0 - 2e9, 80)
cls_obj = LabeledObject('classical', m0, L0, vector(0, L0, 0), color.blue, L0 + 2e9, -80)

# Текущая скорость
current_velocity = v0 * c
current_v_fraction = v0


def handle_velocity_change(v_fraction):
    global current_velocity, current_v_fraction
    current_velocity = v_fraction * c
    current_v_fraction = v_fraction


# Настройка элементов управления
setup_controls(handle_velocity_change, reset_simulation)

# Метка времени
time_label = label(
    pos=vector(0, -2.2e10, 0),
    text=f"Лаб. время: 0.0 с\nСобств. время: 0.0 с\nv = {current_v_fraction:.2f}c\nm = {m0:.2f} кг",
    height=24,
    border=6,
    font='sans',
    color=color.white,
    box=True
)

# Главный цикл анимации
t_lab = 0
simulation_complete = False


def run_simulation():
    global t_lab, simulation_complete

    while t_lab < SIMULATION_TIME:
        rate(FPS)

        # Обновление масштаба
        update_scale()

        # Обновление объектов
        rel_obj.update(current_velocity, t_lab)
        cls_obj.update(current_velocity, t_lab)

        # Обновление информации в нижней метке
        gamma = 1 / np.sqrt(1 - (current_velocity / c) ** 2)
        t_obj = t_lab / gamma
        time_label.text = (f"Лаб. время: {t_lab:.1f} с\n"
                           f"Собств. время: {t_obj:.1f} с\n"
                           f"v = {current_v_fraction:.2f}c\n"
                           f"m = {m0:.2f} кг")

        t_lab += 1 / FPS

    simulation_complete = True
    print("\nСимуляция завершена!")
    print("Финальные параметры:")
    gamma = 1 / np.sqrt(1 - current_v_fraction ** 2)
    print(f"• Гамма-фактор: {gamma:.2f}")
    print(f"• Релятивистский импульс: {m0 * current_velocity * gamma:.2e} кг·м/с")
    print(f"• Кинетическая энергия: {m0 * c ** 2 * (gamma - 1):.2e} Дж")
    print(f"• Сокращение длины: {L0 / gamma:.2e} м (изначально {L0:.2e} м)")
    print(f"• Замедление времени: 1 сек лаборатории = {1 / gamma:.3f} сек для объекта")


# Запуск симуляции
run_simulation()

# Бесконечный цикл для предотвращения закрытия вкладки
while True:
    rate(FPS)
    if not simulation_complete:
        run_simulation()
    pass