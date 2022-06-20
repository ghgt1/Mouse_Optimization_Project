# Mouse_Optimization_Project
연세대학교 ESPORTS LAB에서 2022-1학기에 진행한 마우스 전달함수 최적화 프로그램
Python으로 최적화 프로그램을 실행하고, 아두이노를 사용하여 마우스와 통신하였다.

# 1. 연구목표
*E스포츠 플레이어들에게 개인별로 최적화된 마우스 전달함수 세팅

전달함수란 마우스가 실제로 움직인 거리와 마우스 커서가 공간상에서 움직인 거리 사이의 상관관계를 결정한다. 이것을 개인별로 최적화해 더 나은 게임 performance를 낼 수 있게 한다.

# 2. 연구의 필요성
1. 기존의 전달함수의 한계

![image](https://user-images.githubusercontent.com/35508595/174531913-168bf631-dacf-4c28-9684-a2f991aad3d9.png)


Preset이 정해져있는 기존의 전달함수

2. 게임 프로그램의 전달함수 override 불가
이러한 전달함수는 software 레벨로는 우회 불가

3. Autogain 함수의 Target 특정

![image](https://user-images.githubusercontent.com/35508595/174532095-0eb33f8b-1267-4ec8-b787-cafa460d3004.png)

Undershoot,overshoot을 활용한 오차값 보정
    
# 3. 연구내용
1. 준비물 – 듀얼 센서 마우스

![image](https://user-images.githubusercontent.com/35508595/174532411-44c26be8-6dd6-45c8-bc5d-1a3c0ece7954.png)


2. AutoGain 설계 및 구현
  * Serial Port를 통해 마우스의 움직임 정보(dx, dy, dt, 클릭)를 python 프로그램에 저장
  * 클릭과 클릭 사이의 속도 변화에서 submovement를 추출
  
  ![image](https://user-images.githubusercontent.com/35508595/174532480-35682b08-a647-4072-810c-0d14dfddc5d1.png)
  

  * 추출한 submovement를 기반으로 마우스 전달함수 최적화
  
  ![image](https://user-images.githubusercontent.com/35508595/174532549-a7c7f341-ac27-4004-847a-4c28eac79f62.png)


  * 최적화를 마친 마우스 전달함수를 듀얼 센서 마우스에 적용
3. 연구검증

![image](https://user-images.githubusercontent.com/35508595/174532625-49619da8-0930-4a33-9d28-d0bedb00fe1b.png)

AIMLAB프로그램을 기반으로 최대한 객관적인 검증 수행

# 4. 연구 결과

### [표 넣기]
|변화율|점수|정확도|TTK|
|:---:|:---:|:---:|:---:|
|최소|10.97|1.04|8.10|
|최대|29.21|5.01|18.21|
|평균|21.48|2.66|15.00|



<br>

전체적인 마우스 퍼포먼스의 향상
# 5. 추후 연구 가능성
x축과 y축 움직임의 부호까지 
