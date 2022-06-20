import serial
import math
import copy
import numpy as np
from matplotlib import pyplot as plt
from persistence1d import RunPersistence

# 'COM3' 부분에 환경에 맞는 포트 입력
ser = serial.Serial('COM3', 9600)

# serial port에 's' 전달 -> 마우스 정보 보내기 시작
val = "s\n"
val = val.encode('utf-8')
ser.write(val)

cpi = 1500  # default CPI

kernel = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # smoothing filter(box filter)

gain_x = [1.0] * 200  # x gain
gain_y = [1.0] * 200  # y gain

# sub 1~n까지 저장하는 전역변수
all_data = []  # 0: dx_log, 1: dy_log, 2: dx, 3: dy, 4: s, 5: speed_flag(x_min, x_max, y_min, y_max)

# gain_x의 변화를 가시적으로 확인하기 위한 그래프
LIMIT = 1.25
plt.ion()
fig = plt.figure()
ax = plt.axes(xlim=(0, 10), ylim=(0.97, LIMIT))
plt_line, = ax.plot(np.arange(10), gain_x[0:10])

fig.canvas.draw()
fig.canvas.flush_events()

# 최적화 함수
def optimize(END):
    return

count = 0  # 마우스 총 클릭 횟수
move = 0  # 마우스 총 이동거리
is_double = True  # double click check
rate = 0  # sub n / sub n-1
try:
    while True:
        v = list()  # velocity
        s = list()  # distance

        dx_log = []
        dy_log = []
        dx_abs_log = []  # abs
        dy_abs_log = []  # abs

        while True:
            if ser.readable():
                line = ser.readline().decode()[:- 2]  # line = 'x' + dx + 'y' + dy + 't' + dt
                if not line: continue
                if line[0] == 'x':
                    is_double = False

                    data = line.replace('x', ' ').replace('y', ' ').replace('t', ' ').split()
                    dx = float(data[0]) / 100
                    dy = float(data[1]) / 100
                    dt = float(data[2]) / 1000000  # second

                    dx_log.append(dx)
                    dy_log.append(dy)
                    dx_abs_log.append(abs(dx))
                    dy_abs_log.append(abs(dy))

                    distance = math.sqrt(dx * dx + dy * dy) / cpi * 2.54  # cm
                    velocity = distance / dt  # cm/s

                    move += distance
                    s.append(distance)
                    v.append(velocity)
                elif line[0] == 'p':  # ignore double click
                    if is_double:
                        continue
                    else:  # first click -> optimization
                        count += 1
                        is_double = True
                        break
        
        # smoothing velocity
        smoothed_v = []
        max_smoothed_v = 0
        for j in range(len(v)):
            value = 0
            kernel_sum = 0
            for k in range(-5, 6):
                if 0 <= (j + k) < len(v):
                    value += v[j + k] * kernel[k + 5]
                    kernel_sum += kernel[k + 5]
            max_smoothed_v = max(max_smoothed_v, value / kernel_sum)
            smoothed_v.append(value / kernel_sum)

        if max_smoothed_v == 0: continue

        # persistence 1d
        subdata = np.array(smoothed_v) / max_smoothed_v
        ep = RunPersistence(subdata)
        filtered = [t for t in ep if t[1] > 0.03]
        Sorted = sorted(filtered, key=lambda ep: ep[0])

        prev_min = 0
        for i, E in enumerate(Sorted):
            if i % 2 == 0:
                if E[0] != 0:
                    sub_data = []  # submovement data

                    sub_s = sum(s[prev_min:E[0]])  # submovement distance

                    sub_min_x = min(dx_abs_log[prev_min:E[0]])  # submovement min_x
                    sub_max_x = max(dx_abs_log[prev_min:E[0]])  # submovement max_x
                    sub_min_y = min(dy_abs_log[prev_min:E[0]])  # submovement min_y
                    sub_max_y = max(dy_abs_log[prev_min:E[0]])  # submovement max_y

                    sub_data.append(copy.deepcopy(dx_log[prev_min:E[0]]))
                    sub_data.append(copy.deepcopy(dy_log[prev_min:E[0]]))
                    sub_data.append(sum(dx_log[prev_min:E[0]]))
                    sub_data.append(sum(dy_log[prev_min:E[0]]))
                    sub_data.append(sub_s)
                    sub_data.append([sub_min_x, sub_max_x, sub_min_y, sub_max_y])

                    # submovement를 저장하기 전 최적화 조건에 부합하는지 확인
                    if len(all_data) == 0:  # all_data에 submovement가 없다면 pass
                        pass
                    elif len(all_data) == 1:  # submovement가 1개인 경우
                        if all_data[0][4] != 0:  # 저장된 submovement의 이동거리가 0이 아니라면 rate 계산
                            rate = sub_s / all_data[0][4]
                        else:  # 저장된 submovement의 이동거리가 0이라면 해당 submovement 삭제
                            all_data.clear()
                    else:  # submovement가 2개 이상인 경우
                        if all_data[-1][4] == 0:  # 마지막 submovement의 이동거리가 0이라면 새로운 submovement가 sub 1이기 때문에 바로 최적화
                            target_dx = 0
                            target_dy = 0
                            for sub in all_data[0:-2]:
                                target_dx += sub[2]
                                target_dy += sub[3]

                            target_dx = abs(target_dx)
                            target_dy = abs(target_dy)

                            if all_data[0][2] != 0:
                                rx = 1 + ((target_dx - abs(all_data[0][2])) / abs(all_data[0][2]) * 0.00001)
                            else:
                                rx = 1
                            if all_data[0][3] != 0:
                                ry = 1 + ((target_dy - abs(all_data[0][3])) / abs(all_data[0][3]) * 0.00001)
                            else:
                                ry = 1

                            for i in range(int(all_data[0][5][0] * 2), min(int(all_data[0][5][1] * 2), 199) + 1):
                                gain_x[i] *= rx

                            for i in range(int(all_data[0][5][2] * 2), min(int(all_data[0][5][3] * 2), 199) + 1):
                                gain_x[i] *= ry

                            msg = 'O' + str(int(all_data[0][5][0] * 2)) + ',' + str(
                                min(int(all_data[0][5][1] * 2), 199)) + ',' + str(
                                int(abs(all_data[0][2] * 2))) + ',' + str(int(target_dx * 2)) + ',' + str(
                                int(all_data[0][5][2] * 2)) + ',' + str(
                                min(int(all_data[0][5][3] * 2), 199)) + ',' + str(
                                int(abs(all_data[0][3] * 2))) + ',' + str(int(target_dy * 2)) + "\n"

                            ser.write(msg.encode('utf-8'))
                            all_data.clear()
                        elif rate > sub_s / all_data[-1][4]:  # sub n이 sub 1인지 확인하는 조건(만족하면 sub n이 sub 1)
                            rate = sub_s / all_data[-1][4]
                            target_dx = 0
                            target_dy = 0
                            for sub in all_data[0:-1]:
                                target_dx += sub[2]
                                target_dy += sub[3]

                            target_dx = abs(target_dx)
                            target_dy = abs(target_dy)

                            if all_data[0][2] != 0:
                                rx = 1 + ((target_dx - abs(all_data[0][2])) / abs(all_data[0][2]) * 0.00001)
                            else:
                                rx = 1
                            if all_data[0][3] != 0:
                                ry = 1 + ((target_dy - abs(all_data[0][3])) / abs(all_data[0][3]) * 0.00001)
                            else:
                                ry = 1

                            for i in range(int(all_data[0][5][0] * 2), min(int(all_data[0][5][1] * 2), 199) + 1):
                                gain_x[i] *= rx

                            for i in range(int(all_data[0][5][2] * 2), min(int(all_data[0][5][3] * 2), 199) + 1):
                                gain_x[i] *= ry

                            msg = 'O' + str(int(all_data[0][5][0] * 2)) + ',' + str(
                                min(int(all_data[0][5][1] * 2), 199)) + ',' + str(
                                int(abs(all_data[0][2] * 2))) + ',' + str(int(target_dx * 2)) + ',' + str(
                                int(all_data[0][5][2] * 2)) + ',' + str(
                                min(int(all_data[0][5][3] * 2), 199)) + ',' + str(
                                int(abs(all_data[0][3] * 2))) + ',' + str(int(target_dy * 2)) + "\n"

                            ser.write(msg.encode('utf-8'))

                            all_data = [copy.deepcopy(all_data[-1])]  # sub n만 남겨 놓고 전부 삭제
                        else:  # sub 1이 없다면 rate 계산 후 종료
                            rate = sub_s / all_data[-1][4]

                    all_data.append(copy.deepcopy(sub_data))

                    prev_min = E[0]

        print("p")
        if len(all_data) == 0: continue  # 저장된 submovement가 없다면 coutinue

        target_dx = 0
        target_dy = 0
        for sub in all_data:
            target_dx += sub[2]
            target_dy += sub[3]

        target_dx = abs(target_dx)
        target_dy = abs(target_dy)

        if all_data[0][2] != 0:
            rx = 1 + ((target_dx - abs(all_data[0][2])) / abs(all_data[0][2]) * 0.00001)
        else:
            rx = 1
        if all_data[0][3] != 0:
            ry = 1 + ((target_dy - abs(all_data[0][3])) / abs(all_data[0][3]) * 0.00001)
        else:
            ry = 1

        for i in range(int(all_data[0][5][0] * 2), min(int(all_data[0][5][1] * 2), 199) + 1):
            gain_x[i] *= rx

        for i in range(int(all_data[0][5][2] * 2), min(int(all_data[0][5][3] * 2), 199) + 1):
            gain_x[i] *= ry

        msg = 'O' + str(int(all_data[0][5][0] * 2)) + ',' + str(min(int(all_data[0][5][1] * 2), 199)) + ',' + str(
            int(abs(all_data[0][2] * 2))) + ',' + str(int(target_dx * 2)) + ',' + str(
            int(all_data[0][5][2] * 2)) + ',' + str(min(int(all_data[0][5][3] * 2), 199)) + ',' + str(
            int(abs(all_data[0][3] * 2))) + ',' + str(int(target_dy * 2)) + "\n"

        ser.write(msg.encode('utf-8'))

        all_data.clear()

        # 클릭마다 gain_x 그래프 수정
        if max(gain_x[0:10]) >= LIMIT:
            LIMIT = max(gain_x[0:10]) + 0.1
        ax.set_ylim(0.97, LIMIT)
        plt_line.set_ydata(gain_x[0:10])
        fig.canvas.draw()
        fig.canvas.flush_events()

except KeyboardInterrupt:
    print("distance: " + str(move))  # 총 이동거리 출력
    print("count: " + str(count))  # 총 클릭 횟수 출력

    # serial port에 'e' 전달 -> 마우스 정보 보내기 종료
    val = "e\n"
    val = val.encode('utf-8')
    ser.write(val)