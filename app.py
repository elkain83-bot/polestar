import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import datetime
import os

# 페이지 기본 설정
st.set_page_config(page_title="쇼핑 미션", layout="wide")

# 세션 상태 초기화
if "page" not in st.session_state:
    st.session_state.page = "start"

if "budget" not in st.session_state:
    st.session_state.budget = None

if "cart" not in st.session_state:
    st.session_state.cart = []

if "products" not in st.session_state:
    try:
        st.session_state.products = pd.read_csv("products.csv")
    except:
        st.error("❌ products.csv 파일을 찾을 수 없습니다.")
        st.stop()


# ------------------------------------------
# 🟦 1. 시작 화면
# ------------------------------------------
def start_page():
    st.title("🎯 미션 선택하기")

    st.write("미션에 따라 예산이 다르게 주어집니다. 원하는 미션을 선택하세요.")

    budget_options = {
        "기본 미션 (예산 10,000원)": 10000,
        "중급 미션 (예산 20,000원)": 20000,
        "고급 미션 (예산 30,000원)": 30000,
    }

    choice = st.radio("미션 선택", list(budget_options.keys()))

    if st.button("선택 완료"):
        st.session_state.budget = budget_options[choice]
        st.session_state.page = "shop"
        st.experimental_rerun()


# ------------------------------------------
# 🟩 2. 쇼핑 화면
# ------------------------------------------
def shopping_page():
    st.title("🛒 쇼핑하기")

    st.write(f"💰 현재 예산: **{st.session_state.budget:,}원**")
    st.write("---")

    products = st.session_state.products

    for idx, row in products.iterrows():
        cols = st.columns([1, 2, 1])

        with cols[0]:
            try:
                st.image(row["image_url"], width=120)
            except:
                st.write("(이미지 로드 불가)")

        with cols[1]:
            st.write(f"### {row['name']}")
            st.write(f"가격: **{row['price']:,}원**")

        with cols[2]:
            if st.button("담기", key=f"add_{idx}"):
                st.session_state.cart.append(row.to_dict())
                st.success(f"{row['name']} 장바구니에 담김!")

        st.write("---")

    if st.button("🧺 구매하기 (결과로 이동)"):
        st.session_state.page = "result"
        st.experimental_rerun()


# ------------------------------------------
# PNG 파일 생성 함수
# ------------------------------------------
def create_result_png(reason_text, cart_items):
    width, height = 800, 600
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    title = "🛒 구매 결과"
    draw.text((20, 20), title, fill="black")

    y = 80
    draw.text((20, y), "📦 구매한 물품:", fill="black")
    y += 40

    for item in cart_items:
        draw.text((40, y), f"- {item['name']} / {item['price']:,}원", fill="black")
        y += 30

    y += 20
    draw.text((20, y), "📝 구매 이유:", fill="black")
    y += 40
    draw.text((40, y), reason_text, fill="black")

    filename = f"result_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    img.save(filename)

    return filename


# ------------------------------------------
# 🟥 3. 결과 화면
# ------------------------------------------
def result_page():
    st.title("📊 결과 화면")

    st.write("🧺 **구매한 물품 목록**")
    total_price = sum([item["price"] for item in st.session_state.cart])
    st.write(f"총 비용: **{total_price:,}원** / 예산 {st.session_state.budget:,}원")

    for item in st.session_state.cart:
        st.write(f"- {item['name']} / {item['price']:,}원")

    st.write("---")

    st.write("### 📝 구매 이유 작성")
    reason = st.text_area("구매 이유를 작성하세요.", height=150)

    if st.button("제출"):
        if reason.strip() == "":
            st.warning("구매 이유를 입력해주세요.")
            return

        filename = create_result_png(reason, st.session_state.cart)
        st.success("제출 완료! PNG 파일이 생성되었습니다.")

        with open(filename, "rb") as f:
            st.download_button(
                label="결과 PNG 다운로드",
                data=f,
                file_name=filename,
                mime="image/png"
            )


# ------------------------------------------
# 화면 라우팅
# ------------------------------------------
if st.session_state.page == "start":
    start_page()

elif st.session_state.page == "shop":
    shopping_page()

elif st.session_state.page == "result":
    result_page()
