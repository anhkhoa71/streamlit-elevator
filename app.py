import streamlit as st
import numpy as np
import time
from main import InputData, TotalWaitElevator

st.title("🚪 Mô phỏng thang máy: Thang máy hay thang bộ?")

# Sidebar - cấu hình
st.sidebar.header("🔧 Cài đặt hằng số")
t_between = st.sidebar.slider("⏱Thời gian đi qua 1 tầng (giây)", 1, 10, 2)
t_floor = st.sidebar.slider("Thời gian dừng mở cửa mỗi tầng (giây)", 1, 20, 10)
t_walk = st.sidebar.slider("Thời gian đi bộ mỗi tầng (giây)", 1, 60, 30)
total_floor = st.sidebar.slider("Tầng cao nhất của thang máy", 1, 30, 7)

# Khởi tạo session state
if 'input_data' not in st.session_state:
    st.session_state.input_data = InputData(
        tbetween=t_between,
        tfloor=t_floor,
        total_floors=total_floor,
        twalk_between=t_walk
    )
    st.session_state.time_last_elevator = time.time()

input_data = st.session_state.input_data
time_last_elevator = st.session_state.time_last_elevator

# Nút mở thang máy
if st.button("Mở thang máy"):
    input_data.pop_previous_student()
    st.session_state.time_last_elevator = time.time()

# Chọn tầng đến
destination_floor = st.selectbox("Tầng muốn đến", [i for i in range(1, input_data.elevator.total_floors + 1)])

# Nút xếp hàng
if st.button("Xếp hàng"):
    input_data.new_student_requests(destination_floor)

    elevator = TotalWaitElevator(
        t_floor=input_data.elevator.tfloor,
        t_between=input_data.elevator.tbetween,
        walk_between=input_data.twalk_between
    )

    elevator.fit(
        array_floor=np.array(input_data.get_previous_student()),
        time_last_elevator=st.session_state.time_last_elevator,
        floor_self=destination_floor
    )

    st.subheader("📊 Kết quả mô phỏng")
    st.write(f"⏱️ Thời gian dùng **thang máy**: `{elevator.use_elevator:.2f} giây`")
    st.write(f"🚶‍♀️ Thời gian dùng **thang bộ**: `{elevator.use_stair:.2f} giây`")

    if elevator.recommend == 1:
        st.success("✅ **Khuyến nghị: NÊN dùng thang máy.**")
    else:
        st.warning("⚠️ **Khuyến nghị: NÊN đi bộ.**")

if st.button("Chọn thang bộ"):
    input_data.back_previous_student()

# Hiển thị nhóm sinh viên
st.subheader("👥 Các nhóm sinh viên đã gọi thang máy")
for i, group in enumerate(input_data.get_previous_student()):
    st.text(f"Nhóm {i+1}: " + ', '.join(str(int(f)) for f in group if f != 0))
