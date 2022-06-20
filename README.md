# Mouse_Optimization_Project
연세대학교 ESPORTS LAB에서 2022-1학기에 진행한 마우스 전달함수 최적화 프로그램

# 1. 연구목표
E스포츠 플레이어들에게 개인별로 최적화된 마우스 전달함수 세팅

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
2. AutoGain 설계 및 구현
  * Serial Port를 통해 마우스의 움직임 정보(dx, dy, dt, 클릭)를 python 프로그램에 저장
  * 클릭과 클릭 사이의 속도 변화에서 submovement를 추출
  * 추출한 submovement를 기반으로 마우스 전달함수 최적화
  * 최적화를 마친 마우스 전달함수를 듀얼 센서 마우스에 적용
3. 연구검증

# 4. 연구 결과
# 5. 추후 
