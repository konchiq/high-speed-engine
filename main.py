from vpython import *
import numpy as np

# Константы
c = 3e8  # Скорость света (м/с)

# Ввод параметров
m0 = float(input("Введите массу покоя объекта (кг): "))
L0 = float(input("Введите длину объекта (м): "))
v_fraction = float(input("Введите скорость объекта (доля от c, 0 < v < 1): "))

if not 0 < v_fraction < 1:
    raise ValueError("Скорость должна быть в интервале (0, 1)")

# Релятивистские параметры
gamma = 1 / np.sqrt(1 - v_fraction ** 2)
v = v_fraction * c
contracted_length = L0 * np.sqrt(1 - v_fraction ** 2)

# Настройка сцены
scene = canvas(title='Релятивистское движение', width=1200, height=800)
scene.range = 2e10
scene.forward = vector(-0.5, -0.5, -1)

# Создание осей координат
axis_x = cylinder(pos=vec(-1e11, 0, 0), axis=vec(2e11, 0, 0), radius=3e6, color=color.white)
axis_y = cylinder(pos=vec(0, -1e11, 0), axis=vec(0, 2e11, 0), radius=3e6, color=color.white)
axis_z = cylinder(pos=vec(0, 0, -1e11), axis=vec(0, 0, 2e11), radius=3e6, color=color.white)

# Создание объектов
relativistic_obj = box(pos=vector(0, 0, 0),
                       size=vector(contracted_length, L0 / 10, L0 / 10),
                       color=color.red,
                       make_trail=True,
                       trail_type="points",
                       interval=50,
                       retain=100)

classical_obj = box(pos=vector(0, L0, 0),
                    size=vector(L0, L0 / 10, L0 / 10),
                    color=color.blue,
                    make_trail=True,
                    trail_type="points",
                    interval=50,
                    retain=100)


# Метки только с длиной (без скорости)
rel_label = label(pos=relativistic_obj.pos + vector(0, L0/2 + 1e9, 0),
                 text='Релятивистский объект\n' + f'L = {contracted_length:.2e} м',  # Только длина
                 xoffset=20,
                 yoffset=-60,
                 height=14,
                 border=3,
                 font='sans')

cls_label = label(pos=classical_obj.pos + vector(0, -L0/2 - 1e9, 0),
                 text='Классический объект\n' + f'L = {float(L0):.2e} м',  # Только длина
                 xoffset=20,
                 yoffset=40,
                 height=14,
                 border=3,
                 font='sans')

time_label = label(pos=vector(0, -2e10, 0),
                   text=f"Лаб. время: 0 с\nСобств. время: 0 с\nv = {v_fraction:.2f}c", # Скорость
                   height=24,
                   border=6,
                   font='sans')

# Параметры анимации
dt = 0.1  # Шаг времени (с)
t_lab = 0  # Лабораторное время

# Запуск анимации
while t_lab < 100:
    rate(10)  # Ограничение частоты обновления

    # Обновление положения релятивистского объекта
    relativistic_obj.pos.x = v * t_lab
    rel_label.pos = relativistic_obj.pos

    # Обновление положения классического объекта
    classical_obj.pos.x = v * t_lab
    classical_obj.pos.y = L0  # Поддерживаем вертикальное смещение
    cls_label.pos = classical_obj.pos

    # Расчет собственного времени
    t_obj = t_lab / gamma

    # Обновление меток
    time_label.text = (f"Лаб. время: {t_lab:.1f} с\n"
                       f"Собств. время: {t_obj:.1f} с\n"
                       f"v = {v_fraction:.2f}c")

    # Обновление формы релятивистского объекта
    relativistic_obj.length = contracted_length
    relativistic_obj.height = L0 / 10 * (1 + 0.5 * v_fraction ** 2)  # Визуальный эффект
    relativistic_obj.width = L0 / 10 * (1 + 0.5 * v_fraction ** 2)

    t_lab += dt

# Вывод релятивистских параметров в консоль
print("\nРелятивистские эффекты:")
print(f"1. Гамма-фактор: {gamma:.2f}")
print(f"2. Релятивистская масса: {m0 * gamma:.2f} кг")
print(f"3. Сокращение длины: {contracted_length:.2f} м")
print(f"4. Замедление времени: 1 сек лаборатории = {1 / gamma:.2f} сек для объекта")
